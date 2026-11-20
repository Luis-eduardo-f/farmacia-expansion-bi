"""
Projeto 4 do roteiro: Clustering de perfil de lojas
======================================================
Agrupa as 26 lojas por perfil (mercado + loja + desempenho) para
identificar segmentos operacionais — útil para decidir políticas
diferentes por grupo (ex.: mix de produto, investimento em marketing
local, meta de faturamento) em vez de tratar a rede como um bloco só.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 120

DATA_DIR = "/home/claude/dashboard-remedios-expansao/data"
OUT_DIR = "/home/claude/dashboard-remedios-expansao/output"

# Reaproveita a base já agregada por loja (gerada no script 03)
base = pd.read_csv(f"{OUT_DIR}/regressao_base_lojas.csv")

vendas = pd.read_csv(f"{DATA_DIR}/vendas_remedios_expansao.csv")
margem_loja = (vendas.groupby("loja_id")["margem_pct"].mean()
               .rename("margem_pct_media").reset_index())
base = base.merge(margem_loja, on="loja_id", how="left")
base["faturamento_m2"] = base["faturamento_medio_mensal"] / base["area_m2"]

FEATURES = ["renda_media", "concorrentes", "populacao", "area_m2",
            "idade_loja_meses", "faturamento_medio_mensal",
            "faturamento_m2", "margem_pct_media"]

X = base[FEATURES].copy()
X_scaled = StandardScaler().fit_transform(X)

# ---------------------------------------------------------------------
# 1. Escolha de k: método do cotovelo + silhueta
# ---------------------------------------------------------------------
inercias, silhuetas, ks = [], [], range(2, 7)
for k in ks:
    km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X_scaled)
    inercias.append(km.inertia_)
    silhuetas.append(silhouette_score(X_scaled, km.labels_))

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].plot(list(ks), inercias, marker="o")
axes[0].set_xlabel("k (nº de clusters)")
axes[0].set_ylabel("Inércia (WCSS)")
axes[0].set_title("Método do cotovelo")
axes[1].plot(list(ks), silhuetas, marker="o", color="darkorange")
axes[1].set_xlabel("k (nº de clusters)")
axes[1].set_ylabel("Coeficiente de silhueta")
axes[1].set_title("Silhueta média por k")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/10_clustering_elbow_silhueta.png")
plt.close()

melhor_k = list(ks)[int(np.argmax(silhuetas))]
print(f"Silhuetas por k: {dict(zip(ks, [round(s, 3) for s in silhuetas]))}")
print(f"Melhor k pela silhueta: {melhor_k}")

# Com apenas 26 lojas, 3 clusters é o ponto de equilíbrio entre
# granularidade útil para o negócio e robustez estatística — se a
# silhueta apontar outro k muito próximo do melhor valor, fixamos 3
# para manter grupos com tamanho mínimo interpretável.
k_final = 3 if abs(silhuetas[list(ks).index(3)] - max(silhuetas)) < 0.05 else melhor_k

km_final = KMeans(n_clusters=k_final, random_state=42, n_init=10).fit(X_scaled)
base["cluster"] = km_final.labels_

# ---------------------------------------------------------------------
# 2. Perfil de cada cluster (médias das features originais)
# ---------------------------------------------------------------------
perfil_cluster = base.groupby("cluster")[FEATURES + ["faturamento_medio_mensal"]].mean().round(1)
perfil_cluster["n_lojas"] = base.groupby("cluster").size()
perfil_cluster.to_csv(f"{OUT_DIR}/clustering_perfil.csv")
print(f"\n--- Perfil médio por cluster (k={k_final}) ---")
print(perfil_cluster.to_string())

print("\n--- Lojas por cluster ---")
for c in sorted(base["cluster"].unique()):
    lojas_c = base[base["cluster"] == c][["loja_id", "cidade"]]
    print(f"\nCluster {c} ({len(lojas_c)} lojas):",
          ", ".join(f"{r.loja_id}/{r.cidade}" for r in lojas_c.itertuples()))

base[["loja_id", "cidade", "cluster"] + FEATURES].to_csv(
    f"{OUT_DIR}/clustering_lojas_atribuicao.csv", index=False
)

# ---------------------------------------------------------------------
# 3. Visualização via PCA (2D)
# ---------------------------------------------------------------------
pca = PCA(n_components=2, random_state=42)
coords = pca.fit_transform(X_scaled)
base["pca1"], base["pca2"] = coords[:, 0], coords[:, 1]
var_exp = pca.explained_variance_ratio_

fig, ax = plt.subplots(figsize=(8, 6))
sns.scatterplot(data=base, x="pca1", y="pca2", hue="cluster",
                 style="cidade", s=110, ax=ax, palette="Set2")
for _, row in base.iterrows():
    ax.annotate(row["loja_id"], (row["pca1"], row["pca2"]),
                fontsize=7, xytext=(3, 3), textcoords="offset points")
ax.set_xlabel(f"PC1 ({var_exp[0]*100:.0f}% da variância)")
ax.set_ylabel(f"PC2 ({var_exp[1]*100:.0f}% da variância)")
ax.set_title(f"Clusters de lojas (PCA 2D, k={k_final})")
ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/11_clustering_pca.png")
plt.close()

# ---------------------------------------------------------------------
# 4. Faturamento médio por cluster (para checar se o agrupamento
#    também separa desempenho, não só perfil demográfico)
# ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6.5, 4.5))
sns.boxplot(data=base, x="cluster", y="faturamento_medio_mensal", ax=ax)
sns.stripplot(data=base, x="cluster", y="faturamento_medio_mensal",
              color="black", alpha=0.5, ax=ax)
ax.set_xlabel("Cluster")
ax.set_ylabel("Faturamento médio mensal (R$)")
ax.set_title("Faturamento por cluster")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/12_clustering_faturamento.png")
plt.close()

print("\nClustering concluído. Gráficos e tabelas salvos em", OUT_DIR)
