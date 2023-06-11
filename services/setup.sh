# Install Jacoco
wget https://repo1.maven.org/maven2/org/jacoco/org.jacoco.agent/0.8.7/org.jacoco.agent-0.8.7-runtime.jar
wget https://repo1.maven.org/maven2/org/jacoco/org.jacoco.cli/0.8.7/org.jacoco.cli-0.8.7-nodeps.jar

# Install Evo Bench
. ./java8.env && cd open-source/emb && mvn clean install -DskipTests && mvn dependency:build-classpath -Dmdep.outputFile=cp.txt
cd ../..

# Install Genome-Nexus
. ./java8.env && cd open-source/genome-nexus && mvn clean install -DskipTests
cd ../..

# Install YouTube Mock service
. ./java11.env && cd open-source/youtube && mvn clean install -DskipTests && mvn dependency:build-classpath -Dmdep.outputFile=cp.txt
cd ../..
