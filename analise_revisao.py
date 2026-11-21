
import pandas as pd
import os

# ==========================================
# CONFIGURAÇÕES
# ==========================================

ARQUIVO_ENTRADA = "resultados/busca_completa_gbif.csv"
PASTA_SAIDA = "resultados"

ARQUIVO_REVISAO = os.path.join(
    PASTA_SAIDA, "revisao_completa.csv"
)

ARQUIVO_PRIORITARIO = os.path.join(
    PASTA_SAIDA, "possiveis_morcegos_revisao.csv"
)

ARQUIVO_RESUMO = os.path.join(
    PASTA_SAIDA, "resumo_revisao.csv"
)


# ==========================================
# FAMÍLIAS DE MORCEGOS
# ==========================================

FAMILIAS_MORCEGOS = {
    "Emballonuridae",
    "Furipteridae",
    "Hipposideridae",
    "Megadermatidae",
    "Molossidae",
    "Mormoopidae",
    "Mystacinidae",
    "Natalidae",
    "Noctilionidae",
    "Nycteridae",
    "Phyllostomidae",
    "Pteropodidae",
    "Rhinolophidae",
    "Rhinopomatidae",
    "Thyropteridae",
    "Vespertilionidae"
}


# ==========================================
# GÊNEROS CONHECIDOS DE MORCEGOS
# ==========================================

GENEROS_MORCEGOS = {
    "Anoura", "Artibeus", "Carollia", "Chalinolobus",
    "Corynorhinus", "Cynopterus", "Desmodus",
    "Epomophorus", "Eptesicus", "Hipposideros",
    "Hypsugo", "Lasiurus", "Lophostoma",
    "Micronycteris", "Myotis", "Mystacina",
    "Nyctalus", "Pipistrellus", "Plecotus",
    "Pteronotus", "Pteropus", "Rhinolophus",
    "Rhinophylla", "Rousettus", "Saccopteryx",
    "Sturnira", "Tadarida", "Tonatia",
    "Vampyrum", "Vespertilio", "Brachyphylla",
    "Murina", "Miniopterus", "Molossus",
    "Eumops", "Lasiurus", "Noctilio",
    "Natalus", "Furipterus", "Thyroptera",
    "Nycteris", "Megaderma", "Rhinopoma",
    "Pipistrellus", "Eonycteris", "Macroglossus",
    "Pteronotus", "Phyllostomus", "Glossophaga",
    "Desmodus", "Diaemus", "Diphylla",
    "Trachops", "Uroderma", "Vampyressa",
    "Platyrrhinus", "Sturnira", "Chiroderma",
    "Eptesicus", "Lasiurus", "Lasionycteris",
    "Perimyotis", "Scotophilus", "Scotomanes",
    "Kerivoula", "Murina", "Plecotus",
    "Barbastella", "Antrozous", "Euderma",
    "Cynomops", "Promops", "Nyctinomops",
    "Mormoops", "Pteronotus", "Noctilio",
    "Centurio", "Ectophylla", "Lonchorhina",
    "Macrophyllum", "Tonatia", "Chrotopterus",
    "Lophostoma", "Vampyrum", "Rhinophylla"
}


# ==========================================
# CLASSIFICAÇÃO DOS CASOS
# ==========================================

def analisar_registro(linha):

    ordem = str(linha["ordem"]).strip()
    familia = str(linha["familia"]).strip()
    genero = str(linha["genero"]).strip()

    nome = str(linha["nome_cientifico"]).replace("_", " ")
    genero_nome = nome.split()[0] if nome else ""

    correspondencia = str(
        linha["tipo_correspondencia"]
    ).strip()

    # 1. A API informou diretamente Chiroptera
    if ordem.lower() == "chiroptera":
        return "POSSIVEL_MORCEGO"

    # 2. Família conhecida de morcegos
    if familia in FAMILIAS_MORCEGOS:
        return "POSSIVEL_MORCEGO"

    # 3. Gênero conhecido de morcegos
    if (
        genero in GENEROS_MORCEGOS
        or genero_nome in GENEROS_MORCEGOS
    ):
        return "POSSIVEL_MORCEGO"

    # 4. Outra ordem informada pelo GBIF
    if ordem and ordem.lower() != "nan":
        return "ORDEM_DIFERENTE_DE_CHIROPTERA"

    # 5. Correspondência exata, mas sem ordem
    if correspondencia == "EXACT":
        return "EXATO_SEM_ORDEM"

    # 6. Correspondência aproximada
    if correspondencia == "FUZZY":
        return "CORRESPONDENCIA_APROXIMADA"

    # 7. Correspondência em nível superior
    if correspondencia == "HIGHERRANK":
        return "CORRESPONDENCIA_NIVEL_SUPERIOR"

    return "OUTROS_CASOS"


# ==========================================
# PROGRAMA PRINCIPAL
# ==========================================

def main():

    print("\n===== ANÁLISE DOS CASOS INCONCLUSIVOS =====")

    if not os.path.exists(ARQUIVO_ENTRADA):
        print("Arquivo de entrada não encontrado!")
        return

    # Carregar resultados da consulta
    df = pd.read_csv(
        ARQUIVO_ENTRADA,
        sep=";",
        encoding="utf-8-sig"
    )

    print(f"\nTotal de registros recebidos: {len(df)}")

    # Separar os casos que precisam de revisão
    revisao = df[
        df["validacao"].isin([
            "REVISAR",
            "ERRO_NA_CONSULTA"
        ])
    ].copy()

    print(f"Registros para analisar: {len(revisao)}")

    # Analisar cada registro
    revisao["analise_automatica"] = revisao.apply(
        analisar_registro,
        axis=1
    )

    # Salvar revisão completa
    revisao.to_csv(
        ARQUIVO_REVISAO,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    # Separar possíveis morcegos
    possiveis = revisao[
        revisao["analise_automatica"] == "POSSIVEL_MORCEGO"
    ].copy()

    possiveis.to_csv(
        ARQUIVO_PRIORITARIO,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    # Gerar resumo
    resumo = (
        revisao["analise_automatica"]
        .value_counts()
        .rename_axis("categoria")
        .reset_index(name="quantidade")
    )

    resumo.to_csv(
        ARQUIVO_RESUMO,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    # ======================================
    # EXIBIR RESULTADOS
    # ======================================

    print("\n===== RESULTADO DA ANÁLISE =====")

    print(
        revisao["analise_automatica"]
        .value_counts()
        .to_string()
    )

    print("\nPossíveis morcegos encontrados:")
    print(len(possiveis))

    if len(possiveis) > 0:

        print("\nLista de possíveis morcegos:")

        print(
            possiveis[
                [
                    "indice",
                    "nome_cientifico",
                    "ordem",
                    "familia",
                    "genero",
                    "tipo_correspondencia",
                    "analise_automatica"
                ]
            ].to_string(index=False)
        )

    print("\n===== ARQUIVOS GERADOS =====")
    print(ARQUIVO_REVISAO)
    print(ARQUIVO_PRIORITARIO)
    print(ARQUIVO_RESUMO)

    print("\nAnálise concluída!")


if __name__ == "__main__":
    main()
