# Quantum Finance — Consultor Financeiro Agêntico

Sistema multiagente que atua como consultor financeiro para clientes da Quantum Finance, combinando pesquisa de conceitos de mercado com **dados reais da B3** obtidos em tempo real.

> Projeto do MBA Data Science & Artificial Intelligence — FIAP
> Construído com o **Google Agent Development Kit (ADK)**, reaproveitando os padrões do laboratório Google Cloud Skills Boost 32604.

---

## 1. Arquitetura

```
                        ┌──────────────────────────────┐
                        │   root_agent = LEAD ADVISOR  │
   Cliente  ──────────► │   (Agente Estrategista)      │
                        │   LLM Agent — o "cérebro"    │
                        └───────────┬──────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │ AgentTool                 │ AgentTool                 │ FunctionTool
        ▼                           ▼                           ▼
┌───────────────────┐   ┌────────────────────────┐   ┌────────────────────────┐
│  MARKET ANALYST   │   │     B3 DATA AGENT      │   │  Perfil do cliente     │
│  (Pesquisador)    │   │  (Dados de mercado)    │   │  registrar / obter     │
├───────────────────┤   ├────────────────────────┤   ├────────────────────────┤
│ • Wikipedia (pt)  │   │ • MCP Bolsai (B3) ◄─── │   │ state["perfil_cliente"]│
│ • Busca web       │   │ • brapi.dev (fallback) │   └────────────────────────┘
│                   │   │ • BCB SGS (Selic/IPCA) │
└───────────────────┘   └────────────────────────┘
   conceitos e produtos      números de mercado
   (NÃO dá cotação)          (única fonte autorizada)
```

### Por que `AgentTool` e não `sub_agents`?

Esta é a principal decisão de projeto e vale explicar, porque diverge do laboratório de referência.

| Mecanismo | Semântica | Efeito no controle |
|---|---|---|
| `sub_agents` | Transferência de controle | O filho assume a conversa; o pai só volta no próximo turno |
| `AgentTool` | Chamada de função | O filho executa, devolve o resultado e o **pai mantém o controle** |

O lab do zoo usa `SequentialAgent` + `sub_agents` porque o fluxo é linear e conhecido de antemão: pesquisar → formatar. Um consultor financeiro não tem esse luxo. Diante de *"vale a pena comprar VALE3 hoje?"*, o Lead Advisor precisa acionar o B3 Data Agent (preço, P/L, dividend yield) **e** o Market Analyst (contexto setorial, riscos de commodities) **no mesmo turno**, comparar as duas respostas e só então decidir. Com `sub_agents` ele perderia o controle na primeira delegação e nunca chegaria à consolidação.

O trade-off: `AgentTool` gasta mais tokens (o Lead Advisor carrega o contexto inteiro) e é menos previsível que um fluxo determinístico. Aceitável aqui, porque a flexibilidade de roteamento é justamente o que caracteriza o comportamento agêntico exigido no enunciado.

---

## 2. Os três agentes

### 2.1 Lead Advisor — Agente Estrategista (`sub_agents/lead_advisor.py`)

É o `root_agent`. Recebe o perfil do cliente, decide quem acionar, consolida e recomenda.

**Lógica de roteamento embutida no prompt:**

| Tipo de pergunta | Agentes acionados |
|---|---|
| "Como funciona o Tesouro IPCA+?" | Market Analyst |
| "Quanto está a PETR4?" | B3 Data Agent |
| "Vale a pena investir em VALE3?" | **Ambos** — números + contexto |
| "Monte uma carteira para mim" | B3 (Selic/IPCA) + Market Analyst (produtos) |

**Guardrails principais:** nunca cita número que não veio do B3 Data Agent na mesma conversa; nunca recomenda produto incompatível com o perfil registrado; trata reserva de emergência como prioridade zero; nunca promete rentabilidade futura; sempre encerra com o disclaimer da Resolução CVM 20/2021.

### 2.2 Market Analyst — Agente Pesquisador (`sub_agents/market_analyst.py`)

Explica conceitos e produtos: CDB, Tesouro Direto, LCI/LCA, FIIs, FGC, tributação.

Duas ferramentas com propósitos distintos: **Wikipedia** para conceitos estruturais e estáveis, **busca web** para o que muda rápido (regras vigentes, mudanças tributárias, notícias).

**Fronteira explícita:** este agente é proibido de informar cotação, dividend yield ou qualquer número de ativo específico. Se perguntado, responde que o dado cabe ao B3 Data Agent.

### 2.3 B3 Data Agent — Agente de Dados (`sub_agents/b3_data_agent.py`)

Única fonte autorizada de números de mercado.

| Ferramenta | Retorna |
|---|---|
| `consultar_cotacao_b3` | Preço, variação, mín/máx do dia e 52 semanas, volume, valor de mercado |
| `consultar_fundamentos_b3` | P/L, LPA, VPA, P/VP, dividend yield, beta, setor |
| `consultar_indicadores_macro` | Selic meta e IPCA 12m, direto da API SGS do Banco Central |

Com o MCP ativo, as tools do servidor Bolsai entram como fonte **primária** e as acima ficam como fallback.

---

## 3. Estratégia anti-alucinação

O enunciado é direto: *"um consultor financeiro não pode alucinar cotações"*. Esse é o requisito mais difícil do projeto, porque contraria o comportamento natural de um LLM — o modelo tem cotações desatualizadas no conhecimento paramétrico e, quando uma ferramenta falha, tende a preencher a lacuna com um valor plausível. Em consultoria financeira, **um número plausível e errado é pior que um "não consegui apurar"**.

Quatro camadas de defesa:

**1. Isolamento da fonte.** Só um agente pode produzir números. O Market Analyst é explicitamente proibido, o que elimina a rota mais provável de vazamento (o pesquisador "lembrando" um preço durante a explicação).

**2. Mensagens de erro que instruem o modelo.** As tools não retornam apenas `status: error` — o campo `error_message` carrega a instrução `"Não invente a cotação; informe o usuário da indisponibilidade"`. O texto do erro entra no contexto do LLM e funciona como reforço de guardrail no momento exato do risco.

**3. Token de falha explícito.** Quando todas as fontes falham, o agente deve emitir literalmente `DADO_INDISPONIVEL: ...`. Uma string fixa é mais fácil de o modelo reproduzir do que uma recusa em texto livre, e é auditável em log e em teste automatizado.

**4. Proveniência obrigatória.** Todo retorno traz `fonte` e `consultado_em`. Como o Lead Advisor precisa exibir esses campos, um número sem proveniência fica visivelmente incompleto na saída.

**Limitação honesta:** nada disso é garantia formal. São guardrails probabilísticos em nível de prompt — reduzem muito a chance de alucinação, não a zeram. Uma defesa determinística exigiria um validador pós-geração que extraísse números da resposta final e conferisse cada um contra os retornos das tools. Fica como evolução natural do projeto.

---

## 4. Fontes de dados e o modo `auto`

O MCP da Bolsai é opcional no enunciado e tem limite de **200 requisições/dia** no plano gratuito. Depender só dele é frágil no dia da apresentação; ignorá-lo perde o diferencial. A solução é a variável `B3_DATA_SOURCE`:

| Valor | Comportamento |
|---|---|
| `auto` *(padrão)* | Tenta montar o MCP; se falhar, sobe apenas o fallback. **Nunca deixa a aplicação cair.** |
| `mcp` | Exige o MCP; se falhar, a aplicação não sobe. Modo "produção estrita". |
| `fallback` | Ignora o MCP e usa só brapi.dev + BCB. Útil para desenvolvimento sem gastar cota. |

Em `auto` com MCP disponível, **ambos** os conjuntos de tools são expostos, e o prompt instrui o agente a tentar o MCP primeiro. O nome da fonte ativa é injetado dinamicamente na instrução do agente, então ele sempre sabe declarar de onde o dado veio.

---

## 5. Estrutura do projeto

```
quantum_finance_advisor/
├── __init__.py                    # from . import agent — exigido pelo ADK
├── agent.py                       # expõe root_agent
├── config.py                      # leitura centralizada de env + validação
├── requirements.txt
├── .env.example                   # copiar para .env
├── sub_agents/
│   ├── lead_advisor.py            # Agente Estrategista (root)
│   ├── market_analyst.py          # Agente Pesquisador
│   └── b3_data_agent.py           # Agente de Dados B3
├── tools/
│   ├── b3_tools.py                # MCP Bolsai + fallback brapi.dev + BCB
│   ├── research_tools.py          # Wikipedia + busca web
│   └── profile_tools.py           # suitability no state da sessão
└── scripts/
    ├── smoke_test_tools.py        # testa as tools sem subir o ADK
    ├── deploy_cloud_run.sh
    └── cleanup.sh
```

---

## 6. Como executar

### Local

```bash
pip install -r quantum_finance_advisor/requirements.txt

cp quantum_finance_advisor/.env.example quantum_finance_advisor/.env
# edite o .env: MODEL, GOOGLE_CLOUD_PROJECT, BRAPI_TOKEN, BOLSAI_API_KEY

# valide as integrações HTTP antes de subir o agente
python -m quantum_finance_advisor.scripts.smoke_test_tools

# interface web do ADK (executar no diretório PAI)
adk web
```

Se o smoke test falhar, o problema é rede, token ou API — não o agente. Isolar essa camada economiza muito tempo de depuração.

### Cloud Run

```bash
export REGION=us-central1
./quantum_finance_advisor/scripts/deploy_cloud_run.sh
```

O script habilita as APIs, concede `roles/aiplatform.user` à service account, roda `adk deploy cloud_run --with_ui` e repassa as variáveis de ambiente ao serviço.

Ao terminar a demonstração: `./quantum_finance_advisor/scripts/cleanup.sh`.

---

## 7. Roteiro sugerido para o vídeo de demonstração

Sequência pensada para evidenciar cada caminho de roteamento — é o que diferencia uma demo de um chat genérico:

| # | Prompt | O que demonstra |
|---|---|---|
| 1 | `Olá, quero começar a investir` | Apresentação e coleta de perfil |
| 2 | `Sou moderado, quero aposentadoria, prazo de 10 anos, tenho R$ 50 mil` | `registrar_perfil_cliente` gravando no state |
| 3 | `Como funciona o Tesouro IPCA+?` | Roteamento para **só** o Market Analyst |
| 4 | `Qual a cotação da PETR4 agora?` | Roteamento para **só** o B3 Data Agent, com fonte e horário |
| 5 | `Vale a pena investir em VALE3 hoje?` | **Os dois agentes** no mesmo turno + consolidação |
| 6 | `Monte uma carteira com meu perfil` | Uso do state + Selic/IPCA reais na alocação |
| 7 | `Qual a cotação da ZZZZ9?` | **Anti-alucinação:** `DADO_INDISPONIVEL` em vez de número inventado |
| 8 | `Quero colocar tudo em cripto alavancado` | Guardrail de suitability recusando o descompasso |

Os prompts 5, 7 e 8 são os que mais valem ponto — mostram orquestração real, honestidade sobre falha e aderência regulatória.

---

## 8. Limitações conhecidas

- **Sem memória entre sessões.** O perfil vive no `state` do ADK e se perde ao encerrar a conversa. Persistir exigiria um `SessionService` com backend (Firestore ou Cloud SQL).
- **Latência em perguntas compostas.** Quando o Lead Advisor aciona os dois especialistas, são três chamadas de LLM em cadeia. Um `ParallelAgent` reduziria o tempo de parede, ao custo de perder o roteamento dinâmico.
- **Cota do MCP.** 200 requisições/dia no plano gratuito. Em demonstração ao vivo, considere `B3_DATA_SOURCE=fallback` nos ensaios e `auto` na gravação final.
- **Dados de mercado fechado.** As APIs retornam o último fechamento fora do pregão. O agente é instruído a sinalizar, mas convém validar isso no vídeo.
- **Não substitui consultoria regulada.** O sistema é educacional. A recomendação final carrega o disclaimer da Resolução CVM 20/2021.

---

## 9. Checklist dos entregáveis

- [x] Estrutura multiagente com os três agentes exigidos
- [x] Integração com dados reais da B3 (MCP Bolsai + fallback)
- [x] Documentação técnica descrevendo fluxo de tools e prompts *(este arquivo)*
- [ ] Repositório GitHub — subir o projeto com o `.env` fora do versionamento
- [ ] Vídeo de demonstração — usar o roteiro da seção 7
- [ ] Grupo de até 4 pessoas registrado
