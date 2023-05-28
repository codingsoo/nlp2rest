from flask import Flask, request, jsonify
from rule_extractor import RuleExtractor

app = Flask(__name__)

try:
    rule_extractor = RuleExtractor('settings2.yaml', 'rest_model')
    extractor_ready = True
except Exception as e:
    print(f"Failed to initialize RuleExtractor: {e}")
    extractor_ready = False


@app.route('/status', methods=['GET'])
def status():
    if extractor_ready:
        return jsonify({'status': 'RuleExtractor is ready'}), 200
    else:
        return jsonify({'status': 'RuleExtractor failed to initialize'}), 500


@app.route('/extract_rules', methods=['POST'])
def extract_rules():
    if not extractor_ready:
        return jsonify({'error': 'RuleExtractor is not ready'}), 500

    data = request.get_json()

    param_names = data.get('param_names', [])
    param_name = data.get('param_name', 'requestBody')
    description = data.get('description', '')

    rules = rule_extractor.extract_rules(tuple(param_names), param_name, description)

    return jsonify(rules)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
