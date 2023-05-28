#! /bin/bash
end=$((SECONDS+3600))

while [ $SECONDS -lt $end ]; do
    schemathesis run $SPEC_HERE --hypothesis-database=none --checks all --stateful=links --max-response-time=30000 --validate-schema False --base-url $URL_HERE
    schemathesis run $SPEC_HERE --hypothesis-database=none --stateful=links --max-response-time=30000 --validate-schema False --base-url $URL_HERE
done
