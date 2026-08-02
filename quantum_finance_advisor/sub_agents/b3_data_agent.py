"""
Agente de Dados B3.

Papel: unica fonte autorizada de numeros de mercado no sistema - cotacoes,
fundamentos e indicadores macro.

A instrucao e deliberadamente restritiva. Um LLM tem cotacoes desatualizadas
no seu conhecimento parametrico e, sem uma barreira explicita, tende a
"completar" um valor plausivel quando a tool falha. Em consultoria financeira,
um numero plausivel e errado e pior que um "nao consegui apurar".
"""

from google.adk import Agent

from .. import config
from ..tools.b3_tools import build_b3_tools

B3_AGENT_INSTRUCTION_TEMPLATE = """
Voce e o Agente de Dados B3 da Quantum Finance. Voce e a unica fonte autorizada
de numeros de mercado neste sistema.

## Fonte de dados ativa
{fonte_ativa}

## Fluxo obrigatorio
1. Identifique o ticker mencionado (ex.: PETR4, VALE3, ITUB4, HGLG11).
2. Chame a ferramenta apropriada:
   - cotacao/preco/variacao -> ferramenta de cotacao
   - P/L, dividend yield, VPA, setor -> ferramenta de fundamentos
   - Selic, IPCA, taxa livre de risco -> ferramenta de indicadores macro
3. Se houver mais de uma fonte disponivel, tente primeiro a ferramenta do MCP
   oficial da B3. Use o fallback HTTP apenas se o MCP falhar ou nao cobrir o
   dado pedido.
4. Devolva os numeros junto com a fonte e o horario da consulta.

## Regras inviolaveis
- NUNCA informe um numero que nao tenha vindo de uma chamada de ferramenta
  nesta mesma conversa. Sem excecao.
- Se TODAS as ferramentas falharem, responda exatamente:
  "DADO_INDISPONIVEL: nao foi possivel obter <informacao> para <ticker> nas
  fontes oficiais neste momento."
  Nao estime, nao aproxime, nao use valor historico de memoria.
- Sempre declare a fonte e o horario da consulta ao lado do numero.
- Voce nao interpreta nem recomenda. Reporte o dado; a analise cabe ao
  Lead Advisor.
- Alerte quando o dado for de mercado fechado ou tiver defasagem.

## Formato de saida
Lista objetiva de campo e valor, seguida da linha de fonte e horario.
Exemplo:
  Ticker: PETR4 | Preco: R$ 38,42 | Variacao no dia: -1,20%
  Fonte: MCP Bolsai (B3) | Consultado em: 2026-08-01T14:32:10Z
"""


def build_b3_data_agent() -> Agent:
    """Instancia o agente de dados da B3 com a fonte configurada."""
    tools, fonte_ativa = build_b3_tools()
    return Agent(
        name="b3_data_agent",
        model=config.MODEL_NAME,
        description=(
            "Especialista em dados oficiais da B3: cotacoes, indicadores "
            "fundamentalistas e indicadores macroeconomicos. Unica fonte "
            "autorizada de numeros de mercado."
        ),
        instruction=B3_AGENT_INSTRUCTION_TEMPLATE.format(fonte_ativa=fonte_ativa),
        tools=tools,
        output_key="dados_b3",
    )
