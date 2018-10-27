# Wizard of Minecraft Wizard
The Wizard of Minecraft is a Google DialogFlow chat bot that performs Minecraft server admin commands when you ask it nicely.

![ingame screenshot of the wizard](/readme.png)

## Getting Started
This project is designed to be quickly deployed on the Google Cloud Platform (GCP).

### Deploy Infrastructure
These steps walk you through the installation of the various infrastructure resources described above.
1. create a new GCP project to deploy the infrastructure into
2. open the google cloud platform shell
3. clone this repo into your cloud shell `git clone https://github.com/pvacey/wizard-of-minecraft.git`
4. enter the repo directory `cd wizard-of-minecraft`
5. run the installer script `bash create-resources.sh`
6. when prompted by the script, enable the service APIs required to deploy the resources
7. the script finishes deploying the infrastructure and displays `Minecraft Server IP: X.X.X.X`, use this to connect to your server (it will take several minutes for the server to become available)
8. the final part of the script displays a link for you to enable the DialogFlow API, click on the link and enable the API using your browser

### Setup DialogFlow
These steps will walk you through enabling Google DialogFlow, creating an agent, and importing the agent configuration.  The configuration bundled with this repository contains several `intents` and `entities` used by the agent.
1. login using the same account that you use for GCP https://console.dialogflow.com/api-client/#/login
2. click through the initial setup and agree to the terms of service
3. once you have reached the `Welcome To DialogFlow` page click the `CREATE AGENT` button
4. give your agent a name, for example "Minecraft Wizard" and assign it to the same project that you deployed the infrastructure into and click the `CREATE` button
5. click on the gear icon next to you agent's name to open the settings page
6. select `Export and Import` tab
7. chose the `IMPORT FROM ZIP` option and upload `agent.zip` from the root directory of the repository

### Interacting with the Wizard
1. connect to your minecraft server using the IP address from step 7 of [Deploy Infrastructure](#Deploy_Infrastructure)
2. press `y` to open the chat, you can ask the wizard to do the following:
  - change the weather
    - "can you make it rain?"
    - "please make it sunny"
  - change the time of day
    - "change it to night time"
    - "make it noon again"
  - generic greetings
  - ask the wizard who he is
    - "who are you?" (he's the wizard of minecraft yuh dingus)


## Architecture / Resources
Below are the various services used by the project, what purpose they serve, and how they interact with each other.

- Google Cloud Engine
  - hosts docker and runs [itzg/minecraft-server](https://hub.docker.com/r/itzg/minecraft-server/)
  - docker container exports the minecraft container logs to Google Stackdriver
- Stackdriver
  - filter that captures player chat logs --> exports to pub/sub
  - filter that captures player disconnect logs --> exports to pub/sub
- Pub/Sub
  - aggregates the interesting minecraft server logs from stackdriver exports
- Cloud Functions
  - runs `cloud-function/main.py`
    - is triggered by new logs entering the Pub/Sub topic
    - sends chat messages to DialogFlow agent to determine intents
      - executes RCON commands to the minecraft server via RCON based on the intent
    - shuts down - [ ] he server when there are `0` players left to save your money, you cheap son-of-a
- DialogFlow
  - receives player messages and determines the intent of the message  
- Firewall Rules
  - `0.0.0.0/0 via TCP 25565` for Minecraft
  - `0.0.0.0/0 via TCP 25575` for Minecraft RCON
