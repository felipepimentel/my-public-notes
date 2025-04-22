# Conceitos Fundamentais

O MCP se estrutura em torno de alguns conceitos fundamentais que determinam como os modelos interagem com dados e sistemas externos. Esta seção explora cada um desses componentes essenciais.

## Roots: Territórios de Acesso

```mermaid
graph TD
    R[Roots] --- R1[Root: sistema://clientes]
    R --- R2[Root: operacoes://historico]
    R --- R3[Root: docs://manuais]
    
    R1 --- C1[Cliente A]
    R1 --- C2[Cliente B]
    
    R2 --- T1[Operação X]
    R2 --- T2[Operação Y]
    
    R3 --- P1[Manual do Produto]
    R3 --- P2[Guia de Troubleshooting]
    
    classDef root fill:#fffacd,stroke:#333,stroke-width:2px;
    classDef item fill:#d3f0c2,stroke:#333,stroke-width:1px;
    
    class R,R1,R2,R3 root;
    class C1,C2,T1,T2,P1,P2 item;
```

**O que são:** Roots (raízes) são como os territórios ou zonas que delimitam onde um servidor MCP pode operar. São o equivalente a crachás de segurança que controlam o acesso a diferentes áreas de um prédio.

**Analogia:** Se o MCP fosse um sistema de arquivos, os Roots seriam as pastas principais. Se fosse um shopping, seriam as diferentes lojas e áreas.

**Função na prática:**

- **Segurança:** Limitam o escopo de atuação de cada servidor
- **Organização:** Agrupam recursos relacionados
- **Controle:** Permitem gerenciar permissões de forma granular

Um servidor MCP para recursos humanos, por exemplo, poderia ter acesso ao root `rh://políticas` mas não ao root `financeiro://orçamentos`.

## Resources: A Biblioteca de Conhecimento

```mermaid
graph TD
    Library[Resources: A Biblioteca] --- B1[Políticas da Empresa]
    Library --- B2[Dados de Produtos]
    Library --- B3[Manuais Técnicos]
    Library --- B4[FAQ de Suporte]
    
    classDef library fill:#b5e8f7,stroke:#333,stroke-width:2px;
    classDef book fill:#d3f0c2,stroke:#333,stroke-width:1px;
    
    class Library library;
    class B1,B2,B3,B4 book;
```

**O que são:** Resources são as "fontes de conhecimento" que o LLM pode consultar. São os documentos, dados ou conteúdos que o servidor MCP disponibiliza para o LLM.

**Analogia:** Pense nos Resources como livros em uma biblioteca ou artigos em uma enciclopédia. O LLM pode solicitá-los, lê-los e usar as informações para responder perguntas ou tomar decisões.

**Função na prática:**

- **Contextualização:** Fornecem informações atualizadas e específicas
- **Conhecimento:** Permitem que o LLM acesse dados que não estão em seu treinamento
- **Precisão:** Garantem respostas baseadas em informações oficiais e atuais

Por exemplo, um LLM conectado via MCP poderia acessar o resource `empresa://produtos/catalogo-atual` para fornecer informações precisas sobre os produtos disponíveis no momento.

## Prompts: As Receitas Prontas

```mermaid
graph TD
    P[Prompts: Receitas] --- P1[Análise de Cliente]
    P --- P2[Geração de Relatório]
    P --- P3[Resposta a Dúvidas]
    P --- P4[Resolução de Problemas]
    
    P1 --- S1["1. Verificar perfil
    2. Analisar histórico
    3. Recomendar próximos passos"]
    
    P2 --- S2["1. Coletar dados
    4. Identificar padrões
    5. Formatar insights"]
    
    classDef prompt fill:#f9d5e5,stroke:#333,stroke-width:2px;
    classDef steps fill:#d3f0c2,stroke:#333,stroke-width:1px;
    
    class P,P1,P2,P3,P4 prompt;
    class S1,S2 steps;
```

**O que são:** Prompts são instruções padronizadas que guiam o LLM em tarefas específicas. São como receitas ou templates para interações comuns.

**Analogia:** Se o LLM fosse um chef, os Prompts seriam receitas testadas e aprovadas. Garantem que cada "prato" (resposta) siga um padrão consistente e inclua todos os ingredientes necessários.

**Função na prática:**

- **Padronização:** Garantem consistência nas interações repetitivas
- **Completude:** Asseguram que todas as etapas de um processo sejam seguidas
- **Eficiência:** Eliminam a necessidade de reinventar instruções comuns

Empresas podem criar prompts específicos como "Análise de Cliente" ou "Diagnóstico de Problema" que seguem seus procedimentos internos.

## Tools: A Caixa de Ferramentas

```mermaid
graph TD
    T[Tools: Ferramentas] --- T1[Calculadora de Preços]
    T --- T2[Verificador de Disponibilidade]
    T --- T3[Pesquisa em Documentos]
    T --- T4[Gerador de Relatórios]
    
    T1 --- F1["Calcula preços com base em parâmetros"]
    T2 --- F2["Verifica disponibilidade em estoque"]
    
    classDef tool fill:#9ff,stroke:#333,stroke-width:2px;
    classDef func fill:#d3f0c2,stroke:#333,stroke-width:1px;
    
    class T,T1,T2,T3,T4 tool;
    class F1,F2 func;
```

**O que são:** Tools são funções ou capacidades que o LLM pode invocar para realizar ações no mundo real. São como botões ou controles que permitem que a IA faça algo além de gerar texto.

**Analogia:** Se o LLM fosse um piloto em um cockpit, as Tools seriam os diversos controles e botões que permitem operar a aeronave.

**Função na prática:**

- **Ação:** Permitem que o LLM execute operações em sistemas externos
- **Automação:** Habilitam tarefas que antes exigiam intervenção humana
- **Integração:** Conectam o LLM a funcionalidades de sistemas existentes

Uma Tool pode permitir que o LLM consulte um banco de dados, agende uma reunião, reserve um produto ou calcule métricas complexas.

## Sampling: Consultando o Oráculo

```mermaid
sequenceDiagram
    participant S as Servidor MCP
    participant C as Cliente MCP
    participant LLM as Modelo de IA
    participant U as Usuário
    
    S->>C: "Preciso gerar texto com esses dados"
    C->>U: "Posso usar o LLM para esta tarefa?"
    U->>C: "Sim, autorizado"
    C->>LLM: "Gerar texto conforme especificação"
    LLM->>C: "Texto gerado"
    C->>S: "Aqui está o resultado"
    
    Note over S,C: O servidor pediu ajuda ao LLM
```

**O que é:** Sampling é quando um servidor MCP precisa da inteligência do LLM para gerar conteúdo. É um fluxo inverso onde o servidor pede ao cliente LLM para resolver um problema.

**Analogia:** Imagine um assistente (servidor) que, ao se deparar com uma tarefa criativa, pede ajuda a um especialista (LLM) via o gerente (cliente MCP).

**Função na prática:**

- **Geração de conteúdo:** Permite que servidores utilizem o poder dos LLMs
- **Controle:** Mantém o usuário no comando, podendo aprovar ou rejeitar
- **Flexibilidade:** Possibilita criar conteúdo dinâmico sem reescrever servidores

Um exemplo seria um servidor MCP de gestão de documentos que solicita ao LLM para gerar um resumo de um relatório extenso.

---

[Anterior: Arquitetura MCP](04-mcp-arquitetura-mcp.md) | [Próximo: Como o MCP Funciona Por Baixo dos Panos](05-mcp-funcionamento-interno.md) 