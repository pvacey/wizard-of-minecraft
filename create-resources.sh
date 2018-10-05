#!/usr/bin/env bash

# replace placeholder values in the code
echo "enter password for RCON:"
read -s NEW_PASSWORD
echo "[*] replace placeholder values in project files"
sed -i "s/PLACEHOLDER_PASSWORD/${NEW_PASSWORD}/g" instance.yml
sed -i "s/PLACEHOLDER_PASSWORD/${NEW_PASSWORD}/g" cloud-function/main.py
sed -i "s/PROJECT_ID/${GOOGLE_CLOUD_PROJECT}/g" instance.yml
sed -i "s/PLACEHOLDER_PROJECT_ID/${GOOGLE_CLOUD_PROJECT}/g" cloud-function/main.py

# create the minecraft instance and open firewall rules
echo "[*] create compute instance and firewall rules"
gcloud deployment-manager deployments create mc --config instance.yml


# create a pubsub topic for the interesting minecraft logs
echo "[*] create pubsub topic"
gcloud beta pubsub topics create minecraft-logs

# create filters to send events to the pubsub topic
echo "[*] create stackdriver logging sinks"
gcloud beta logging sinks create minecraft-chat-logs pubsub.googleapis.com/projects/minecraft-212921/topics/minecraft-logs --log-filter='jsonPayload.instance.name="minecraft-vm" "]: <"'
gcloud beta logging sinks create minecraft-disconnect-logs pubsub.googleapis.com/projects/minecraft-212921/topics/minecraft-logs --log-filter='jsonPayload.instance.name="minecraft-vm" "left the game"'

# grant sink identities access to pubsub
echo "[*] grant logging sink identities access to pubsub topic"
TMP1=$(gcloud beta logging sinks describe minecraft-chat-logs | grep writerIdentity | cut -d" " -f2)
TMP2=$(gcloud beta logging sinks describe minecraft-disconnect-logs | grep writerIdentity | cut -d" " -f2)
gcloud beta pubsub topics add-iam-policy-binding minecraft-logs --member $TMP1 --role roles/pubsub.publisher
gcloud beta pubsub topics add-iam-policy-binding minecraft-logs --member $TMP2 --role roles/pubsub.publisher

# deploy cloud function
echo "[*] deploy cloud function"
cd cloud-function
gcloud beta functions deploy minecraft-bot --entry-point log_handler --runtime python37 --trigger-topic minecraft-logs
cd ..

# add permssions to cloud function service role, if possible
echo "[*] grant cloud function service role access to compute and dialogflow"
TMP=$(gcloud iam service-accounts list --filter "app engine" | grep @ | rev | cut -d" " -f1 | rev)
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT  --member serviceAccount:$TMP --role "roles/compute.instanceAdmin"
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT  --member serviceAccount:$TMP --role "roles/dialogflow.client"

# retrieve the server IP
echo "[*] done..."
IP=$(gcloud compute instances describe minecraft-vm --zone us-central1-f | grep natIP | cut -d\: -f2)
echo
echo "Minecraft Server IP: $IP"
echo
