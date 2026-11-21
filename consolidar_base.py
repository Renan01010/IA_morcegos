
import pandas as pd
import os

# ==========================================
# CONFIGURAÇÕES
# ==========================================

ARQUIVO_BASE = "resultados/base_organizada.csv"
ARQUIVO_VALIDOS = "resultados/morcegos_validados.csv"
ARQUIVO_BUSCA = "resultados/busca_completa_gbif.csv"

PASTA_RESULTADOS = "resultados"

ARQUIVO_FINAL = os.path.join(
    PASTA_RESULTADOS,
    "base_classificada_provisoria.csv"
)

ARQUIVO_INDICES = os.path.join(
    PASTA_RESULTADOS,
    "indices_morcegos.txt"
)

ARQUIVO_RESUMO = os.path.join(
    PASTA_RESULTADOS,
    "resumo_consolidacao.csv"
)


# ==========================================
# FUNÇÃO PARA CARREGAR CSV
# ==========================================

def carregar_csv(caminho):

    if not os.path.exists(caminho):
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    df = pd.read_csv(
        caminho,
        sep=None,
        engine="python",
        encoding="utf-8-sig"
    )

    df.columns = df.columns.str.strip()

    return df


# ==========================================
# PROGRAMA PRINCIPAL
# ==========================================

def main():

    print("\n===== CONSOLIDAÇÃO DA BASE =====")

    # Carregar os três arquivos
    base = carregar_csv(ARQUIVO_BASE)
    validados = carregar_csv(ARQUIVO_VALIDOS)
    busca = carregar_csv(ARQUIVO_BUSCA)

    print("Base original:", len(base))
    print("Morcegos validados inicialmente:", len(validados))
    print("Organismos consultados no GBIF:", len(busca))

    # Conferir se os arquivos possuem índice
    for nome, df in [
        ("base", base),
        ("validados", validados),
        ("busca", busca)
    ]:

        if "indice" not in df.columns:
            raise ValueError(
                f"O arquivo {nome} não possui a coluna indice."
            )

        df["indice"] = pd.to_numeric(
            df["indice"],
            errors="raise"
        ).astype(int)

    # ======================================
    # INICIALIZAR RÓTULOS
    # ======================================

    # -1 = não identificado
    #  0 = outro organismo
    #  1 = morcego

    base["rotulo"] = -1
    base["status_classificacao"] = "NAO_IDENTIFICADO"

    # Dicionário para guardar os rótulos
    rotulos = {}

    # ======================================
    # 76 MORCEGOS JÁ VALIDADOS
    # ======================================

    morcegos_iniciais = validados[
        validados["validacao"] == "CONFIRMADO_MORCEGO"
    ]

    for _, linha in morcegos_iniciais.iterrows():

        indice = int(linha["indice"])

        rotulos[indice] = (
            1,
            "MORCEGO_VALIDADO_INICIALMENTE"
        )

    # ======================================
    # RESULTADOS DOS 8350 ORGANISMOS
    # ======================================

    for _, linha in busca.iterrows():

        indice = int(linha["indice"])
        validacao = linha["validacao"]

        if validacao == "CONFIRMADO_MORCEGO":

            novo_rotulo = (
                1,
                "MORCEGO_CONFIRMADO_GBIF"
            )

        elif validacao == "CONFIRMADO_NAO_MORCEGO":

            novo_rotulo = (
                0,
                "OUTRO_CONFIRMADO_GBIF"
            )

        else:

            novo_rotulo = (
                -1,
                "NAO_IDENTIFICADO"
            )

        # Verificar conflitos
        if indice in rotulos:

            rotulo_anterior = rotulos[indice][0]

            if rotulo_anterior != novo_rotulo[0]:

                raise ValueError(
                    f"Conflito de classificação no índice {indice}"
                )

        else:

            rotulos[indice] = novo_rotulo

    # ======================================
    # APLICAR RÓTULOS À BASE ORIGINAL
    # ======================================

    for indice, (rotulo, status) in rotulos.items():

        mascara = base["indice"] == indice

        if mascara.sum() == 0:
            print(
                f"Aviso: índice {indice} não encontrado na base."
            )
            continue

        base.loc[mascara, "rotulo"] = rotulo

        base.loc[
            mascara,
            "status_classificacao"
        ] = status

    # ======================================
    # VERIFICAÇÕES
    # ======================================

    print("\n===== VERIFICAÇÃO =====")

    print("Total na base:", len(base))
    print("Índices únicos:", base["indice"].nunique())

    duplicados = base["indice"].duplicated().sum()

    print("Índices duplicados:", duplicados)

    if duplicados > 0:
        raise ValueError(
            "Existem índices duplicados na base original."
        )

    # ======================================
    # RESUMO
    # ======================================

    resumo = (
        base["rotulo"]
        .value_counts()
        .sort_index()
    )

    print("\n===== RESULTADO DA CLASSIFICAÇÃO =====")

    print("Morcegos (1):", resumo.get(1, 0))
    print("Outros (0):", resumo.get(0, 0))
    print("Não identificados (-1):", resumo.get(-1, 0))

    # ======================================
    # SALVAR BASE FINAL PROVISÓRIA
    # ======================================

    base.to_csv(
        ARQUIVO_FINAL,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    # ======================================
    # SALVAR ÍNDICES DOS MORCEGOS
    # ======================================

    indices_morcegos = sorted(
        base.loc[
            base["rotulo"] == 1,
            "indice"
        ].tolist()
    )

    with open(
        ARQUIVO_INDICES,
        "w",
        encoding="utf-8"
    ) as arquivo:

        arquivo.write(
            "\n".join(map(str, indices_morcegos))
        )

    # ======================================
    # SALVAR RESUMO
    # ======================================

    resumo_df = pd.DataFrame({
        "rotulo": [-1, 0, 1],
        "classificacao": [
            "Nao identificado",
            "Outro organismo",
            "Morcego"
        ],
        "quantidade": [
            resumo.get(-1, 0),
            resumo.get(0, 0),
            resumo.get(1, 0)
        ]
    })

    resumo_df.to_csv(
        ARQUIVO_RESUMO,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print("\n===== ARQUIVOS GERADOS =====")
    print(ARQUIVO_FINAL)
    print(ARQUIVO_INDICES)
    print(ARQUIVO_RESUMO)

    print("\nConsolidação concluída!")


if __name__ == "__main__":
    main()
