---
tipo: review
contrato: 1
pedido: release-0.48.0
branch: melhoria/release-0-48-0
commit: 74d2a59cad1d0edf5b69bdaeb191b3cb9cdef2e6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: release-0.48.0

1.ª rodada (release-0.48.0 E2.1), leva da 0.48.0 contra a main (`origin/main..74d2a59c`), PR #953. Cada item já teve review no seu PR; aqui se confere a leva junta.

## O que entrou
- `git log origin/main..74d2a59c`: 8 commits, os 7 itens (#938 319a968d, #945 b3dfe154, #946 05441491, #948 502c235b, #949 b414714c, #950 b60f53d7, #951 e2b2dbb2), todos MERGED na `develop`, e a marca (74d2a59c).
- Nada fora deles: a lista de arquivos de `git diff origin/main 74d2a59c` (75 arquivos) é igual à união dos arquivos dos 8 commits, sem os 7 fragmentos de `changelog.d/`, que nascem nos itens e a marca apaga. O #939 e o #941 já estão na main (fora de `origin/main..`).
- `git diff --check origin/main 74d2a59c`: limpo.

## A marca
- `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json`: 0.47.20 → 0.48.0, a mesma versão da main mais um minor; bate com a regra do patch até .9 que o #951 traz (depois de 0.47.20 vem 0.48.0).
- `CHANGELOG.md:7-18`: seção `[0.48.0] - 2026-11-28` com 8 linhas `- `, cada uma igual, palavra por palavra, à do fragmento apagado: #938 (:9), #945 (:10), #946 (:11), #951 (:13), #948 (:14 e :15; o E47.6 está no corpo do #948), #949 (:17), #950 (:18). Nenhuma linha cita item que não entrou.
- `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes"; `python3 -m unittest tests.test_changelog`: 93 testes, OK.

## Regras afrouxadas
- Rótulo `afrouxa-regra` em 3 dos 7: #938, #945 e #948; os outros quatro sem rótulo e sem marca no título. A tabela do corpo do #953 lista os três: completa.
- O corpo cita `forge-check afrouxamentos --prs 938,945,948 --ref 74d2a59`: `real=0 so-protegido=3`. Rodei sobre os 7: `rotulados=7 real=0 so-protegido=3 sem-violacao=4 sem-commit=0 erro-git=0 ref=74d2a59` (os 4 sem rótulo não tocam caminho protegido). O mérito do afrouxamento é da segurança (E2.2).

## Achados
- A1 (recomendado) CHANGELOG.md:14 · No PR homolog → main (E3.1), o #948 entra na lista das afrouxadas com o motivo (ordem do dono de 26/11, F1-ESPERA-NAO-E-VERMELHO, v0481 E47.1), mesmo com a ferramenta dando só-protegido; #938 e #945 à parte, como "rótulo sem afrouxar".

## Parecer
Aprovado no head 74d2a59c: a marca bate com os 7 fragmentos e os 7 PRs, nada fora deles entrou, a tabela das afrouxadas está completa e o CHANGELOG só cita o que entrou. O A1 é para o corpo do PR da main.

- ci: 74d2a59cad1d0edf5b69bdaeb191b3cb9cdef2e6 verde
