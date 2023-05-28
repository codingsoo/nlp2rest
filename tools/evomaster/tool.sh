#! /bin/bash
end=$((SECONDS+3600))

while [ $SECONDS -lt $end ]; do
    java -jar ../../evomaster.jar --blackBox true --bbSwaggerUrl file://$SPEC_HERE --maxTime 1h --outputFormat JAVA_JUNIT_4
done
