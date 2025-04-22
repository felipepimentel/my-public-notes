# Arquitetura MCP: Como Tudo se Conecta

O MCP se baseia em uma arquitetura cliente-servidor elegante e flexível:

```mermaid
flowchart LR
    subgraph "Dispositivo/Rede"
        Host["Aplicações IA\n(Claude, Chatbots, IDEs)"]
        S1["Servidor MCP\nSistema A"]
        S2["Servidor MCP\nSistema B"]
        S3["Servidor MCP\nSistema C"]
        Host <-->|"Protocolo MCP"| S1
        Host <-->|"Protocolo MCP"| S2
        Host <-->|"Protocolo MCP"| S3
        S1 <--> D1[("Banco de Dados\nSistema A")]
        S2 <--> D2[("Arquivos\nSistema B")]
    end
    subgraph "Serviços Externos"
        S3 <-->|"API"| D3[("Serviço\nExterno C")]
    end
    
    classDef host fill:#f9d5e5,stroke:#333,stroke-width:2px;
    classDef servidor fill:#9ff,stroke:#333,stroke-width:1px;
    classDef dados fill:#b5e8f7,stroke:#333,stroke-width:1px;
    classDef api fill:#d3f0c2,stroke:#333,stroke-width:1px;
    
    class Host host;
    class S1,S2,S3 servidor;
    class D1,D2 dados;
    class D3 api;
```

## Os Três Pilares do MCP

### 1. MCP Hosts (Clientes)

- As aplicações que incorporam LLMs e precisam de acesso a dados/ferramentas
- Exemplos: Claude Desktop, plugins de IDE, chatbots corporativos
- Função: Coordenar a comunicação entre os LLMs e os servidores MCP

### 2. MCP Servers (Servidores)

- Componentes que fornecem acesso a sistemas específicos
- Cada servidor é especializado em um sistema ou fonte de dados
- Operam independentemente, podendo ser locais ou remotos
- Exemplos: Um servidor para dados de clientes, outro para documentação técnica

### 3. O Protocolo MCP

- A "língua comum" falada entre hosts e servidores
- Define formatos de mensagens padronizados
- Estabelece regras claras de comunicação
- Garante segurança e controle de acesso

## Como Funciona na Prática

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

Este fluxo é semelhante a um intérprete que facilita uma conversa entre pessoas que falam idiomas diferentes: o protocolo traduz as necessidades do LLM para os sistemas externos e vice-versa.

## Flexibilidade da Arquitetura

Uma das principais vantagens do MCP é sua arquitetura distribuída e agnóstica em relação a implementações. Isso significa que:

- Servidores podem ser desenvolvidos independentemente
- Múltiplos servidores podem operar em paralelo
- Clientes podem se conectar a diversos servidores simultaneamente
- A comunicação pode acontecer local ou remotamente

Este design permite que organizações implementem o MCP de forma incremental, começando com integrações simples e expandindo conforme necessário.

---

[Anterior: O MCP Como Solução Universal](03-mcp-solucao-universal.md) | [Próximo: Conceitos Fundamentais](05-mcp-conceitos-fundamentais.md) 