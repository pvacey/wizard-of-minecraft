#!/usr/bin/env bash
echo "enter password for RCON:"
read -s NEW_PASSWORD
sed -i "s/PLACEHOLDER_PASSWORD/${NEW_PASSWORD}/g" instance.yml
sed -i "s/PROJECT_ID/${GOOGLE_CLOUD_PROJECT}/g" instance.yml
gcloud deployment-manager deployments create mc --config instance.yml
IP=$(gcloud compute instances describe minecraft-vm --zone us-central1-f | grep natIP | cut -d\: -f2)
echo "Server IP: $IP"
