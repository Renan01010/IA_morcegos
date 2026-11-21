
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

# ==========================================
# 1. CARREGAR A BASE
# ==========================================

arquivo = "resultados/base_classificada_provisoria.csv"

df = pd.read_csv(arquivo, sep=";")

print("Base carregada:", len(df), "organismos")

# ==========================================
# 2. SEPARAR ORGANISMOS CONHECIDOS
# ==========================================

conhecidos = df[df["rotulo"].isin([0, 1])].copy()

# Organismos ainda não identificados
desconhecidos = df[df["rotulo"] == -1].copy()

print("Organismos conhecidos:", len(conhecidos))
print("Organismos desconhecidos:", len(desconhecidos))

# ==========================================
# 3. SELECIONAR AS 50 CARACTERÍSTICAS
# ==========================================

colunas_features = [
    f"caracteristica_{i}" for i in range(1, 51)
]

X_treino = conhecidos[colunas_features].apply(
    pd.to_numeric, errors="coerce"
)

y_treino = conhecidos["rotulo"].astype(int)

X_desconhecidos = desconhecidos[colunas_features].apply(
    pd.to_numeric, errors="coerce"
)

# Verificar dados ausentes
if X_treino.isna().any().any():
    raise ValueError("Existem valores ausentes no treinamento.")

if X_desconhecidos.isna().any().any():
    raise ValueError("Existem valores ausentes nos organismos desconhecidos.")

# ==========================================
# 4. CRIAR OS MODELOS
# ==========================================

modelo_knn = Pipeline([
    ("normalizacao", StandardScaler()),
    ("modelo", KNeighborsClassifier(
        n_neighbors=5,
        weights="distance"
    ))
])

modelo_svm = Pipeline([
    ("normalizacao", StandardScaler()),
    ("modelo", SVC(
        class_weight="balanced",
        random_state=42
    ))
])

# ==========================================
# 5. TREINAR COM TODOS OS ORGANISMOS
#    JÁ CLASSIFICADOS
# ==========================================

print("\nTreinando KNN...")
modelo_knn.fit(X_treino, y_treino)

print("Treinando SVM...")
modelo_svm.fit(X_treino, y_treino)

# ==========================================
# 6. PREVER OS ORGANISMOS DESCONHECIDOS
# ==========================================

print("\nAnalisando organismos desconhecidos...")

previsao_knn = modelo_knn.predict(X_desconhecidos)
previsao_svm = modelo_svm.predict(X_desconhecidos)

desconhecidos["previsao_knn"] = previsao_knn
desconhecidos["previsao_svm"] = previsao_svm

# ==========================================
# 7. COMPARAR AS PREVISÕES
# ==========================================

def classificar_candidato(linha):

    knn = linha["previsao_knn"]
    svm = linha["previsao_svm"]

    if knn == 1 and svm == 1:
        return "CANDIDATO_PRIORITARIO"

    elif knn == 1 or svm == 1:
        return "REVISAR"

    else:
        return "BAIXA_PRIORIDADE"


desconhecidos["resultado_modelos"] = desconhecidos.apply(
    classificar_candidato,
    axis=1
)

# ==========================================
# 8. EXIBIR RESULTADOS
# ==========================================

print("\n===== RESULTADO DA PROSPECÇÃO =====")

print(
    desconhecidos["resultado_modelos"].value_counts()
)

# ==========================================
# 9. SALVAR RESULTADOS
# ==========================================

desconhecidos.to_csv(
    "resultados/prospeccao_modelos.csv",
    sep=";",
    index=False
)

candidatos = desconhecidos[
    desconhecidos["resultado_modelos"].isin([
        "CANDIDATO_PRIORITARIO",
        "REVISAR"
    ])
].copy()

candidatos.to_csv(
    "resultados/candidatos_modelo.csv",
    sep=";",
    index=False
)

print("\nArquivos gerados:")
print("resultados/prospeccao_modelos.csv")
print("resultados/candidatos_modelo.csv")

print("\nProspecção concluída!")
