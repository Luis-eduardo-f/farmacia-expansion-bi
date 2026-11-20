"""
Projeto 2 do roteiro: Regressão linear de potencial de faturamento
====================================================================
Pergunta de negócio: dado o perfil demográfico/competitivo de uma
cidade (população, renda média, nº de concorrentes) e características
da loja (área, idade, tipo), qual faturamento mensal uma loja deveria
gerar? E, a partir disso, qual o potencial de uma NOVA loja em cada
cidade da base?

Dados: vendas_remedios_expansao.csv e lojas_cadastro.csv (26 lojas,
8 cidades, 18 meses de vendas).
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 120

DATA_DIR = "/home/claude/dashboard-remedios-expansao/data"
OUT_DIR = "/home/claude/dashboard-remedios-expansao/output"

vendas = pd.read_csv(f"{DATA_DIR}/vendas_remedios_expansao.csv")
lojas = pd.read_csv(f"{DATA_DIR}/lojas_cadastro.csv")

# ---------------------------------------------------------------------
# 1. Agregar vendas ao nível de loja (faturamento médio mensal)
# ---------------------------------------------------------------------
fat_mensal_loja = (vendas.groupby(["loja_id", "ano_mes"])["faturamento"]
                   .sum().reset_index())
resumo_loja = (fat_mensal_loja.groupby("loja_id")["faturamento"]
               .agg(faturamento_medio_mensal="mean", desvio_padrao="std")
               .reset_index())

base = resumo_loja.merge(lojas, on="loja_id", how="left")
base["log_populacao"] = np.log(base["populacao"])
base["tipo_franquia"] = (base["tipo"] == "Franquia").astype(int)

print("=" * 60)
print("BASE DE MODELAGEM (nível loja, n =", len(base), ")")
print("=" * 60)
print(base[["loja_id", "cidade", "faturamento_medio_mensal", "populacao",
            "renda_media", "concorrentes", "area_m2", "idade_loja_meses",
            "tipo"]].to_string(index=False))

# ---------------------------------------------------------------------
# 2. Regressão OLS (statsmodels, para ler coeficientes e p-valores)
# ---------------------------------------------------------------------
X_cols = ["log_populacao", "renda_media", "concorrentes", "area_m2",
          "idade_loja_meses", "tipo_franquia"]
X = sm.add_constant(base[X_cols])
y = base["faturamento_medio_mensal"]

modelo = sm.OLS(y, X).fit()
print("\n" + "=" * 60)
print("RESULTADO DA REGRESSÃO (OLS)")
print("=" * 60)
print(modelo.summary())

coef_tab = pd.DataFrame({
    "coeficiente": modelo.params,
    "p_valor": modelo.pvalues,
    "significativo_5pct": modelo.pvalues < 0.05,
}).round(4)
coef_tab.to_csv(f"{OUT_DIR}/regressao_coeficientes.csv")

base["faturamento_previsto"] = modelo.predict(X)
base["residuo"] = base["faturamento_medio_mensal"] - base["faturamento_previsto"]
base.to_csv(f"{OUT_DIR}/regressao_base_lojas.csv", index=False)

print(f"\nR² = {modelo.rsquared:.3f} | R² ajustado = {modelo.rsquared_adj:.3f}")

# ---------------------------------------------------------------------
# 2b. Diagnóstico de multicolinearidade (VIF) — o condition number alto
#     do OLS acima é um alerta: população, renda e nº de concorrentes
#     tendem a crescer juntos (cidades grandes são ricas e competitivas),
#     o que torna os coeficientes individuais instáveis mesmo com R² alto.
# ---------------------------------------------------------------------
vif_tab = pd.DataFrame({
    "variavel": X_cols,
    "VIF": [variance_inflation_factor(base[X_cols].values, i)
            for i in range(len(X_cols))],
}).round(2).sort_values("VIF", ascending=False)
vif_tab.to_csv(f"{OUT_DIR}/regressao_vif.csv", index=False)
print("\n--- VIF (Variance Inflation Factor) por variável ---")
print(vif_tab.to_string(index=False))
print("(VIF > 5-10 indica multicolinearidade relevante)")

corr_preditores = base[X_cols].corr().round(2)
fig, ax = plt.subplots(figsize=(6.5, 5.5))
sns.heatmap(corr_preditores, annot=True, cmap="coolwarm", center=0, ax=ax)
ax.set_title("Correlação entre variáveis preditoras")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/06b_correlacao_preditores.png")
plt.close()

# ---------------------------------------------------------------------
# 3. Diagnóstico: previsto vs. real, e resíduos
# ---------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
sns.scatterplot(data=base, x="faturamento_previsto", y="faturamento_medio_mensal",
                 hue="cidade", ax=axes[0], s=70, legend=False)
lims = [base[["faturamento_previsto", "faturamento_medio_mensal"]].min().min(),
        base[["faturamento_previsto", "faturamento_medio_mensal"]].max().max()]
axes[0].plot(lims, lims, "--", color="gray")
axes[0].set_xlabel("Faturamento previsto (R$)")
axes[0].set_ylabel("Faturamento real (R$)")
axes[0].set_title("Previsto vs. Real")

sns.scatterplot(data=base, x="faturamento_previsto", y="residuo",
                 hue="cidade", ax=axes[1], s=70, legend=False)
axes[1].axhline(0, linestyle="--", color="gray")
axes[1].set_xlabel("Faturamento previsto (R$)")
axes[1].set_ylabel("Resíduo (R$)")
axes[1].set_title("Resíduos do modelo")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/07_regressao_diagnostico.png")
plt.close()

# ---------------------------------------------------------------------
# 4. Coeficientes padronizados (quem pesa mais na decisão)
# ---------------------------------------------------------------------
X_std = (base[X_cols] - base[X_cols].mean()) / base[X_cols].std()
X_std = sm.add_constant(X_std)
modelo_std = sm.OLS(y, X_std).fit()
coef_std = modelo_std.params.drop("const").sort_values()

fig, ax = plt.subplots(figsize=(7, 4.5))
colors = ["#C0392B" if v < 0 else "#2471A3" for v in coef_std.values]
ax.barh(coef_std.index, coef_std.values, color=colors)
ax.set_xlabel("Efeito padronizado no faturamento médio mensal")
ax.set_title("Importância relativa das variáveis (coeficientes padronizados)")
ax.axvline(0, color="black", linewidth=0.8)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/08_regressao_importancia.png")
plt.close()

# ---------------------------------------------------------------------
# 5. Aplicação: potencial de NOVA loja em cada cidade
# ---------------------------------------------------------------------
cidades_perfil = (lojas.groupby("cidade")
                   .agg(populacao=("populacao", "first"),
                        renda_media=("renda_media", "first"),
                        concorrentes=("concorrentes", "first"),
                        n_lojas_atuais=("loja_id", "nunique"))
                   .reset_index())
cidades_perfil["log_populacao"] = np.log(cidades_perfil["populacao"])
# Cenário: nova loja própria, 150 m², recém-aberta (0 meses)
cidades_perfil["area_m2"] = 150
cidades_perfil["idade_loja_meses"] = 0
cidades_perfil["tipo_franquia"] = 0

X_novas = sm.add_constant(
    cidades_perfil[X_cols], has_constant="add"
)
cidades_perfil["faturamento_potencial_novaloja"] = modelo.predict(X_novas).round(0)
cidades_perfil = cidades_perfil.sort_values(
    "faturamento_potencial_novaloja", ascending=False
)
cidades_perfil.to_csv(f"{OUT_DIR}/potencial_nova_loja_por_cidade.csv", index=False)

print("\n--- Potencial estimado de faturamento para NOVA loja (150m², própria, recém-aberta) ---")
print(cidades_perfil[["cidade", "n_lojas_atuais", "concorrentes",
                       "faturamento_potencial_novaloja"]].to_string(index=False))
n_negativos = (cidades_perfil["faturamento_potencial_novaloja"] < 0).sum()
if n_negativos:
    print(f"\nAVISO: {n_negativos} cidade(s) com previsão negativa — artefato de "
          f"extrapolação do modelo linear fora da faixa observada (apenas 1 loja "
          f"nesses mercados). Não deve ser lido como 'a loja dará prejuízo', e sim "
          f"como 'dado insuficiente para esses mercados pequenos'.")

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(data=cidades_perfil, y="cidade", x="faturamento_potencial_novaloja",
            ax=ax, color="#1B9E77")
ax.set_xlabel("Faturamento mensal potencial de nova loja (R$)")
ax.set_ylabel("Cidade")
ax.set_title("Potencial estimado de faturamento para nova loja, por cidade")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/09_potencial_nova_loja.png")
plt.close()

print("\nRegressão concluída. Gráficos e tabelas salvos em", OUT_DIR)
