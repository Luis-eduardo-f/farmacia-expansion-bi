# Estudo de caso — Drogaria Garibaldi: canibalização quantitativa (Angelim vs. Mocambinho, Teresina)

Substitui um número único estimado por intuição ("~12% porque está
longe") por um **modelo de interação espacial (Huff, 1963)**: a
canibalização passa a ser calculada a partir da distância e do porte dos
concorrentes, não estimada "no olho".

> **O que é dado real e o que é estimativa — leia antes dos números:**
> o gasto per capita em farmácia usado aqui foi **derivado da base da
> rede em Teresina** (faturamento das 5 lojas da rede ÷ participação
> estimada de mercado). Já a **população no raio de influência** de
> cada bairro e a **lista de concorrentes com distância** são
> ilustrativas — não há população por bairro nem geolocalização de
> farmácias publicamente disponível em busca rápida (exigiria cruzar
> setor censitário do IBGE ou contagem no Google Maps). O
> `scripts/05_canibalizacao_huff.py` foi escrito para você trocar esses
> números pelos reais sem mudar o método.

## Resumo executivo

| Métrica | Angelim | Mocambinho |
|---|---|---|
| Participação de mercado da nova loja (Huff) | ≈54% | ≈57–58% |
| % do faturamento vindo da Pague Menos (canibalização) | **≈16,6%** | **≈24,0%** |
| Faturamento líquido de mercado novo | **maior** | menor |

**Recomendação direcional:** entre os dois pontos, **Angelim sai na
frente** no critério que mais importa — não o faturamento bruto (os dois
são parecidos), mas a canibalização: Angelim rouba proporcionalmente
menos da Pague Menos, porque no cenário ilustrativo a Pague Menos de
referência está um pouco mais distante (0,7 km vs. 0,6 km) e há mais
concorrentes pequenos dividindo a demanda. Isso é direcional, não
definitivo — depende dos inputs reais que faltam (ver Limitações).

**Extensão com fluxo de pedestres** (`scripts/06_fluxo_e_distancia.py`):
ao incorporar geradores de fluxo (feira, UBS, escola, terminal, comércio
de rua forte) a até 300 m de cada ponto como multiplicador de
atratividade, a participação de mercado sobe nos dois pontos — mais no
Mocambinho (mais geradores no cenário ilustrativo) do que no Angelim — o
que reduz a vantagem do Angelim, mas não inverte a recomendação.

## Metodologia

**Modelo de Huff:** a probabilidade/participação de um cliente escolher a
loja *i* entre *n* opções é proporcional ao tamanho da loja e inversamente
proporcional à distância elevada a um expoente de sensibilidade (β=2,
valor clássico da literatura de varejo):

```
P_i = (Área_i / Distância_i^β) / Σ_k (Área_k / Distância_k^β)
```

**Canibalização sobre a Pague Menos** = fração do faturamento da loja nova
que, pelo modelo, "viria" especificamente da atração perdida pela Pague
Menos (não de outros concorrentes nem de demanda nova do bairro).

**Gasto per capita (ancoragem nos dados da rede):** faturamento mensal da
rede em Teresina ÷ participação de mercado estimada (nº de lojas da rede
÷ nº total de farmácias da cidade) ÷ população de Teresina. Premissa
simplificadora: participação de mercado ∝ nº de lojas (na ausência de
dado melhor).

**Fator de fluxo** (`scripts/06_fluxo_e_distancia.py`): atratividade =
área × (1 + 0,15 por gerador de fluxo relevante a até 300 m) — um ajuste
simples e explícito, fácil de recalibrar.

**Análise de sensibilidade** (`14_huff_sensibilidade_distancia.png`):
mostra como a % de canibalização muda se a Pague Menos mais próxima
estiver entre 0,2 km e 2,0 km — em vez de fixar a distância, a curva
inteira fica visível, para ler o número certo quando a distância real for
confirmada.

## Arquivos gerados

```
scripts/05_canibalizacao_huff.py        (modelo reutilizável — edite os
                                          dicionários "pontos" com dados reais)
scripts/06_fluxo_e_distancia.py         (extensão com fluxo de pedestres)
output/huff_comparacao_pontos.csv
output/huff_com_fluxo.csv
output/distancia_concorrentes.csv
output/geradores_fluxo.csv
output/13_huff_comparacao_pontos.png    (faturamento bruto + % canibalização)
output/14_huff_sensibilidade_distancia.png
output/15_fluxo_efeito_market_share.png
```

## Limitações e próximos passos

- População no raio de influência e a lista de concorrentes (distâncias)
  são **ilustrativas** — validar com contagem real no Google Maps e, se
  possível, dados do setor censitário do IBGE antes de decidir.
- O resultado é **muito sensível à distância** até a Pague Menos mais
  próxima: pequenas mudanças nesse número alteram bastante a
  canibalização estimada — ver gráfico de sensibilidade.
- Próximo passo prático: ir ao Google Maps, contar farmácias
  (principalmente Pague Menos, Drogasil, Drogaria Globo) em raio de 1 km
  dos dois pontos e medir a distância real até a nova loja proposta, e
  então rodar os scripts de novo com os números reais.
