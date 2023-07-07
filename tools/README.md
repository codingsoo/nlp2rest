# Tools Directory

This directory introduces a curated collection of eight REST API testing tools, each of which can substantially enhance your testing results when paired with improved specifications.

## Overview

In this directory, you'll find eight tools specifically designed for REST API testing. These include [bBOXRT](https://eden.dei.uc.pt/~cnl/papers/2020-access.zip), [EvoMaster](https://github.com/EMResearch/EvoMaster), [Morest](https://github.com/codingsoo/REST_Go/tree/master/tool/morest), [RESTest](https://github.com/isa-group/RESTest), [RESTler](https://github.com/microsoft/restler-fuzzer), [RestTestGen](https://github.com/SeUniVr/RestTestGen), [Schemathesis](https://github.com/schemathesis/schemathesis), and [Tcases](https://github.com/Cornutum/tcases).

## Recommendation

Each tool comes with its own set of dependencies which may sometimes cause conflict with others. To circumvent such issues, we strongly recommend setting up a separate virtual environment tailored specifically for this project. This advice is particularly relevant if you're working with Morest, as its dependencies have been known to clash with those of our project.

## EvoMaster

Download the Jar file from [EvoMaster's releases](https://github.com/EMResearch/EvoMaster/releases), and execute the following command:

```
java -jar evomaster.jar --blackBox true --bbSwaggerUrl file://$SPEC_HERE --maxTime 1h --outputFormat JAVA_JUNIT_4
```


If you encounter any errors, feel free to report them directly on their repository: https://github.com/EMResearch/EvoMaster.

## Schemathesis

You can download Schemathesis using pip:

```
pip install schemathesis
```

To run the tool, refer to the script provided at https://github.com/codingsoo/nlp2rest/blob/main/tools/schemathesis/tool.sh. Don't forget to replace `$SPEC_HERE` with your specification path and `$URL_HERE` with your URL.

Any errors should be reported directly to the Schemathesis repository: https://github.com/schemathesis/schemathesis. If you encounter script-related issues, please report them to us.

## Tcases

For Tcases, use the script provided at https://github.com/codingsoo/nlp2rest/blob/main/tools/tcases/tool.sh. Ensure that you replace `$SPEC_HERE` with the correct specification path. For tool-related errors, report them directly to the Tcases repository: https://github.com/Cornutum/tcases. For script-related issues, please reach out to us.

## bBOXRT

For Tcases, use the script provided at [https://github.com/codingsoo/nlp2rest/blob/main/tools/tcases/tool.sh](https://github.com/codingsoo/nlp2rest/blob/main/tools/bboxrt/tool.sh). Ensure that you replace `$SPEC_HERE` with the correct specification path. For tool-related errors, report them directly (As there's no official repository, errors should be reported directly to the authors [here](https://ieeexplore.ieee.org/document/9344640)). For script-related issues, please reach out to us.

## Other Tools

For the rest of the tools, please refer to the README files in each tool's respective directory. These documents provide comprehensive instructions on how to utilize each tool.

In case you encounter any errors, report them directly to the respective developers:

- RESTest: https://github.com/isa-group/RESTest
- RESTler: https://github.com/microsoft/restler-fuzzer
- RestTestGen: https://github.com/SeUniVr/RestTestGen
- Morest: Errors should be reported directly to the authors [here](https://dl.acm.org/doi/10.1145/3510003.3510133)
