#! /bin/bash
end=$((SECONDS+3600))

while [ $SECONDS -lt $end ]; do
    ./bin/tcases-api-test -o src/test/java/tcases -p tcases -u 30000 -d false -S $SPEC_HERE && mvn clean test
    rm -rf src
done
