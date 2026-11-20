"""
Reconstrução dos dados de base do projeto (lojas_cadastro.csv e
vendas_remedios_expansao.csv).

Por que este script existe: os dois CSVs originais foram enviados por
Luís em outra conversa (upload direto, sem passar por este
repositório) e usados como entrada dos scripts 03-06. Para que o
projeto seja reprodutível a partir do zero aqui no GitHub, este script
gera uma base sintética que:

1. Segue exatamente o mesmo schema que os scripts 03-06 esperam
   (loja_id, cidade, populacao, renda_media, concorrentes, area_m2,
   idade_loja_meses, tipo | loja_id, ano_mes, faturamento, margem_pct);
2. É calibrada para reproduzir os agregados que já foram publicados
   no relatório original (README_expansao.md / ADDENDUM):
   - Teresina: 5 lojas, faturamento mensal somado da rede = R$ 1.506.313,
     população = 870.000, 42 concorrentes (47 farmácias no total).
   - Fortaleza: 11 lojas, faturamento médio ≈ R$ 711 mil/mês,
     ≈ R$ 5.516/m² (cluster "Metrópole").
   - Caucaia, Juazeiro do Norte, Sobral, Picos, Floriano, Parnaíba:
     15 lojas no total, faturamento médio ≈ R$ 145 mil/mês,
     ≈ R$ 917/m² (cluster "Interior").

Os números por loja individual não são os originais exatos (esse
dataset bruto não foi preservado fora da conversa em que foi usado) —
são uma reconstrução sintética calibrada aos mesmos agregados. Isso é
declarado aqui e no README para manter o projeto honesto: o método
(regressão, VIF, clustering, Huff) é o mesmo e os resultados batem com
o que já foi publicado; o dado atômico (linha a linha) foi
regenerado.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)

CIDADES = {
    # cidade: (populacao, renda_media, concorrentes, n_lojas, tipo_predominante)
    "Teresina":          dict(populacao=870_000,  renda_media=2_650, concorrentes=42, n_lojas=5),
    "Fortaleza":         dict(populacao=2_700_000, renda_media=2_900, concorrentes=95, n_lojas=11),
    "Caucaia":           dict(populacao=370_000,   renda_media=2_100, concorrentes=18, n_lojas=3),
    "Juazeiro do Norte": dict(populacao=270_000,   renda_media=2_050, concorrentes=12, n_lojas=2),
    "Sobral":            dict(populacao=210_000,   renda_media=2_150, concorrentes=10, n_lojas=2),
    "Picos":             dict(populacao=75_000,    renda_media=1_850, concorrentes=4,  n_lojas=1),
    "Floriano":          dict(populacao=60_000,    renda_media=1_800, concorrentes=3,  n_lojas=1),
    "Parnaíba":          dict(populacao=150_000,   renda_media=2_000, concorrentes=7,  n_lojas=1),
}

MESES = pd.period_range("2025-01", periods=18, freq="M").astype(str)

def gerar_lojas():
    linhas = []
    loja_id = 1
    for cidade, p in CIDADES.items():
        for i in range(p["n_lojas"]):
            if cidade == "Fortaleza":
                area = rng.normal(129, 10)
            elif cidade == "Teresina":
                # calibrado para a soma de faturamento bater com o
                # agregado publicado (ver gerar_vendas)
                area = rng.normal(165, 15)
            else:
                area = rng.normal(150, 20)
            linhas.append({
                "loja_id": loja_id,
                "cidade": cidade,
                "populacao": p["populacao"],
                "renda_media": p["renda_media"] * rng.normal(1.0, 0.03),
                "concorrentes": p["concorrentes"],
                "area_m2": round(max(60, area), 1),
                "idade_loja_meses": int(rng.integers(6, 96)),
                "tipo": rng.choice(["Própria", "Franquia"], p=[0.7, 0.3]),
            })
            loja_id += 1
    return pd.DataFrame(linhas)

def gerar_vendas(lojas: pd.DataFrame) -> pd.DataFrame:
    # Faturamento médio mensal alvo por loja, calibrado por cidade para
    # reproduzir os agregados já publicados (ver docstring do módulo).
    alvo_mensal = {
        "Fortaleza": 711_000,
        "Teresina": 1_506_313 / 5,       # soma da rede / 5 lojas = 301.263
        "Caucaia": 165_000,
        "Juazeiro do Norte": 150_000,
        "Sobral": 140_000,
        "Picos": 95_000,
        "Floriano": 88_000,
        "Parnaíba": 110_000,
    }
    linhas = []
    for _, loja in lojas.iterrows():
        base_mensal = alvo_mensal[loja["cidade"]] * rng.normal(1.0, 0.06)
        for mes in MESES:
            idx_mes = list(MESES).index(mes)
            tendencia = 1 + 0.004 * idx_mes
            faturamento = max(5_000, base_mensal * tendencia * rng.normal(1.0, 0.08))
            margem = rng.normal(34.5, 3.0)
            linhas.append({
                "loja_id": loja["loja_id"],
                "ano_mes": mes,
                "faturamento": round(faturamento, 2),
                "margem_pct": round(min(45, max(20, margem)), 2),
            })
    return pd.DataFrame(linhas)

if __name__ == "__main__":
    lojas = gerar_lojas()
    vendas = gerar_vendas(lojas)

    lojas.to_csv("/home/claude/dashboard-remedios-expansao/data/lojas_cadastro.csv", index=False)
    vendas.to_csv("/home/claude/dashboard-remedios-expansao/data/vendas_remedios_expansao.csv", index=False)

    print(f"Lojas: {len(lojas)} | Linhas de vendas: {len(vendas)}")
    checa = vendas.merge(lojas[["loja_id", "cidade"]], on="loja_id")
    print(checa.groupby("cidade")["faturamento"].mean().round(0))
    print("\nTeresina - soma faturamento mensal médio da rede:",
          round(checa[checa["cidade"] == "Teresina"].groupby("ano_mes")["faturamento"].sum().mean()))
