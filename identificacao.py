
import pandas as pd
from processamento import carregar_dados


# ==========================================
# 1. GÊNEROS CONHECIDOS DE MORCEGOS
# ==========================================

GENEROS_MORCEGOS = {

    # Gêneros da lista inicial
    "Myotis",
    "Pipistrellus",
    "Artibeus",
    "Carollia",
    "Pteropus",
    "Rousettus",
    "Molossus",
    "Tadarida",
    "Rhinolophus",
    "Miniopterus",
    "Eptesicus",
    "Lasiurus",
    "Nyctalus",
    "Plecotus",
    "Vespertilio",
    "Noctilio",
    "Desmodus",
    "Glossophaga",
    "Phyllostomus",
    "Pteronotus",
    "Mormoops",
    "Natalus",
    "Nycteris",
    "Eumops",
    "Cynomops",
    "Mormopterus",
    "Otomops",
    "Cheiromeles",
    "Furipterus",
    "Thyroptera",
    "Mystacina",
    "Myzopoda",
    "Kerivoula",
    "Scotophilus",
    "Histiotus",
    "Chalinolobus",
    "Barbastella",
    "Rhinopoma",
    "Hipposideros",
    "Megaderma",
    "Corynorhinus",
    "Antrozous",

    # Família Molossidae
    "Nyctinomops",
    "Promops",
    "Molossops",
    "Chaerephon",

    # Família Phyllostomidae
    "Anoura",
    "Lonchophylla",
    "Lonchorhina",
    "Trachops",
    "Tonatia",
    "Lophostoma",
    "Micronycteris",
    "Vampyrum",
    "Chrotopterus",
    "Diaemus",
    "Diphylla",
    "Macrotus",
    "Leptonycteris",
    "Sturnira",
    "Platyrrhinus",
    "Uroderma",
    "Vampyressa",
    "Rhinophylla",
    "Dermanura",
    "Pygoderma",

    # Outras famílias
    "Saccopteryx",
    "Peropteryx",
    "Eidolon",
    "Epomophorus",
    "Cynopterus",
    "Acerodon",
    "Dobsonia",
    "Macroglossus",
    "Nyctimene",
    "Eonycteris",
    "Nyctophilus",
    "Hypsugo",
    "Lasionycteris"
}


# ==========================================
# 2. IDENTIFICAÇÃO DOS CANDIDATOS
# ==========================================

def identificar_candidatos():

    print("\n===== IDENTIFICANDO CANDIDATOS =====")

    # Carrega a base de dados
    df = carregar_dados()

    # Extrai o gênero dos nomes científicos
    generos = (
        df["nome_cientifico"]
        .astype(str)
        .str.strip()
        .str.replace("_", " ", regex=False)
        .str.split()
        .str[0]
    )

    # Procura gêneros conhecidos de morcegos
    mascara = (
        generos.isin(GENEROS_MORCEGOS)
        | df["nome_cientifico"].astype(str).str.contains(
            "Chiroptera",
            case=False,
            na=False
        )
    )

    # Separa os candidatos
    candidatos = df.loc[mascara].copy()

    # ==========================================
    # 3. CRIAÇÃO DOS RÓTULOS PROVISÓRIOS
    # ==========================================

    # -1 = organismo ainda não identificado
    #  1 = candidato a morcego

    df["rotulo_provisorio"] = -1

    df.loc[mascara, "rotulo_provisorio"] = 1

    # Define o status de identificação
    df["status_identificacao"] = "Nao identificado"

    df.loc[
        mascara,
        "status_identificacao"
    ] = "Candidato a morcego"

    # ==========================================
    # 4. SALVAMENTO DOS ARQUIVOS
    # ==========================================

    # Salva a base completa com os rótulos
    df.to_csv(
        "resultados/base_rotulada_inicial.csv",
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    # Salva somente os candidatos
    candidatos.to_csv(
        "resultados/candidatos_morcegos.csv",
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    print("\nArquivos salvos com sucesso!")

    # ==========================================
    # 5. RESULTADOS DA IDENTIFICAÇÃO
    # ==========================================

    print("\n===== CANDIDATOS A MORCEGOS =====")

    print("Quantidade encontrada:", len(candidatos))

    print(
        candidatos[
            ["indice", "nome_cientifico"]
        ].to_string(index=False)
    )

    # ==========================================
    # 6. RESUMO DOS RÓTULOS
    # ==========================================

    print("\n===== RESUMO DOS RÓTULOS =====")

    print(
        df["rotulo_provisorio"]
        .value_counts()
        .sort_index()
    )

    print("\nTotal de organismos:", len(df))

    print(
        "Candidatos a morcegos:",
        (df["rotulo_provisorio"] == 1).sum()
    )

    print(
        "Não identificados:",
        (df["rotulo_provisorio"] == -1).sum()
    )

    print("\nProcessamento concluído!")


# ==========================================
# 7. VERIFICAÇÃO DOS NOMES DA BASE
# ==========================================

def verificar_nomes():

    df = carregar_dados()

    print("\n===== PRIMEIROS 30 NOMES =====")

    for indice, nome in zip(
        df["indice"].head(30),
        df["nome_cientifico"].head(30)
    ):
        print(indice, "-", repr(nome))

    print("\n===== EXEMPLOS ALEATÓRIOS =====")

    print(
        df["nome_cientifico"]
        .sample(min(20, len(df)))
        .to_string(index=False)
    )


# ==========================================
# 8. EXECUÇÃO PRINCIPAL
# ==========================================

if __name__ == "__main__":

    identificar_candidatos()
