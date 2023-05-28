import re
import yaml
import stanza
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from train import FastTextTrainer
from collections import defaultdict


def remove_special_chars(text):
    if type(text) is str and len(text) > 1:
        text = text.strip()
        if text[0] in ["'", '"', '`', ".", "*", ","]:
            text = text[1:]
        if text[-1] in ["'", '"', '`', ".", "*", ","]:
            text = text[:-1]
    return text


def extract_special_format_elements(text):
    output = (
            re.findall(r'`[^`]*`', text) +
            re.findall(r'"[^"]*"', text) +
            re.findall(r"'[^']*'(?!\w)", text) +
            re.findall(r'\{[^\}]*\}', text)
    )

    if '- ' in text:
        temp_text = text[text.find("- "):]
        temp = re.findall('-[^\n]*\n', temp_text)
        temp.append(temp_text[temp_text.rfind('-'):])
        for t in temp:
            focus_value = t.strip().strip('-').strip().split()[0]
            output.append(focus_value)

    if '* ' in text:
        temp_text = text[text.find("* "):]
        temp = re.findall('\*[^\n]*\n', temp_text)
        temp.append(temp_text[temp_text.rfind('*'):])
        for t in temp:
            focus_value = t.strip().strip('*').strip().split()[0]
            output.append(focus_value)

    temp_output = list(set(output))

    for i in reversed(range(len(temp_output))):
        if "\"" in temp_output[i] or "'" in temp_output[i]:
            for j in reversed(range(len(temp_output))):
                if i != j and temp_output[i] in temp_output[j]:
                    del (temp_output[i])
                    break

    for i in reversed(range(len(temp_output))):
        temp_output[i] = remove_special_chars(temp_output[i].strip())

    return temp_output


def extract_values(target_values, param_name, param_names):
    values = []
    for element in target_values:
        if '=' in element:
            e1 = element[:element.find('=')]
            e2 = element[element.find('=') + 1:]
            if e1 == param_name:
                values.append(e2)
            elif e1 in param_names:
                pass
            else:
                values.append(element)
        else:
            values.append(element)
    return values


class RuleExtractor:
    def __init__(self, settings_path, model_path):
        # Load settings
        with open(settings_path, 'r') as f:
            self.settings = yaml.safe_load(f)

        # Load the FastText model
        fasttext_trainer = FastTextTrainer("./APIs-guru/specifications", model_path)
        self.model = fasttext_trainer.load_model(model_path)

        # Set up the Stanza pipeline
        self.nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,constituency', logging_level="FATAL")
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.stop_words.update(["parameter", "type", "format", "tag", "operation", "schema"])

    def match_keywords_and_values(self, word):
        matched_rule = {}
        for category, category_data in self.settings.items():
            if category == "enum":
                for keyword, values in category_data.items():
                    for value, terms in values.items():
                        if word in terms:
                            matched_rule[keyword] = value
                            return matched_rule
                    for value, terms in values.items():
                        for term in terms:
                            similarity = self.model.wv.similarity(word, term)
                            if round(similarity, 2) > 0.7:
                                matched_rule[keyword] = value
                                return matched_rule
            else:
                for keyword, values in category_data.items():
                    if word in values:
                        return keyword
                for keyword, values in category_data.items():
                    for term in values:
                        similarity = self.model.wv.similarity(word, term)
                        if round(similarity, 2) > 0.7:
                            return keyword

    def traverse_tree(self, node, param_names, found_rules, found_params, found_values, sbar_param, sbar_value,
                      sbar_rule):
        flag = True

        if node.children and len(node.leaf_labels()) == 1:
            word = node.leaf_labels()[0]
            if len(word) > 1:
                word = remove_special_chars(word.strip())
                if param_names:
                    for param in param_names:
                        if param == word:
                            found_params.append(word)
                            flag = False
                            break
                if flag:
                    lemma = self.lemmatizer.lemmatize(word.lower())
                    rule = self.match_keywords_and_values(lemma)
                    if rule:
                        found_rules.append(rule)
                        flag = False
        if flag:
            if node.label in ["CD", "NNP", "NN"] or (node.label == "NP" and (
                    len(node.leaf_labels()) == 1 or (len(node.leaf_labels()) == 2 and node.leaf_labels()[-1] == '.'))):
                word = node.leaf_labels()[0]
                is_num = False
                try:
                    word = int(word.replace(',', '').replace('.', ''))
                    is_num = True
                except Exception:
                    pass
                for i in range(len(found_rules)):
                    if found_rules[i] == "default":
                        found_rules[i] = {"default": word}
                        break
                    elif is_num and found_rules[i] == "minimum":
                        found_rules[i] = {"minimum": word}
                        break
                    elif is_num and found_rules[i] == "maximum":
                        found_rules[i] = {"maximum": word}
                        break
                    elif found_rules[i] == "example" and word not in param_names:
                        found_values.append(word)
            elif (node.label == "NP" or node.label == "VP") and "(, ,)" in str(node) and "example" in found_rules:
                words = ' '.join(node.leaf_labels())
                for child in node.children:
                    if child.label == "NP":
                        start = child.leaf_labels()[0]
                        words = words[words.find(start):].split(',')
                        for word in words:
                            found_values.append(word.strip())
                        break
            elif not sbar_param and not sbar_value and node.label == "SBAR":
                self.process_sbar(node, sbar_rule, sbar_value, sbar_param, param_names)
            else:
                for child in node.children:
                    self.traverse_tree(child, param_names, found_rules, found_params, found_values, sbar_param,
                                       sbar_value, sbar_rule)

    def process_sbar(self, node, sbar_rule, sbar_value, sbar_param, param_names):
        flag = True

        if node.children and len(node.leaf_labels()) == 1:
            word = node.leaf_labels()[0]
            if len(word) > 1:
                word = remove_special_chars(word.strip())
                if param_names:
                    for param in param_names:
                        if param == word:
                            sbar_param.append(word)
                            flag = False
                            break
                if flag:
                    lemma = self.lemmatizer.lemmatize(word.lower())
                    rule = self.match_keywords_and_values(lemma)
                    if rule:
                        sbar_rule.append(rule)
                        flag = False
        if flag:
            for child in node.children:
                if child.label == "JJ":
                    sbar_value.append(node.leaf_labels()[0])
                self.process_sbar(child, sbar_rule, sbar_value, sbar_param, param_names)

    def extract_rules(self, param_names, param_name, param_description):
        if param_description:
            if param_description[0] == "'" or param_description[0] == '"':
                param_description = param_description[1:]
            if param_description[-1] == "'" or param_description[-1] == '"':
                param_description = param_description[:-1]
            doc = self.nlp(param_description)
            rules = []
            special_format_elements = extract_special_format_elements(param_description)
            if special_format_elements:
                for i in reversed(range(len(special_format_elements))):
                    if special_format_elements[i] in param_names:
                        del (special_format_elements[i])
            has_sfe = False
            # Traverse the constituency parse tree for each sentence
            for sentence in doc.sentences:
                processed_rules = []
                found_rules = []
                found_params = []
                found_values = []
                sbar_rule = []
                sbar_param = []
                sbar_value = []
                enumerated_text = ''.join(sentence.text.lower().split())
                if param_name in enumerated_text and ':' in enumerated_text:
                    if special_format_elements:
                        values = extract_values(special_format_elements, param_name, param_names)
                        rules.append({"example": values})
                        has_sfe = True
                    else:
                        enumerated_text = enumerated_text[enumerated_text.find(":") + 1:]
                        if ',' in enumerated_text:
                            sen = sentence.text[sentence.text.find(':') + 1:]
                            found_values = sen.split(',')
                            values = []
                            for value in found_values:
                                value = remove_special_chars(value.strip())
                                values.append(value)
                            has_sfe = True
                            rules.append({"example": values})

                root = sentence.constituency.children[0]
                self.traverse_tree(root, param_names, found_rules, found_params, found_values, sbar_param, sbar_value,
                                   sbar_rule)
                used_value = []

                for rule in found_rules:
                    if type(rule) is dict:
                        used_value.append(rule[list(rule.keys())[0]])
                for rule in found_rules:
                    if not has_sfe and rule == "example" and "example" not in processed_rules:
                        processed_rules.append("example")
                        if special_format_elements:
                            values = extract_values(special_format_elements, param_name, param_names)
                            rule = {"example": values}
                            rules.append(rule)
                            has_sfe = True
                        elif found_values:
                            values = []
                            for value in found_values:
                                values.append(value)
                            if values:
                                rule = {"example": values}
                                rules.append(rule)
                    elif rule in ["Or", "OnlyOne", "AllOrNone", "ZeroOrOne"]:
                        if len(found_params) == 2 and found_params[0] != param_name and found_params[1] != param_name:
                            if sbar_value:
                                rule = {"IPD": [
                                    "IF " + param_name + " == " + sbar_value[0] + " THEN " + rule + "(" + param_name + "," +
                                    found_params[0] + ")"]}
                                if rule not in rules:
                                    rules.append(rule)
                        elif len(found_params) > 0 and found_params[0] != param_name:
                            rule = {"IPD": [rule + "(" + param_name + "," + found_params[0] + ")"]}
                            rules.append(rule)
                    elif rule == "requires":
                        if special_format_elements:
                            for param in param_names:
                                for element in special_format_elements:
                                    if param != param_name and param in element:
                                        rule = {"IPD": ["IF " + param_name + " THEN " + element]}
                                        rules.append(rule)
                                        break
                    elif type(rule) is dict:
                        if rule not in rules:
                            rules.append(rule)
                for rule in sbar_rule:
                    if rule == "requires":
                        if sbar_param:
                            pass
                        else:
                            if found_params and found_params[0] != param_name:
                                if found_values:
                                    rule = {"IPD": [
                                        "IF " + param_name + " THEN " + found_params[0] + " == " + found_values[0]]}
                                else:
                                    rule = {"IPD": ["IF " + param_name + " THEN " + found_params[0]]}
                                rules.append(rule)

            rules_dict = defaultdict(list)

            for rule in rules:
                for key, values in rule.items():
                    if type(values) is list:
                        for value in values:
                            value = remove_special_chars(value)
                            if value not in rules_dict[key]:
                                if type(value) is str:
                                    if value.lower() not in self.stop_words:
                                        rules_dict[key].append(value)
                                else:
                                    rules_dict[key].append(value)
                    elif values not in rules_dict[key]:
                        values = remove_special_chars(values)
                        if values not in rules_dict[key]:
                            if type(values) is str:
                                if values.lower() not in self.stop_words:
                                    rules_dict[key].append(values)
                            else:
                                rules_dict[key].append(values)

            rules_dict = dict(rules_dict)
            return rules_dict
