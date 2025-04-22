# MCP - Model Context Protocol

## O adaptador universal para IAs

  

---

  

# O que é o MCP?

  

> 💡 O Model Context Protocol (MCP) é o "adaptador universal" do mundo da IA. Ele permite que modelos de linguagem se conectem facilmente com dados e ferramentas externas, transformando IAs isoladas em assistentes verdadeiramente contextuais e capazes.

  

---

  

# O Desafio das IAs Isoladas

  

![](https://placehold.co/800x400/e9ecef/495057?text=IA+Isolada)

  

- LLMs não têm acesso nativo aos seus sistemas

- Sem acesso a dados específicos e atualizados

- Respostas genéricas e potencialmente desatualizadas

- Incapacidade de realizar ações em sistemas externos

  

---

  

# A Torre de Babel Digital

  

```mermaid

graph LR

A1[IA de Atendimento] --> D1(Sistema de Clientes)

A1 --> T1(Ferramenta CRM)

A2[IA de Análise de Dados] --> D1(Sistema de Clientes)

A2 --> D2(Histórico Operacional)

A3[IA de Compliance] --> D2(Histórico Operacional)

A3 --> T1(Ferramenta CRM)

```

  

- **Duplicação de esforços:** A mesma conexão recriada múltiplas vezes

- **Inconsistência:** Diferentes padrões para cada integração

- **Custos elevados:** Mudanças em um sistema exigem múltiplas atualizações

  

---

  

# MCP Como Solução Universal

  

```mermaid

graph LR

A1[IA de Atendimento] --> C1(Protocolo MCP)

A2[IA de Análise de Dados] --> C1(Protocolo MCP)

A3[IA de Compliance] --> C1(Protocolo MCP)

C1 --> S1[Servidor MCP Clientes]

C1 --> S2[Servidor MCP Operações]

C1 --> S3[Servidor MCP CRM]

```

  

- Todas as IAs falam a mesma "língua"

- Reutilização de servidores entre aplicações

- Interoperabilidade entre diferentes LLMs

  

---

  

# Analogia USB

  

![](https://placehold.co/800x400/e9ecef/495057?text=USB+Universal)

  

O MCP é para a IA o que os padrões USB são para dispositivos eletrônicos:

- **Um conector universal**

- **Elimina adaptadores específicos**

- **Simplifica integrações**

- **Padroniza comunicações**

  

---

  

# Arquitetura MCP: Cliente-Servidor

  

```mermaid

flowchart LR

subgraph "Dispositivo/Rede"

Host["Aplicações IA\n(Claude, Chatbots, IDEs)"]

S1["Servidor MCP\nSistema A"]

S2["Servidor MCP\nSistema B"]

Host <-->|"Protocolo MCP"| S1

Host <-->|"Protocolo MCP"| S2

end

```

  

---

  

# Os Três Pilares do MCP

  

1. **MCP Hosts (Clientes):**

- Aplicações que incorporam LLMs (Claude, chatbots, IDEs)

- Coordenam comunicação entre LLMs e servidores

  

2. **MCP Servers (Servidores):**

- Fornecem acesso a sistemas específicos

- Cada servidor é especializado em um sistema/fonte

  

3. **O Protocolo MCP:**

- A "língua comum" entre hosts e servidores

- Define formato de mensagens padronizado

  

---

  

# Como Funciona na Prática

  

```mermaid

sequenceDiagram

participant U as Usuário

participant H as Host (Cliente MCP)

participant S as Servidor MCP

participant D as Sistema/Dados

U->>H: "Preciso de informação X"

H->>S: Estabelece conexão

S-->>H: Confirma capacidades

H->>S: Solicita dados/ação

S->>D: Acessa o sistema real

D-->>S: Retorna dados/resultado

S-->>H: Envia resposta formatada

H->>U: Apresenta informação ao usuário

```

  

---

  

# Conceitos Fundamentais: Roots

  

```mermaid

graph TD

R[Roots] --- R1[Root: sistema://clientes]

R --- R2[Root: operacoes://historico]

R --- R3[Root: docs://manuais]

```

  

- **Territórios de acesso** que delimitam onde um servidor pode operar

- Funcionam como "crachás de segurança" para diferentes áreas

- Permitem controle granular de permissões

  

---

  

# Conceitos Fundamentais: Resources

  

```mermaid

graph TD

Library[Resources: Biblioteca] --- B1[Políticas da Empresa]

Library --- B2[Dados de Produtos]

Library --- B3[Manuais Técnicos]

```

  

- "Fontes de conhecimento" que o LLM pode consultar

- Documentos, dados ou conteúdos disponibilizados pelo servidor MCP

- Permitem acesso a dados que não estão no treinamento do LLM

  

---

  

# Conceitos Fundamentais: Tools

  

```mermaid

graph TD

T[Tools: Ferramentas] --- T1[Calculadora de Preços]

T --- T2[Verificador de Disponibilidade]

T --- T3[Pesquisa em Documentos]

```

  

- Funções que o LLM pode invocar para realizar ações

- Permitem que a IA faça algo além de gerar texto

- Conectam o LLM a funcionalidades de sistemas existentes

  

---

  

# Conceitos Fundamentais: Prompts

  

```mermaid

graph TD

P[Prompts: Receitas] --- P1[Análise de Cliente]

P --- P2[Geração de Relatório]

P --- P3[Resposta a Dúvidas]

```

  

- Instruções padronizadas que guiam o LLM em tarefas específicas

- "Receitas testadas" para garantir respostas consistentes

- Asseguram que todas as etapas de um processo sejam seguidas

  

---

  

# Conceitos Fundamentais: Sampling

  

```mermaid

sequenceDiagram

participant S as Servidor MCP

participant C as Cliente MCP

participant LLM as Modelo de IA

S->>C: "Preciso gerar texto com esses dados"

C->>LLM: "Gerar texto conforme especificação"

LLM->>C: "Texto gerado"

C->>S: "Aqui está o resultado"

```

  

- Permite que o servidor solicite geração de conteúdo do LLM

- Fluxo reverso: servidor pede ajuda ao cliente/LLM

  

---

  

# Como o MCP Funciona Por Baixo

  

```mermaid

graph TB

A[MCP] --> B[Camada de Protocolo]

A --> C[Camada de Transporte]

B --> D[Mensagens JSON-RPC]

C --> G["STDIO (Local)"]

C --> H["HTTP/SSE (Rede)"]

```

  

- Baseado em JSON-RPC 2.0

- Dois métodos de transporte: STDIO (local) e HTTP/SSE (rede)

- Sistema de requisição-resposta com monitoramento

  

---

  

# A Evolução das IAs Com MCP

  

```mermaid

graph LR

F1[Fase 1:<br/>Ferramentas Isoladas] --> F2[Fase 2:<br/>Assistentes Conectados]

```

  

**Antes:**

- IAs limitadas ao seu treinamento

- Respostas genéricas

- Dados potencialmente desatualizados

  

**Com MCP:**

- Acesso a dados atualizados e específicos

- Execução de ações em sistemas externos

- Contextualização baseada em dados reais

  

---

  

# MCP na Prática: Setor Financeiro

  

```mermaid

sequenceDiagram

participant G as Analista

participant A as Assistente IA

participant MCP as Protocolo MCP

participant SC as Servidor Clientes

participant SR as Servidor Risco

G->>A: "Analisar crédito para cliente X"

A->>MCP: Solicita dados do cliente

MCP->>SC: Busca perfil e histórico

SC->>MCP: Retorna dados do cliente

A->>MCP: Solicita análise de risco

MCP->>SR: Executa modelos de risco

MCP->>A: Compila informações

A->>G: "Aqui está a análise completa"

```

  

---

  

# MCP na Prática: Saúde

  

```mermaid

graph TD

A[Assistente Médico IA] --> MCP[Cliente MCP]

MCP --> S1[Servidor Prontuários]

MCP --> S2[Servidor Literatura Médica]

MCP --> S3[Servidor Farmacologia]

S1 --> D1[(Sistema EMR)]

S2 --> D2[(PubMed/Literatura)]

S3 --> D3[(Base Medicamentos)]

```

  

- Assistência em tempo real durante consultas

- Acesso a literatura médica atualizada

- Análise de histórico completo do paciente

  

---

  

# MCP na Prática: E-commerce

  

```mermaid

sequenceDiagram

participant C as Cliente

participant A as Assistente IA

participant MCP as Protocolo MCP

participant SO as Servidor Pedidos

participant SL as Servidor Logística

C->>A: "Onde está meu pedido #123?"

A->>MCP: Busca informações do pedido

MCP->>SO: Consulta pedido #123

MCP->>SL: Consulta rastreamento

MCP->>A: Compila informações

A->>C: "Seu pedido está em trânsito..."

```

  

---

  

# MCP na Prática: Desenvolvimento

  

```mermaid

sequenceDiagram

participant D as Desenvolvedor

participant V as VSCode + MCP

participant S1 as Servidor Repositório

participant S2 as Servidor APIs

D->>V: Escreve código que usa API X

V->>S2: Solicita documentação da API

S2->>V: Retorna esquema e exemplos

V->>D: Sugere completions corretas

```

  

- Sugestões contextualmente relevantes

- Acesso à documentação atualizada

- Verificações de segurança em tempo real

  

---

  

# O Futuro do MCP

  

### 1. Federação e Descoberta de Servidores

  

```mermaid

graph LR

C[Cliente MCP] --> R[Registro Central]

R --> S1[Servidor Empresa A]

R --> S2[Servidor Empresa B]

R --> S3[Servidor Público]

```

  

### 2. Modelos Especializados por Domínio

  

### 3. Segurança e Conformidade Avançadas

  

---

  

# Recursos para Aprofundamento

  

- **Documentação Oficial:** [modelcontextprotocol.io](https://modelcontextprotocol.io/)

- **GitHub:** [github.com/modelcontextprotocol](https://github.com/modelcontextprotocol)

- **Anúncio Anthropic:** [anthropic.com/news/model-context-protocol](https://www.anthropic.com/news/model-context-protocol)

- **Especificação:** [spec.modelcontextprotocol.io](https://spec.modelcontextprotocol.io/)

  

---

  

# Obrigado!

  

> 💼 Apresentação preparada por Pimentel

>

> Junho 2024