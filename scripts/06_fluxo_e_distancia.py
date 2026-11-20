"""
Extensão do modelo de Huff (script 05): incorpora FLUXO (proximidade a
geradores de tráfego de pedestres — feira, terminal de ônibus, UBS, escola,
comércio de rua forte) e exibe explicitamente a distância a cada concorrente.

Antes: atratividade da loja = área (m²).
Agora:  atratividade = área (m²) × fator_fluxo
  fator_fluxo = 1 + 0,15 por gerador de fluxo relevante a até 300 m.

IMPORTANTE: a presença/distância de cada gerador de fluxo abaixo é
ILUSTRATIVA (mesma ressalva dos scripts anteriores) — não confirmada em
campo. Troque a tabela GERADORES_FLUXO pelos dados reais (Google Maps /
visita local) antes de decidir.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 120

OUT_DIR = "/home/claude/dashboard-remedios-expansao/output"
AREA_NOVA_LOJA = 120

# ---------------------------------------------------------------------
# 1. Concorrentes (mesma lista do script 05) — tabela explícita de
#    distância, pedida pelo usuário.
# ---------------------------------------------------------------------
concorrentes_por_ponto = {
    "Angelim": [
        ("Pague Menos - Av. principal", 200, 0.7),
        ("Drogasil - próxima", 180, 0.9),
        ("Farmácia independente A", 80, 0.4),
    ],
    "Mocambinho": [
        ("Pague Menos - avenida nova centralidade", 200, 0.6),
        ("Farmácia independente B", 90, 0.5),
        ("Farmácia independente C", 70, 1.0),
    ],
}

tab_concorrentes = pd.DataFrame(
    [(ponto, nome, area, dist) for ponto, lista in concorrentes_por_ponto.items()
     for nome, area, dist in lista],
    columns=["ponto", "concorrente", "area_m2", "distancia_km"]
).sort_values(["ponto", "distancia_km"])
tab_concorrentes.to_csv(f"{OUT_DIR}/distancia_concorrentes.csv", index=False)
print("=" * 70)
print("1. DISTÂNCIA DA LOJA NOVA A CADA CONCORRENTE (ilustrativo)")
print("=" * 70)
print(tab_concorrentes.to_string(index=False))

# ---------------------------------------------------------------------
# 2. Geradores de fluxo (ILUSTRATIVO) — presença a até 300 m do ponto
# ---------------------------------------------------------------------
GERADORES_FLUXO = {
    "Angelim": {
        "comércio de rua forte": True,
        "escola": True,
        "UBS": False,
        "terminal de ônibus": False,
        "feira": False,
    },
    "Mocambinho": {
        "comércio de rua forte (nova centralidade)": True,
        "feira/comércio informal": True,
        "UBS": True,
        "escola": False,
        "terminal de ônibus": False,
    },
}

tab_fluxo = pd.DataFrame(
    [(ponto, gerador, presente) for ponto, geradores in GERADORES_FLUXO.items()
     for gerador, presente in geradores.items()]
)
tab_fluxo.columns = ["ponto", "gerador_de_fluxo", "presente_300m"]
tab_fluxo.to_csv(f"{OUT_DIR}/geradores_fluxo.csv", index=False)

fator_fluxo = {
    ponto: 1 + 0.15 * sum(geradores.values())
    for ponto, geradores in GERADORES_FLUXO.items()
}
print("\n" + "=" * 70)
print("2. FATOR DE FLUXO (ilustrativo, 1 + 0,15 por gerador a até 300 m)")
print("=" * 70)
for ponto, fator in fator_fluxo.items():
    n_geradores = sum(GERADORES_FLUXO[ponto].values())
    print(f"{ponto}: {n_geradores} geradores presentes -> fator = {fator:.2f}x")

# ---------------------------------------------------------------------
# 3. Recalcular o Huff com atratividade = área × fator_fluxo
# ---------------------------------------------------------------------
def huff_share_com_fluxo(area_nova, dist_nova, fator_fluxo_novo, concorrentes, beta=2.0):
    atração_nova = (area_nova * fator_fluxo_novo) / dist_nova**beta
    atração_total = atração_nova + sum(a / d**beta for _, a, d in concorrentes)
    return atração_nova / atração_total, atração_nova, atração_total

resultados = []
for ponto, concorrentes in concorrentes_por_ponto.items():
    dist_nova = 0.3
    share_sem_fluxo, _, _ = huff_share_com_fluxo(AREA_NOVA_LOJA, dist_nova, 1.0, concorrentes)
    share_com_fluxo, atr_nova, atr_total = huff_share_com_fluxo(
        AREA_NOVA_LOJA, dist_nova, fator_fluxo[ponto], concorrentes)

    atração_pm = sum(a / d**2 for nm, a, d in concorrentes if "pague menos" in nm.lower())
    pct_canibalizacao = (atr_nova * atração_pm) / (atr_total ** 2) / share_com_fluxo

    resultados.append({
        "ponto": ponto,
        "market_share_sem_fluxo_pct": round(share_sem_fluxo * 100, 1),
        "market_share_com_fluxo_pct": round(share_com_fluxo * 100, 1),
        "ganho_de_participacao_pp": round((share_com_fluxo - share_sem_fluxo) * 100, 1),
        "pct_canibalizacao_pague_menos": round(pct_canibalizacao * 100, 1),
    })

df_resultados = pd.DataFrame(resultados)
df_resultados.to_csv(f"{OUT_DIR}/huff_com_fluxo.csv", index=False)
print("\n" + "=" * 70)
print("3. EFEITO DO FLUXO NA PARTICIPAÇÃO DE MERCADO (modelo de Huff)")
print("=" * 70)
print(df_resultados.to_string(index=False))

# ---------------------------------------------------------------------
# 4. Gráfico: participação sem fluxo vs. com fluxo, por ponto
# ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 5))
x = range(len(df_resultados))
width = 0.35
ax.bar([i - width/2 for i in x], df_resultados["market_share_sem_fluxo_pct"],
       width, label="Sem fluxo (só área e distância)", color="#95A5A6")
ax.bar([i + width/2 for i in x], df_resultados["market_share_com_fluxo_pct"],
       width, label="Com fluxo (geradores a até 300m)", color="#1B9E77")
ax.set_xticks(list(x))
ax.set_xticklabels(df_resultados["ponto"])
ax.set_ylabel("Participação de mercado estimada (%)")
ax.set_title("Efeito do fluxo de pedestres na participação de mercado")
ax.legend()
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/15_fluxo_efeito_market_share.png")
plt.close()

print("\nArquivos salvos:")
print(" -", f"{OUT_DIR}/distancia_concorrentes.csv")
print(" -", f"{OUT_DIR}/geradores_fluxo.csv")
print(" -", f"{OUT_DIR}/huff_com_fluxo.csv")
print(" -", f"{OUT_DIR}/15_fluxo_efeito_market_share.png")
print("\nLEMBRETE: geradores de fluxo e distâncias são ilustrativos — confirme no "
      "Google Maps/visita local antes de decidir.")
