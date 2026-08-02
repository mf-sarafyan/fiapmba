"""
Diagnostico do sistema multiagente Quantum Finance.

Valida conformidade com o PDF do trabalho FIAP e registra evidencias
de runtime em debug-86d071.log (modo debug).

Uso (a partir do diretorio PAI 'Multi Agents'):
    python -m quantum_finance_advisor.scripts.diagnostic_agent
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

# #region agent log
_LOG_PATH = Path(__file__).resolve().parents[1] / "debug-86d071.log"
_SESSION = "86d071"


def _dbg(location: str, message: str, data: dict, hypothesis_id: str) -> None:
    payload = {
        "sessionId": _SESSION,
        "timestamp": int(time.time() * 1000),
        "location": location,
        "message": message,
        "data": data,
        "hypothesisId": hypothesis_id,
        "runId": "diagnostic",
    }
    with open(_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


# #endregion


def _check_pdf_requirements() -> dict[str, bool]:
    """Verifica arquivos/modulos exigidos pelo PDF."""
    base = Path(__file__).resolve().parents[1]
    checks = {
        "lead_advisor": (base / "sub_agents" / "lead_advisor.py").exists(),
        "market_analyst": (base / "sub_agents" / "market_analyst.py").exists(),
        "b3_data_agent": (base / "sub_agents" / "b3_data_agent.py").exists(),
        "b3_tools": (base / "tools" / "b3_tools.py").exists(),
        "research_tools": (base / "tools" / "research_tools.py").exists(),
        "profile_tools": (base / "tools" / "profile_tools.py").exists(),
        "readme": (base / "README.md").exists(),
        "init_py": (base / "__init__.py").exists(),
        "agent_py": (base / "agent.py").exists(),
    }
    _dbg(
        "diagnostic_agent.py:requirements",
        "PDF requirement file checks",
        checks,
        "REQ",
    )
    return checks


def _check_agent_tool_wiring() -> dict:
    """H-C: AgentTools expostos com nomes corretos ao Lead Advisor."""
    from google.adk.tools.agent_tool import AgentTool

    from quantum_finance_advisor import agent

    root = agent.root_agent
    agent_tools = [t for t in root.tools if isinstance(t, AgentTool)]
    names = [t.agent.name for t in agent_tools]
    result = {
        "root_agent": root.name,
        "agent_tool_count": len(agent_tools),
        "agent_tool_names": names,
        "has_market_analyst": "market_analyst" in names,
        "has_b3_data_agent": "b3_data_agent" in names,
        "function_tools": [
            getattr(t, "__name__", type(t).__name__) for t in root.tools if not isinstance(t, AgentTool)
        ],
    }
    _dbg("diagnostic_agent.py:wiring", "AgentTool wiring", result, "C")
    return result


def _check_b3_data_source() -> dict:
    """H-B: MCP vs fallback conforme B3_DATA_SOURCE."""
    from quantum_finance_advisor import config
    from quantum_finance_advisor.tools.b3_tools import build_b3_tools

    tools, fonte = build_b3_tools()
    tool_types = [type(t).__name__ for t in tools]
    result = {
        "B3_DATA_SOURCE": config.B3_DATA_SOURCE,
        "BOLSAI_MCP_URL_set": bool(config.BOLSAI_MCP_URL),
        "BOLSAI_API_KEY_set": bool(config.BOLSAI_API_KEY),
        "BRAPI_TOKEN_set": bool(config.BRAPI_TOKEN),
        "fonte_ativa": fonte,
        "tool_count": len(tools),
        "tool_types": tool_types,
    }
    _dbg("diagnostic_agent.py:b3_source", "B3 data source resolution", result, "B")
    return result


def _check_env_and_model() -> dict:
    """H-E: Variaveis de ambiente necessarias para adk web / Vertex."""
    from quantum_finance_advisor import config

    env_path = Path(__file__).resolve().parents[1] / ".env"
    result = {
        "env_file_exists": env_path.exists(),
        "MODEL": config.MODEL_NAME,
        "GOOGLE_CLOUD_PROJECT": os.getenv("GOOGLE_CLOUD_PROJECT", ""),
        "GOOGLE_GENAI_USE_VERTEXAI": os.getenv("GOOGLE_GENAI_USE_VERTEXAI", ""),
        "has_gcp_project": bool(os.getenv("GOOGLE_CLOUD_PROJECT")),
    }
    _dbg("diagnostic_agent.py:env", "Environment config", result, "E")
    return result


def _run_http_smoke() -> dict:
    """H-D: Camada HTTP (brapi + BCB) responde sem alucinacao."""
    from quantum_finance_advisor.tools.b3_tools import (
        consultar_cotacao_b3,
        consultar_indicadores_macro,
    )

    cotacao = consultar_cotacao_b3("PETR4")
    macro = consultar_indicadores_macro()
    result = {
        "cotacao_status": cotacao.get("status"),
        "cotacao_fonte": cotacao.get("fonte"),
        "cotacao_tem_preco": cotacao.get("preco_atual") is not None,
        "macro_status": macro.get("status"),
        "macro_selic": (macro.get("selic_meta_ao_ano") or {}).get("valor"),
    }
    _dbg("diagnostic_agent.py:http_smoke", "HTTP tools smoke", result, "D")
    return result


def main() -> None:
    print("=" * 60)
    print("Quantum Finance — Diagnostico Multiagente (AgentTool)")
    print("=" * 60)

    req = _check_pdf_requirements()
    print("\n[1] Requisitos do PDF (arquivos):")
    for k, ok in req.items():
        print(f"  {'OK' if ok else 'FALTA'}  {k}")

    wiring = _check_agent_tool_wiring()
    print("\n[2] AgentTool wiring (Lead Advisor):")
    print(f"  root_agent: {wiring['root_agent']}")
    print(f"  AgentTools: {wiring['agent_tool_names']}")
    print(f"  FunctionTools: {wiring['function_tools']}")

    b3 = _check_b3_data_source()
    print("\n[3] Fonte de dados B3:")
    print(f"  modo: {b3['B3_DATA_SOURCE']}")
    print(f"  fonte ativa: {b3['fonte_ativa']}")
    print(f"  tools: {b3['tool_types']}")

    env = _check_env_and_model()
    print("\n[4] Ambiente:")
    print(f"  .env existe: {env['env_file_exists']}")
    print(f"  MODEL: {env['MODEL']}")
    print(f"  GCP project: {env['GOOGLE_CLOUD_PROJECT'] or '(nao configurado)'}")

    http = _run_http_smoke()
    print("\n[5] Smoke HTTP:")
    print(f"  PETR4: {http['cotacao_status']} via {http['cotacao_fonte']}")
    print(f"  Selic: {http['macro_selic']}%")

    all_files = all(req.values())
    wiring_ok = wiring["has_market_analyst"] and wiring["has_b3_data_agent"]
    http_ok = http["cotacao_status"] == "success"

    print("\n" + "=" * 60)
    if all_files and wiring_ok and http_ok:
        print("RESULTADO: Estrutura OK. Proximo passo: adk web + prompts do README secao 7.")
    else:
        print("RESULTADO: Corrija os itens acima antes de subir o ADK.")
    print(f"Logs de debug: {_LOG_PATH}")


if __name__ == "__main__":
    main()
