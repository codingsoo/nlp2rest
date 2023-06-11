# Enhancing REST API Testing with NLP Techniques

## Getting Started

This section provides a comprehensive guide to setting up an artifact and validating its functionality using a simple example. The setup process was successfully tested on a Google Cloud EC2 machine using an Ubuntu 20.04 image.

1. Setup environment:

First, Please ensure that the paths to Java 8 and Java 11 are correctly defined in the `java8.env` and `java11.env` files respectively. Then, start by setting up your environment. This can be done by executing the setup script in your terminal as shown below:

```
sh setup.sh
```

2. Run Service Proxy:

Navigate to the services directory and run the Service Proxy using Python3:

```
cd services
python3 run_service.py rest-countries no_token
```

3. Run Rule Extractor:

Before running the Rule Extractor, download the following pretrained models and place them in the `rule_extractor` directory:
- [model](https://drive.google.com/file/d/1-jawBqo3c3eMRkXF8Y73oLEFNSOphbpF/view?usp=share_link)
- [model_ngram](https://drive.google.com/file/d/1j1XA1dufDgqSkIGlQn97-WeKElaL8708/view?usp=share_link)

Then, navigate to the `rule_extractor` directory and build a Docker image tagged 'rex'. Please allow around 5 minutes to build the Docker image. Finally, run the Docker image, mapping the host port 4000 to the Docker container's port 4000.

```
cd rule_extractor
docker build -t rex .
docker run -p 4000:4000 rex
```

4. Run Rule Validator:

Firstly, adjust the `specificationFileName` in the `rtg_config.json` file to point to the desired specification. We preconfigured the file to use the specification of rest-countries, and our NLP-based strategy (named `NlpStrategy`). Then, use Gradle to run the Rule Validator as follows:

```
./gradlew run
```
> To run the above command, the `gradlew` file must be executable. Make it executable with `sudo chmod +x gradlew`

This will generate an enhanced specification in the `output` directory.

## Detailed Instructions

This repository contains the components necessary to run NLP2REST, an approach designed to automatically enhance OpenAPI specifications with rules extracted from natural language description fields. These rules include constraints and example values. 

In addition, this repository provides all the components required to replicate the experiment described in our paper, including testing tools and benchmark APIs.

### Table of Contents

1. [Recommended Environment](#recommended-environment)
2. [Setup](#setup)
3. [Steps to Use NLP2REST](#steps-to-use-nlp2rest)
    - REST API(s)
    - Deployment of the Rule Extractor Service
    - Run the Rule Validator

### Recommended Environment

This project has been tested and is known to work well on the following setup:

- Ubuntu 20.04
- Google Cloud EC2 machine with 24-core CPU and 128GB memory

### Setup

We provide a setup script to install the necessary packages and set up the environment for the project:

```
./setup.sh
```

It will take around 10 minutes.

### Steps to Use NLP2REST

1. **REST API(s):** NLP2REST is designed to be applied to one or more target REST APIs. The APIs should be accessible at the URLs detailed in their OpenAPI specifications. We have provided several REST APIs in the [services](https://github.com/codingsoo/nlp2rest/tree/main/services) directory along with a manuscript for running these services. Alternatively, you can use any public APIs accessible online that have OpenAPI specifications. For a quick trial of our approach, we suggest using the [FDIC REST API](https://banks.data.fdic.gov/). This is an online API and its specification is available in our `specifications` directory.

2. **Deployment of the Rule Extractor Service:** This is a Python-based service accessible via a REST API. It's designed to extract formal OpenAPI rules from natural language descriptions. To run the Rule Extractor service, please adhere to the instructions provided in the [rule_extractor](https://github.com/codingsoo/nlp2rest/tree/main/rule_extractor) directory. In brief, you will need to:
    - Obtain a model either by training one yourself or by downloading the pre-trained model from the Google Drive link supplied in the README.
    - Build and run the Python application. We provide a `Dockerfile` for rapid deployment of the service. Alternatively, you can follow the instructions to install the service directly on your system.
    - The service is designed to run on `localhost` on port `4000`, i.e., [http://localhost:4000/]().

3. **Run the Rule Validator:** This is a bespoke strategy built upon the RestTestGen framework, which is available in the [rule_validator](https://github.com/codingsoo/nlp2rest/tree/main/rule_validator) directory. The strategy parses the OpenAPI specification of the chosen API, uses the Rule Extractor service to draw out rules from natural language descriptions, and interacts with the target API to validate the extracted rules.
To employ our strategy within RestTestGen, you need to configure RestTestGen to run the strategy named `NlpStrategy`. For guidance, refer to the official RestTestGen README file available in the [rule_validator](https://github.com/codingsoo/nlp2rest/tree/main/rule_validator) directory or in the [official RestTestGen repository](https://github.com/SeUniVr/RestTestGen).
The results of RestTestGen will be stored in an `output` directory. This directory will hold the enhanced OpenAPI specification and reports of the HTTP interactions generated by the Rule Validator. Please note that RestTestGen expects the Rule Extractor to be running at [http://localhost:4000/](http://localhost:4000/). If the Rule Extractor is running on a different port or host, update the `baseUrl` field in the `RuleExtractorProxy` class of RestTestGen.

Congratulations! You have successfully generated an enhanced OpenAPI specification. Using this enhanced specification can significantly boost the performance of REST API testing tools. To utilize these tools, please consult the instructions in the [tools](https://github.com/codingsoo/nlp2rest/tree/main/tools) directory.
