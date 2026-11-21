
import pandas as pd

# ==========================================
# 1. CARREGAR A BASE
# ==========================================

arquivo = "resultados/base_classificada_provisoria.csv"

df = pd.read_csv(arquivo, sep=";")

print("Base carregada:", len(df))

# ==========================================
# 2. CRIAR CLASSIFICAÇÃO FINAL
# ==========================================

# 1 = Morcego confirmado
# 0 = Não identificado como morcego

df["classe_final"] = df["rotulo"].replace(-1, 0)

# Identificar quais registros foram originalmente inconclusivos
df["situacao_final"] = df["rotulo"].map({
    1: "MORCEGO_CONFIRMADO",
    0: "OUTRO_CONFIRMADO",
    -1: "NAO_IDENTIFICADO_COMO_MORCEGO"
})

# ==========================================
# 3. CONFERIR A CLASSIFICAÇÃO
# ==========================================

print("\nDistribuição final:")

print(df["classe_final"].value_counts())

print("\nSituação dos registros:")

print(df["situacao_final"].value_counts())

# ==========================================
# 4. GERAR ARQUIVO COMPLETO
# ==========================================

df.to_csv(
    "resultados/base_final_8426.csv",
    sep=";",
    index=False
)

# ==========================================
# 5. GERAR LISTA DE ÍNDICES DOS MORCEGOS
# ==========================================

morcegos = df[df["classe_final"] == 1]

indices = morcegos["indice"].tolist()

with open(
    "resultados/indices_morcegos_final.txt",
    "w",
    encoding="utf-8"
) as arquivo:

    for indice in indices:
        arquivo.write(f"{indice}\n")

# ==========================================
# 6. GERAR RESUMO
# ==========================================

resumo = pd.DataFrame({
    "Categoria": [
        "Total de organismos",
        "Morcegos confirmados",
        "Outros confirmados",
        "Não identificados como morcegos",
        "Total classificados como 0",
        "Total classificados como 1"
    ],
    "Quantidade": [
        len(df),
        (df["rotulo"] == 1).sum(),
        (df["rotulo"] == 0).sum(),
        (df["rotulo"] == -1).sum(),
        (df["classe_final"] == 0).sum(),
        (df["classe_final"] == 1).sum()
    ]
})

resumo.to_csv(
    "resultados/resumo_final.csv",
    sep=";",
    index=False
)

print("\nArquivos finais gerados:")
print("1. resultados/base_final_8426.csv")
print("2. resultados/indices_morcegos_final.txt")
print("3. resultados/resumo_final.csv")

print("\nFinalização concluída!")
