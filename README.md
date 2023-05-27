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

2. Download NLTK stopwords:

```terminal
python -m nltk.downloader stopwords
```

This command downloads the "stopwords" package from NLTK, which is used for removing common words (like "the", "is", "in") from text during text processing.

## Run Service

We provide a Python script that starts services using Tmux sessions and runs a Mitmproxy instance for each service to intercept and manipulate the traffic.

The script requires two command-line arguments: the name of the service to start and a token. The name can be one of the following: `fdic`, `genome-nexus`, `language-tool`, `ocvn`, `ohsome`, `omdb`, `rest-countries`, `spotify`, `youtube`, `all (starts all the services)`.

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
