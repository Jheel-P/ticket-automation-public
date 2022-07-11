gcloud functions deploy servicenow-client-function-stg --region={GCP_REGION} \
    --entry-point=MAIN \
    --memory=256MB \
    --runtime=python38 \
    --service-account={SA_EMAIL} \
    --source={GSR_SOURCE_PATH} \
    --timeout=60s \
    --update-labels=LABELS \
    --set-env-vars=CONFIG_KEY=ticket-automation/incident-processing-function-config \
    --max-instances=20 \
    --trigger-http \
    --project={DEPLOYMENT_PROJECT}
