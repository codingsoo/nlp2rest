import os
import re
import yaml
import nltk
import pandas as pd
from tqdm import tqdm
from yaml import Loader
from gensim.models import FastText
from gensim.models import Word2Vec
from nltk import WordNetLemmatizer


def preprocess_text(document):
    """
    Preprocesses a given document by performing several operations:
    1. Removing extra white spaces
    2. Removing all special characters
    3. Removing all single characters
    4. Converting to lowercase
    5. Tokenizing the words
    6. Lemmatizing the tokens
    7. Removing English stop words

    Parameters:
    document (str): The document to be preprocessed.

    Returns:
    str: The preprocessed document as a string of lemmatized words.
    """
    stemmer = WordNetLemmatizer()
    en_stop = set(nltk.corpus.stopwords.words('english'))

    # Remove extra white space from text
    document = re.sub(r'\s+', ' ', document, flags=re.I)

    # Remove all the special characters from text
    document = re.sub(r'\W', ' ', str(document))

    # Remove all single characters from text
    document = re.sub(r'\s+[a-zA-Z]\s+', ' ', document)

    # Converting to Lowercase
    document = document.lower()

    # Word tokenization
    tokens = document.split()
    lemma_txt = [stemmer.lemmatize(word) for word in tokens]
    lemma_no_stop_txt = [word for word in lemma_txt if word not in en_stop]

    clean_txt = ' '.join(lemma_no_stop_txt)

    return clean_txt


class FastTextTrainer:
    """
    A class to train a FastText model from a directory of specification files.

    Attributes:
    specs_dir (str): The path to the directory containing the specification files.
    output_model_file (str): The path to the file where the trained model will be saved.
    model (gensim.models.Word2Vec): The trained FastText model.

    Methods:
    extract_description_summary(search_dict: dict) -> list:
        Extracts the "description" and "summary" fields from a nested dictionary.
    train_model():
        Processes the text data from the specification files, trains the FastText model, and saves the model to a file.
    load_model(model_path: str):
        Loads a pre-trained FastText model from a given file path. If no model exists at that path, trains a new model.
    """
    def __init__(self, specs_dir, output_model_file):
        """
        Initializes the FastTextTrainer with a directory of specification files and the path to the output model file.

        Parameters:
        specs_dir (str): The path to the directory containing the specification files.
        output_model_file (str): The path to the file where the trained model will be saved.
        """
        self.specs_dir = specs_dir
        self.output_model_file = output_model_file
        self.model = None

    def extract_description_summary(self, search_dict):
        """
        Takes a dict with nested lists and dicts,
        and searches all dicts for a key of the "description" and "summary" field.
        """
        fields_found = []

        for key, value in search_dict.items():

            if key == "description":
                fields_found.append(value)
            elif key == "summary":
                fields_found.append(value)
            elif isinstance(value, dict):
                results = self.extract_description_summary(value)
                for result in results:
                    fields_found.append(result)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        more_results = self.extract_description_summary(item)
                        for another_result in more_results:
                            fields_found.append(another_result)

        return fields_found

    def train_model(self):
        """
        Processes the text data from a given directory of specifications and trains a FastText model. The processing
        includes extracting descriptions and summaries, preprocessing the text, and storing the processed data. It also
        provides progress information during processing and training.

        The trained model is saved to a file and stored in the 'model' attribute of the class.

        Note: This function modifies the 'model' attribute of the class.

        Raises:
        Exception: If there is any error during processing the specifications or training the model.
        """
        swaggers = [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.specs_dir) for f in filenames]
        total_swagger = len(swaggers)
        total_processed = 0

        num_swagger = 0
        num_nl = 0
        no_nl = 0
        result = ""
        for swagger in swaggers:
            print(swagger + " is processing...")
            total_processed = total_processed + 1
            with open(swagger) as f:
                try:
                    data = yaml.load(f, Loader=Loader)
                    num_swagger = num_swagger + 1

                    nls = self.extract_description_summary(data)
                    if not nls:
                        no_nl = no_nl + 1
                        print("No NL!")
                        continue
                    for nl in nls:
                        if isinstance(nl, str):
                            processed_nl = preprocess_text(nl)
                            if len(processed_nl) > 3:
                                result = result + "{\"text\": \"" + processed_nl + "\"}\n"
                                num_nl = num_nl + 1

                    if num_swagger % 200 == 0:
                        print("Processed " + str(total_processed) + " out of " + str(total_swagger) + '.')
                        print("Saved!")
                        with open("nl.json", 'w') as fnl:
                            fnl.write(result)

                except Exception as msg:
                    print(msg)

        print(str(total_processed) + " number of specifications are processed.")
        print(str(num_nl) + " number of descriptions are processed.")

        with open("nl.json", 'w') as fnl:
            fnl.write(result)

        rest_df = pd.read_json("nl.json", lines=True)
        all_sent = list(rest_df['text'])

        word_tokenizer = nltk.WordPunctTokenizer()
        word_tokens = [word_tokenizer.tokenize(sent) for sent in tqdm(all_sent)]

        # Defining values for parameters
        window_size = 3
        min_word = 3
        down_sampling = 1e-2

        fasttext_model = FastText(word_tokens,
                                  window=window_size,
                                  min_count=min_word,
                                  sample=down_sampling,
                                  workers=4,
                                  sg=1)

        fasttext_model.save(self.output_model_file)
        return Word2Vec.load(self.output_model_file)

    def load_model(self, model_path):
        """
        Loads a pre-trained FastText model from the given file path.

        Parameters:
        model_path (str): The path to the model file.

        Note: This function modifies the 'model' attribute of the class.
        """
        if os.path.exists(model_path):
            print(f"Loading existing model from '{model_path}'.")
            return Word2Vec.load(model_path)
        else:
            print(f"Training new model, as '{model_path}' not found.")
            ft_trainer = FastTextTrainer(specs_dir="../APIs-guru/specifications", output_model_file=model_path)
            ft_trainer.train_model()
            return Word2Vec.load(model_path)
