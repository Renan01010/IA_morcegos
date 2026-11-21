
import urllib.request
import json

# Teste com o identificador do Acrochordus granulatus
chave = 2472757

url = f"https://api.gbif.org/v1/species/{chave}/parents"

requisicao = urllib.request.Request(
    url,
    headers={"User-Agent": "Trabalho-Academico-Morcegos/1.0"}
)

with urllib.request.urlopen(requisicao) as resposta:
    dados = json.loads(resposta.read().decode("utf-8"))

print("===== HIERARQUIA TAXONÔMICA =====")

for item in dados:
    print(
        item.get("rank"),
        "-",
        item.get("scientificName")
    )
