from pathlib import Path
import numpy as np
import pandas as pd

# Caminhos dos arquivos
ARQUIVO_DADOS = Path("dados/Wpc50.dat")
ARQUIVO_NOMES = Path("dados/Names.txt")


def verificar_arquivos():

    print("=== VERIFICAÇÃO DOS ARQUIVOS ===")

    if not ARQUIVO_DADOS.exists():
        print("ERRO: Wpc50.dat não encontrado!")
        return False

    if not ARQUIVO_NOMES.exists():
        print("ERRO: Names.txt não encontrado!")
        return False

    print("Wpc50.dat encontrado!")
    print("Names.txt encontrado!")

    return True


def visualizar_arquivos():

    print("\n=== PRIMEIRAS LINHAS DOS DADOS ===")

    with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
        for i in range(3):
            print(arquivo.readline().strip())

    print("\n=== PRIMEIROS NOMES CIENTÍFICOS ===")

    with open(
        ARQUIVO_NOMES,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as arquivo:
        for i in range(5):
            print(arquivo.readline().strip())


def contar_registros():

    with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
        total_dados = sum(1 for linha in arquivo if linha.strip())

    with open(
        ARQUIVO_NOMES,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as arquivo:
        total_nomes = sum(1 for linha in arquivo if linha.strip())

    print("\n=== QUANTIDADE DE REGISTROS ===")
    print("Registros numéricos:", total_dados)
    print("Nomes científicos:", total_nomes)

    if total_dados == total_nomes:
        print("OK: Quantidades correspondentes!")
    else:
        print("ATENÇÃO: Quantidades diferentes!")


def main():

    if verificar_arquivos():
        visualizar_arquivos()
        contar_registros()


if __name__ == "__main__":
    main()






def carregar_dados():

    print("\n=== CARREGANDO BASE DE DADOS ===")

    # Carregar características numéricas
    dados = np.loadtxt(ARQUIVO_DADOS)

    # Carregar nomes científicos
    with open(
        ARQUIVO_NOMES,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as arquivo:
        nomes = [linha.strip() for linha in arquivo if linha.strip()]

    # Validar quantidade de registros
    if dados.shape[0] != len(nomes):
        raise ValueError("Os arquivos possuem quantidades diferentes!")

    # Validar quantidade de características
    if dados.shape[1] != 50:
        raise ValueError(
            f"Esperadas 50 características, encontradas {dados.shape[1]}"
        )

    # Criar DataFrame
    df = pd.DataFrame(
        dados,
        columns=[
            f"caracteristica_{i+1}"
            for i in range(dados.shape[1])
        ]
    )

    df.insert(0, "nome_cientifico", nomes)
    df.insert(0, "indice", np.arange(1, len(nomes) + 1))

    print("Dados carregados com sucesso!")
    print("Dimensões:", df.shape)

    return df


def salvar_dados(df):

    df.to_csv(
        "resultados/base_organizada.csv",
        index=False
    )

    print("Base organizada salva com sucesso!")
