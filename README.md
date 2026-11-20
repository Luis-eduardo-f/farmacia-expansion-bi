# farmacia-expansion-bi

> 🚧 **Status: em construção.** Este README descreve o escopo e a abordagem planejada; notebooks e dashboard serão adicionados conforme o projeto avança.

Dashboard e estudo analítico de **inteligência de expansão** para uma rede de farmácias: identifica onde abrir novas lojas e qual o impacto esperado sobre as unidades já existentes.

*(Projeto de portfólio com dados fictícios/sintéticos — cenário ilustrativo "Drogaria Garibaldi", Teresina/PI.)*

---

## 🎯 Problema de negócio

Antes de abrir uma nova loja, uma rede de farmácias precisa responder: **essa região tem potencial de faturamento suficiente, e o quanto essa nova loja vai "roubar" vendas das lojas vizinhas (canibalização)?**

## 🔎 Abordagem analítica

1. **EDA (Análise Exploratória):** vendas por região, sazonalidade e perfil de demanda por categoria de produto.
2. **Regressão de potencial de faturamento:** estimativa do faturamento esperado para um novo ponto, a partir de variáveis socioeconômicas e de concorrência da região.
3. **Clustering de perfil de lojas:** agrupamento das unidades existentes por padrão de consumo e porte, para comparar uma nova praça com lojas "parecidas" já em operação.
4. **Modelo de canibalização (Huff):** aplicação do **Modelo de Huff** (gravitacional de atração de clientes) para estimar quanto uma nova loja desvia de faturamento das lojas próximas, com base em distância e atratividade relativa.
5. **Dashboard interativo:** consolidação dos resultados em um painel para simular cenários de expansão.

## 📊 Entregas planejadas

* [ ] Ranking de regiões por potencial de faturamento.
* [ ] Clusters de lojas por perfil de consumo.
* [ ] Estimativa de canibalização por cenário de nova loja (estudo de caso "Drogaria Garibaldi").
* [ ] Dashboard interativo para explorar os cenários.

## 🛠️ Stack

* **Linguagem:** Python (`pandas`, `scikit-learn`, `statsmodels`)
* **Visualização / Dashboard:** Plotly / Dash
* **Métodos:** Regressão, Clustering (k-means), Modelo de Huff

## 📁 Estrutura

```
farmacia-expansion-bi/
├── data/                  # Dados sintéticos de entrada
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_regressao_potencial.ipynb
│   ├── 03_clustering_lojas.ipynb
│   └── 04_modelo_huff.ipynb
├── dashboard/              # App do dashboard interativo
└── README.md
```

## ▶️ Como executar (quando o código estiver disponível)

```bash
git clone https://github.com/Luis-eduardo-f/farmacia-expansion-bi.git
cd farmacia-expansion-bi
pip install -r requirements.txt
python dashboard/app.py
```

## 📌 Próximos passos

* Implementar o notebook de EDA (`01_eda.ipynb`).
* Adicionar mais cenários de expansão além de "Drogaria Garibaldi".
* Publicar o estudo de caso completo (com visualizações) também no LinkedIn.
