# PROJETO DE CREDIT SCORING - QUANTUM FINANCE
## MBA em Data Science & Artificial Intelligence - Applied Statistics
---
## CONTEXTO EMPRESARIAL
A **Quantum Finance** é uma fintech inovadora que está entrando no mercado financeiro para competir com grandes players estabelecidos. Como parte de sua estratégia de crescimento sustentável, a empresa está enfrentando um crescimento preocupante na taxa de inadimplência entre seus clientes atuais.
Para tomar decisões mais precisas sobre concessões de crédito e atrair novos clientes com perfil de baixo risco, a Quantum Finance precisa desenvolver um modelo robusto de **Credit Scoring** utilizando técnicas avançadas de ciência de dados e machine learning.
---
## OBJETIVO DO PROJETO
Desenvolver um modelo preditivo de credit scoring utilizando regressão linear múltipla para prever o **SCORE_CREDITO** dos clientes, permitindo à Quantum Finance tomar decisões mais assertivas na concessão de crédito e reduzir significativamente a taxa de inadimplência.
---
## DATASET DISPONÍVEL
O dataset `Base_ScoreCredito_QuantumFinance.csv` contém **10.128 registros** de clientes com as seguintes variáveis:
### Variáveis Demográficas:
- **id**: Identificador único do cliente
- **idade**: Idade em anos
- **sexo**: Gênero (F = Feminino, M = Masculino)
- **estado_civil**: Estado civil (Solteiro, Casado, Divorciado)
- **escola**: Nível de escolaridade (ensino fundam, ensino médio, graduação, mestrado, doutorado)
- **Qte_dependentes**: Quantidade de dependentes
### Variáveis Profissionais e Financeiras:
- **tempo_ultimoservico**: Tempo no último emprego (meses)
- **trabalha**: Situação atual de trabalho (0=Não, 1=Sim)
- **vl_salario_mil**: Salário em milhares de reais
### Variáveis Patrimoniais:
- **reg_moradia**: Região da moradia (1 a 6 - segmentos geográficos A a F)
- **casa_propria**: Possui casa própria (0=Não, 1=Sim)
- **vl_imovel_em_mil**: Valor do imóvel em milhares de reais
- **Qte_cartoes**: Quantidade de cartões de crédito
- **Qte_carros**: Quantidade de carros
### Variável Target:
- **SCORE_CREDITO**: Score de crédito (variável dependente a ser predita)
---
## ETAPAS DO PROJETO
### 1. ANÁLISE EXPLORATÓRIA DE DADOS (EDA)
#### 1.1 Análise Descritiva Univariada
- Calcular estatísticas descritivas para todas as variáveis numéricas (média, mediana, desvio padrão, quartis, valores mínimos e máximos)
- Analisar a distribuição da variável target `SCORE_CREDITO` através de histogramas e boxplots
- Verificar a presença de outliers em todas as variáveis numéricas
- Analisar a distribuição de frequências das variáveis categóricas
#### 1.2 Análise de Dados Faltantes
- Identificar padrões de missing values em todas as variáveis
- Calcular percentual de dados faltantes por variável
- Decidir estratégias de tratamento (imputação, remoção, etc.)
#### 1.3 Visualizações Gráficas
- Criar histogramas e boxplots para variáveis numéricas
- Criar gráficos de barras para variáveis categóricas
- Analisar a distribuição da variável target por diferentes segmentos
### 2. TESTE DE HIPÓTESE E INTERVALO DE CONFIANÇA
#### 2.1 Teste de Hipótese para Diferença de Médias
Realizar teste t para comparar o score de crédito médio entre dois grupos:
**Hipótese a ser testada:**
- H₀: μ₁ = μ₂ (Não há diferença significativa no score de crédito médio entre clientes que
possuem casa própria e os que não possuem)
- H₁: μ₁ ≠ μ₂ (Há diferença significativa no score de crédito médio entre os grupos)
**Procedimento:**
- Aplicar teste de normalidade (Shapiro-Wilk ou Kolmogorov-Smirnov)
- Realizar teste t independente ou Mann-Whitney (caso não haja normalidade)
- Definir nível de significância α = 0,05
- Interpretar o p-valor e tomar decisão sobre as hipóteses
#### 2.2 Intervalo de Confiança
Calcular o intervalo de confiança de 95% para a média do score de crédito da população, interpretando os resultados no contexto do negócio.
### 3. ANÁLISE DE CORRELAÇÃO
#### 3.1 Matrix de Correlação
- Calcular correlação de Pearson entre todas as variáveis numéricas
- Criar heatmap da matriz de correlação
- Identificar variáveis com alta correlação (|r| > 0,7) para detectar possível multicolinearidade
#### 3.2 Análise de Associação
- Investigar relação entre variáveis categóricas e o score de crédito
- Realizar ANOVA para testar diferenças de médias entre grupos
- Criar boxplots para visualizar relações
### 4. PRÉ-PROCESSAMENTO DOS DADOS
#### 4.1 Tratamento de Dados Faltantes
- Implementar estratégias de imputação baseadas na análise exploratória
- Documentar todas as decisões tomadas
#### 4.2 Tratamento de Outliers
- Identificar outliers usando método IQR ou Z-score
- Decidir sobre remoção, transformação ou manutenção dos outliers
- Justificar decisões baseando-se no contexto do negócio
#### 4.3 Codificação de Variáveis Categóricas
- Aplicar One-Hot Encoding ou Label Encoding conforme apropriado
- Tratar a variável `estado_civil` que contém valores "na"
#### 4.4 Normalização/Padronização
- Avaliar necessidade de normalização das variáveis numéricas
- Aplicar técnicas apropriadas se necessário
#### 4.5 Divisão dos Dados
- Dividir dataset em treino (70%) e teste (30%)
- Utilizar stratified split se necessário
- Definir random_state para reprodutibilidade
### 5. MODELAGEM
#### 5.1 Modelo de Regressão Linear Múltipla
- Implementar modelo de regressão linear múltipla usando todas as variáveis
- Verificar significância estatística dos coeficientes
- Interpretar coeficientes no contexto do negócio
#### 5.2 Seleção de Variáveis
- Aplicar métodos de seleção de features:
- Forward Selection
- Backward Elimination
- Stepwise Selection
- Comparar modelos com diferentes conjuntos de variáveis
#### 5.3 Validação das Suposições do Modelo
- **Linearidade**: Analisar scatter plots de variáveis vs. target
- **Independência**: Verificar independência dos resíduos
- **Homocedasticidade**: Testar homogeneidade da variância dos resíduos
- **Normalidade dos resíduos**: Aplicar testes de normalidade e Q-Q plots
- **Ausência de multicolinearidade**: Calcular VIF (Variance Inflation Factor)
### 6. ANÁLISE DE RESÍDUOS
#### 6.1 Diagnóstico dos Resíduos
- Criar gráficos de resíduos vs. valores preditos
- Analisar normalidade dos resíduos com histogramas e Q-Q plots
- Identificar padrões que violem as suposições do modelo
- Detectar outliers e pontos de alta alavancagem
#### 6.2 Testes Estatísticos
- Teste de Breusch-Pagan para homocedasticidade
- Teste de Durbin-Watson para autocorrelação
- Teste de normalidade dos resíduos
### 7. MÉTRICAS DE AVALIAÇÃO
#### 7.1 Métricas de Regressão
- **MAE (Mean Absolute Error)**: Erro médio absoluto
- **MSE (Mean Squared Error)**: Erro quadrático médio
- **RMSE (Root Mean Squared Error)**: Raiz do erro quadrático médio
- **R² (Coeficiente de Determinação)**: Porcentagem da variância explicada
- **R² Ajustado**: R² penalizado pelo número de variáveis
#### 7.2 Análise de Performance
- Comparar métricas entre conjunto de treino e teste
- Avaliar se há overfitting ou underfitting
- Criar gráficos de valores reais vs. preditos
#### 7.3 Validação Cruzada
- Implementar k-fold cross-validation (k=5)
- Calcular média e desvio padrão das métricas
- Avaliar estabilidade do modelo
### 8. INTERPRETAÇÃO E CONCLUSÕES
#### 8.1 Interpretação dos Coeficientes
- Explicar o impacto de cada variável no score de crédito
- Identificar as variáveis mais importantes para o modelo
- Contextualizar resultados para o negócio da Quantum Finance
#### 8.2 Recomendações de Negócio
- Sugerir estratégias para melhoria do modelo
- Recomendar variáveis adicionais que poderiam ser coletadas
- Propor limites de score para decisões de crédito
---
## ENTREGÁVEIS
### 1. Arquivo Word com Resultados e Interpretações
O documento deve conter:
#### Quadro Conceitual Estatístico
Preencher a tabela com os seguintes componentes:
- **Tema**: Desenvolvimento de modelo de credit scoring
- **Problema**: [Definir problema específico]
- **Hipóteses conceituais**: [Elaborar hipóteses do estudo]
- **Objetivo principal**: [Objetivo específico do modelo]
- **População de estudo**: [Definir população-alvo]
- **Plano básico de análise**: [Estratégia de análise]
- **Técnica estatística**: Regressão Linear Múltipla
- **Resultado principal**: [Resultado esperado]
#### Análises Obrigatórias:
- **Análise descritiva das variáveis**: Estatísticas resumo e visualizações
- **Análise de correlação das variáveis**: Matriz de correlação e interpretações
- **Análise de resíduos**: Gráficos e testes diagnósticos
- **Acurácia e medidas de erros do modelo**: Todas as métricas calculadas
#### Recomendações Críticas:
Responder obrigatoriamente:
- **As variáveis são suficientes para tomada de decisão?**
- Análise da capacidade preditiva do modelo
- Sugestões de variáveis adicionais
- Limitações identificadas
- **As suposições do modelo de regressão linear múltipla foram atendidas?**
- Verificação de cada suposição
- Impacto das violações encontradas
- Sugestões de melhorias ou modelos alternativos
### 2. Script Python Completo
- Código comentado com todas as análises
- Estrutura organizada e reprodutível
- Documentação clara de cada etapa
- Visualizações de alta qualidade
---
## CRITÉRIOS DE AVALIAÇÃO
### Técnicos (70%)
- Correção metodológica das análises estatísticas
- Qualidade do pré-processamento dos dados
- Adequação das técnicas de modelagem
- Interpretação correta dos resultados
### Negócio (30%)
- Contextualização dos resultados para a Quantum Finance
- Qualidade das recomendações estratégicas
- Viabilidade das sugestões propostas
## RECURSOS NECESSÁRIOS
### Bibliotecas Python Recomendadas:
- `pandas`, `numpy`: Manipulação de dados
- `matplotlib`, `seaborn`: Visualizações
- `scikit-learn`: Modelagem e métricas
- `scipy`, `statsmodels`: Testes estatísticos e regressão
- `warnings`: Controle de avisos
### Referências Bibliográficas:
- James, G. et al. "An Introduction to Statistical Learning"
- Hastie, T. et al. "The Elements of Statistical Learning"
- Documentação oficial do scikit-learn
---
**Data de Entrega**: [Definir data]
**Formato de Entrega**: Arquivo Word + Script Python (.py ou .ipynb)
---
*Este projeto simula um desafio real de uma fintech, desenvolvendo competências essenciais em ciência de dados aplicada ao setor financeiro.*