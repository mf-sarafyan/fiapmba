"""
Quantum Finance - Consultor Financeiro Agentico
MBA Data Science & Artificial Intelligence - FIAP

Ponto de entrada do sistema multiagente. O ADK procura por `root_agent`
neste modulo.

Arquitetura:

    root_agent  =  lead_advisor  (Agente Estrategista - LLM Agent)
                        |
        +---------------+----------------+
        |                                |
    AgentTool                        AgentTool
        |                                |
  market_analyst                   b3_data_agent
  (Wikipedia, busca web)     (MCP Bolsai -> fallback brapi.dev + BCB)

O Lead Advisor decide dinamicamente quais especialistas acionar em cada turno,
podendo chamar os dois e consolidar - comportamento que um SequentialAgent
fixo nao permitiria.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from . import config
from .sub_agents.lead_advisor import build_lead_advisor

config.setup_logging()
config.validate()

root_agent = build_lead_advisor()
