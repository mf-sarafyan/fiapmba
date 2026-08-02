"""
Ferramentas de perfil do investidor (suitability).

O perfil fica no state da sessao (memoria de curto prazo do ADK), exatamente
como o 'add_prompt_to_state' do lab 32604 faz com o prompt do visitante.
A diferenca e que aqui o dado e estruturado e persiste por toda a conversa,
porque toda recomendacao subsequente depende dele.
"""

import logging
from typing import Any

from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)

PERFIS_VALIDOS = {"conservador", "moderado", "arrojado"}

# Bandas de referencia usadas apenas como ponto de partida da conversa.
# Nao substituem a analise do Lead Advisor nem constituem recomendacao formal.
ALOCACAO_REFERENCIA: dict[str, dict[str, str]] = {
    "conservador": {
        "renda_fixa_pos_fixada": "70-85%",
        "renda_fixa_inflacao": "10-20%",
        "renda_variavel": "0-10%",
        "observacao": (
            "Prioriza liquidez e protecao do principal. Foco em Tesouro Selic, "
            "CDBs de liquidez diaria e produtos cobertos pelo FGC."
        ),
    },
    "moderado": {
        "renda_fixa_pos_fixada": "40-55%",
        "renda_fixa_inflacao": "20-30%",
        "renda_variavel": "20-35%",
        "observacao": (
            "Aceita oscilacao em parte da carteira em troca de retorno real. "
            "Combina Tesouro IPCA+, FIIs e acoes de empresas consolidadas."
        ),
    },
    "arrojado": {
        "renda_fixa_pos_fixada": "15-30%",
        "renda_fixa_inflacao": "10-20%",
        "renda_variavel": "50-70%",
        "observacao": (
            "Tolera volatilidade elevada e horizonte longo. Ainda assim mantem "
            "reserva de emergencia em liquidez diaria antes de qualquer risco."
        ),
    },
}


def registrar_perfil_cliente(
    tool_context: ToolContext,
    perfil_risco: str,
    objetivo: str,
    horizonte_meses: int,
    valor_disponivel: float,
) -> dict[str, Any]:
    """Registra o perfil de suitability do cliente na memoria da sessao.

    Chame esta ferramenta assim que o cliente informar perfil de risco,
    objetivo, prazo e valor. Toda recomendacao posterior deve se apoiar
    nestes dados.

    Args:
        perfil_risco: "conservador", "moderado" ou "arrojado".
        objetivo: Meta do investimento em texto livre
            (ex.: "reserva de emergencia", "aposentadoria", "entrada de imovel").
        horizonte_meses: Prazo pretendido em meses (ex.: 6, 24, 120).
        valor_disponivel: Valor a investir em reais.

    Returns:
        Dicionario com 'status' e o perfil consolidado, incluindo uma banda de
        alocacao de referencia para o perfil informado.
    """
    perfil = perfil_risco.strip().lower()
    if perfil not in PERFIS_VALIDOS:
        return {
            "status": "error",
            "error_message": (
                f"Perfil '{perfil_risco}' invalido. "
                f"Use um destes: {', '.join(sorted(PERFIS_VALIDOS))}."
            ),
        }
    if horizonte_meses <= 0:
        return {"status": "error", "error_message": "horizonte_meses deve ser > 0."}
    if valor_disponivel <= 0:
        return {"status": "error", "error_message": "valor_disponivel deve ser > 0."}

    dados_perfil = {
        "perfil_risco": perfil,
        "objetivo": objetivo.strip(),
        "horizonte_meses": horizonte_meses,
        "valor_disponivel": valor_disponivel,
        "alocacao_referencia": ALOCACAO_REFERENCIA[perfil],
    }
    tool_context.state["perfil_cliente"] = dados_perfil
    logger.info("[state] perfil_cliente registrado: %s", perfil)
    return {"status": "success", "perfil_cliente": dados_perfil}


def obter_perfil_cliente(tool_context: ToolContext) -> dict[str, Any]:
    """Le o perfil do cliente ja registrado na sessao.

    Use antes de recomendar qualquer produto. Se retornar 'not_found',
    pergunte ao cliente e chame 'registrar_perfil_cliente' primeiro.

    Returns:
        Dicionario com 'status' ('success' ou 'not_found') e o perfil, se houver.
    """
    perfil = tool_context.state.get("perfil_cliente")
    if not perfil:
        return {
            "status": "not_found",
            "mensagem": (
                "Perfil ainda nao registrado. Pergunte ao cliente o perfil de "
                "risco, objetivo, prazo e valor disponivel."
            ),
        }
    return {"status": "success", "perfil_cliente": perfil}
