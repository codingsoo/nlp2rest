DEFAULT_DIR=$(pwd)

# Add docker repo
sudo apt-get update
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update

# Install Common Utilities
sudo apt-get install -y software-properties-common \
unzip wget gcc git vim libcurl4-nss-dev tmux mitmproxy

# Install Java
sudo apt-add-repository 'deb http://security.debian.org/debian-security stretch/updates main'
sudo apt update
sudo apt-get install -y openjdk-8-jdk
sudo apt-get install -y maven gradle
sudo apt-get install -y openjdk-11-jdk

# Install Python3
sudo apt-get install -y python3-pip python3-venv
python3 -m venv venv

# Install Dotnet 6
wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install -y dotnet-runtime-6.0
sudo apt-get install -y dotnet-sdk-6.0
rm packages-microsoft-prod.deb

# Install RESTler
. ./venv/bin/activate && cd DEFAULT_DIR/tools/restler && mkdir restler_bin && python ./build-restler.py --dest_dir ./restler_bin

# Install Schemathesis
cd DEFAULT_DIR
. ./venv/bin/activate && pip install requests schemathesis

# Install EvoMaster
wget https://github.com/EMResearch/EvoMaster/releases/download/v1.5.0/evomaster.jar.zip
unzip evomaster.jar.zip
rm evomaster.jar.zip

# Install RESTest
cd DEFAULT_DIR
. ./java8.env && cd tools/restest && sh scripts/install_dependencies.sh && mvn clean install -DskipTests

# Install RestTestGen
cd DEFAULT_DIR
. ./java11.env && cd tools/resttestgen && ./gradlew install

# Install bBOXRT
cd DEFAULT_DIR
. ./java11.env && cd tools/bboxrt && mvn clean install -DskipTests

# Install MoREST
cd DEFAULT_DIR
cd tools/morest && pip install -r requirements.txt

# Install Docker
sudo apt-get install -y docker.io

# Install Jacoco
wget https://repo1.maven.org/maven2/org/jacoco/org.jacoco.agent/0.8.7/org.jacoco.agent-0.8.7-runtime.jar
wget https://repo1.maven.org/maven2/org/jacoco/org.jacoco.cli/0.8.7/org.jacoco.cli-0.8.7-nodeps.jar

# Install Evo Bench
cd DEFAULT_DIR
. ./java8.env && cd services/emb && mvn clean install -DskipTests && mvn dependency:build-classpath -Dmdep.outputFile=cp.txt

# Install Genome-Nexus
cd DEFAULT_DIR
. ./java8.env && cd services/genome-nexus && mvn clean install -DskipTests

# Install YouTube Mock service
cd DEFAULT_DIR
. ./java11.env && cd services/youtube && mvn clean install -DskipTests && mvn dependency:build-classpath -Dmdep.outputFile=cp.txt
