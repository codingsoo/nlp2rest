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