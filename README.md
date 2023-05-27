# NLP2REST

## Recommended Environment

This project has been tested and is known to work well on the following setup:

- Ubuntu 20.04
- Google Cloud EC2 machine with 24-core CPU and 128GB memory

## Setup

To set up the environment for this project, you will need to run a setup script and download some NLTK resources.

1. Run the setup script:

```bash
./setup.sh
```
   
This script installs necessary packages and sets up the environment for the project.

2. Download requirements and NLTK stopwords:

```terminal
pip3 install -r requirements.txt
python -m nltk.downloader stopwords
```

This command downloads the "stopwords" package from NLTK, which is used for removing common words (like "the", "is", "in") from text during text processing.

## Run NLP2REST's Rule Generator

### Training the Model

Run the following commands in your terminal:

```
python3 train.py
```

Note: Training the model will take approximately 20 hours.

You can also use the pre-trained models.

- [model](https://drive.google.com/file/d/1-jawBqo3c3eMRkXF8Y73oLEFNSOphbpF/view?usp=share_link)
- [model_ngram](https://drive.google.com/file/d/1j1XA1dufDgqSkIGlQn97-WeKElaL8708/view?usp=share_link)

Make sure to download both models and place them in the root directory of the project.

### HTTP interface

To run the API, execute the `app.py` script using the following command:

```
python app.py
```

You can also use Dockerfile:

```
docker build -t nlp2rest .
docker run -p 4000:4000 --name nlp2rest-demo nlp2rest
```

By default, the application will start on `0.0.0.0` (accessible from any IP address) and port `4000`. You can access the application via `http://localhost:4000`.

#### Example Usage

Here is an example of how to use the /generate_rules endpoint with curl:

```
curl -X POST -H "Content-Type: application/json" -d '{"param_names": ["param1", "param2"], "param_name": "param3", "description": "Some description"}' http://localhost:4000/generate_rules
```

This command sends a POST request to the `/generate_rules` endpoint with the provided JSON data, and the server will respond with the generated rules.

#### Endpoints

There are two endpoints available:

1. `/status`: This is a GET endpoint that checks if the service is running. It returns a 200 OK status code if the RuleGenerator instance is ready, and a 500 status code if the RuleGenerator failed to initialize.

2. `/generate_rules`: This is a POST endpoint that accepts JSON data in the request body and generates rules based on the provided parameters. The JSON data should contain:
   - `requestParameters`: This is a comma-separated value of parameter names. It is optional and defaults to an empty list.
   - `target`: This is a single parameter name. It is optional and defaults to an empty string.
   - `description`: This is a string that provides a description. It is optional and defaults to an empty string.

This command sends a POST request to the /generate_rules endpoint with the provided JSON data, and the server will respond with the generated rules.

### Command Line Interface (CLI)

To run the CLI, execute the `nlp2rest.py` script (or whatever your file with the CLI code is named) with the required arguments:

```
python main.py --option [values]
```

The script accepts the following options:

`--specs_dir`: The path to the directory containing the specification files. This is required if `--train` is given.
`--output_model_file`: The path to the file where the trained model will be saved. This is required if `--train` is given.
`--train`: If given, the model will be trained.
`--generate_rules`: If given, rules will be generated.
`--spec_path`: The path to the OpenAPI specification. This is required if `--generate_rules` is given.
`--settings`: The path to the settings file. This is required if `--generate_rules` is given.
`--model_name`: The name of the model. This is required if `--generate_rules` is given.

For example, to train a model, you might run:

```
python main.py --train --specs_dir ./specs --output_model_file ./model
```

And to generate rules, you might run:

```
python main.py --generate_rules --spec_path ./openapi_spec.yaml --settings ./settings2.yaml --model_name rest_model
```

The generated rules are saved to a file named `found_rules.json` in the project root directory.


## Run Service

We provide a Python script that starts services using Tmux sessions and runs a Mitmproxy instance for each service to intercept and manipulate the traffic.

The script requires two command-line arguments: the name of the service to start and a token. The name can be one of the following: `fdic`, `genome-nexus`, `language-tool`, `ocvn`, `ohsome`, `omdb`, `rest-countries`, `spotify`, `youtube`, `all (starts all the services)`.

### Obtain authentication

1. Obtain a Spotify API key by visiting https://developer.spotify.com/console/get-playlists/ and clicking "Get Token".
2. Obtain a OMDB API key by visiting https://www.omdbapi.com/apikey.aspx

### Example Usage

Here's how you can use the script:

```
python script.py fdic no_token
```

If you want to run OMDB, please replace the `YOUR_TOKEN_HERE` in `omdb.py` (located in the root directory) to your token. To run Spotify, please replace `no_token` in the command to your token.

### Troubleshooting

If a service fails to start, you can check the Tmux session for that service to see any error messages. First, list the currently running Tmux sessions with:

```
tmux ls
```

Then, attach to a Tmux session with the following command:

```
tmux attach -t session-name
```

Replace `session-name` with the name of the Tmux session for the service (e.g., `fdic-proxy`). To detach from a Tmux session, press `Ctrl + b` followed by `d`.
