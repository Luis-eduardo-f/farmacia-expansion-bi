"""
Projeto 3 do roteiro: Canibalização simulada — Angelim vs. Mocambinho (Teresina)
==================================================================================
Em vez de uma estimativa qualitativa ("~12% porque está longe"), este
script constrói um modelo quantitativo — um modelo gravitacional de
interação espacial (Huff, 1963) — que calcula a canibalização como
função explícita da distância e do porte dos concorrentes, e mostra
como esse número muda se a distância real for diferente da suposta.
Este é o modelo usado no estudo de caso "Drogaria Garibaldi" (nova
loja de farmácia em Teresina).

IMPORTANTE — o que é dado real e o que é estimativa:
- Preço/ticket e margem por categoria, e a renda/concorrência de Teresina
  como cidade: vêm da base da rede (vendas_remedios_expansao.csv,
  lojas_cadastro.csv) e do modelo de regressão já calibrado no script 03.
- População no raio de influência de cada bairro e a lista de concorrentes
  próximos (nome, distância, porte): não há fonte oficial por bairro em
  busca rápida (IBGE não publica população por bairro de forma direta;
  exigiria cruzar setores censitários). Uso aqui valores ILUSTRATIVOS,
  claramente marcados, e o próprio script foi escrito para que você troque
  esses números pelos reais (contagem no Google Maps + Censo por setor
  censitário do IBGE) sem mudar nada do método.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 120

DATA_DIR = "/home/claude/dashboard-remedios-expansao/data"
OUT_DIR = "/home/claude/dashboard-remedios-expansao/output"

# ---------------------------------------------------------------------
# 0. Ancorar o "gasto per capita em farmácia/mês" nos dados REAIS de
#    Teresina já calibrados no script 03, em vez de inventar um número.
#    Premissa simplificadora explícita: a participação de mercado da
#    rede ~ participação em número de lojas (5 lojas da rede entre 47
#    farmácias totais da cidade, incluindo os 42 "concorrentes").
# ---------------------------------------------------------------------
base = pd.read_csv(f"{OUT_DIR}/regressao_base_lojas.csv")
ter = base[base["cidade"] == "Teresina"]
fat_rede_teresina = ter["faturamento_medio_mensal"].sum()
n_lojas_rede = len(ter)
n_farmacias_total_teresina = ter["concorrentes"].iloc[0] + n_lojas_rede
populacao_teresina = ter["populacao"].iloc[0]

market_size_estimado = fat_rede_teresina / (n_lojas_rede / n_farmacias_total_teresina)
gasto_percapita_mes = market_size_estimado / populacao_teresina

print("=" * 70)
print("0. ANCORAGEM DO GASTO PER CAPITA (a partir da base real de Teresina)")
print("=" * 70)
print(f"Faturamento mensal da rede em Teresina (5 lojas, dado real): "
      f"R$ {fat_rede_teresina:,.0f}")
print(f"Nº de farmácias na cidade (rede + concorrentes, dado real): "
      f"{n_farmacias_total_teresina}")
print(f"Mercado total estimado (premissa: share ~ nº de lojas):    "
      f"R$ {market_size_estimado:,.0f}/mês")
print(f"Gasto per capita/mês implícito:                             "
      f"R$ {gasto_percapita_mes:.2f}")

# ---------------------------------------------------------------------
# 1. Modelo de Huff (interação espacial)
#    P_i = (S_i / D_i^beta) / sum_k(S_k / D_k^beta)
#    S = tamanho/atratividade da loja (aqui: área em m²)
#    D = distância até o cliente médio da área de influência (km)
#    beta = sensibilidade à distância (2.0 é o valor clássico de Huff)
# ---------------------------------------------------------------------
def huff_market_share(area_nova, dist_nova, concorrentes, beta=2.0):
    """concorrentes: lista de (nome, area_m2, distancia_km)."""
    atração_nova = area_nova / dist_nova**beta
    atração_total = atração_nova + sum(a / d**beta for _, a, d in concorrentes)
    return atração_nova / atração_total

def simular_ponto(nome, populacao_influencia, area_nova, dist_nova,
                   concorrentes, gasto_percapita, beta=2.0):
    share = huff_market_share(area_nova, dist_nova, concorrentes, beta)
    mercado_total_area = populacao_influencia * gasto_percapita
    faturamento_bruto = mercado_total_area * share

    # Canibalização: fração do faturamento da nova loja que teria vindo
    # especificamente da(s) loja(s) "Pague Menos" identificada(s), e não
    # de demanda nova/outros concorrentes.
    atração_nova = area_nova / dist_nova**beta
    atração_pague_menos = sum(a / d**beta for nm, a, d in concorrentes
                               if "pague menos" in nm.lower())
    atração_total = atração_nova + sum(a / d**beta for _, a, d in concorrentes)
    # fração do mercado que ERA da Pague Menos e migra para a nova loja
    pct_canibalizacao = (atração_nova * atração_pague_menos) / (atração_total ** 2) \
                         / share if share > 0 else 0

    return {
        "ponto": nome,
        "market_share_pct": round(share * 100, 2),
        "faturamento_bruto_mensal": round(faturamento_bruto, 0),
        "pct_canibalizacao_pague_menos": round(pct_canibalizacao * 100, 2),
        "faturamento_liquido_novo_mercado": round(
            faturamento_bruto * (1 - pct_canibalizacao), 0),
    }

# ---------------------------------------------------------------------
# 2. Inputs dos dois pontos — ILUSTRATIVOS onde não há fonte oficial
#    (ver cabeçalho do arquivo). Troque por dados de campo antes de
#    decidir de verdade.
# ---------------------------------------------------------------------
AREA_NOVA_LOJA = 120  # m², conforme cenário do usuário

pontos = {
    "Angelim": dict(
        populacao_influencia=17000,   # ILUSTRATIVO — bairro consolidado, zona leste
        dist_nova=0.3,                # km até o centro da área de influência
        concorrentes=[
            ("Pague Menos - Av. principal", 200, 0.7),
            ("Drogasil - próxima", 180, 0.9),
            ("Farmácia independente A", 80, 0.4),
        ],
    ),
    "Mocambinho": dict(
        populacao_influencia=15500,   # ILUSTRATIVO — zona norte, comércio em expansão
        dist_nova=0.3,
        concorrentes=[
            ("Pague Menos - avenida nova centralidade", 200, 0.6),
            ("Farmácia independente B", 90, 0.5),
            ("Farmácia independente C", 70, 1.0),
        ],
    ),
}

resultados = [
    simular_ponto(nome, p["populacao_influencia"], AREA_NOVA_LOJA, p["dist_nova"],
                  p["concorrentes"], gasto_percapita_mes)
    for nome, p in pontos.items()
]
df_resultados = pd.DataFrame(resultados)
df_resultados.to_csv(f"{OUT_DIR}/huff_comparacao_pontos.csv", index=False)

print("\n" + "=" * 70)
print("2. COMPARAÇÃO ANGELIM vs. MOCAMBINHO (modelo de Huff, beta=2.0)")
print("=" * 70)
print(df_resultados.to_string(index=False))

# ---------------------------------------------------------------------
# 3. Gráfico comparativo
# ---------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
sns.barplot(data=df_resultados, x="ponto", y="faturamento_bruto_mensal",
            ax=axes[0], color="#2471A3")
axes[0].set_title("Faturamento potencial bruto (R$/mês)")
axes[0].set_xlabel("")
axes[0].set_ylabel("R$/mês")
for i, v in enumerate(df_resultados["faturamento_bruto_mensal"]):
    axes[0].text(i, v + 300, f"{v:,.0f}", ha="center")

sns.barplot(data=df_resultados, x="ponto", y="pct_canibalizacao_pague_menos",
            ax=axes[1], color="#C0392B")
axes[1].set_title("% do faturamento vindo da Pague Menos (canibalização)")
axes[1].set_xlabel("")
axes[1].set_ylabel("% canibalização")
for i, v in enumerate(df_resultados["pct_canibalizacao_pague_menos"]):
    axes[1].text(i, v + 0.3, f"{v:.1f}%", ha="center")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/13_huff_comparacao_pontos.png")
plt.close()

# ---------------------------------------------------------------------
# 4. Sensibilidade: como a canibalização muda com a distância até a
#    Pague Menos mais próxima — é essa curva que torna o número
#    "mais preciso" (explícito e verificável) em vez de um chute fixo.
# ---------------------------------------------------------------------
distancias = np.arange(0.2, 2.01, 0.1)
curvas = {}
for nome, p in pontos.items():
    concorrentes = p["concorrentes"]
    outros = [c for c in concorrentes if "pague menos" not in c[0].lower()]
    area_pm = next(a for nm, a, d in concorrentes if "pague menos" in nm.lower())
    pct = []
    for d_pm in distancias:
        conc_variavel = outros + [("Pague Menos", area_pm, d_pm)]
        r = simular_ponto(nome, p["populacao_influencia"], AREA_NOVA_LOJA,
                           p["dist_nova"], conc_variavel, gasto_percapita_mes)
        pct.append(r["pct_canibalizacao_pague_menos"])
    curvas[nome] = pct

fig, ax = plt.subplots(figsize=(8, 5))
for nome, pct in curvas.items():
    ax.plot(distancias, pct, marker="o", markersize=3, label=nome)
ax.set_xlabel("Distância até a Pague Menos mais próxima (km)")
ax.set_ylabel("% de canibalização estimada")
ax.set_title("Sensibilidade: canibalização vs. distância ao concorrente")
ax.legend()
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/14_huff_sensibilidade_distancia.png")
plt.close()

print("\nGráficos salvos em", OUT_DIR)
print("\nLEMBRETE: população de influência e lista de concorrentes são "
      "ilustrativas. Substitua por contagem real (Google Maps) e, se possível, "
      "população do setor censitário do IBGE antes de decidir.")
