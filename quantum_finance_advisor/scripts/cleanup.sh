#!/usr/bin/env bash
# Remove os recursos criados no Cloud Run para evitar custos.
set -euo pipefail
REGION="${REGION:-us-central1}"
gcloud run services delete quantum-finance-advisor --region="$REGION" --quiet
gcloud artifacts repositories delete cloud-run-source-deploy --location="$REGION" --quiet
echo "Recursos removidos."
