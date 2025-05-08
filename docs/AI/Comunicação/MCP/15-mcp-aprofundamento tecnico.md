# MCP: Guia Técnico Profundo

## O Que É MCP E Por Que Existe

O Model Context Protocol (MCP) é um protocolo especializado para conectar aplicações de IA a fontes de dados e ferramentas. Não é uma API genérica, mas sim um protocolo completo com estado, descoberta dinâmica e ciclo de vida gerenciado.

### Diferença Fundamental De APIs Tradicionais

```
API REST/GraphQL: Cliente → Servidor (stateless, request/response)
MCP: Host → Cliente MCP → Servidor MCP (stateful, bidirecional, com sessão)
```

MCP resolve o problema de fragmentação: ao invés de cada aplicação de IA implementar integrações customizadas com cada fonte de dados, MCP padroniza essa conexão.

## Arquitetura Real

### Componentes

```
Aplicação Host (ex: Claude Desktop)
    ↓
Cliente MCP (1 por servidor)
    ↓
Servidor MCP (expõe recursos e ferramentas)
    ↓
Fonte de Dados/Sistema
```

### Fluxo De Dados

1. **Host cria clientes MCP** - um para cada servidor
2. **Cliente negocia com servidor** - capacidades, versão
3. **Descoberta dinâmica** - tools, resources, prompts
4. **Operação contínua** - chamadas, notificações, assinaturas

## Protocolo Por Dentro

### Mensagens JSON-RPC 2.0

Todas as comunicações são JSON-RPC:

```json
// Request
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": { "name": "get_weather", "arguments": {...} }
}

// Response
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": { "content": [...] }
}

// Notification (sem id)
{
  "jsonrpc": "2.0",
  "method": "notifications/resources/updated",
  "params": { "uri": "file://data.txt" }
}
```

### Estado Mantido

MCP mantém estado **em memória** durante a sessão:

```typescript
// Cliente mantém
{
  protocolVersion: string,
  serverCapabilities: Capabilities,
  activeSubscriptions: Map<string, Subscription>,
  pendingRequests: Map<string, Request>
}

// Servidor mantém (por cliente)
{
  clientCapabilities: Capabilities,
  minimumLogLevel: LogLevel,
  activeSubscriptions: Set<string>,
  authorizedResources: Set<string>
}
```

## Primitivas Do MCP

### 1. Resources (Dados)

- **Controle**: Aplicação
- **Propósito**: Fornecer contexto para LLMs
- **Uso**: Arquivos, databases, APIs
- **Exemplo**: Conteúdo lido e incluído no prompt

```json
{
  "uri": "file:///config.json",
  "mimeType": "application/json",
  "text": "{\"apiKey\": \"...\"}"
}
```

### 2. Tools (Ações)

- **Controle**: Modelo (LLM)
- **Propósito**: Executar operações
- **Uso**: CRUD, API calls, comandos
- **Exemplo**: LLM chama `create_file()`

```json
{
  "name": "create_file",
  "description": "Creates a new file",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": { "type": "string" },
      "content": { "type": "string" }
    }
  }
}
```

### 3. Prompts (Templates)

- **Controle**: Usuário
- **Propósito**: Templates reutilizáveis
- **Uso**: Comandos, workflows
- **Exemplo**: Slash commands

## Ciclo De Vida

### 1. Inicialização

```
Client → Server: initialize (with capabilities)
Server → Client: initialize response (with capabilities)
Client → Server: initialized notification
```

### 2. Descoberta

```typescript
// Cliente descobre o que servidor oferece
const tools = await client.list_tools()
const resources = await client.list_resources()
const prompts = await client.list_prompts()
```

### 3. Operação

- Chamadas de tools
- Leitura de resources
- Assinaturas e notificações
- Progress tracking
- Cancelamento

### 4. Shutdown

- Fechamento gracioso
- Limpeza de recursos
- Fim da sessão

## Human-in-the-Loop

MCP implementa controle humano por design:

```typescript
// Quando LLM quer executar tool
if (tool.name === "delete_file") {
  // UI mostra para usuário
  const decision = await showApprovalUI({
    tool: "delete_file",
    args: { path: "/important.txt" }
  })
  
  if (decision === "ALLOW") {
    result = await mcp.callTool(tool)
  }
}
```

### Níveis De Controle

1. **Auto-aprovação**: Operações seguras
2. **Sempre perguntar**: Operações sensíveis
3. **Sempre negar**: Operações proibidas

## Relação Com LLMs

### LLMs NÃO Conhecem MCP

```
Fluxo real:
LLM ← (tools, context) ← Aplicação ← Cliente MCP ← Servidor MCP

LLM vê apenas:
- Lista de ferramentas disponíveis
- Contexto de resources incluído no prompt
```

### Tool Calling

```python
# LLMs com suporte nativo (GPT-4, Claude)
response = llm.chat(
  messages=[...],
  tools=mcp_tools  # LLM pode chamar diretamente
)

# LLMs sem suporte (GPT-3, modelos antigos)
# Cliente precisa fazer parsing manual
response = llm.complete(
  prompt="You have these tools: ... To use: TOOL_CALL: name(args)"
)
```

## Diferenças De Outros Protocolos

### Vs REST

- MCP: Stateful, descoberta dinâmica, notificações
- REST: Stateless, endpoints fixos, polling

### Vs GraphQL

- MCP: Protocolo completo, tools/resources nativos
- GraphQL: Query language, cliente define estrutura

### Vs gRPC

- MCP: JSON-RPC, descoberta runtime
- gRPC: Protobuf, schema compilado

### MCP É Especializado Para IA

- Human-in-the-loop integrado
- Primitivas para contexto de LLM
- Descoberta dinâmica de capacidades
- Não é protocolo de integração geral

## Limitações E Escalabilidade

### Problemas Em Escala Corporativa

```
Atual: Cliente ←→ Servidor (1:1, direto)

Problemas:
- Sem message broker
- Notificações síncronas
- Broadcast storm possível
- Conexões ponto-a-ponto
```

### Por Que Não Usa Kafka/RabbitMQ?

1. **Simplicidade**: Zero dependências externas
2. **Facilidade**: "Servers should be extremely easy to build"
3. **Localidade**: Funciona em localhost sem infra

### Soluções Para Escala

```typescript
// Wrapper corporativo
class EnterpriseMCPGateway {
  async handleNotification(notification) {
    // MCP → Kafka
    await kafka.send('mcp-events', notification)
    
    // Kafka → Clientes
    await fanOutToClients(notification)
  }
}
```

## Roadmap E Futuro

### 1. Validation

- Testes de conformidade
- Certificação de implementações

### 2. Registry

- "App store" para servidores MCP
- Descoberta centralizada

### 3. Agents

- Grafos de agentes
- Comunicação complexa
- Workflows avançados

### 4. Multimodality

- Suporte a vídeo
- Streaming bidirecional

### 5. Governance

- Padronização formal
- Desenvolvimento comunitário

## Conclusões Chave

1. **MCP é um protocolo, não uma API**
    
    - Estado mantido
    - Ciclo de vida completo
    - Descoberta dinâmica
2. **Especializado para IA, não integração geral**
    
    - Primitivas para LLMs
    - Human-in-the-loop
    - Não compete com REST/GraphQL
3. **LLMs não conhecem MCP**
    
    - Aplicação faz a ponte
    - MCP pode existir sem LLMs
4. **Simplicidade sobre escalabilidade**
    
    - Fácil de implementar
    - Limitações em ambientes corporativos
    - Evolução focada em agentes
5. **Futuro é vertical, não horizontal**
    
    - Mais profundo em IA/agentes
    - Não expansão para casos gerais