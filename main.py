
from processamento import (
    verificar_arquivos,
    visualizar_arquivos,
    contar_registros,
    carregar_dados,
    salvar_dados
)


def main():

    print("================================")
    print("   PROJETO: É MORCEGO?")
    print("================================")

    # 1. Verificar arquivos
    if not verificar_arquivos():
        return

    # 2. Visualizar os dados
    visualizar_arquivos()

    # 3. Contar registros
    contar_registros()

    # 4. Carregar dados
    df = carregar_dados()

    # 5. Mostrar primeiros registros
    print("\n=== BASE ORGANIZADA ===")
    print(df.head())

    # 6. Salvar CSV
    salvar_dados(df)

    print("\nProcessamento concluído!")


if __name__ == "__main__":
    main()
