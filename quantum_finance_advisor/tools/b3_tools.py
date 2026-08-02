"""
Camada de acesso a dados da B3.

Estrategia (definida em config.B3_DATA_SOURCE):
  - 'mcp'      -> apenas o MCP da Bolsai. Se falhar, a aplicacao nao sobe.
  - 'fallback' -> apenas a API HTTP (brapi.dev).
  - 'auto'     -> tenta montar o MCPToolset; se nao conseguir, expoe o fallback.

Motivacao: o enunciado exige que o agente NUNCA invente cotacao. Ter duas fontes
verificaveis reduz o risco de o agente "preencher a lacuna" com conhecimento
parametrico do modelo quando uma delas estiver fora do ar ou sem cota.
"""

import logging
from datetime import datetime, timezone
from typing import Any

import requests

from .. import config

logger = logging.getLogger(__name__)

_TIMEOUT_SEGUNDOS = 15


# ----------------------------------------------------------------------------
# 1. Fonte primaria: MCP da Bolsai
# ----------------------------------------------------------------------------
def build_bolsai_mcp_toolset():
    """
    Monta o MCPToolset apontando para o servidor MCP da Bolsai.

    Segue o mesmo padrao do lab 32604 (StreamableHTTPConnectionParams +
    header Authorization). A diferenca e que a Bolsai usa uma API key estatica,
    e nao um ID token de service account do Cloud Run.

    Retorna None quando o MCP nao esta configurado ou nao pode ser instanciado.
    """
    from google.adk.tools.mcp_tool.mcp_toolset import (
        MCPToolset,
        StreamableHTTPConnectionParams,
    )

    if not config.BOLSAI_MCP_URL:
        logger.warning("BOLSAI_MCP_URL nao configurada; MCP desabilitado.")
        return None

    headers: dict[str, str] = {}
    if config.BOLSAI_API_KEY:
        headers["Authorization"] = f"Bearer {config.BOLSAI_API_KEY}"
    else:
        logger.warning(
            "BOLSAI_API_KEY vazia: o MCP provavelmente rejeitara as chamadas."
        )

    toolset = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=config.BOLSAI_MCP_URL,
            headers=headers,
        )
    )
    logger.info("MCPToolset da Bolsai configurado em %s", config.BOLSAI_MCP_URL)
    return toolset


# ----------------------------------------------------------------------------
# 2. Fonte de fallback: brapi.dev
# ----------------------------------------------------------------------------
def _brapi_get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    """Chamada HTTP crua a brapi.dev, com token opcional."""
    if config.BRAPI_TOKEN:
        params = {**params, "token": config.BRAPI_TOKEN}
    url = f"{config.BRAPI_BASE_URL}{path}"
    resposta = requests.get(url, params=params, timeout=_TIMEOUT_SEGUNDOS)
    resposta.raise_for_status()
    return resposta.json()


def consultar_cotacao_b3(ticker: str) -> dict[str, Any]:
    """Consulta a cotacao atual e dados de mercado de um ativo listado na B3.

    Use esta ferramenta sempre que precisar do preco, variacao, volume ou valor
    de mercado de uma acao, BDR ou FII brasileiro. NUNCA responda um preco de
    memoria: se esta ferramenta falhar, informe a falha ao usuario.

    Args:
        ticker: Codigo de negociacao na B3, com ou sem sufixo .SA
            (exemplos: "PETR4", "VALE3", "HGLG11").

    Returns:
        Dicionario com 'status' ('success' ou 'error'). Em caso de sucesso,
        traz preco, variacao percentual, minima/maxima do dia, volume,
        valor de mercado, a fonte do dado e o horario da consulta.
    """
    codigo = ticker.strip().upper().removesuffix(".SA")
    if not codigo:
        return {"status": "error", "error_message": "Ticker vazio."}

    try:
        dados = _brapi_get(f"/quote/{codigo}", {"range": "1d", "interval": "1d"})
        resultados = dados.get("results") or []
        if not resultados:
            return {
                "status": "error",
                "error_message": f"Ticker '{codigo}' nao encontrado na B3.",
            }
        r = resultados[0]
        return {
            "status": "success",
            "fonte": "brapi.dev (fallback)",
            "consultado_em": datetime.now(timezone.utc).isoformat(),
            "ticker": r.get("symbol"),
            "empresa": r.get("longName") or r.get("shortName"),
            "moeda": r.get("currency", "BRL"),
            "preco_atual": r.get("regularMarketPrice"),
            "variacao_percentual_dia": r.get("regularMarketChangePercent"),
            "minima_dia": r.get("regularMarketDayLow"),
            "maxima_dia": r.get("regularMarketDayHigh"),
            "fechamento_anterior": r.get("regularMarketPreviousClose"),
            "volume": r.get("regularMarketVolume"),
            "valor_de_mercado": r.get("marketCap"),
            "minima_52_semanas": r.get("fiftyTwoWeekLow"),
            "maxima_52_semanas": r.get("fiftyTwoWeekHigh"),
        }
    except requests.HTTPError as exc:
        logger.exception("Erro HTTP ao consultar %s", codigo)
        return {
            "status": "error",
            "error_message": (
                f"Falha HTTP ao consultar '{codigo}' na brapi.dev: {exc}. "
                "Nao invente a cotacao; informe o usuario da indisponibilidade."
            ),
        }
    except Exception as exc:  # rede, timeout, JSON malformado
        logger.exception("Erro ao consultar %s", codigo)
        return {
            "status": "error",
            "error_message": (
                f"Nao foi possivel obter dados de '{codigo}': {exc}. "
                "Nao invente a cotacao; informe o usuario da indisponibilidade."
            ),
        }


def consultar_fundamentos_b3(ticker: str) -> dict[str, Any]:
    """Consulta indicadores fundamentalistas de um ativo listado na B3.

    Use para avaliar se um ativo esta caro ou barato, sua rentabilidade e seu
    historico de dividendos. Complementa a cotacao com dados de balanco.

    Args:
        ticker: Codigo de negociacao na B3 (exemplos: "ITUB4", "BBAS3").

    Returns:
        Dicionario com 'status' e, em caso de sucesso, indicadores como
        P/L, LPA, VPA, dividend yield e setor de atuacao.
    """
    codigo = ticker.strip().upper().removesuffix(".SA")
    if not codigo:
        return {"status": "error", "error_message": "Ticker vazio."}

    try:
        dados = _brapi_get(
            f"/quote/{codigo}",
            {"fundamental": "true", "modules": "defaultKeyStatistics,summaryProfile"},
        )
        resultados = dados.get("results") or []
        if not resultados:
            return {
                "status": "error",
                "error_message": f"Ticker '{codigo}' nao encontrado na B3.",
            }
        r = resultados[0]
        estatisticas = r.get("defaultKeyStatistics") or {}
        perfil = r.get("summaryProfile") or {}
        return {
            "status": "success",
            "fonte": "brapi.dev (fallback)",
            "consultado_em": datetime.now(timezone.utc).isoformat(),
            "ticker": r.get("symbol"),
            "empresa": r.get("longName") or r.get("shortName"),
            "setor": perfil.get("sector"),
            "industria": perfil.get("industry"),
            "preco_lucro_pl": r.get("priceEarnings"),
            "lucro_por_acao_lpa": r.get("earningsPerShare"),
            "valor_patrimonial_por_acao": estatisticas.get("bookValue"),
            "preco_sobre_valor_patrimonial": estatisticas.get("priceToBook"),
            "dividend_yield": estatisticas.get("dividendYield"),
            "beta": estatisticas.get("beta"),
            "valor_de_mercado": r.get("marketCap"),
        }
    except Exception as exc:
        logger.exception("Erro ao consultar fundamentos de %s", codigo)
        return {
            "status": "error",
            "error_message": (
                f"Nao foi possivel obter fundamentos de '{codigo}': {exc}. "
                "Nao invente indicadores; informe a indisponibilidade."
            ),
        }


def consultar_indicadores_macro() -> dict[str, Any]:
    """Consulta indicadores macroeconomicos brasileiros de referencia.

    Use para contextualizar recomendacoes de renda fixa (CDB, Tesouro Direto,
    LCI/LCA) ou para comparar o retorno de uma acao com a taxa livre de risco.
    Retorna a taxa Selic e o IPCA acumulado, direto da API de dados abertos do
    Banco Central (series SGS 432 e 13522).

    Returns:
        Dicionario com 'status' e, em caso de sucesso, os valores mais recentes
        de Selic meta (% a.a.) e IPCA acumulado em 12 meses (%).
    """
    series = {"selic_meta_ao_ano": 432, "ipca_acumulado_12m": 13522}
    resultado: dict[str, Any] = {
        "status": "success",
        "fonte": "Banco Central do Brasil - API SGS",
        "consultado_em": datetime.now(timezone.utc).isoformat(),
    }
    erros: list[str] = []

    for nome, codigo_serie in series.items():
        url = (
            f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}"
            "/dados/ultimos/1?formato=json"
        )
        try:
            resposta = requests.get(url, timeout=_TIMEOUT_SEGUNDOS)
            resposta.raise_for_status()
            registro = resposta.json()[0]
            resultado[nome] = {
                "valor": float(registro["valor"]),
                "data_referencia": registro["data"],
            }
        except Exception as exc:
            logger.warning("Falha na serie SGS %s: %s", codigo_serie, exc)
            erros.append(f"{nome} (SGS {codigo_serie})")

    if erros:
        resultado["series_indisponiveis"] = erros
        if len(erros) == len(series):
            return {
                "status": "error",
                "error_message": (
                    "Nenhuma serie do Banco Central respondeu. "
                    "Nao estime Selic ou IPCA de memoria."
                ),
            }
    return resultado


# ----------------------------------------------------------------------------
# 3. Montagem da lista de tools conforme a estrategia configurada
# ----------------------------------------------------------------------------
def build_b3_tools() -> tuple[list[Any], str]:
    """
    Retorna (lista_de_tools, descricao_da_fonte_ativa).

    A descricao e injetada no prompt do agente B3 para que ele saiba de onde
    o dado veio e possa declarar a fonte na resposta - requisito de auditoria
    de um consultor financeiro.
    """
    tools_fallback = [
        consultar_cotacao_b3,
        consultar_fundamentos_b3,
        consultar_indicadores_macro,
    ]

    if config.B3_DATA_SOURCE == "fallback":
        return tools_fallback, "API publica brapi.dev + Banco Central (SGS)"

    mcp = None
    try:
        mcp = build_bolsai_mcp_toolset()
    except Exception as exc:
        logger.exception("Falha ao montar o MCPToolset da Bolsai: %s", exc)
        if config.B3_DATA_SOURCE == "mcp":
            raise

    if config.B3_DATA_SOURCE == "mcp":
        if mcp is None:
            raise RuntimeError(
                "B3_DATA_SOURCE=mcp, mas o MCPToolset da Bolsai nao pode ser "
                "criado. Verifique BOLSAI_MCP_URL e BOLSAI_API_KEY."
            )
        return [mcp], "MCP da Bolsai (dados oficiais B3)"

    # modo 'auto'
    if mcp is not None:
        return (
            [mcp, *tools_fallback],
            "MCP da Bolsai como fonte primaria; brapi.dev e Banco Central como fallback",
        )
    logger.warning("MCP indisponivel; operando somente com fallback HTTP.")
    return tools_fallback, "API publica brapi.dev + Banco Central (MCP indisponivel)"
