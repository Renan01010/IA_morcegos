
import pandas as pd
import urllib.request
import urllib.parse
import urllib.error
import json
import time
import os

# ==========================================
# CONFIGURAÇÕES
# ==========================================

ENTRADA = "resultados/revisao_completa.csv"
SAIDA = "resultados/taxonomia_enriquecida.csv"

SALVAR_A_CADA = 20
INTERVALO = 0.3


# ==========================================
# CONSULTA À API DO GBIF
# ==========================================

def requisitar_json(url):

    requisicao = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Trabalho-Academico-Morcegos/1.0"
        }
    )

    for tentativa in range(3):

        try:
            with urllib.request.urlopen(
                requisicao,
                timeout=30
            ) as resposta:

                return json.loads(
                    resposta.read().decode("utf-8")
                )

        except urllib.error.HTTPError as erro:

            if erro.code == 404:
                print("Registro não encontrado no GBIF:", url)
                return None

            print(
                f"Erro HTTP {erro.code}, "
                f"tentativa {tentativa + 1}/3"
            )

        except Exception as erro:

            print(
                f"Falha na tentativa {tentativa + 1}/3: {erro}"
            )

        if tentativa < 2:
            time.sleep(3)

    return None


# ==========================================
# RECUPERAR CLASSIFICAÇÃO TAXONÔMICA
# ==========================================

def obter_classificacao(chave):

    if not chave:
        return None

    url = (
        f"https://api.gbif.org/v1/species/{chave}/parents"
    )

    dados = requisitar_json(url)

    if dados is None:
        return None

    classificacao = {}

    # Recuperar os níveis dos ancestrais
    for item in dados:

        nivel = str(item.get("rank", "")).upper()
        nome = item.get("scientificName", "")

        if nivel and nome:
            classificacao[nivel] = nome

    # Consultar o próprio táxon
    url_detalhes = (
        f"https://api.gbif.org/v1/species/{chave}"
    )

    detalhes = requisitar_json(url_detalhes)

    if detalhes:

        nivel = str(
            detalhes.get("rank", "")
        ).upper()

        nome = detalhes.get("scientificName", "")

        if nivel and nome:
            classificacao[nivel] = nome

    return classificacao


# ==========================================
# ANALISAR UM ORGANISMO
# ==========================================

def analisar_organismo(nome):

    nome_formatado = str(nome).replace("_", " ")
    nome_url = urllib.parse.quote(nome_formatado)

    url = (
        "https://api.gbif.org/v1/species/match"
        f"?name={nome_url}&kingdom=Animalia&verbose=true"
    )

    dados = requisitar_json(url)

    if not dados:

        return {
            "taxon_key": "",
            "nome_gbif": "",
            "rank_gbif": "",
            "correspondencia_gbif": "",
            "confianca_gbif": "",
            "ordem_hierarquia": "",
            "familia_hierarquia": "",
            "genero_hierarquia": "",
            "classificacao_detalhada": "",
            "resultado_taxonomico": "ERRO_NA_CONSULTA"
        }

    correspondencia = dados.get("matchType", "")
    rank = dados.get("rank", "")
    confianca = dados.get("confidence", "")

    # Priorizar o identificador do táxon aceito
    chave = (
        dados.get("acceptedUsageKey")
        or dados.get("usageKey")
    )

    print("\n--- DIAGNÓSTICO GBIF ---")
    print("Nome consultado:", nome_formatado)
    print("Nome encontrado:", dados.get("scientificName"))
    print("Correspondência:", correspondencia)
    print("Identificador:", chave)
    print("Ordem informada pelo GBIF:", dados.get("order"))

    if not chave:

        return {
            "taxon_key": "",
            "nome_gbif": dados.get("scientificName", ""),
            "rank_gbif": rank,
            "correspondencia_gbif": correspondencia,
            "confianca_gbif": confianca,
            "ordem_hierarquia": "",
            "familia_hierarquia": "",
            "genero_hierarquia": "",
            "classificacao_detalhada": "",
            "resultado_taxonomico": "SEM_IDENTIFICADOR_TAXONOMICO"
        }

    # Recuperar hierarquia
    detalhes = obter_classificacao(chave)

    if detalhes is None:

        return {
            "taxon_key": chave,
            "nome_gbif": dados.get("scientificName", ""),
            "rank_gbif": rank,
            "correspondencia_gbif": correspondencia,
            "confianca_gbif": confianca,
            "ordem_hierarquia": "",
            "familia_hierarquia": "",
            "genero_hierarquia": "",
            "classificacao_detalhada": "",
            "resultado_taxonomico": "ERRO_NA_CONSULTA"
        }

    # ======================================
    # EXTRAIR HIERARQUIA
    # IMPORTANTE: AS CHAVES SÃO MAIÚSCULAS
    # ======================================

    ordem = detalhes.get("ORDER", "")
    familia = detalhes.get("FAMILY", "")
    genero = detalhes.get("GENUS", "")

    # Complementar com dados do match
    if not ordem:
        ordem = dados.get("order", "")

    if not familia:
        familia = dados.get("family", "")

    if not genero:
        genero = dados.get("genus", "")

    # ======================================
    # MONTAR CLASSIFICAÇÃO DETALHADA
    # ======================================

    campos = [
        ("KINGDOM", "Reino"),
        ("PHYLUM", "Filo"),
        ("CLASS", "Classe"),
        ("ORDER", "Ordem"),
        ("FAMILY", "Família"),
        ("GENUS", "Gênero"),
        ("SPECIES", "Espécie")
    ]

    classificacao = []

    for campo, nome_campo in campos:

        valor = detalhes.get(campo)

        if valor:
            classificacao.append(
                f"{nome_campo}: {valor}"
            )

    classificacao_texto = " | ".join(classificacao)

    print("\nHierarquia recuperada:")

    for campo, nome_campo in campos:

        valor = detalhes.get(campo)

        if valor:
            print(f"{nome_campo}: {valor}")

    print("------------------------")

    # ======================================
    # CLASSIFICAÇÃO CONSERVADORA
    # ======================================

    if correspondencia == "EXACT" and ordem == "Chiroptera":

        resultado = "CONFIRMADO_MORCEGO"

    elif correspondencia == "EXACT" and ordem:

        resultado = "CONFIRMADO_NAO_MORCEGO"

    elif ordem == "Chiroptera":

        resultado = "INDICIO_MORCEGO_REVISAR"

    elif ordem:

        resultado = "ORDEM_IDENTIFICADA_REVISAR"

    else:

        resultado = "SEM_CLASSIFICACAO_SUFICIENTE"

    return {
        "taxon_key": chave,
        "nome_gbif": dados.get("scientificName", ""),
        "rank_gbif": rank,
        "correspondencia_gbif": correspondencia,
        "confianca_gbif": confianca,
        "ordem_hierarquia": ordem,
        "familia_hierarquia": familia,
        "genero_hierarquia": genero,
        "classificacao_detalhada": classificacao_texto,
        "resultado_taxonomico": resultado
    }


# ==========================================
# SALVAR RESULTADOS
# ==========================================

def salvar(resultados):

    df = pd.DataFrame(resultados)

    df = df.drop_duplicates(
        subset=["indice"],
        keep="last"
    )

    df.to_csv(
        SAIDA,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )


# ==========================================
# PROGRAMA PRINCIPAL
# ==========================================

def main():

    print("\n===== ENRIQUECIMENTO TAXONÔMICO =====")

    if not os.path.exists(ENTRADA):

        print("Arquivo de entrada não encontrado!")
        return

    df = pd.read_csv(
        ENTRADA,
        sep=";",
        encoding="utf-8-sig"
    )

    categorias = [
        "EXATO_SEM_ORDEM",
        "CORRESPONDENCIA_NIVEL_SUPERIOR",
        "CORRESPONDENCIA_APROXIMADA"
    ]

    pendentes = df[
        df["analise_automatica"].isin(categorias)
    ].copy()

    print("Registros selecionados:", len(pendentes))

    # ======================================
    # CARREGAR PROGRESSO ANTERIOR
    # ======================================

    if os.path.exists(SAIDA):

        anterior = pd.read_csv(
            SAIDA,
            sep=";",
            encoding="utf-8-sig"
        )

        resultados = anterior.to_dict("records")

        # Só considerar concluídos os resultados
        # que não tiveram erro de consulta.
        concluidos = set(
            anterior.loc[
                ~anterior["resultado_taxonomico"].isin([
                    "ERRO_NA_CONSULTA"
                ]),
                "indice"
            ].astype(int)
        )

    else:

        resultados = []
        concluidos = set()

    pendentes = pendentes[
        ~pendentes["indice"].astype(int).isin(concluidos)
    ]

    total = len(pendentes)

    print("Já concluídos:", len(concluidos))
    print("Restantes:", total)

    # ======================================
    # CONSULTAR REGISTROS
    # ======================================

    for posicao, (_, linha) in enumerate(
        pendentes.iterrows(),
        start=1
    ):

        indice = int(linha["indice"])
        nome = str(linha["nome_cientifico"])

        print(
            f"\nConsultando {posicao}/{total}: {nome}"
        )

        resultado = analisar_organismo(nome)

        resultado["indice"] = indice
        resultado["nome_cientifico"] = nome
        resultado["categoria_anterior"] = (
            linha["analise_automatica"]
        )

        resultados.append(resultado)

        print("Ordem:", resultado["ordem_hierarquia"])
        print("Resultado:", resultado["resultado_taxonomico"])

        if posicao % SALVAR_A_CADA == 0:

            salvar(resultados)
            print("\nProgresso salvo!")

        time.sleep(INTERVALO)

    # Salvar ao finalizar
    salvar(resultados)

    # ======================================
    # RESUMO FINAL
    # ======================================

    final = pd.read_csv(
        SAIDA,
        sep=";",
        encoding="utf-8-sig"
    )

    print("\n===== RESULTADO FINAL =====")

    print(
        final["resultado_taxonomico"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nTotal de registros salvos:", len(final))
    print("Arquivo:", SAIDA)
    print("\nAnálise concluída!")


if __name__ == "__main__":
    main()
