# farmacia-expansion-bi

Dashboard e estudo analítico de inteligência de expansão para uma rede de farmácias: identifica onde abrir novas lojas e qual o impacto esperado sobre as unidades já existentes.

(Projeto de portfólio com dados fictícios/sintéticos — cenário ilustrativo "Drogaria Garibaldi", Teresina/PI.)

**Ver [`README_expansao.md`](README_expansao.md) para o resumo executivo completo e [`ADDENDUM_canibalizacao.md`](ADDENDUM_canibalizacao.md) para o estudo de caso de canibalização.**

## 🎯 Problema de negócio

Antes de abrir uma nova loja, uma rede de farmácias precisa responder: essa região tem potencial de faturamento suficiente, e o quanto essa nova loja vai "roubar" vendas das lojas vizinhas (canibalização)?

## 🔎 Abordagem analítica

- **Geração de dados sintéticos** (`scripts/00_gerar_dados.py`): base calibrada para reproduzir os agregados publicados do estudo original.
- **Regressão de potencial de faturamento** (`scripts/03_regressao_potencial.py`): estimativa do faturamento esperado para um novo ponto, com diagnóstico de multicolinearidade (VIF).
- **Clustering de perfil de lojas** (`scripts/04_clustering_lojas.py`): agrupamento das unidades existentes (K-Means + PCA) por padrão de consumo e porte.
- **Modelo de canibalização — Huff** (`scripts/05_canibalizacao_huff.py`): modelo gravitacional de interação espacial para estimar quanto uma nova loja desvia de faturamento das lojas próximas.
- **Extensão de fluxo de pedestres** (`scripts/06_fluxo_e_distancia.py`): incorpora geradores de tráfego (feira, UBS, escola, comércio) ao modelo de Huff.

## 🛠️ Stack

- Linguagem: Python (pandas, NumPy, statsmodels, scikit-learn)
- Visualização: matplotlib / seaborn

## 📁 Estrutura

```
farmacia-expansion-bi/
├── README_expansao.md                 (resumo executivo completo)
├── ADDENDUM_canibalizacao.md          (estudo de caso Drogaria Garibaldi)
├── data/
│   ├── lojas_cadastro.csv
│   └── vendas_remedios_expansao.csv
├── scripts/
│   ├── 00_gerar_dados.py
│   ├── 03_regressao_potencial.py
│   ├── 04_clustering_lojas.py
│   ├── 05_canibalizacao_huff.py
│   └── 06_fluxo_e_distancia.py
└── output/                            (gerado ao rodar os scripts)
```

## ▶️ Como executar

```
git clone https://github.com/Luis-eduardo-f/farmacia-expansion-bi.git
cd farmacia-expansion-bi
pip install pandas numpy statsmodels scikit-learn matplotlib seaborn
python scripts/00_gerar_dados.py
python scripts/03_regressao_potencial.py
python scripts/04_clustering_lojas.py
python scripts/05_canibalizacao_huff.py
python scripts/06_fluxo_e_distancia.py
```

(os scripts 04, 05 e 06 dependem do `output/regressao_base_lojas.csv` gerado pelo 03, então a ordem importa.)
