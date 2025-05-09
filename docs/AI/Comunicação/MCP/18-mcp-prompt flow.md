# Passo a passo - do prompt 

## Introdução Ao MCP

O Model Context Protocol (MCP) é um protocolo aberto que padroniza como aplicações de IA se conectam a ferramentas e fontes de dados externas. Funciona como um "USB-C para IA" - um conector universal que permite que modelos de linguagem acessem diferentes sistemas sem necessidade de integrações customizadas.

## Arquitetura MCP - Componentes Principais

```mermaid
graph TD
    subgraph "MCP Host Application"
        H[Host - Claude Desktop/VSCode]
        C1[MCP Client 1]
        C2[MCP Client 2]
        C3[MCP Client 3]
        LLM[LLM - Claude/GPT]
    end
    
    S1[MCP Server - Google Drive]
    S2[MCP Server - GitHub]
    S3[MCP Server - Slack]
    
    API1[Google Drive API]
    API2[GitHub API]
    API3[Slack API]
    
    H --> C1
    H --> C2
    H --> C3
    H <--> LLM
    
    C1 <--> S1
    C2 <--> S2
    C3 <--> S3
    
    S1 <--> API1
    S2 <--> API2
    S3 <--> API3
    
    style H fill:#e1f5fe
    style LLM fill:#fff3e0
    style C1 fill:#f3e5f5
    style C2 fill:#f3e5f5
    style C3 fill:#f3e5f5
    style S1 fill:#e8f5e9
    style S2 fill:#e8f5e9
    style S3 fill:#e8f5e9
```

### Componentes E Suas Responsabilidades

#### 1. MCP Host

- Aplicação principal que o usuário interage (Claude Desktop, VSCode, Cursor)
- Coordena todo o sistema
- Gerencia interações com a LLM
- Cria e mantém múltiplos MCP Clients

#### 2. MCP Client

- Componente dentro do host
- Mantém conexão 1:1 com um MCP Server específico
- Gerencia protocolo JSON-RPC 2.0
- Descobre capacidades do server
- Roteia requisições e respostas

#### 3. MCP Server

- Programa externo que expõe funcionalidades
- Oferece três tipos de capacidades:
    - **Tools**: Funções executáveis
    - **Resources**: Dados acessíveis
    - **Prompts**: Templates pré-definidos
- Conecta-se a sistemas externos (APIs, bancos de dados, etc.)

## Relação Client-Server (1:1)

```mermaid
graph LR
    subgraph "MCP Host"
        H[Host Controller]
        C1[Client 1]
        C2[Client 2]
        C3[Client 3]
    end
    
    S1[Google Drive Server]
    S2[GitHub Server]
    S3[Slack Server]
    
    H --> C1
    H --> C2
    H --> C3
    
    C1 -- "1:1 dedicada" --> S1
    C2 -- "1:1 dedicada" --> S2
    C3 -- "1:1 dedicada" --> S3
    
    style C1 fill:#e3f2fd
    style C2 fill:#f3e5f5
    style C3 fill:#e8f5e9
```

Cada MCP Client mantém uma conexão exclusiva com seu MCP Server correspondente, garantindo:

- Isolamento entre conexões
- Segurança e estabilidade
- Gerenciamento de estado independente
- Simplicidade na comunicação

## Fluxo Detalhado De Operação

### Fase 1: Inicialização E Descoberta

```mermaid
sequenceDiagram
    participant H as Host
    participant C as MCP Client
    participant S as MCP Server
    
    H->>C: Criar cliente
    C->>S: Conectar via stdio/SSE
    S->>C: Handshake (versão, capacidades)
    C->>S: initialize request
    S->>C: initialize response
    C->>S: tools/list
    S->>C: Lista de ferramentas disponíveis
    C->>H: Reportar capacidades
```

1. **Carregamento de Configuração**
    
    ```json
    {
      "mcpServers": {
        "google-drive": {
          "command": "node",
          "args": ["@modelcontextprotocol/server-gdrive"]
        },
        "github": {
          "command": "python",
          "args": ["-m", "mcp_server_github"]
        }
      }
    }
    ```
    
2. **Criação de Clients**
    
    - Para cada server configurado, o host cria um MCP Client
    - Client inicia conexão com seu server
3. **Descoberta de Capacidades**
    
    - Server anuncia suas ferramentas, recursos e prompts
    - Client coleta e reporta ao host

### Fase 2: Preparação Do Ambiente LLM

```mermaid
graph TD
    subgraph "Host"
        CM[Capability Manager]
        TC[Tool Converter]
        LC[LLM Context]
    end
    
    C1[Client 1]
    C2[Client 2]
    
    C1 --> CM
    C2 --> CM
    CM --> TC
    TC --> LC
    
    style CM fill:#e3f2fd
    style TC fill:#f3e5f5
    style LC fill:#fff3e0
```

O host:

1. Coleta todas as capacidades dos servers
2. Converte para formato de ferramentas da LLM
3. Injeta no contexto/instruções de sistema

Exemplo de ferramentas expostas à LLM:

```json
{
  "available_tools": [
    {
      "name": "search_google_drive",
      "description": "Search files in Google Drive",
      "parameters": {
        "query": {
          "type": "string",
          "description": "Search query"
        }
      }
    },
    {
      "name": "create_github_issue",
      "description": "Create a new GitHub issue",
      "parameters": {
        "title": {"type": "string"},
        "body": {"type": "string"},
        "labels": {"type": "array", "items": {"type": "string"}}
      }
    }
  ]
}
```

### Fase 3: Interação Usuário-LLM

```mermaid
sequenceDiagram
    participant U as Usuário
    participant H as Host
    participant L as LLM
    
    U->>H: "Busque notas da reunião e crie issue"
    H->>L: Prompt + ferramentas disponíveis
    L->>L: Análise do contexto
    L->>H: Tool call: search_google_drive
    Note over L,H: LLM decide usar ferramenta
```

### Fase 4: Execução De Ferramentas

```mermaid
sequenceDiagram
    participant H as Host
    participant L as LLM
    participant C as MCP Client
    participant S as MCP Server
    participant API as External API
    
    L->>H: Tool call request
    H->>H: Identificar client apropriado
    H->>C: Executar ferramenta
    C->>S: JSON-RPC: tools/call
    S->>API: Chamada API externa
    API->>S: Resposta
    S->>C: Resultado formatado
    C->>H: Retornar resultado
    H->>L: Adicionar ao contexto
```

Exemplo de mensagem JSON-RPC:

```json
{
  "jsonrpc": "2.0",
  "id": "call_123",
  "method": "tools/call",
  "params": {
    "name": "search_google_drive",
    "arguments": {
      "query": "meeting notes yesterday"
    }
  }
}
```

### Fase 5: Processamento De Resultados

```mermaid
graph LR
    subgraph "Fluxo de Dados"
        R1[Resultado Server 1]
        R2[Resultado Server 2]
        H[Host Aggregator]
        L[LLM Context]
        F[Resposta Final]
    end
    
    R1 --> H
    R2 --> H
    H --> L
    L --> F
    
    style R1 fill:#e8f5e9
    style R2 fill:#e3f2fd
    style H fill:#f3e5f5
    style L fill:#fff3e0
    style F fill:#c8e6c9
```

## Fluxo Completo - Exemplo Prático

```mermaid
sequenceDiagram
    participant U as Usuário
    participant H as MCP Host
    participant L as LLM
    participant C1 as Client Drive
    participant C2 as Client GitHub
    participant S1 as Server Drive
    participant S2 as Server GitHub
    participant API1 as Google API
    participant API2 as GitHub API
    
    Note over H,S2: Fase 1: Inicialização
    H->>C1: Criar client
    H->>C2: Criar client  
    C1->>S1: Conectar
    C2->>S2: Conectar
    S1->>C1: Capacidades
    S2->>C2: Capacidades
    
    Note over U,L: Fase 2: Interação
    U->>H: "Busque notas e crie issue"
    H->>L: Prompt + tools
    
    Note over L,API1: Fase 3: Busca no Drive
    L->>H: search_google_drive("meeting notes")
    H->>C1: Executar busca
    C1->>S1: tools/call
    S1->>API1: Search files
    API1->>S1: Resultados
    S1->>C1: Notas encontradas
    C1->>H: Retornar dados
    H->>L: Contexto atualizado
    
    Note over L,API2: Fase 4: Criar Issue
    L->>H: create_github_issue(title, body)
    H->>C2: Criar issue
    C2->>S2: tools/call
    S2->>API2: Create issue
    API2->>S2: Issue criada
    S2->>C2: Confirmação
    C2->>H: Sucesso
    H->>L: Contexto final
    
    Note over L,U: Fase 5: Resposta
    L->>H: Resposta formatada
    H->>U: "Encontrei as notas e criei issue #123"
```

## Mecanismos De Transporte

```mermaid
graph TD
    subgraph "Tipos de Transporte"
        T1[stdio - Local]
        T2[HTTP/SSE - Remoto]
    end
    
    subgraph "Protocolo"
        P[JSON-RPC 2.0]
    end
    
    T1 --> P
    T2 --> P
    
    style T1 fill:#e8f5e9
    style T2 fill:#e3f2fd
    style P fill:#fff3e0
```

### 1. Standard Input/Output (stdio)

- Para servers locais
- Comunicação via streams de entrada/saída
- Ideal para ferramentas CLI
- Baixa latência

### 2. HTTP Com Server-Sent Events (SSE)

- Para servers remotos
- Conexões persistentes
- Suporte a eventos em tempo real
- Escalável para cloud

## Formato De Mensagens

### Requisição De Ferramenta

```json
{
  "jsonrpc": "2.0",
  "id": "req_1",
  "method": "tools/call",
  "params": {
    "name": "search_files",
    "arguments": {
      "query": "project proposal",
      "limit": 10
    }
  }
}
```

### Resposta De Ferramenta

```json
{
  "jsonrpc": "2.0",
  "id": "req_1",
  "result": {
    "files": [
      {
        "id": "file_123",
        "name": "Project Proposal Q2.docx",
        "path": "/documents/proposals/",
        "modified": "2025-05-08T14:30:00Z"
      }
    ]
  }
}
```

## Separação De Responsabilidades

```mermaid
graph TD
    subgraph "O que a LLM vê"
        T[Tool Signatures]
        P[Parameters]
        R[Results]
    end
    
    subgraph "O que a LLM NÃO vê"
        I[Implementação]
        PR[Protocolo JSON-RPC]
        A[Autenticação]
        TR[Transporte]
    end
    
    style T fill:#c8e6c9
    style P fill:#c8e6c9
    style R fill:#c8e6c9
    style I fill:#ffcdd2
    style PR fill:#ffcdd2
    style A fill:#ffcdd2
    style TR fill:#ffcdd2
```

## Benefícios Da Arquitetura MCP

1. **Padronização**: Um protocolo para múltiplos sistemas
2. **Modularidade**: Componentes independentes e reutilizáveis
3. **Escalabilidade**: Fácil adicionar novos servers
4. **Segurança**: Isolamento entre conexões
5. **Flexibilidade**: Suporte a diferentes transportes
6. **Simplicidade**: Interface clara para desenvolvedores

## Conclusão

O MCP resolve o problema de conectar IAs a sistemas externos de forma padronizada. Com sua arquitetura cliente-servidor e relação 1:1 entre clients e servers, oferece uma solução robusta, segura e escalável para integração de ferramentas em aplicações de IA.

A separação clara de responsabilidades entre Host, Client e Server permite que cada componente evolua independentemente, enquanto o protocolo JSON-RPC 2.0 garante comunicação confiável e padronizada.