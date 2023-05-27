from prance import ResolvingParser


def parse_properties(properties, data={}, indent=2):
    for prop_name, prop_val in properties.items():
        data[prop_name] = {
            "type": prop_val.get("type"),
            "description": prop_val.get("description"),
            "items": prop_val.get("items", {}).get("type") if prop_val.get('type') == 'array' else None,
            "properties": parse_properties(prop_val.get("items", {}).get('properties', {}), {}, indent + 2)
            if prop_val.get("items", {}).get('type') == 'object' else None,
        }
    return data


def parse_parameters(file_path):
    parser = ResolvingParser(file_path)
    spec = parser.specification

    param_data = {}
    for path, path_item in spec.get('paths', {}).items():
        for method, operation in path_item.items():
            if method in ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace']:
                operation_key = f"{path} {method}"
                if operation_key not in param_data:
                    param_data[operation_key] = []

                for parameter in operation.get('parameters', []):
                    param_data[operation_key].append({
                        "name": parameter.get("name"),
                        "type": parameter.get("type"),
                        "description": parameter.get("description"),
                        "in": parameter.get("in"),
                        "items": parameter.get("schema", {}).get("items", {}).get("type")
                        if parameter.get("schema", {}).get("type") == "array" else None,
                        "properties": parse_properties(parameter.get("schema", {}).get('properties', {}))
                        if parameter.get("schema", {}).get("type") == "object" else None,
                    })

                if 'requestBody' in operation:
                    param_data[operation_key].append({
                        "name": "requestBody",
                        "description": operation.get("requestBody").get('description', ''),
                        "requestBody": operation.get("requestBody"),
                    })

    return param_data

