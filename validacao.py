
import pandas as pd
import urllib.request
import urllib.parse
import json
import time


# ==========================================
# 1. CONFIGURAÇÕES
# ==========================================

ARQUIVO_ENTRADA = "resultados/candidatos_morcegos.csv"
ARQUIVO_SAIDA = "resultados/morcegos_validados.csv"

URL_GBIF = "https://api.gbif.org/v1/species/match"


# ==========================================
# 2. CONSULTA AO GBIF
# ==========================================

def consultar_gbif(nome_cientifico):

    # Substitui underline por espaço
    nome = nome_cientifico.replace("_", " ").strip()

    # Monta os parâmetros da consulta
    parametros = urllib.parse.urlencode({
        "name": nome,
        "kingdom": "Animalia",
        "verbose": "true"
    })

    url = f"{URL_GBIF}?{parametros}"

    try:
        requisicao = urllib.request.Request(
            url,
            headers={"User-Agent": "Projeto-Reconhecimento-Morcegos/1.0"}
        )

        with urllib.request.urlopen(requisicao, timeout=20) as resposta:
            dados = json.loads(resposta.read().decode("utf-8"))

        return dados, url

    except Exception as erro:

        print(f"Erro ao consultar {nome}: {erro}")

        return None, url


# ==========================================
# 3. CLASSIFICAÇÃO TAXONÔMICA
# ==========================================

def classificar_resultado(dados):

    if dados is None:
        return "ERRO_NA_CONSULTA"

    ordem = dados.get("order")
    tipo_correspondencia = dados.get("matchType")

    # Não houve correspondência
    if tipo_correspondencia in (None, "NONE"):
        return "REVISAR"

    # Correspondência aproximada precisa de revisão
    if tipo_correspondencia != "EXACT":
        return "REVISAR"

    # Correspondência exata e ordem Chiroptera
    if ordem == "Chiroptera":
        return "CONFIRMADO_MORCEGO"

    # Correspondência exata em outra ordem
    if ordem is not None:
        return "CONFIRMADO_NAO_MORCEGO"

    return "REVISAR"


# ==========================================
# 4. VALIDAÇÃO DOS CANDIDATOS
# ==========================================

def validar_morcegos():

    print("\n===== VALIDAÇÃO TAXONÔMICA =====")

    # Carrega os candidatos encontrados anteriormente
    df = pd.read_csv(
        ARQUIVO_ENTRADA,
        sep=";",
        encoding="utf-8-sig"
    )

    resultados = []

    print("Total de nomes para consultar:", len(df))

    for posicao, linha in df.iterrows():

        nome = str(linha["nome_cientifico"])

        print(
            f"\nConsultando {posicao + 1}/{len(df)}: {nome}"
        )

        dados, url = consultar_gbif(nome)

        if dados is None:
            dados = {}

        classificacao = classificar_resultado(
            dados if dados else None
        )

        resultado = {
            "indice": linha["indice"],
            "nome_cientifico": nome,
            "nome_gbif": dados.get("scientificName"),
            "nome_canonico": dados.get("canonicalName"),
            "ordem": dados.get("order"),
            "familia": dados.get("family"),
            "genero": dados.get("genus"),
            "status_gbif": dados.get("status"),
            "tipo_correspondencia": dados.get("matchType"),
            "confianca": dados.get("confidence"),
            "validacao": classificacao,
            "url_consulta": url
        }

        resultados.append(resultado)

        print("Ordem:", dados.get("order", "Não encontrada"))
        print("Correspondência:", dados.get("matchType", "Sem resultado"))
        print("Validação:", classificacao)

        # Pequeno intervalo entre consultas
        time.sleep(0.2)

    # ==========================================
    # 5. SALVAMENTO DOS RESULTADOS
    # ==========================================

    df_resultados = pd.DataFrame(resultados)


    # Revisões manuais baseadas em fontes taxonômicas
    revisoes_manuais = {
        "Lophostoma_silvicolum":
            "https://www.iucnredlist.org/species/88149202",

        "Rhinolophus_yunnanensis":
            "https://datacenter.kiz.ac.cn/DataBase/SouthwestVertebrateDetail/23809"
    }

    df_resultados["fonte_revisao_manual"] = ""

    for nome, fonte in revisoes_manuais.items():

        mascara_manual = (
            df_resultados["nome_cientifico"] == nome
        )

        df_resultados.loc[
            mascara_manual, "validacao"
        ] = "CONFIRMADO_MORCEGO"

        df_resultados.loc[
            mascara_manual, "fonte_revisao_manual"
        ] = fonte


    df_resultados.to_csv(
        ARQUIVO_SAIDA,
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    print("\n===== RESUMO DA VALIDAÇÃO =====")

    print(
        df_resultados["validacao"]
        .value_counts()
    )

    print("\nTotal consultado:", len(df_resultados))

    print("\nArquivo gerado:", ARQUIVO_SAIDA)

    print("\nValidação concluída!")


# ==========================================
# 6. EXECUÇÃO PRINCIPAL
# ==========================================

if __name__ == "__main__":

    validar_morcegos()
