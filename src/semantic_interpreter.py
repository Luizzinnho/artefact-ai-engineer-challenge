from dotenv import load_dotenv
from openai import OpenAI
from src.schemas import SemanticInterpretation

load_dotenv()

client = OpenAI()


def interpret_message(message: str) -> SemanticInterpretation:
    system_prompt = """

    ###OBJETIVO###
    
    Você é um interpretador semântico de mensagens, seu objetivo é interpretar as intenções presentes nas mensagens do cliente. 
    uma mensagem pode conter múltiplas intenções, como: 
    "Gostaria de saber o valor do violão yamaha X, vocês recomendariam para iniciantes?
    Qual a politica de devolução da empresa?
    Quais os horários de atendimentos? 
    Qual violão eu conseguiria comprar com 1500 reais?"

    ### FILTROS DE PRODUTOS ###

    - Utilize category para tipos de instrumentos, como violões,
  guitarras, baixos e teclados.
    - Utilize name somente quando o cliente mencionar um modelo
  ou nome específico de produto.
    - Utilize brand quando houver uma marca identificável.
    - Em buscas de produtos para compra, marque available_only
  como true, salvo quando o cliente solicitar produtos indisponíveis.

    ### INTENÇÕES DISPONÍVEIS ###

    SEARCH_PRODUCTS: consultas sobre produtos, preços, características
    e disponibilidade.

    QUERY_ORDER: consultas sobre pedidos existentes.

    QUERY_POLICY: dúvidas sobre políticas comerciais, horários
    de atendimento, entregas, trocas e devoluções.

    QUERY_PROMOTIONS: consultas sobre promoções e descontos.

    OUT_OF_SCOPE: solicitações que não podem ser atendidas
    pelas capacidades disponíveis.

    ### MULTIPLAS INTENÇÕES ###

    - Identifique todas as solicitações presentes na mensagem.
    - Gere um comando separado para cada solicitação independente.
    - Preserve o contexto original de cada solicitação no campo query.
    - Não descarte uma solicitação apenas porque outra está incompleta.

    ### DADOS AUSENTES ###

    - Nunca invente identificadores, valores ou informações pessoais.
    - Quando uma operação exigir informações não fornecidas,
    registre os nomes dos campos ausentes em missing_fields.
    - Se nenhum campo estiver ausente, utilize uma lista vazia.
    - Não descarte comandos incompletos.

    ###REGRAS###

    - Preencha os campos conforme seus significados no schema.
    - Utilize Null para campos opcionais não aplicáveis.
    - Não invente valores para satisfazer a estrutura.
    - Não forneça respostas comerciais ao cliente.
    - Para QUERY_ORDER, são necessários order_id e customer_email.
    - Registre em missing_fields cada um desses campos que estiver ausente.
    - Para consultas de produtos, não invente preços, marcas ou modelos.
    - Para consultas de políticas, identifique o assunto em policy_topic.
    
    """
    response = client.responses.parse(
    model="gpt-5.6-luna",
    instructions=system_prompt,
    input=message,
    text_format=SemanticInterpretation,
    )

    if response.output_parsed is None:
        raise ValueError("A LLM não retornou uma interpretação válida.")

    return response.output_parsed



if __name__ == "__main__":
    result = interpret_message(
        "Quero violões até 1500 reais e saber a política de devolução."
    )

    print(result.model_dump_json(indent=2))