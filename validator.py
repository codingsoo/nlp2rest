import copy
import sys
import json
import requests
import urllib.parse
from prance import ResolvingParser


def send_body_request(_url, _header, _data, _param):
    try:
        if operation == "post":
            _res = requests.post(url=_url, headers=_header, data= _param + '=' + urllib.parse.quote(str(_data).replace("'", "\"")))
        else:
            _res = requests.get(url=_url, headers=_header, data= _param + '=' + urllib.parse.quote(str(_data).replace("'", "\"")))

        text = _res.text
        return _res.status_code, text

    except Exception as message:
        print(message)
        return 0, ""

def send_body_request2(_url, _header, _data1, _param1, _data2, _param2):
    try:
        if operation == "post":
            _res = requests.post(url=_url, headers=_header, data= _param1 + '=' + urllib.parse.quote(str(_data1).replace("'", "\"")) + "&" + _param2 + "=" + urllib.parse.quote(str(_data2).replace("'", "\"")))
        else:
            _res = requests.get(url=_url, headers=_header, data= _param1 + '=' + urllib.parse.quote(str(_data1).replace("'", "\"")) + "&" + _param2 + "=" + urllib.parse.quote(str(_data2).replace("'", "\"")))

        text = _res.text
        return _res.status_code, text

    except Exception as message:
        print(message)
        return 0, ""

nlp_url = "http://localhost:4000/extract_rules"
cached_nl = []
cached_rest = []
NLP2REST = {}
validated_rules = {}

# parse OpenAPI specification
parser = ResolvingParser(sys.argv[1])
openapi = parser.specification

base_url = openapi["servers"][0]["url"]
if base_url[-1] == '/':
    base_url = base_url[:-1]

# iterate through all paths in the specification
for path, path_def in openapi["paths"].items():
    print(path + " is processing...")
    # iterate through all operations in the path
    NLP2REST[path] = {}
    validated_rules[path] = {}
    for operation, operation_def in path_def.items():
        print(f"Operation: {operation}")

        param2text = {}
        param2value = {}
        param2type = {}
        param2place = {}
        param2default = {}
        param2maximum = {}
        param2minimum = {}
        enum_params = []
        required_params = []
        if 'requestBody' in operation_def:
            request_body = operation_def['requestBody']
            if 'required' in request_body and request_body['required']:
                required_params.append('body')
            if 'content' in request_body:
                for media_type, media_def in request_body['content'].items():
                    if 'schema' in media_def:
                        schema = media_def['schema']
                        if "required" in schema:
                            if required_params and required_params[-1] == "body":
                                required_params[-1] = schema["required"][0]
                        if 'properties' in schema:
                            properties = schema['properties']

                            for name, property in properties.items():
                                param2text[name] = property.get('description', 'N/A')
                                param2type[name] = property['type']

                                param2place[name] = media_type
                                if 'enum' in property:
                                    param2value[name] = property.get('enum')[0]
                                    enum_params.append(name)
                                elif 'example' in property:
                                    param2value[name] = property.get('example')
                                if 'default' in property:
                                    param2default[name] = property.get('default')
                                    param2value[name] = property.get('default')
                                if 'maximum' in property:
                                    param2maximum[name] = property.get('maximum')
                                if 'minimum' in property:
                                    param2minimum[name] = property.get('minimum')
                        if 'items' in schema and schema['items']['type'] == 'object':
                            for key in schema['items']['properties'].keys():
                                param2text[key] = schema['items']['properties'][key].get('description', 'N/A')
                                if 'enum' in schema['items']['properties'][key]:
                                    param2value[key] = schema['items']['properties'][key].get('enum')[0]
                                    enum_params.append(key)
                                elif 'example' in schema['items']['properties'][key]:
                                    param2value[key] = schema['items']['properties'][key].get('example')
                                if 'default' in schema['items']['properties'][key]:
                                    param2default[key] = schema['items']['properties'][key].get('default')
                                    param2value[key] = schema['items']['properties'][key].get('default')
                                if 'maximum' in schema['items']['properties'][key]:
                                    param2maximum[key] = schema['items']['properties'][key].get('maximum')
                                if 'minimum' in schema['items']['properties'][key]:
                                    param2minimum[key] = schema['items']['properties'][key].get('minimum')
                                param2type[key] = schema['items']['properties'][key].get('type')
                                param2place[key] = media_type
                                if required_params:
                                    if required_params[-1] == "body":
                                        required_params[-1] = "body-object-" + key
                                    elif 'body-object' in required_params[-1]:
                                        required_params[-1] = required_params[-1] + '-' + key

                        elif 'type' in schema and schema['type'] == 'array':
                            if required_params and required_params[-1] == "body":
                                required_params[-1] = required_params[-1] + "-array"
                            param2text['body-array'] = request_body['description']
                            param2type['body-array'] = 'array'
                            param2place['body-array'] = 'body'
        # iterate through all parameters in the operation
        for param in operation_def.get("parameters", []):
            if param["in"] == "body":
                param2text[param['name']] = param.get('description', 'N/A')
                if 'enum' in param:
                    param2value[param['name']] = param.get('enum')[0]
                    enum_params.append(param['name'])
                elif 'example' in param:
                    param2value[param['name']] = param.get('example')
                if 'default' in param:
                    param2default[param['name']] = param.get('default')
                    param2value[param['name']] = param.get('default')
                if 'maximum' in param:
                    param2maximum[param['name']] = param.get('maximum')
                if 'minimum' in param:
                    param2minimum[param['name']] = param.get('minimum')
                param2type[param['name']] = param['schema']['type']
                param2place[param['name']] = param['in']
                if param['schema']['type']=='object':
                    for key in param['schema']['properties'].keys():
                        param2text[key] = param['schema']['properties'][key].get('description', 'N/A')
                        if 'enum' in param['schema']['properties'][key]:
                            param2value[key] = param['schema']['properties'][key]['enum'][0]
                            enum_params.append(key)
                        elif 'example' in param['schema']['properties'][key]:
                            param2value[key] = param['schema']['properties'][key]['example']
                        if 'default' in param['schema']['properties'][key]:
                            param2default[key] = param['schema']['properties'][key]['default']
                            param2value[key] = param['schema']['properties'][key]['default']
                        if 'maximum' in param['schema']['properties'][key]:
                            param2maximum[key] = param['schema']['properties'][key]['maximum']
                        if 'minimum' in param['schema']['properties'][key]:
                            param2minimum[key] = param['schema']['properties'][key]['minimum']
                        param2type[key] = param['schema']['properties'][key].get('type')
                        param2place[key] = param['in']
            else:
                param2text[param['name']] = param.get('description', 'N/A')
                param2type[param['name']] = param['schema']['type']
                param2place[param['name']] = param['in']
                if 'enum' in param['schema']:
                    param2value[param['name']] = param['schema'].get('enum')[0]
                    enum_params.append(param['name'])
                elif 'example' in param:
                    param2value[param['name']] = param.get('example')
                if 'default' in param['schema']:
                    param2default[param['name']] = param['schema']['default']
                    param2value[param['name']] = param['schema']['default']
                if 'maximum' in param['schema']:
                    param2maximum[param['name']] = param['schema']['maximum']
                if 'minimum' in param['schema']:
                    param2minimum[param['name']] = param['schema']['minimum']
                if 'required' in param and param['required']:
                    required_params.append(param['name'])
        rest = {}

        for i in range(len(cached_nl)):
            if cached_nl[i] == param2text:
                rest = cached_rest[i]
                break
        params = {"param_names": list(param2text.keys())}
        if rest == {}:
            for param in param2text:
                params["param_name"] = param
                params["description"] = param2text[param]
                res = requests.post(url=nlp_url, headers={"Content-Type": "application/json"}, data=json.dumps(params))
                found_rest = res.json()[param]
                if found_rest:
                    rest[param] = found_rest
            cached_nl.append(param2text)
            cached_rest.append(rest)

        print("NLP2REST found: " + str(rest))
        NLP2REST[path][operation] = rest
        validated_rules[path][operation] = copy.deepcopy(rest)

        need_validation = False
        for name in rest:
            sorted_keys = sorted(rest[name].keys(), key=lambda x: 1 if x == "IPD" else 0)
            dropped = []
            print("The parameter " + name)
            for found in sorted_keys:
                need_validation = True
                if found == "IPD":
                    for item in rest[name][found]:
                        if "(" in item:
                            temp = item[item.find('(')+1:item.find(')')]
                            temp = temp.split(',')
                            if len(temp) != len(list(set(temp))):
                                print(item + " is ruled out.")
                                dropped.append(item)
                elif (found == "minimum" or found == "maximum" or found == "example" or found == "enum") and name in enum_params:
                    print(str(rest[name][found]) + " is ruled out from the " + found + ".")
                else:
                    if param2type[name] == "string":
                        if found == "minimum":
                            for item in rest[name][found]:
                                print(param2value[name])
                                if name in param2value and len(param2value[name]) < item:
                                    print("Minimum value " + str(item) + " is ruled out.")
                                    dropped.append(item)
                        elif found == "maximum":
                            for item in rest[name][found]:
                                if param2place[name] == "query" and item > 2048:
                                    print("Maximum value " + str(item) + " is ruled out.")
                                    dropped.append(item)
                                if name in param2value and len(param2value[name]) > item:
                                    print("Maximum value " + str(item) + " is ruled out.")
                                    dropped.append(item)
                    if found == "example":
                        for item in rest[name][found]:
                            if name not in param2value:
                                param2value[name] = item
                            if param2type[name] == "integer":
                                try:
                                    int(item)
                                except Exception:
                                    print(item + " is ruled out from the example.")
                                    dropped.append(item)
                            elif param2type[name] == "boolean":
                                if "true" not in item and "false" not in item:
                                    print(item + " is ruled out from the example.")
                                    dropped.append(item)
                    if found == "enum":
                        if name not in param2value:
                            param2value[name] = rest[name][found][0]
                for rule in validated_rules[path][operation][name]:
                    for i in reversed(range(len(validated_rules[path][operation][name][rule]))):
                        if validated_rules[path][operation][name][rule][i] in dropped:
                            del(validated_rules[path][operation][name][rule][i])
        if need_validation:
            url = base_url + path
            temp_url = url
            headers = {'content-type': 'application/json'}
            data = ""
            if required_params and required_params[0] in param2place and param2place[required_params[0]] == 'path':
                if required_params[0] in param2value:
                    temp_url = temp_url.replace("{" + required_params[0] + "}", str(param2value[required_params[0]]))
                else:
                    temp_url = temp_url.replace("{" + required_params[0] + "}", "NLP2REST")
            if operation == "get":
                if required_params and param2place[required_params[0]] == "query":
                    val = "NLP2REST"
                    if required_params[0] in param2value:
                        val = param2value[required_params[0]]
                    if type(val) == list:
                        val = val[0]
                    temp_url = temp_url + "?" + required_params[0] + "=" + val

                    if len(required_params) == 2:
                        val = "NLP2REST"
                        if required_params[1] in param2value:
                            val = param2value[required_params[1]]
                            temp_url = temp_url + "&" + required_params[1] + "=" + val
                    response = requests.get(temp_url, allow_redirects=False)
                else:
                    response = requests.get(temp_url, allow_redirects=False)

            else:
                data = {}
                if required_params:
                    if required_params[0] == 'body-array':
                        data = [param2value['body-array']]
                    elif 'body-object' in required_params[0]:
                        temp_params = required_params[0].split('-')

                        for param in temp_params:
                            if param in param2value:
                                data[param] = param2value
                            elif param in param2type:
                                if param2type[param] == "string":
                                    data[param] = "NLP2REST"
                                if param2type[param] == "integer":
                                    data[param] = 1
                    elif required_params[0] in param2value:
                        data[required_params[0]] = param2value[required_params[0]]
                    if required_params and required_params[0] in param2place and param2place[required_params[0]] == "application/x-www-form-urlencoded":
                        headers = {"Content-Type": "application/x-www-form-urlencoded"}
                        temp_url = url + "?" + required_params[0] + '=' + param2value[required_params[0]]
                    else:
                        if required_params and required_params[0] in param2type:
                            if param2type[required_params[0]] == "string":
                                data[required_params[0]] = "NLP2REST"
                            if param2type[required_params[0]] == "integer":
                                data[required_params[0]] = 1


                response = requests.post(temp_url, data=json.dumps(data), headers=headers, allow_redirects=False)

            # check if the request was successful
            if 200 <= response.status_code < 300:
                print("Validation is processing...")

                for name in rest:
                    dropped = []
                    if "IPD" in rest[name]:
                        for ipd in rest[name]["IPD"]:
                            if "IF " in ipd and "Or " in ipd:
                                print("Complex IPD is not supported yet.")
                                dropped.append(ipd)
                            elif "Or(" in ipd:
                                if not required_params:
                                    print(ipd + " is dropped during validation.")
                                    dropped.append(ipd)

                            elif "OnlyOne(" in ipd:
                                if not required_params:
                                    print(ipd + " is dropped during validation.")
                                    dropped.append(ipd)
                                else:
                                    param1 = ipd[ipd.find("OnlyOne(") + 8:ipd.find(",")].strip()
                                    param2 = ipd[ipd.find(",") + 1:ipd.find(");")].strip()
                                    if param1 not in required_params or param2 not in required_params:
                                        print(ipd + " is dropped during validation.")
                                        dropped.append(ipd)
                            elif "AllOrNone(" in ipd:
                                param1 = ipd[ipd.find("AllOrNone(") + 10:ipd.find(",")].strip()
                                param2 = ipd[ipd.find(",") + 1:ipd.find(");")].strip()

                                val1 = "NLP2REST"
                                val2 = "NLP2REST"

                                if "==" in param1:
                                    param1, val1 = param1[:param1.find("==")], param1[param1.find("==") + 2:]
                                elif "=" in param1:
                                    param1, val1 = param1[:param1.find("=")], param1[param1.find("=") + 1:]
                                if "==" in param2:
                                    param2, val2 = param2[:param2.find("==")], param2[param2.find("==") + 2:]
                                elif "=" in param2:
                                    param2, val2 = param2[:param2.find("=")], param2[param2.find("=") + 1:]

                                if param1 in rest and param2 in rest and "example" in rest[param1] and "example" in rest[param2]:
                                    ipd_flag = False
                                    param1s = []
                                    param2s = []
                                    for val1 in rest[param1]["example"]:
                                        for val2 in rest[param2]["example"]:
                                            if "?" in temp_url:
                                                temp_url2 = temp_url + '&' + param1 + '=' + val1
                                            else:
                                                temp_url2 = temp_url + '?' + param1 + '=' + val1
                                            temp_url3 = temp_url2 + '&' + param2 + '=' + val2
                                            if operation == "get":
                                                response = requests.get(temp_url3, allow_redirects=False)
                                            else:
                                                response = requests.post(temp_url3, data=json.dumps(data),
                                                                         headers=headers,
                                                                         allow_redirects=False)
                                            if 200 <= response.status_code < 300:
                                                if val1 not in param1s:
                                                    param2value[param1s] = val1
                                                    param1s.append(val1)
                                                param2value[param2s] = val2
                                                param2s.append(val2)
                                    if not param1s and not param2s:
                                        print("AllOrNone is dropped during validation.")
                                        dropped.append(ipd)
                                    else:
                                        print("AllOrNone is accepted during validation.")
                                else:
                                    if val1 == "NLP2REST" and param1 in param2value:
                                        val1 = param2value[param1]
                                    if val2 == "NLP2REST" and param2 in param2value:
                                        val2 = param2value[param2]

                                    if param2place[param1] == 'query':

                                        if "?" in temp_url:
                                            temp_url2 = temp_url + '&' + param1 + '=' + val1
                                        else:
                                            temp_url2 = temp_url + '?' + param1 + '=' + val1
                                        if operation == "get":
                                            response = requests.get(temp_url2, allow_redirects=False)
                                        else:
                                            response = requests.post(temp_url2, data=json.dumps(data), headers=headers,
                                                                     allow_redirects=False)
                                        if 200 <= response.status_code < 300:
                                            print(ipd + " is dropped during validation.")
                                            dropped.append(ipd)
                                        else:
                                            temp_url3 = temp_url + '&' + param2 + '=' + val2
                                            if operation == "get":
                                                response = requests.get(temp_url3, allow_redirects=False)
                                            else:
                                                response = requests.post(temp_url3, data=json.dumps(data),
                                                                         headers=headers,
                                                                         allow_redirects=False)
                                            if 200 <= response.status_code < 300:
                                                print(ipd + " is dropped during validation.")
                                                dropped.append(ipd)
                                            else:
                                                temp_url3 = temp_url2 + '&' + param2 + '=' + val2
                                                if operation == "get":
                                                    response = requests.get(temp_url3, allow_redirects=False)
                                                else:
                                                    response = requests.post(temp_url3, data=json.dumps(data),
                                                                             headers=headers,
                                                                             allow_redirects=False)
                                                if 200 <= response.status_code < 300:
                                                    print(ipd + " is accepted during validation.")
                                                else:
                                                    print(ipd + " is dropped during validation.")
                                                    dropped.append(ipd)

                            elif "IF " in ipd:
                                param1 = ipd[ipd.find("IF") + 2:ipd.find("THEN")].strip()
                                if "NOT" in param1:
                                    param1 = param1[param1.find("NOT") + 3:].strip()
                                param2 = ipd[ipd.find("THEN") + 4:ipd.find(";")].strip()
                                val1 = "NLP2REST"
                                val2 = "NLP2REST"

                                if "==" in param1:
                                    param1, val1 = param1[:param1.find("==")], param1[param1.find("==")+2:]
                                elif "=" in param1:
                                    param1, val1 = param1[:param1.find("=")], param1[param1.find("=") + 1:]
                                if "==" in param2:
                                    param2, val2 = param2[:param2.find("==")], param2[param2.find("==")+2:]
                                elif "=" in param2:
                                    param2, val2 = param2[:param2.find("=")], param2[param2.find("=")+1:]

                                if val1 == "NLP2REST" and param1 in param2value:
                                    val1 = param2value[param1]
                                if val2 == "NLP2REST" and param2 in param2value:
                                    val2 = param2value[param2]

                                if param2place[param1] == 'query':
                                    if "?" in temp_url:
                                        temp_url2 = temp_url + '&' + param2 + '=' + val2
                                    else:
                                        temp_url2 = temp_url + '?' + param2 + '=' + val2
                                    if operation == "get":
                                        response = requests.get(temp_url2, allow_redirects=False)
                                    else:
                                        response = requests.post(temp_url2, data=json.dumps(data), headers=headers,
                                                                 allow_redirects=False)
                                    if 200 <= response.status_code < 300:
                                        print(ipd + " is dropped during validation.")
                                        dropped.append(ipd)
                                    else:
                                        temp_url3 = temp_url2 + '&' + param1 + '=' + val1
                                        if operation == "get":
                                            response = requests.get(temp_url3, allow_redirects=False)
                                        else:
                                            response = requests.post(temp_url3, data=json.dumps(data), headers=headers,
                                                                     allow_redirects=False)
                                        if 200 <= response.status_code < 300:
                                            print(ipd + " is accepted during validation.")
                                        else:
                                            print(ipd + " is dropped during validation.")
                                            dropped.append(ipd)
                    if "enum" in rest[name]:
                        for val in rest[name]["enum"]:
                            if param2place[name] == "query":
                                if "?" in temp_url:
                                    temp_url2 = temp_url + '&' + name + '=' + val
                                else:
                                    temp_url2 = temp_url + '?' + name + '=' + val
                                if operation == "get":
                                    response = requests.get(temp_url2, allow_redirects=False)
                                else:
                                    response = requests.post(temp_url2, data=json.dumps(data), headers=headers,
                                                             allow_redirects=False)
                                if 200 <= response.status_code < 300:
                                    print(str(val) + " is accepted during validation.")
                                else:
                                    print(str(val) + " is dropped during validation.")
                                    dropped.append(val)
                            elif param2place[name] == "path":
                                temp_url2 = temp_url.replace(param2value[required_params[0]], val)
                                if operation == "get":
                                    response = requests.get(temp_url2, allow_redirects=False)
                                else:
                                    response = requests.post(temp_url2, data=json.dumps(data), headers=headers,
                                                             allow_redirects=False)
                                if 200 <= response.status_code < 300:
                                    print(str(val) + " is accepted during validation.")
                                else:
                                    print(str(val) + " is dropped during validation.")
                                    dropped.append(val)
                    if "example" in rest[name]:
                        for val in rest[name]["example"]:
                            if str(val) in temp_url and name in temp_url:
                                print(str(val) + " is accepted during validation.")
                                param2value[name] = val
                                continue
                            if name in param2place and param2place[name] == "application/json":
                                if name in param2type and param2type[name] == "array":
                                    temp_data = {name: [val]}
                                else:
                                    temp_data = {name: val}
                                if operation == "get":
                                    response = requests.get(temp_url, allow_redirects=False)
                                else:
                                    response = requests.post(temp_url, data=json.dumps(temp_data), headers=headers,
                                                             allow_redirects=False)
                                if 200 <= response.status_code < 300:
                                    print(str(val) + " is accepted during validation.")
                                else:
                                    print(str(val) + " is dropped during validation.")
                                    dropped.append(val)
                            if name == "body-array":
                                if operation == "get":
                                    response = requests.get(temp_url, allow_redirects=False)
                                else:
                                    response = requests.post(temp_url, data=json.dumps([val]), headers=headers,
                                                             allow_redirects=False)
                                if 200 <= response.status_code < 300:
                                    print(str(val) + " is accepted during validation.")
                                else:
                                    print(str(val) + " is dropped during validation.")
                                    dropped.append(val)
                            elif param2place[name] == "query":
                                if "?" in temp_url:
                                    temp_url2 = temp_url + '&' + name + '=' + val
                                else:
                                    temp_url2 = temp_url + '?' + name + '=' + val
                                if operation == "get":
                                    response = requests.get(temp_url2, allow_redirects=False)
                                else:
                                    response = requests.post(temp_url2, data=json.dumps(data), headers=headers,
                                                             allow_redirects=False)
                                if 200 <= response.status_code < 300:
                                    print(str(val) + " is accepted during validation.")
                                    if "-" in val and ":" in val:
                                        print("date-time format is aceepted.")
                                    if name not in param2value:
                                        param2value[name] = val
                                else:
                                    print(str(val) + " is dropped during validation.")
                                    dropped.append(val)

                    if "collectionFormat" in rest[name]:
                        for item in rest[name]["collectionFormat"]:
                            if item == "csv":
                                if param2type[name] == "array":
                                    print("csv is accepted.")
                                elif name in param2value:
                                    if "," in param2value[name]:
                                        print("csv is accepted.")
                    if "type" in rest[name]:
                        for item in rest[name]["type"]:
                            if item == "string":
                                if param2type[name] == "string":
                                    print("string type is accepted.")
                            elif item == "array":
                                if param2type[name] == "array":
                                    print("array type is accepted.")
                                elif name in param2value:
                                    if "," in param2value[name]:
                                        print("array type is accepted.")
                                elif name == "body-array":
                                    print("array type is accepted.")
                            elif item == "number":
                                temp_url2 = temp_url + '?' + name + '=1.2'
                                if operation == "get":
                                    response = requests.get(temp_url2, allow_redirects=False)
                                else:
                                    response = requests.post(temp_url2, data=json.dumps(data), headers=headers,
                                                             allow_redirects=False)
                                if 200 <= response.status_code < 300:
                                    print("number type is accepted during validation.")
                                else:
                                    print("number type is dropped during validation.")
                                    dropped.append(item)
                            elif item == "object":
                                if param2type[name] == "object":
                                    print("object type is accepted..")
                                else:
                                    print("object type is dropped.")
                                    dropped.append(item)
                            elif item == "boolean":
                                if param2type[name] == "boolean":
                                    print("boolean type is accepted..")
                                else:
                                    print("boolean type is dropped.")
                                    dropped.append(item)
                    if "default" in rest[name]:
                        if name in param2default and str(param2default[name]) == rest[name]["default"][0]:
                            print("Specification already has the default value.")
                        elif param2place[name] == "query":
                            if operation == "get":
                                response1 = requests.get(temp_url, allow_redirects=False)
                            else:
                                response1 = requests.post(temp_url, data=json.dumps(data), headers=headers,
                                                         allow_redirects=False)
                            if "?" in temp_url:
                                temp_url2 = temp_url + '&' + name + '=' + str(rest[name]["default"][0])
                            else:
                                temp_url2 = temp_url + '?' + name + '=' + str(rest[name]["default"][0])
                            if operation == "get":
                                response2 = requests.get(temp_url2, allow_redirects=False)
                            else:
                                response2 = requests.post(temp_url2, data=json.dumps(data), headers=headers,
                                                         allow_redirects=False)
                            if response1.text == response2.text:
                                print("Default value " + str(rest[name]["default"][0]) + " is accepted.")
                            else:
                                print("Default value " + str(rest[name]["default"][0]) + " is dropped.")
                                dropped.append(rest[name]["default"][0])

                    if "maximum" in rest[name]:
                        val = rest[name]["maximum"][0]
                        if name in param2maximum and param2maximum[name] == val:
                            print("Specification already has the maximum value.")
                        elif param2place[name] == "query":
                            if "?" in temp_url:
                                temp_url2 = temp_url + '&' + name + '=' + str(val)
                            else:
                                temp_url2 = temp_url + '?' + name + '=' + str(val)
                            if operation == "get":
                                response = requests.get(temp_url2, allow_redirects=False)
                            else:
                                response = requests.post(temp_url2, data=json.dumps(data), headers=headers,
                                                         allow_redirects=False)
                            if 200 <= response.status_code < 300:
                                temp_url2 = temp_url + '?' + name + '=' + str(val + 1)
                                if operation == "get":
                                    response = requests.get(temp_url2, allow_redirects=False)
                                else:
                                    response = requests.post(temp_url2, data=json.dumps(data), headers=headers,
                                                             allow_redirects=False)
                                if 200 <= response.status_code < 300:
                                    print("maximum " + str(val) + " is dropped during validation")
                                    dropped.append(val)
                                else:
                                    print("maximum " + str(val) + " is accepted during validation")
                            else:
                                print("maximum " + str(val) + " is dropped during validation.")
                                dropped.append(val)
                    if "minimum" in rest[name]:
                        val = rest[name]["minimum"][0]
                        if name in param2minimum and param2minimum[name] == val:
                            print("Specification already has the minimum value.")
                        elif param2place[name] == "query":
                            if "?" in temp_url:
                                temp_url2 = temp_url + '&' + name + '=' + str(val)
                            else:
                                temp_url2 = temp_url + '?' + name + '=' + str(val)
                            if operation == "get":
                                response = requests.get(temp_url2, allow_redirects=False)
                            else:
                                response = requests.post(temp_url2, data=json.dumps(data), headers=headers,
                                                         allow_redirects=False)
                            if 200 <= response.status_code < 300:
                                temp_url2 = temp_url + '?' + name + '=' + str(val-1)
                                if operation == "get":
                                    response = requests.get(temp_url2, allow_redirects=False)
                                else:
                                    response = requests.post(temp_url2, data=json.dumps(data), headers=headers,
                                                             allow_redirects=False)
                                if 200 <= response.status_code < 300:
                                    print("minimum " + str(val) + " is dropped during validation")
                                    dropped.append(val)
                                else:
                                    print("minimum " + str(val) + " is accepted during validation")
                            else:
                                print("minimum " + str(val) + " is dropped during validation.")
                    if "format" in rest[name]:
                        for item in rest[name]["format"]:
                            if item == "date-time":
                                if param2type[name] != "string":
                                    print("date-time format is dropped.")
                                    dropped.append(item)
                                elif name in param2value and "-" in param2value[name] and ":" in param2value[name]:
                                    print("date-time format is aceepted.")
                            elif item == "url":
                                if name in param2value:
                                    if "http" in param2value[name]:
                                        print("URL format is accepted.")
                                else:
                                    print("URL format is rejected.")
                                    dropped.append(item)

                    for rule in validated_rules[path][operation][name]:
                        for i in reversed(range(len(validated_rules[path][operation][name][rule]))):
                            if validated_rules[path][operation][name][rule][i] in dropped:
                                del (validated_rules[path][operation][name][rule][i])

            else:
                print('Trying to find required parameters from the NLP2REST result...')

                temp_required = []
                ipd_rel = {}
                temp_params = params["param_names"]
                if "application/x-www-form-urlencoded" in response.text:
                    headers = {"Content-Type": "application/x-www-form-urlencoded"}
                    if operation == "get":
                        response = requests.get(temp_url, allow_redirects=False)
                    else:
                        response = requests.post(temp_url, headers=headers,
                                                 allow_redirects=False)
                fail_msg = response.text
                for name in temp_params:

                    if name in fail_msg:
                        if param2place[name] == "application/x-www-form-urlencoded":
                            code, _ = send_body_request(temp_url, headers, "NLP2REST", name)
                            if 200 <= code < 300:
                                temp_required.append(name)
                                break
                        elif param2place[name] == "query":
                            val = "NLP2REST"
                            if name in param2value:
                                val = param2value[name]

                            temp_url = url + '?' + name + '=' + str(val)
                            try:
                                if operation == "get":
                                    response = requests.get(temp_url, allow_redirects=False)
                                else:
                                    response = requests.post(temp_url, headers=headers,
                                                             allow_redirects=False)
                                if 200 <= response.status_code < 300:
                                    temp_required.append(name)
                                    break
                            except Exception:
                                print("TIME OUT")
                if temp_required:
                    if required_params == [] and len(temp_required) == 1:
                        print("Found new required param - " + str(temp_required))
                        required_params.append(temp_required[0])
                        temp_required = []
                    for name in rest:
                        dropped = []
                        if "type" in rest[name]:
                            for item in rest[name]["type"]:
                                if item == "array":
                                    if param2type[name] == "array":
                                        print("array type is accepted.")
                                    elif name in param2value:
                                        if "," in param2value[name]:
                                            print("array type is accepted.")
                                    elif name == "body-array":
                                        print("array type is accepted.")
                                    else:
                                        dropped.append(item)
                                        print("Cannot validate this array.")
                                elif item == "number":
                                    temp_url2 = temp_url + '?' + name + '=1.2'
                                    if operation == "get":
                                        response = requests.get(temp_url2, allow_redirects=False)
                                    else:
                                        response = requests.post(temp_url2, data=json.dumps(data), headers=headers,
                                                                 allow_redirects=False)
                                    if 200 <= response.status_code < 300:
                                        print("number type is accepted during validation.")
                                    else:
                                        print("number type is dropped during validation.")
                                        dropped.append(item)
                                elif item == "object":
                                    if param2type[name] == "object":
                                        print("object type is accepted..")
                                    else:
                                        dropped.append(item)
                                        print("object type is dropped.")
                                elif item == "boolean":
                                    if param2type[name] == "boolean":
                                        print("boolean type is accepted..")
                        if "IPD" in rest[name]:
                            for ipd in rest[name]["IPD"]:
                                success = [False, False, False]
                                if "THEN " in ipd and "Or(" in ipd:
                                    print("Complex IPD is not supported yet.")
                                    dropped.append(ipd)
                                elif "THEN " in ipd:
                                    is_not = False
                                    param1 = ipd[ipd.find("IF") + 2:ipd.find("THEN")].strip()
                                    val1 = ""
                                    if "NOT" in param1:
                                        is_not = True
                                        param1 = param1[param1.find("NOT") + 3:].strip()
                                    if "==" in param1:
                                        val1, param1 = param1[param1.find("==") + 2:], param1[:param1.find("==")]

                                    param2 = ipd[ipd.find("THEN") + 4:].strip()

                                    if "==" in param2:
                                        val2, param2 = param2[param2.find("==") + 2:], param2[:param2.find("==")]
                                    elif param2 in param2type and param2type[param2] == "boolean":
                                        val2 = True
                                    elif param2 in param2value:
                                        val2 = param2value[param2]
                                    else:
                                        val2 = "NLP2REST"

                                    if param2 in required_params:
                                        print(ipd + " is rejected during validation.")
                                        dropped.append(ipd)
                                    elif param1 in required_params and is_not:
                                        print(ipd + " is rejected during validation.")
                                        dropped.append(ipd)
                                    elif param1 in required_params and val1 != "":
                                        temp_url2 = temp_url.replace(param2value[param1], val1)

                                        code, _ = send_body_request(temp_url2, headers, "NLP2REST", temp_required[0])

                                        if 200 <= code < 300:
                                            code, _ = send_body_request2(temp_url2, headers, "NLP2REST",
                                                                         temp_required[0], val2, param2)
                                            if 200 <= code < 300:
                                                print(ipd + " is accepted during validation.")
                                                if name not in ipd_rel:
                                                    ipd_rel[name] = temp_url2
                                            else:
                                                print(ipd + " is rejected during validation.")
                                                dropped.append(ipd)
                                        else:
                                            print(ipd + " is rejected during validation.")
                                            dropped.append(ipd)
                                    else:
                                        val2 = "NLP2REST"
                                        if param2 in param2type and param2type[param2] == "boolean":
                                            val2 = True
                                        code, _ = send_body_request2(temp_url, headers, "NLP2REST", temp_required[0],val2,param2)
                                        if 200 <= code < 300:
                                            print(ipd + " is rejected during validation.")
                                            dropped.append(ipd)

                                elif "Or(" in ipd:
                                    param1 = ipd[ipd.find("Or(") + 3:ipd.find(",")].strip()
                                    param2 = ipd[ipd.find(",") + 1:ipd.find(")")].strip()
                                    val1 = "NLP2REST"
                                    val2 = "NLP2REST"
                                    if param1 in param2value:
                                        val1 = param2value[param1]
                                    if param2 in param2value:
                                        val2 = param2value[param2]
                                    print(param2value)

                                    code, _ = send_body_request(temp_url,headers,val1,param1)
                                    if 200 <= code < 300:
                                        success[0] = True
                                        if param1 not in temp_required:
                                            temp_required.append(param1)
                                    code, _ = send_body_request(temp_url, headers, val2, param2)
                                    if 200 <= code < 300:
                                        success[1] = True
                                        if param2 not in temp_required:
                                            temp_required.append(param2)
                                    code, _ = send_body_request2(temp_url, headers, val1, param1, val2, param2)
                                    if 200 <= code < 300:
                                        success[2] = True
                                    print(success)
                                    if success == [True, True, True]:
                                        new_ipd = "Or(" + param1 + "," + param2 + ")"
                                        print(ipd + " is accepted as Or during validation.")
                                        validated_rules[path][name]["IPD"] = new_ipd
                                    elif success == [True, True, False]:
                                        new_ipd = "OnlyOne(" + param1 + "," + param2 + ")"
                                        print(ipd + " is accepted as OnlyOne during validation.")
                                        validated_rules[path][name]["IPD"] = new_ipd
                                    else:
                                        print(ipd + " is rejected during validation.")
                                        dropped.append(ipd)

                        if "enum" in rest[name]:
                            temp_val = "NLP2REST"
                            if temp_required and temp_required[0] in param2value:
                                temp_val = param2value[temp_required[0]]
                            if name in temp_required:
                                for val in rest[name]["enum"]:
                                    code, _ = send_body_request(temp_url, headers, val, name)
                                    if 200 <= code < 300:
                                        print(str(val) + " is accepted during validation.")
                                    else:
                                        print(str(val) + " is rejected during validation.")
                                        dropped.append(val)
                            elif name in required_params:
                                if temp_required:
                                    for val in rest[name]["enum"]:
                                        temp_url2 = temp_url.replace(param2value[name],val)
                                        code, _ = send_body_request(temp_url2, headers, temp_val, temp_required[0])
                                        if 200 <= code < 300:
                                            print(str(val) + " is accepted during validation.")
                                        else:
                                            print(str(val) + " is rejected during validation.")
                                            dropped.append(val)
                                else:
                                    for val in rest[name]["enum"]:
                                        code, _ = send_body_request(url, headers, val, name)
                                        if 200 <= code < 300:
                                            print(str(val) + " is accepted during validation.")
                                        else:
                                            print(str(val) + " is rejected during validation.")
                                            dropped.append(val)
                            else:
                                if temp_required:

                                    for val in rest[name]["enum"]:
                                        code, _ = send_body_request2(temp_url, headers, temp_val, temp_required[0], val, name)
                                        if 200 <= code < 300:
                                            print(str(val) + " is accepted during validation.")
                                        else:
                                            print(str(val) + " is rejected during validation.")
                                            dropped.append(val)
                                else:
                                    for val in rest[name]["enum"]:
                                        code, _ = send_body_request(temp_url, headers, val, name)
                                        if 200 <= code < 300:
                                            print(str(val) + " is accepted during validation.")
                                        else:
                                            print(str(val) + " is rejected during validation.")
                                            dropped.append(val)
                        if "example" in rest[name]:
                            temp_val = "NLP2REST"
                            if temp_required and temp_required[0] in param2value:
                                temp_val = param2value[temp_required[0]]
                            if name in temp_required:
                                for val in rest[name]["example"]:
                                    code, _ = send_body_request(temp_url, headers, val, name)
                                    if 200 <= code < 300:
                                        param2value[name] = val
                                        print(str(val) + " is accepted during validation.")
                                    else:
                                        print(str(val) + " is rejected during validation.")
                                        dropped.append(val)
                            elif name in required_params:
                                if temp_required:
                                    for val in rest[name]["example"]:
                                        temp_url2 = temp_url.replace(param2value[name],val)
                                        code, _ = send_body_request(temp_url2, headers, temp_val, temp_required[0])
                                        if 200 <= code < 300:
                                            param2value[name] = val
                                            print(str(val) + " is accepted during validation.")
                                        else:
                                            print(str(val) + " is rejected during validation.")
                                            dropped.append(val)
                                else:
                                    for val in rest[name]["example"]:
                                        code, _ = send_body_request(url, headers, val, name)
                                        if 200 <= code < 300:
                                            param2value[name] = val
                                            print(str(val) + " is accepted during validation.")
                                        else:
                                            print(str(val) + " is rejected during validation.")
                                            dropped.append(val)
                            elif name in ipd_rel:
                                for val in rest[name]["example"]:
                                    code, _ = send_body_request2(ipd_rel[name], headers, temp_val, temp_required[0], val, name)
                                    if 200 <= code < 300:
                                        print(str(val) + " is accepted during validation.")
                                    else:
                                        print(str(val) + " is rejected during validation.")
                                        dropped.append(val)
                            else:
                                if temp_required:
                                    for val in rest[name]["example"]:
                                        code, _ = send_body_request2(temp_url, headers, temp_val, temp_required[0], val, name)
                                        if 200 <= code < 300:
                                            print(str(val) + " is accepted during validation.")
                                            param2value[name] = val
                                        else:
                                            print(str(val) + " is rejected during validation.")
                                            dropped.append(val)
                                else:
                                    for val in rest[name]["example"]:
                                        code, _ = send_body_request(url, headers, val, name)
                                        if 200 <= code < 300:
                                            print(str(val) + " is accepted during validation.")
                                            param2value[name] = val
                                        else:
                                            print(str(val) + " is rejected during validation.")
                                            dropped.append(val)
                        if "default" in rest[name]:
                            temp_val = "NLP2REST"
                            if temp_required and temp_required[0] in param2value:
                                temp_val = param2value[temp_required[0]]
                            if temp_required and temp_required[0] in param2value:
                                temp_val = param2value[temp_required[0]]
                                for val in rest[name]["default"]:
                                    code, _ = send_body_request(temp_url, headers, val, name)
                                    if 200 <= code < 300:
                                        print(str(val) + " is accepted during validation.")
                                    else:
                                        print(str(val) + " is rejected during validation.")
                                        dropped.append(val)
                            elif name in required_params:
                                if temp_required:
                                    for val in rest[name]["default"]:
                                        temp_url2 = temp_url.replace(param2value[name],val)
                                        code, _ = send_body_request(temp_url2, headers, temp_val, temp_required[0])
                                        if 200 <= code < 300:
                                            print(str(val) + " is accepted during validation.")
                                        else:
                                            print(str(val) + " is rejected during validation.")
                                            dropped.append(val)
                                else:
                                    for val in rest[name]["default"]:
                                        code, _ = send_body_request(url, headers, val, name)
                                        if 200 <= code < 300:
                                            print(str(val) + " is accepted during validation.")
                                        else:
                                            print(str(val) + " is rejected during validation.")
                                            dropped.append(val)
                            elif name in ipd_rel:
                                for val in rest[name]["default"]:
                                    code, _ = send_body_request2(ipd_rel[name], headers, temp_val, temp_required[0], val, name)
                                    if 200 <= code < 300:
                                        print(str(val) + " is accepted during validation.")
                                    else:
                                        print(str(val) + " is rejected during validation.")
                                        dropped.append(val)
                            else:
                                if temp_required:
                                    for val in rest[name]["default"]:
                                        code, _ = send_body_request2(temp_url, headers, temp_val, temp_required[0], val, name)
                                        if 200 <= code < 300:
                                            print(str(val) + " is accepted during validation.")
                                        else:
                                            print(str(val) + " is rejected during validation.")
                                            dropped.append(val)
                                else:
                                    for val in rest[name]["default"]:
                                        code, _ = send_body_request(url, headers, val, name)
                                        if 200 <= code < 300:
                                            print(str(val) + " is accepted during validation.")
                                        else:
                                            print(str(val) + " is rejected during validation.")
                                            dropped.append(val)
                        for rule in validated_rules[path][operation][name]:
                            for i in reversed(range(len(validated_rules[path][operation][name][rule]))):
                                if validated_rules[path][operation][name][rule][i] in dropped:
                                    del (validated_rules[path][operation][name][rule][i])

with open('nlp-result.json', 'w') as f:
    json.dump(NLP2REST, f)
with open('validation-result.json', 'w') as f:
    json.dump(validated_rules, f)
