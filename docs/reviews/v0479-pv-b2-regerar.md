---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-b2-regerar
commit: c5815650ef8c81b24ca7d466b7a23f04239458b6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E57.44 (PR-VERDE B2, regerador)

Diff `ed5bfa02..c5815650`: `bin/forge-testes` (+76, modo `--regerar`), `tests/test_testes_tocados.py` (classe `Regerar`, 11 testes), duas specs de mutantes (16 guardas) e o fragmento do changelog. Abaixo do teto H1.

## Achados
- A1 (recomendado) bin/forge-testes:1015 · arquivo novo não versionado em bin/ dispara o índice, mas scripts/indice-forge.py:33 lê só `git ls-files`: sonda (bin/forge-x sem `git add`) deu `regerar rc=0 (índice do Forge)` com o índice sem a linha. Avisar quando a fonte é não versionada, ou pedir o `git add` antes.

## Parecer
Aprovado. Faz o que o desenho pede (`docs/propostas/v0479-pr-verde-de-primeira.md`, B2): lista fechada `DERIVADOS` com o índice e os pesos, geradores existentes chamados com `-I` e ambiente sem `GIT_*`/`FORGE_*`, recusa de link no derivado e na pasta antes de rodar o gerador, e conferência por fotografia do `git status` antes e depois (sai 2 se algo fora da lista mudou, inclusive arquivo de controle ou arquivo já sujo reescrito). Os mapas do `forge-testes` ficam fora, conforme a decisão de 17:58 no pedido. O `--regerar` só combina com `--base`, igual ao `--registros`.

Testes: os geradores falsos reprovam o ambiente herdado (AR-4) e só aceitam os argumentos do script real; o subprocesso limpa o ambiente e chama Python com `-I`; há teste do ramo de falha de cada guarda.

Mutantes (`bin/forge-mutante`, 1 processo, no head c5815650): G1 a G16 morreram (16/16); `--cobertura --base ed5bfa02` marca todas as guardas do diff como cobertas por mutante declarado. Suíte inteira: fica com o CI do PR (`R-REVIEW`), não rerrodada.

O A1 não bloqueia: o envio confere o índice com os arquivos já commitados (B1), então o caso custa uma volta local, não um CI vermelho. Vira cartão depois do merge.
