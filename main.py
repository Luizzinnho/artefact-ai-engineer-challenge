from src.semantic_interpreter import interpret_message
from src.executor import execute_commands
from src.response_composer import compose_response


def process_message(message: str) -> str:
    interpretation = interpret_message(message)
    results = execute_commands(interpretation)
    return compose_response(message, results)
    


def main() -> None:
    print("\n=== Empório da Música | Assistente Virtual ===")
    print("Digite sua mensagem ou 'sair' para encerrar.")

    while True:
        try:
            message = input("\nVocê: ").strip()

            if not message:
                continue

            if message.casefold() in {"sair", "exit", "quit"}:
                print("\nAtendimento encerrado. Até logo!")
                break

            answer = process_message(message)
            print(f"\nEmpório da Música: {answer}")

        except (KeyboardInterrupt, EOFError):
            print("\nAtendimento encerrado.")
            break

        except Exception as exc:
            print(f"\nErro ao processar a mensagem: {exc}")


if __name__ == "__main__":
    main()
