"""
Configuracao central do Consultor Financeiro Agentico da Quantum Finance.

Toda leitura de variavel de ambiente acontece aqui. Os demais modulos importam
deste arquivo, o que evita 'os.getenv' espalhado pelo projeto e deixa explicito
o contrato de configuracao da aplicacao.
"""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

# --- Modelo ---
MODEL_NAME = os.getenv("MODEL", "gemini-2.5-flash")

# --- Fonte de dados da B3 ---
# auto | mcp | fallback  (ver .env.example)
B3_DATA_SOURCE = os.getenv("B3_DATA_SOURCE", "auto").strip().lower()

BOLSAI_MCP_URL = os.getenv("BOLSAI_MCP_URL", "").strip()
BOLSAI_API_KEY = os.getenv("BOLSAI_API_KEY", "").strip()

BRAPI_TOKEN = os.getenv("BRAPI_TOKEN", "").strip()
BRAPI_BASE_URL = os.getenv("BRAPI_BASE_URL", "https://brapi.dev/api").strip()

# --- Observabilidade ---
# Cloud Logging so faz sentido quando ha credenciais GCP disponiveis.
# Em desenvolvimento local o logging padrao do Python ja resolve.
def setup_logging() -> None:
    """Configura logging: Cloud Logging no GCP, logging padrao localmente."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    if os.getenv("GOOGLE_CLOUD_PROJECT"):
        try:
            import google.cloud.logging

            google.cloud.logging.Client().setup_logging()
            logging.info("Cloud Logging habilitado.")
        except Exception as exc:  # pragma: no cover - depende do ambiente
            logging.warning("Cloud Logging indisponivel (%s). Usando stdout.", exc)


def validate() -> None:
    """Falha cedo em configuracoes incoerentes, com mensagem acionavel."""
    if B3_DATA_SOURCE not in {"auto", "mcp", "fallback"}:
        raise ValueError(
            f"B3_DATA_SOURCE invalido: '{B3_DATA_SOURCE}'. "
            "Use 'auto', 'mcp' ou 'fallback'."
        )
    if B3_DATA_SOURCE == "mcp" and not BOLSAI_MCP_URL:
        raise ValueError(
            "B3_DATA_SOURCE=mcp exige BOLSAI_MCP_URL preenchida no .env."
        )
    if B3_DATA_SOURCE == "fallback" and not BRAPI_TOKEN:
        logging.warning(
            "BRAPI_TOKEN vazio: a brapi.dev limita fortemente chamadas anonimas."
        )
