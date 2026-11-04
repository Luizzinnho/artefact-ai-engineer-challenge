# Empório da Música — Assistente de atendimento com IA

Projeto desenvolvido em Python para o desafio técnico de AI Engineer da Artefact. O assistente interpreta mensagens de clientes de uma loja fictícia de instrumentos musicais e responde a perguntas sobre produtos, pedidos, promoções e políticas comerciais.

A interação acontece pelo terminal. Os dados utilizados são os arquivos CSV e o PDF de políticas fornecidos no desafio. Não há integração com um sistema de vendas real.

## Como funciona

A implementação separa a interpretação da mensagem, a consulta aos dados e a redação da resposta:

```text
Mensagem do cliente
        |
        v
Semantic Interpreter (OpenAI API)
        |
        v
Comandos estruturados (Pydantic)
        |
        v
Executor (Python / pandas)
        |
        +---- CSV: produtos, categorias, pedidos e promoções
        |
        +---- PDF: políticas da loja
        |
        v
Resultados verificados
        |
        v
Response Composer (OpenAI API)
        |
        v
Resposta ao cliente
```

O primeiro modelo identifica as intenções do usuário e produz comandos em um formato definido com Pydantic. O executor interpreta esses comandos e consulta os arquivos locais, aplicando filtros e regras comerciais em Python. Por fim, um segundo modelo transforma os resultados em uma resposta natural.

A opção por duas etapas com LLM foi uma escolha de arquitetura: o modelo pode lidar com diferentes maneiras de formular uma pergunta, mas não recebe a responsabilidade de consultar arquivos ou decidir valores comerciais por conta própria. Isso não elimina a possibilidade de erro na interpretação ou na redação; torna essas etapas mais fáceis de inspecionar e testar separadamente.

## Funcionalidades

O executor reconhece cinco operações:

| Intenção | Responsabilidade |
| --- | --- |
| `SEARCH_PRODUCTS` | Buscar produtos por categoria, marca, modelo, característica, preço e disponibilidade |
| `QUERY_ORDER` | Consultar um pedido por número e e-mail informado pelo cliente |
| `QUERY_POLICY` | Consultar o documento de políticas comerciais, incluindo entregas, horários e devoluções |
| `QUERY_PROMOTIONS` | Buscar promoções ativas e calcular os preços aplicáveis |
| `OUT_OF_SCOPE` | Identificar solicitações que o assistente não consegue atender |

Uma mensagem pode gerar vários comandos. Assim, o cliente pode perguntar sobre um produto e o horário da loja na mesma interação.

Algumas regras de busca receberam tratamento específico. Uma marca digitada como `Tajima` pode ser normalizada para `Tagima` quando a correspondência é suficientemente clara. A expressão `Yamaha ou Tagima` é tratada como uma alternativa entre marcas. Características como `folk` são procuradas no nome e na descrição dos produtos, sem serem confundidas com um modelo específico.

Na consulta de pedidos, o sistema exige número e e-mail correspondentes antes de retornar os dados. Em promoções, os limites de preço são aplicados ao preço promocional e os descontos de promoção e PIX não são acumulados.

## Tecnologias e organização

Python, OpenAI API, Pydantic, pandas, pypdf, python-dotenv e pytest.

```text
.
├── data/                       # Seis arquivos CSV e políticas_da_loja.pdf
├── src/
│   ├── brand_normalizer.py     # Identificação e normalização de marcas
│   ├── config.py               # Configuração do modelo por variável de ambiente
│   ├── data_loader.py          # Consultas aos dados tabulares
│   ├── executor.py             # Execução dos comandos interpretados
│   ├── policy_loader.py        # Extração do texto do PDF
│   ├── response_composer.py    # Redação da resposta final
│   ├── schemas.py              # Contratos de dados com Pydantic
│   └── semantic_interpreter.py # Interpretação da mensagem com LLM
├── tests/
├── .env.example
├── main.py
├── requirements.txt
└── README.md
```

## Instalação

O desenvolvimento e os testes locais foram realizados em Windows com Python 3.14.3. Para reproduzir o ambiente:

```bash
git clone https://github.com/Luizzinnho/artefact-ai-engineer-challenge.git
cd artefact-ai-engineer-challenge
python -m venv .venv
```

No PowerShell, instale as dependências e execute o programa usando o Python do ambiente virtual:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edite o `.env` e configure sua própria chave:

```dotenv
OPENAI_API_KEY=sua_chave_da_api
OPENAI_MODEL=gpt-4.1-mini
```

O parâmetro `OPENAI_MODEL` é opcional e permite escolher outro modelo compatível com a Responses API e com Structured Outputs. O acesso a cada modelo depende da conta e da configuração da API. O arquivo `.env` não é versionado.

Para iniciar:

```powershell
.\.venv\Scripts\python.exe main.py
```

O atendimento recebe mensagens até que o usuário digite `sair`. As chamadas de modelo utilizam a API da OpenAI e podem gerar custos.

## Conversas de exemplo

Os exemplos abaixo foram observados durante testes manuais. Nas respostas com listas, a apresentação foi condensada sem alterar nomes ou valores.

### Busca por marcas alternativas

**Cliente:** Gostaria de um violão folk de até 1000 reais, de preferência Yamaha ou Tagima.

**Assistente:** Encontrei duas opções de violão folk de aço, Yamaha e Tagima, por até R$ 1.000:

- Tagima Dallas Tuner Aço Natural — R$ 749,00; 9 unidades em estoque.
- Yamaha F310 Aço Natural — R$ 699,90; 14 unidades em estoque.

Os dois estão dentro do orçamento e disponíveis.

### Promoções com limite de preço

**Cliente:** Quais instrumentos estão em promoção por menos de 400 reais?

**Assistente:** Encontrei este instrumento em promoção por menos de R$ 400:

- Kalani KAL-700T Tenor Natural — de R$ 359,00 por R$ 323,10 (10% de desconto); 11 unidades em estoque.

Os descontos promocional e PIX não são cumulativos.

### Consulta de pedido sem todos os dados

**Cliente:** Meu pedido é o número 1, mas não lembro o e-mail usado na compra.

**Assistente:** Para consultar o pedido nº 1, preciso do e-mail utilizado na compra. Você consegue informá-lo?

### Pergunta fora do escopo

**Cliente:** Como vai estar o tempo amanhã em Campo Grande? Vai chover?

**Assistente:** Não consigo consultar a previsão do tempo por aqui. Para saber se vai chover amanhã em Campo Grande, consulte um aplicativo ou site de previsão meteorológica.

### Múltiplas intenções

**Cliente:** Quero um violão folk até 1000 reais, saber o horário da loja, consultar meu pedido e conhecer as promoções.

**Assistente:** Claro! Encontrei estas informações:

**Violões folk até R$ 1.000:** Tagima Dallas (R$ 749,00), Yamaha F310 (R$ 699,90), Giannini GF-1R (R$ 579,90) e Shelby SN-100 (R$ 549,00), todos disponíveis.

**Horário da loja:** segunda a sexta, das 9h às 18h; sábado, das 9h às 13h; domingos e feriados, fechado.

**Consulta do pedido:** para consultar, preciso do número do pedido e do e-mail utilizado na compra.

**Promoções ativas:** Crafter HT-100 (R$ 1.967,18), Taylor 110e (R$ 5.519,08), Ohana CK-20 (R$ 439,20) e Kalani KAL-700T (R$ 323,10). Promoções e desconto de PIX não são cumulativos.

## Testes e validação

Execute:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Na validação local de 4 de novembro de 2026, a suíte terminou com **49 testes aprovados**. Os testes cobrem consultas a produtos, filtros, normalização de marcas, pedidos, promoções, políticas, contratos Pydantic e integração do fluxo. As chamadas ao modelo são simuladas em parte dos testes automatizados; também foram realizadas interações reais com a API durante o desenvolvimento.

Alguns defeitos foram descobertos nessas interações e corrigidos: a interpretação de `Yamaha ou Tagima` como uma única marca, a confusão entre uma afirmação sobre preço e um orçamento de compra, e a busca por `folk` apenas no nome de determinados produtos.

## Decisões e limitações

A solução utiliza arquivos locais porque o desafio já fornece uma base delimitada. Um banco de dados ou API externa adicionaria infraestrutura sem ser necessário para demonstrar a interpretação e as consultas. Da mesma forma, foi escolhida uma interface de terminal para concentrar o trabalho na lógica do agente.

O uso de um executor próprio, em vez de delegar as consultas diretamente ao modelo por chamadas de ferramentas, permitiu testar regras comerciais e filtros independentemente da LLM. Em contrapartida, essa decisão exige manter os contratos e o roteamento dos comandos.

Limitações conhecidas:

- **Sem memória entre turnos:** cada mensagem é interpretada de maneira independente. Uma segunda mensagem não recupera automaticamente informações enviadas na primeira.
- **Dados estáticos:** os valores e estoques refletem os CSV fornecidos. Não há atualização ou reserva de produtos em tempo real.
- **Busca textual:** características são localizadas nos nomes e descrições; não há embeddings ou busca semântica vetorial.
- **Políticas:** o texto completo do PDF é fornecido ao compositor. Não existe recuperação por seção ou trecho relevante.
- **Resposta generativa:** mesmo quando os dados estão corretos, a LLM pode omitir itens ou redigir informações incorretamente. Os prompts impõem limites, mas não há uma verificação determinística completa da resposta final.
- **Tratamento de falhas:** erros da API são apresentados no terminal; não foram implementados retries e gerenciamento avançado de indisponibilidade.

Não foram desenvolvidas integrações com WhatsApp, autenticação de usuários, persistência de conversas ou criação e alteração de pedidos.

Como possíveis evoluções, eu priorizaria a memória conversacional, uma fonte de dados atualizável, recuperação mais seletiva de políticas e uma validação final de preços e condições comerciais antes da resposta ao cliente.

## Uso de IA no desenvolvimento

O ChatGPT foi utilizado como assistente técnico durante o desenvolvimento, incluindo discussões de arquitetura, esclarecimento de conceitos, sugestões de implementação, revisão de código, elaboração de testes e apoio à documentação.

O trabalho foi conduzido de forma iterativa, com implementação, execução local, análise dos resultados e correções a partir de comportamentos observados. As decisões sobre escopo, arquitetura e validação foram realizadas ao longo desse processo.

Os testes automatizados e as interações reais foram utilizados para verificar as sugestões antes de incorporá-las à solução.

## Autor

Luiz Henrique Rodrigues  
GitHub: https://github.com/Luizzinnho
