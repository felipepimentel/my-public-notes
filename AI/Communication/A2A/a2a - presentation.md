# 🤝 A2A — Do Zero Ao Hero: Conversas Entre Agentes Como Se Martin Fowler Estivesse Rabiscando no Quadro

> _“Não precisamos de um único agente omnisciente; precisamos de uma liga inteira de agentes especialistas que cooperam como uma orquestra bem ensaiada.”_

![Banner A2A](https://google.github.io/A2A/assets/A2A_banner.png)

---

## 1 · Onde Estamos & Para Onde Vamos

- **Modelos isolados** eram como _programas monolíticos_: geniais, mas sem portas nem janelas.
    
- **MCP** abriu as primeiras janelas — agentes com acesso a ferramentas.
    
- **A2A** derruba as paredes: agentes falando entre si, cada um dono de um micro‑domínio.
    

```mermaid
graph TD
    A[História da IA] --> B[Monolitos]
    A --> C[Agentes + Ferramentas<br>(MCP)]
    A --> D[Ecossistemas de Agentes<br>(A2A)]
    style A fill:#e8e8e8,stroke:#333,stroke-width:2px
```

> **Pense nisso**: A2A é para agentes o que REST foi para serviços web — um protocolo simples que destrava inovação distribuída.

---

## 2 · O Problema Da Cola

Sem A2A:

- Integração **N × N** – cada nova combinação exige mais cola de código.
    
- Pouco reaproveitamento, acoplamento alto, dores de manutenção.
    

Com A2A:

- Integração **N × 1** – qualquer agente fala _A2A_ e pronto.
    
- Evolução independente, _plug‑and‑play_ de especialistas.
    

```mermaid
graph TD
    subgraph "Sem A2A"
        A1[Agente A] --> B1[Agente B]
        A1 --> C1[Agente C]
        B1 --> C1
    end
    subgraph "Com A2A"
        A2[Agente A] <-->|A2A| B2[Agente B]
        A2 <-->|A2A| C2[Agente C]
        B2 <-->|A2A| C2
    end
```

> **Regra de ouro**: elimine integrações específicas; invista em protocolos genéricos.

---

## 3 · Princípios Arquiteturais

1. **Autonomia** – cada agente gerencia seu estado.
    
2. **Interoperabilidade** – qualquer stack, mesma língua.
    
3. **Modularidade** – _divide‑and‑conquer_ aplicado à IA.
    
4. **Segurança by design** – autenticação, autorização & auditoria.
    
5. **Dinamismo** – negociações em tempo real (streaming + SSE).
    

---

## 4 · Os Quatro Pilares Do A2A

|Pilar|O que é|Por quê importa|
|---|---|---|
|**Agent Card**|`/.well-known/agent.json`|_Discovery_ automático|
|**Task**|Ciclo de vida de trabalho|Orquestração previsível|
|**Message & Parts**|Texto, arquivos, dados estruturados|Payloads flexíveis|
|**Artifact**|Resultado persistente|Compartilhamento & auditoria|

### Exemplo De Agent Card

```json
{
  "name": "Finance Agent",
  "description": "Performs financial analysis",
  "url": "https://example.com/agents/finance",
  "version": "1.0.0",
  "capabilities": { "streaming": true },
  "skills": [{
    "id": "investment_analysis",
    "name": "Investment Analysis",
    "description": "Evaluates options by risk profile"
  }]
}
```

---

## 5 · Ciclo De Vida De Uma Task

```mermaid
stateDiagram-v2
    [*] --> submitted
    submitted --> working
    working --> input-required
    input-required --> working
    working --> completed
    working --> failed
    working --> canceled
```

> **Insight**: Estados claros = debug claro = menos noites mal dormidas.

---

## 6 · Under the Hood – JSON‑RPC 2.0 + HTTP(S)

- `tasks/send` – inicia ou continua trabalho
    
- `tasks/sendSubscribe` – streaming via SSE
    
- `tasks/get` – _poll_ sem culpa
    
- `tasks/cancel` – _fail‑fast_ consciente
    

```mermaid
sequenceDiagram
    participant C as Client
    participant S as A2A Server
    C->>S: GET agent.json
    S-->>C: Agent Card
    C->>S: tasks/send
    S-->>C: Task ➜ submitted ➜ working ➜ completed
```

---

## 7 · Casos De Uso Que Brilham

### 7.1 Equipe De Software

```mermaid
graph TD
    PO[Agente Product Owner] --> DEV[Agente Developer]
    DEV --> QA[Agente Tester]
    QA --> OPS[Agente Ops]
```

- De backlog → código → teste → deploy sem humanos no caminho crítico.
    

### 7.2 Automação Empresarial

- Atendimento, logística, finanças – cada qual seu agente, todos falam A2A.
    

### 7.3 Assistente Pessoal

- Um maestro coordena voo, hotel, agenda & saúde.
    

---

## 8 · Desafios & Armadilhas

- **Padrão em movimento** – verifique _changelogs_.
    
- **Confiança** – reputação de agente é a nova chave pública.
    
- **Latência** – pipelines chatos? Use streaming.
    
- **Governança** – quem paga a conta do erro coletivo?
    

---

## 9 · Do Zero ➡ Hello World

```python
from a2a.common.server import A2AServer
from a2a.common.task_manager import InMemoryTaskManager
from a2a.common.types import AgentCard

agent_card = AgentCard(
    name="Demo Agent",
    description="Hello‑world A2A agent",
    url="http://localhost:8000",
    version="1.0.0"
)

async def handle_message(task_id, message):
    reply = f"Processed: {message.parts[0].text}"
    return create_response(task_id, reply)

server = A2AServer(
    agent_card=agent_card,
    task_manager=InMemoryTaskManager(),
    message_processor=handle_message
)

app = server.create_app()
```

> **Pro tip**: faça o _curl_ primeiro, GUI depois.

---

## 10 · A2A ❤ MCP – Dê a Mão Que Falta

```mermaid
graph TD
    U[Usuário] --> ORQ[Orquestrador]
    ORQ <-->|A2A| SPEC[Agente Especialista]
    ORQ -->|MCP| TOOL[Ferramenta]
```

- **MCP** liga cada agente a dados & ferramentas.
    
- **A2A** costura a conversa entre agentes.
    

---

## 11 · Roadmap Pessoal: Seu Caminho Hero

1. **Explorar exemplos oficiais** – entender _happy path_.
    
2. **Publicar seu Agent Card** – _discovery_ first.
    
3. **Orquestrar dois agentes** – mínimo viável colaborativo.
    
4. **Adicionar streaming** – UX em tempo real.
    
5. **Contribuir** – PR + RFC deixam o padrão melhor.
    

---

## 12 · Conclusão

> _“Em sistemas complexos, colaboração > centralização. Protocolos vencem pipelines manuais.”_

A2A transforma a IA de ferramenta solitária em sociedade de especialistas. O próximo passo está na sua IDE – coloque dois agentes para conversar e veja a mágica surgir.

---

### Recursos

- Documentação → [https://google.github.io/A2A](https://google.github.io/A2A)
    
- GitHub → [https://github.com/google/A2A](https://github.com/google/A2A)
    
- Comunidade → Discord & fóruns (link na doc)