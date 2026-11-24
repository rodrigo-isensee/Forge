---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-dir28-sandbox
commit: 43d2f378e0b83258a958f24ec97a51c2bbeb9719
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E151.7, PR #847, diretriz 28 no Jarvis, delta das voltas E151.5 e E151.6)

## Delta lido
`forge-check parecer delta` deste parecer: intervalo `4568c9b7..43d2f378`, sem o que veio da `develop` (merge `bb5a6041`
do `forge-fechar`, merge-tree limpo); no domínio só `changelog.d/v0480-dir28-sandbox.md` e
`skills/fluxo-do-pedido/SKILL.md`. Dois commits do autor: `847becf9` (tipo do fragmento) e `43d2f378` (ponteiro da
resposta curta). Nenhuma linha de guarda de código mudou, sem mutante a declarar.

## Conferências
- **Fragmento (E151.5):** `### Mudado` virou `### Alterado`, tipo aceito pelo `forge-changelog` (o run 45379441484 recusava
  o anterior). `bin/forge-changelog conferir --base 0f4a7791 --branch melhoria/v0480-dir28-sandbox`: `ok: 1 fragmento(s)
  novo(s)`, rc=0. A frase nova do fragmento descreve o ponteiro da E151.6.
- **Resposta curta (E151.6, diretriz 25):** o parágrafo removido de `skills/fluxo-do-pedido/SKILL.md:40` está inteiro, letra
  por letra, em `skills/falar-com-o-dono/resposta-curta.md:7` (código `1a)`, as três marcas, `decisoes --resposta`, corte com
  `origem:`, `procurado:`, `seguir:`, `não seguir:`, `aprovo` só na recomendada `[reversível]`). O ponteiro usa
  `${CLAUDE_PLUGIN_ROOT}/skills/falar-com-o-dono/resposta-curta.md`, caminho que existe, e é o mesmo que
  `skills/falar-com-o-dono/SKILL.md:16` já usa. Os invariantes da regra (`tests/config.json:305-307`) e a proteção do arquivo
  (`tests/config.json:802`) apontam para `resposta-curta.md`, não para a `fluxo-do-pedido`: nenhum invariante caiu.
- **Carga do Jarvis:** o commit declara 40403 contra teto 40566; `tests.test_orcamento_instrucao` e `tests.test_jarvis_nucleo`
  verdes, sem teto alterado no diff.
- **Testes dos arquivos tocados** (sem suíte local, pelo brief): `tests.test_jarvis_nucleo`, `tests.test_forge.Referencias`,
  `RegrasInviolaveis` e `Neutralidade` (55 testes, OK); `tests.test_changelog`, `tests.test_orcamento_instrucao` e
  `tests.test_guia_varios_projetos` (103 testes, OK).
- **CI do PR #847:** a suíte inteira roda no CI; o merge espera o CI verde no head final (`R-FLUXO`).
- **Commits:** Conventional Commits em português, com o motivo no corpo.

## Parecer
Aprovado no head `43d2f378`. As duas voltas corrigem o que o CI apontou sem perder regra: a resposta curta segue inteira em
`resposta-curta.md` e o ponteiro leva a ela.
