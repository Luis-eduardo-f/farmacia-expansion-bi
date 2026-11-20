# Dashboard de Inteligência de Expansão — Rede de Farmácias

Projeto de portfólio em Ciência de Dados/BI: dado o cadastro e as vendas de
uma rede de farmácias fictícia em 8 cidades do Nordeste, três modelos
respondem três perguntas de expansão: **onde investir** (regressão),
**como a rede se segmenta** (clustering) e **quanto uma nova loja
canibalizaria a rede já instalada** (modelo de Huff) — este último é o
estudo de caso **"Drogaria Garibaldi"** (nova farmácia em Teresina).

> **Sobre os dados:** o cadastro de lojas e o histórico de vendas
> (`data/*.csv`) são uma base **sintética**, gerada por
> `scripts/00_gerar_dados.py` e calibrada para reproduzir os agregados
> já publicados neste estudo (ex.: faturamento da rede em Teresina,
> faturamento médio e R$/m² dos clusters "Fortaleza" e "Interior"). A
> base linha-a-linha original não ficou preservada fora da conversa em
> que os modelos foram construídos pela primeira vez — os números
> aqui reproduzem a mesma estrutura e as mesmas conclusões, mas não
> são idênticos valor a valor ao histórico original. O **método**
> (regressão OLS + VIF, clustering K-Means + PCA, modelo gravitacional
> de Huff) é o que importa para o portfólio, e é o mesmo.

---

## Resumo executivo

### 1. O que mais explica o faturamento de uma loja?

Regressão linear (OLS) com faturamento médio mensal como alvo e população
da cidade, renda média, nº de concorrentes, área da loja, idade da loja e
tipo (própria/franquia) como variáveis explicativas. O modelo explica a
maior parte da variação de faturamento entre as 26 lojas, mas a variável
mais confiável é o **nº de concorrentes na cidade** (proxy de tamanho de
mercado) — as demais variáveis, isoladamente, não têm efeito que se possa
afirmar com confiança nesta amostra.

**Achado que exige atenção antes de agir:** população, renda e nº de
concorrentes andam juntos nestes dados — cidades grandes são também as
mais ricas e mais competitivas (VIF alto para essas três variáveis). Isso
faz o modelo "confundir" o efeito de cada uma isoladamente. Para decisão
de expansão, o resultado confiável é o conjunto população+renda+concorrência
= "tamanho de mercado", não cada variável isolada.

### 2. Potencial de uma nova loja, por cidade

Simulando uma loja nova padrão (150 m², recém-aberta, própria) em cada
cidade (`output/potencial_nova_loja_por_cidade.csv`): Fortaleza e Teresina
seguem como prioridade óbvia de expansão (mercado grande, dado mais
confiável); Caucaia e Juazeiro do Norte são a aposta de segunda linha;
cidades com apenas 1 loja de referência (Picos, Floriano, Parnaíba) têm
previsão de maior incerteza — tratar como direcional, não como número
definitivo.

### 3. A rede se comporta como um ou vários perfis de loja?

O agrupamento (K-Means) das 26 lojas por perfil (mercado + loja +
desempenho) aponta, pela silhueta, **k=2** como ótimo estatístico:

- **Grupo "Metrópole"** (11 lojas, todas em Fortaleza): faturamento e
  R$/m² muito acima da média da rede.
- **Grupo "Interior"** (15 lojas: Teresina, Caucaia, Juazeiro, Sobral,
  Picos, Floriano, Parnaíba): faturamento e R$/m² bem menores — cidades
  de porte populacional bem diferente entre si caem no mesmo cluster, ou
  seja, a distância para o padrão "Fortaleza" pesa mais do que as
  diferenças de porte dentro do interior.

### 4. Estudo de caso — Drogaria Garibaldi (Angelim x Mocambinho, Teresina)

Ver **`ADDENDUM_canibalizacao.md`** para o detalhe completo. Resumo:
usando um modelo de Huff (gravitacional) com o gasto per capita ancorado
no faturamento real da rede em Teresina, **Angelim canibaliza menos a
Pague Menos (≈16,6%) do que Mocambinho (≈24,0%)** — e segue na frente
mesmo depois de incorporar fatores de fluxo de pedestres (feira, UBS,
escola, comércio de rua) nos dois pontos.

---

## Seção técnica

**Stack:** Python · pandas · NumPy · statsmodels (OLS, VIF) · scikit-learn
(KMeans, PCA, silhueta) · matplotlib/seaborn

### Regressão (`scripts/03_regressao_potencial.py`)
- Unidade de análise: loja (n = 26), alvo = faturamento médio mensal.
- Preditores: `log(população)`, `renda_média`, `concorrentes`, `area_m2`,
  `idade_loja_meses`, `tipo_franquia` (dummy).
- **Diagnóstico de multicolinearidade (VIF):** `concorrentes` e
  `log_população` muito acima do limite de alerta (5–10), confirmando
  que essas variáveis (junto com `renda_média`) medem essencialmente a
  mesma dimensão latente ("tamanho do mercado") — ver
  `06b_correlacao_preditores.png`.
- Diagnóstico previsto-vs-real e resíduos (`07_regressao_diagnostico.png`).
- Aplicação (`09_potencial_nova_loja.png`,
  `potencial_nova_loja_por_cidade.csv`): previsão fora da amostra para
  cidades com poucas lojas tem incerteza alta — tratar como direcional.

### Clustering (`scripts/04_clustering_lojas.py`)
- Features padronizadas (StandardScaler): renda, concorrentes, população,
  área, idade, faturamento médio, faturamento/m², margem.
- Seleção de k por silhueta sobre k=2..6 (`10_clustering_elbow_silhueta.png`).
- Visualização via PCA 2D (`11_clustering_pca.png`) e comparação de
  faturamento por cluster (`12_clustering_faturamento.png`).

### Canibalização / Huff (`scripts/05_canibalizacao_huff.py` e
`scripts/06_fluxo_e_distancia.py`)
- Ver `ADDENDUM_canibalizacao.md` para a metodologia completa.

## Estrutura do repositório

```
dashboard-remedios-expansao/   (conteúdo deste repositório)
├── README_expansao.md                 (este arquivo)
├── ADDENDUM_canibalizacao.md          (estudo de caso Drogaria Garibaldi)
├── data/
│   ├── lojas_cadastro.csv
│   └── vendas_remedios_expansao.csv
├── scripts/
│   ├── 00_gerar_dados.py              (gera a base sintética calibrada)
│   ├── 03_regressao_potencial.py
│   ├── 04_clustering_lojas.py
│   ├── 05_canibalizacao_huff.py
│   └── 06_fluxo_e_distancia.py
└── output/                            (gerado ao rodar os scripts)
    ├── regressao_* / clustering_* / huff_* / potencial_* / *.png
```

**Para reproduzir:**
```
pip install pandas numpy statsmodels scikit-learn matplotlib seaborn
python scripts/00_gerar_dados.py
python scripts/03_regressao_potencial.py
python scripts/04_clustering_lojas.py
python scripts/05_canibalizacao_huff.py
python scripts/06_fluxo_e_distancia.py
```
(os scripts 04, 05 e 06 dependem do `output/regressao_base_lojas.csv`
gerado pelo 03, então a ordem importa.)
