"""
Ferramentas de pesquisa publica usadas pelo Agente Market Analyst.

Wikipedia cobre conceitos estruturais e estaveis (o que e um CDB, como funciona
o FGC, o que caracteriza um FII). A busca web cobre o que muda rapido
(regras vigentes do Tesouro Direto, mudancas tributarias, noticias de mercado).

A separacao importa: o Market Analyst explica CONCEITOS e PRODUTOS.
Preco de ativo especifico e responsabilidade exclusiva do agente da B3.
"""

import logging

logger = logging.getLogger(__name__)


def build_wikipedia_tool():
    """Adapta o WikipediaQueryRun do LangChain para o formato de tool do ADK."""
    from google.adk.tools.langchain_tool import LangchainTool
    from langchain_community.tools import WikipediaQueryRun
    from langchain_community.utilities import WikipediaAPIWrapper

    return LangchainTool(
        tool=WikipediaQueryRun(
            api_wrapper=WikipediaAPIWrapper(
                lang="pt",
                top_k_results=2,
                doc_content_chars_max=3000,
            )
        )
    )


def build_web_search_tool():
    """
    Busca web via DuckDuckGo (sem necessidade de API key).

    Retorna None se a dependencia nao estiver instalada - o Market Analyst
    continua funcional apenas com a Wikipedia.
    """
    try:
        from google.adk.tools.langchain_tool import LangchainTool
        from langchain_community.tools import DuckDuckGoSearchRun

        return LangchainTool(tool=DuckDuckGoSearchRun())
    except Exception as exc:
        logger.warning("Busca web indisponivel (%s). Seguindo so com Wikipedia.", exc)
        return None


def build_research_tools() -> list:
    """Monta a lista de tools de pesquisa disponiveis."""
    tools = [build_wikipedia_tool()]
    web = build_web_search_tool()
    if web is not None:
        tools.append(web)
    return tools
