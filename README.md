# Empório da Música — AI Customer Service Assistant

Python project developed for Artefact's AI Engineer technical challenge. The assistant interprets messages from customers of a fictional musical instrument store and answers questions about products, orders, promotions, and store policies.

The interface runs in a terminal. It uses the CSV files and store policy PDF supplied with the challenge; it does not connect to a live sales system.

## How it works

The implementation separates message interpretation, data retrieval, and response generation:

```text
Customer message
        |
        v
Semantic Interpreter (OpenAI API)
        |
        v
Structured commands (Pydantic)
        |
        v
Executor (Python / pandas)
        |
        +---- CSV: products, categories, orders, and promotions
        |
        +---- PDF: store policies
        |
        v
Verified results
        |
        v
Response Composer (OpenAI API)
        |
        v
Customer-facing response
```

The first model identifies the customer's intent and produces commands following a Pydantic schema. The executor processes those commands and queries the local files, applying filters and business rules in Python. A second model then turns the results into a natural-language response.

Using two LLM stages was an architectural choice. The model can handle different ways of phrasing a request, but it is not responsible for reading the files or independently determining commercial values. This does not eliminate interpretation or generation errors; it makes those stages easier to inspect and test separately.

## Features

The executor supports five operations:

| Intent | Responsibility |
| --- | --- |
| `SEARCH_PRODUCTS` | Search by category, brand, model, features, price, and availability |
| `QUERY_ORDER` | Look up an order using its number and the customer's email |
| `QUERY_POLICY` | Consult store policies, including shipping, opening hours, and returns |
| `QUERY_PROMOTIONS` | Find active promotions and calculate applicable prices |
| `OUT_OF_SCOPE` | Identify requests the assistant cannot handle |

One message can produce multiple commands. For example, a customer can ask about a product and the store's opening hours in the same message.

Some search cases require specific handling. A misspelled brand such as `Tajima` can be normalized to `Tagima` when the match is sufficiently clear. `Yamaha or Tagima` is handled as an alternative between brands. Features such as `folk` are searched for in product names and descriptions rather than treated as a specific model.

For order lookups, the system requires a matching order number and email before returning data. For promotions, price limits are applied to promotional prices, and promotional and PIX payment discounts cannot be combined.

## Technology and project structure

Python, OpenAI API, Pydantic, pandas, pypdf, python-dotenv, and pytest.

```text
.
├── data/                       # Six CSV files and políticas_da_loja.pdf
├── src/
│   ├── brand_normalizer.py     # Brand identification and normalization
│   ├── config.py               # Model configuration via environment variable
│   ├── data_loader.py          # Tabular data queries
│   ├── executor.py             # Execution of interpreted commands
│   ├── policy_loader.py        # PDF text extraction
│   ├── response_composer.py    # Customer-facing response generation
│   ├── schemas.py              # Pydantic data contracts
│   └── semantic_interpreter.py # LLM-based message interpretation
├── tests/
├── .env.example
├── main.py
├── requirements.txt
└── README.md
```

## Setup

Development and local testing were carried out on Windows with Python 3.14.3. To reproduce the environment:

```bash
git clone https://github.com/Luizzinnho/artefact-ai-engineer-challenge.git
cd artefact-ai-engineer-challenge
python -m venv .venv
```

In PowerShell, install dependencies with the virtual environment's Python and create your local configuration file:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and provide your own API key:

```dotenv
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-5.6-luna
```

`OPENAI_MODEL` is optional. You can set it to another model available to your account that supports the Responses API and Structured Outputs. The project was primarily tested with `gpt-5.6-luna`; a basic end-to-end compatibility test was also performed with `gpt-4.1-mini`. Access to individual models depends on the API account. The `.env` file is excluded from version control.

Run the assistant:

```powershell
.\.venv\Scripts\python.exe main.py
```

The terminal accepts messages until the customer enters `sair` (Portuguese for "exit"). OpenAI API calls may incur usage charges.

## Example conversations

The following cases were observed during manual tests conducted in Portuguese. Customer prompts and assistant responses below are translated into English for this submission. Responses containing lists have been shortened without changing product names or numerical values.

### Search with alternative brands

**Customer:** I would like a folk acoustic guitar for up to BRL 1,000, preferably Yamaha or Tagima.

**Assistant:** I found two steel-string folk acoustic guitars from Yamaha and Tagima within your budget:

- Tagima Dallas Tuner Aço Natural — BRL 749.00; 9 units in stock.
- Yamaha F310 Aço Natural — BRL 699.90; 14 units in stock.

Both are available and within your budget.

### Promotions with a price limit

**Customer:** Which instruments are on promotion for less than BRL 400?

**Assistant:** I found one instrument on promotion for under BRL 400:

- Kalani KAL-700T Tenor Natural — from BRL 359.00 to BRL 323.10 (10% off); 11 units in stock.

Promotional discounts cannot be combined with the PIX payment discount.

### Order lookup with missing information

**Customer:** My order number is 1, but I don't remember which email I used.

**Assistant:** To look up order 1, I need the email address used for the purchase. Could you provide it?

### Out-of-scope request

**Customer:** What will the weather be like tomorrow in Campo Grande? Will it rain?

**Assistant:** I can't check the weather forecast here. To find out whether it will rain tomorrow in Campo Grande, please use a weather app or website.

### Multiple intents in one message

**Customer:** I want a folk acoustic guitar for up to BRL 1,000, the store's opening hours, information about my order, and current promotions.

**Assistant:** Here is what I found:

**Folk acoustic guitars up to BRL 1,000:** Tagima Dallas (BRL 749.00), Yamaha F310 (BRL 699.90), Giannini GF-1R (BRL 579.90), and Shelby SN-100 (BRL 549.00), all available.

**Opening hours:** Monday through Friday, 9 a.m. to 6 p.m.; Saturday, 9 a.m. to 1 p.m.; closed on Sundays and public holidays.

**Order lookup:** I need the order number and the email used for the purchase.

**Active promotions:** Crafter HT-100 (BRL 1,967.18), Taylor 110e (BRL 5,519.08), Ohana CK-20 (BRL 439.20), and Kalani KAL-700T (BRL 323.10). Promotional and PIX discounts cannot be combined.

## Testing and validation

Run the test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

During local validation on November 4, 2026, **all 49 tests passed**. Tests cover product queries, filters, brand normalization, orders, promotions, store policies, Pydantic schemas, and pipeline integration. Model calls are mocked in part of the automated suite; real API interactions were also tested during development.

Some issues were discovered and corrected during those interactions: interpreting `Yamaha or Tagima` as a single brand, mistaking a statement about a product's price for a purchasing budget, and searching for `folk` only in certain product names rather than their descriptions.

## Design decisions and limitations

Local files were used because the challenge provides a bounded dataset. Adding a database or external API would introduce infrastructure that is unnecessary to demonstrate interpretation and retrieval. A terminal interface was chosen for the same reason: to focus on the agent's behavior.

Using a dedicated executor rather than letting the model query data directly through tool calls made it possible to test filters and commercial rules independently of the LLM. The trade-off is maintaining the command schemas and routing logic.

Known limitations:

- **No cross-turn memory:** Each message is processed independently. A follow-up message does not automatically recover information from previous turns.
- **Static data:** Prices and inventory reflect the supplied CSV files. There are no real-time updates or product reservations.
- **Text-based search:** Features are matched against names and descriptions; embeddings and vector-based retrieval are not implemented.
- **Store policies:** The full PDF text is passed to the response composer. There is no section-level retrieval.
- **Generative responses:** Even with correct retrieved data, the LLM may omit items or introduce inaccuracies. Prompts impose constraints, but there is no complete deterministic validation of the final response.
- **Error handling:** API failures are reported in the terminal; retries and advanced recovery mechanisms are not implemented.

WhatsApp integration, user authentication, conversation persistence, and order creation or modification were outside the implementation scope.

Given more time, I would prioritize conversational memory, an updatable data source, more targeted policy retrieval, and final validation of prices and commercial conditions before replying to the customer.

## Use of AI during development

ChatGPT was used as a technical assistant during development, including architecture discussions, concept explanations, implementation suggestions, code review, test development, and documentation support.

The work followed an iterative process of implementation, local execution, result analysis, and corrections based on observed behavior. Decisions about scope, architecture, and validation were made throughout that process.

Automated tests and real interactions were used to verify suggestions before they were incorporated into the solution.

## Author

Luiz Henrique Rodrigues  
GitHub: https://github.com/Luizzinnho
