# usage
1. open a google cloud platform shell, clone this repo
2. `cd minecraft-gcp/`
3. replace PROJECT_ID placeholder `sed -i "s/PROJECT_ID/${GOOGLE_CLOUD_PROJECT}/g" instance.yml`
4. create the resources `gcloud deployment-manager deployments create mc --config instance.yml`
