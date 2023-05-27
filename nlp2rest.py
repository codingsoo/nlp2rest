import json
import argparse
from train import FastTextTrainer
from rule_generator import RuleGenerator
from openapi_parser import parse_parameters

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train a FastText model or generate rules.')
    parser.add_argument('--specs_dir', type=str, help='The path to the directory containing the specification files.', required=False)
    parser.add_argument('--output_model_file', type=str, help='The path to the file where the trained model will be saved.', required=False)
    parser.add_argument('--train', action='store_true', help='If given, the model will be trained.')
    parser.add_argument('--generate_rules', action='store_true', help='If given, rules will be generated.')
    parser.add_argument('--spec_path', type=str, help='The path to the OpenAPI specification.', required=False)
    parser.add_argument('--settings', type=str, help='The path to the settings file.', required=False)
    parser.add_argument('--model_name', type=str, help='The name of the model.', required=False)
    args = parser.parse_args()

    if args.train:
        if not args.specs_dir or not args.output_model_file:
            parser.error("--train requires --specs_dir and --output_model_file.")
        trainer = FastTextTrainer(args.specs_dir, args.output_model_file)
        trainer.train_model()

    if args.generate_rules:
        if not args.spec_path or not args.settings or not args.model_name:
            parser.error("--generate_rules requires --spec_path, --settings and --model_name.")
        # Parse the OpenAPI specification
        operation_data = parse_parameters(args.spec_path)
        # Create an instance of RuleGenerator
        rule_generator = RuleGenerator(args.settings, args.model_name)
        # Load previous results, if they exist

        prev_results = {}
        results = {}
        # Pass the operation data to the rule generator
        for operation, parameters in operation_data.items():
            param_names = [param["name"] for param in parameters]
            for param in parameters:
                # Generate rules for the parameter
                param_key = (tuple(param_names), param["name"], param["description"])
                if param_key in prev_results:
                    if operation not in results:
                        results[operation] = {}
                    results[operation][param["name"]] = prev_results[param_key]
                else:
                    if operation not in results:
                        results[operation] = {}
                    prev_results[param_key] = rule_generator.generate_rules(*param_key)
                    results[operation][param["name"]] = prev_results[param_key]
                if param["properties"] is not None:
                    # Generate rules for each property
                    for prop_name, prop_info in param["properties"].items():
                        prop_key = (tuple(param_names), prop_name, prop_info["description"])
                        if prop_key in prev_results:
                            if operation not in results:
                                results[operation] = {}
                            results[operation][param["name"]] = prev_results[param_key]
                        else:
                            if operation not in results:
                                results[operation] = {}
                            prev_results[prop_key] = rule_generator.generate_rules(*prop_key)
                            results[operation][param["name"]] = prev_results[param_key]
        # Save the results
        with open('found_rules.json', 'w') as f:
            results = {operation: {param: rules for param, rules in param_rules.items() if rules} for
                       operation, param_rules in results.items() if param_rules}
            json.dump(results, f)
