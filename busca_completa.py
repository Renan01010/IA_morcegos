
import pandas as pd
import urllib.request
import urllib.parse
import json
import time
import os

# ==========================================
# CONFIGURAÇÕES
# ==========================================

PASTA_RESULTADOS = "resultados"

ARQUIVO_BASE = os.path.join(
    PASTA_RESULTADOS,
    "base_organizada.csv"
)

ARQUIVO_VALIDOS = os.path.join(
    PASTA_RESULTADOS,
    "morcegos_validados.csv"
)

ARQUIVO_SAIDA = os.path.join(
    PASTA_RESULTADOS,
    "busca_completa_gbif.csv"
)

# Intervalo entre consultas
INTERVALO = 0.2

# Salvar progresso a cada 25 consultas
SALVAR_A_CADA = 25


# ==========================================
# FUNÇÃO PARA CONSULTAR O GBIF
# ==========================================

def consultar_gbif(nome):

    nome_formatado = str(nome).replace("_", " ")
    nome_url = urllib.parse.quote(nome_formatado)

    url = (
        "https://api.gbif.org/v1/species/match"
        f"?name={nome_url}&kingdom=Animalia&verbose=true"
    )

    requisicao = urllib.request.Request(
        url,
        headers={"User-Agent": "Trabalho-Academico-Morcegos/1.0"}
    )

    for tentativa in range(3):

        try:
            with urllib.request.urlopen(
                requisicao, timeout=20
            ) as resposta:

                dados = json.loads(
                    resposta.read().decode("utf-8")
                )

            ordem = dados.get("order", "")
            correspondencia = dados.get("matchType", "")
            
            if ordem == "Chiroptera":
                validacao = (
                    "CONFIRMADO_MORCEGO"
                    if correspondencia == "EXACT"
                    else "REVISAR"
                )

            elif ordem and correspondencia == "EXACT":
                validacao = "CONFIRMADO_NAO_MORCEGO"

            else:
                validacao = "REVISAR"

            return {
                "nome_gbif": dados.get("scientificName", ""),
                "nome_canonico": dados.get("canonicalName", ""),
                "ordem": ordem,
                "familia": dados.get("family", ""),
                "genero": dados.get("genus", ""),
                "status_gbif": dados.get("status", ""),
                "tipo_correspondencia": correspondencia,
                "confianca": dados.get("confidence", ""),
                "validacao": validacao,
                "url_consulta": url
            }

        except Exception as erro:
            print(f"Erro na consulta de {nome}: {erro}")
            time.sleep(2)

    return {
        "nome_gbif": "",
        "nome_canonico": "",
        "ordem": "",
        "familia": "",
        "genero": "",
        "status_gbif": "",
        "tipo_correspondencia": "",
        "confianca": "",
        "validacao": "ERRO_NA_CONSULTA",
        "url_consulta": url
    }


# ==========================================
# SALVAR RESULTADOS
# ==========================================

def salvar_resultados(resultados):

    df = pd.DataFrame(resultados)

    df.to_csv(
        ARQUIVO_SAIDA,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )


# ==========================================
# PROGRAMA PRINCIPAL
# ==========================================

def main():

    print("\n===== BUSCA COMPLETA DE MORCEGOS =====")

    # Carregar base original
    base = pd.read_csv(
        ARQUIVO_BASE,
        sep=None,
        engine="python",
        encoding="utf-8-sig"
    )

    # Carregar os 76 morcegos já validados
    validados = pd.read_csv(
        ARQUIVO_VALIDOS,
        sep=";",
        encoding="utf-8-sig"
    )

    indices_ja_validados = set(
        validados["indice"].astype(int)
    )

    # Carregar progresso anterior, se existir
    if os.path.exists(ARQUIVO_SAIDA):

        progresso = pd.read_csv(
            ARQUIVO_SAIDA,
            sep=";",
            encoding="utf-8-sig"
        )

        resultados = progresso.to_dict("records")

        indices_concluidos = set(
            progresso.loc[
                progresso["validacao"] != "ERRO_NA_CONSULTA",
                "indice"
            ].astype(int)
        )

    else:
        resultados = []
        indices_concluidos = set()

    # Selecionar os organismos ainda não consultados
    pendentes = base[
        ~base["indice"].astype(int).isin(indices_ja_validados)
        & ~base["indice"].astype(int).isin(indices_concluidos)
    ]

    total = len(pendentes)

    print(f"Organismos na base: {len(base)}")
    print(f"Já validados anteriormente: {len(indices_ja_validados)}")
    print(f"Já consultados nesta etapa: {len(indices_concluidos)}")
    print(f"Restantes para consultar: {total}")

    for posicao, (_, linha) in enumerate(
        pendentes.iterrows(), start=1
    ):

        indice = int(linha["indice"])
        nome = str(linha["nome_cientifico"])

        print(f"\nConsultando {posicao}/{total}: {nome}")

        resultado = consultar_gbif(nome)

        resultado["indice"] = indice
        resultado["nome_cientifico"] = nome

        resultados.append(resultado)

        print("Ordem:", resultado["ordem"])
        print("Resultado:", resultado["validacao"])

        # Salvar periodicamente
        if posicao % SALVAR_A_CADA == 0:
            salvar_resultados(resultados)
            print("\nProgresso salvo!")

        time.sleep(INTERVALO)

    # Salvar ao terminar
    salvar_resultados(resultados)

    print("\n===== BUSCA FINALIZADA =====")
    print(f"Registros consultados nesta execução: {total}")
    print(f"Arquivo gerado: {ARQUIVO_SAIDA}")

    if resultados:
        resumo = pd.DataFrame(resultados)
        print("\nResumo:")
        print(resumo["validacao"].value_counts())


if __name__ == "__main__":
    main()
