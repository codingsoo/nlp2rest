#! /bin/bash
end=$((SECONDS+3600))

while [ $SECONDS -lt $end ]; do
    java -jar ./target/REST_API_Robustness_Tester-1.0.jar --api-file ./src/main/java/test.java --api-yaml-file $SPEC_HERE
done
