#!/usr/bin/env bash
# Deploy do Consultor Financeiro da Quantum Finance no Cloud Run.
# Baseado no fluxo do lab Google Cloud Skills Boost 32604.
set -euo pipefail

SERVICE_NAME="quantum-finance-advisor"

# --- 1. Variaveis de ambiente ---
export PROJECT_ID=$(gcloud config get-value project)
export PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
export REGION="${REGION:-us-central1}"
export SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "Projeto: $PROJECT_ID | Regiao: $REGION"

# --- 2. APIs necessarias ---
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  compute.googleapis.com

# --- 3. Permissao para a service account chamar os modelos ---
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"

# --- 4. Deploy ---
# Executar a partir do diretorio PAI de quantum_finance_advisor/
adk deploy cloud_run \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --service_name="$SERVICE_NAME" \
  --with_ui \
  ./quantum_finance_advisor

# --- 5. Variaveis de ambiente no servico ---
# Carrega o .env local e repassa ao Cloud Run.
set -a; source ./quantum_finance_advisor/.env; set +a

gcloud run services update "$SERVICE_NAME" \
  --region="$REGION" \
  --set-env-vars="MODEL=${MODEL},B3_DATA_SOURCE=${B3_DATA_SOURCE},BOLSAI_MCP_URL=${BOLSAI_MCP_URL},BOLSAI_API_KEY=${BOLSAI_API_KEY},BRAPI_TOKEN=${BRAPI_TOKEN},GOOGLE_CLOUD_LOCATION=global"

echo "Deploy concluido. URL do servico:"
gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)"
