from flask import Flask, request, jsonify
from rule_generator import RuleGenerator

app = Flask(__name__)

# Create an instance of RuleGenerator
try:
    rule_generator = RuleGenerator('settings2.yaml', 'rest_model')
    generator_ready = True
except Exception as e:
    print(f"Failed to initialize RuleGenerator: {e}")
    generator_ready = False


@app.route('/status', methods=['GET'])
def status():
    # This is a simple endpoint to check if the service is running
    # It will return a 200 OK status code if the RuleGenerator instance is ready
    if generator_ready:
        return jsonify({'status': 'RuleGenerator is ready'}), 200
    else:
        return jsonify({'status': 'RuleGenerator failed to initialize'}), 500


@app.route('/generate_rules', methods=['POST'])
def generate_rules():
    if not generator_ready:
        return jsonify({'error': 'RuleGenerator is not ready'}), 500

    data = request.get_json()

    param_names = data.get('requestParameters',)
    param_names = param_names.replace(" ", "").split(',')
    param_name = data.get('target', '')
    description = data.get('description', '')

    # Generate rules
    rules = rule_generator.generate_rules(tuple(param_names), param_name, description)

    return jsonify(rules)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
