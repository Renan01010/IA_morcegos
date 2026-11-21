
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    balanced_accuracy_score,
    confusion_matrix,
    classification_report
)

# ==========================================
# 1. CARREGAR A BASE DE DADOS
# ==========================================

arquivo = "resultados/base_classificada_provisoria.csv"

# IMPORTANTE: o arquivo utiliza ponto e vírgula
df = pd.read_csv(arquivo, sep=";")

print("Base carregada com sucesso!")
print("Total de registros:", len(df))

# ==========================================
# 2. SELECIONAR ORGANISMOS CLASSIFICADOS
# ==========================================

# Utilizar somente:
# 1 = morcego
# 0 = não morcego
# -1 = não identificado (excluído)

df = df[df["rotulo"].isin([0, 1])].copy()

print("\nDistribuição das classes:")
print(df["rotulo"].value_counts())

# ==========================================
# 3. SELECIONAR AS 50 CARACTERÍSTICAS
# ==========================================

colunas_features = [
    f"caracteristica_{i}" for i in range(1, 51)
]

X = df[colunas_features]
y = df["rotulo"]

# Garantir que as características sejam numéricas
X = X.apply(pd.to_numeric, errors="coerce")

# Remover registros com valores ausentes
validos = X.notna().all(axis=1)

X = X.loc[validos]
y = y.loc[validos]

print("\nTotal utilizado no treinamento:", len(X))
print("Morcegos:", (y == 1).sum())
print("Outros organismos:", (y == 0).sum())

# ==========================================
# 4. DIVIDIR TREINAMENTO E TESTE
# ==========================================

X_treino, X_teste, y_treino, y_teste = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

print("\nDivisão dos dados:")
print("Treinamento:", len(X_treino))
print("Teste:", len(X_teste))

# ==========================================
# 5. CRIAR OS MODELOS
# ==========================================

modelos = {

    "KNN": Pipeline([
        ("normalizacao", StandardScaler()),
        ("modelo", KNeighborsClassifier(
            n_neighbors=5,
            weights="distance"
        ))
    ]),

    "SVM": Pipeline([
        ("normalizacao", StandardScaler()),
        ("modelo", SVC(
            class_weight="balanced",
            random_state=42
        ))
    ]),

    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
}

# ==========================================
# 6. TREINAR E AVALIAR OS MODELOS
# ==========================================

resultados = []

for nome, modelo in modelos.items():

    print("\n" + "=" * 50)
    print("TREINANDO:", nome)
    print("=" * 50)

    # Treinamento
    modelo.fit(X_treino, y_treino)

    # Previsões
    previsoes = modelo.predict(X_teste)

    # Métricas
    acuracia = accuracy_score(y_teste, previsoes)

    precisao = precision_score(
        y_teste,
        previsoes,
        zero_division=0
    )

    sensibilidade = recall_score(
        y_teste,
        previsoes,
        zero_division=0
    )

    f1 = f1_score(
        y_teste,
        previsoes,
        zero_division=0
    )

    acuracia_balanceada = balanced_accuracy_score(
        y_teste,
        previsoes
    )

    # Exibir resultados
    print(f"Acurácia: {acuracia:.4f}")
    print(f"Precisão: {precisao:.4f}")
    print(f"Sensibilidade: {sensibilidade:.4f}")
    print(f"F1-score: {f1:.4f}")
    print(f"Acurácia balanceada: {acuracia_balanceada:.4f}")

    print("\nMatriz de confusão:")
    print(confusion_matrix(y_teste, previsoes))

    print("\nRelatório de classificação:")
    print(classification_report(
        y_teste,
        previsoes,
        target_names=["Não morcego", "Morcego"],
        zero_division=0
    ))

    # Guardar métricas
    resultados.append({
        "Modelo": nome,
        "Acuracia": acuracia,
        "Precisao": precisao,
        "Sensibilidade": sensibilidade,
        "F1_score": f1,
        "Acuracia_balanceada": acuracia_balanceada
    })

# ==========================================
# 7. COMPARAR OS MODELOS
# ==========================================

tabela = pd.DataFrame(resultados)

print("\n")
print("=" * 60)
print("COMPARAÇÃO FINAL DOS MODELOS")
print("=" * 60)

print(tabela.to_string(index=False))

# ==========================================
# 8. SALVAR RESULTADOS
# ==========================================

tabela.to_csv(
    "resultados/comparacao_modelos.csv",
    sep=";",
    index=False
)

print("\nResultados salvos em:")
print("resultados/comparacao_modelos.csv")

print("\nTreinamento concluído!")
