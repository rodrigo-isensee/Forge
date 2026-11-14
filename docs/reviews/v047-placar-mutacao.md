---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-placar-mutacao
commit: 4b465b8cef7333485127a1abdadb21d7546a3bbc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047, placar de mutação com avisos (E1.101, portão E1.179)

Escopo: `origin/develop..4b465b8c` (develop em 6517ff14), 3 commits (6cb789cb, 05f09f2d e o merge da develop 4b465b8c), 6 arquivos. Quem revisa não fez a entrega. Comparei o diff com o item E1.101 do pedido v047 (PLACAR-MUTACAO-AVISOS): M10 da spec v0457-escopo-ponto-2 no trecho atual, `falhas=` na linha `placar:` para spec com rc diferente de zero, aviso quando `--desde` não é a tag da release anterior. Classe C, catraca em `scripts/placar-mutacao.py`.

Veredito sobre `4b465b8c`: **APROVADO**, com 1 recomendado.

## Ferramentas (saída citada, não refeita)
- CI do PR #556 no head 4b465b8c, na hora do review: `catraca` pass; `bateria (passos)` e `bateria (verificações longas)` pass; suíte 3.12 partes 1 e 2 e 3.14 parte 2 pass; as outras três partes pendentes; `bateria (pareceres)` falha porque os pareceres ainda não estão na branch (este é um deles). O merge espera o CI inteiro verde (`R-FLUXO`).
- Teste da classe tocada: `python3 -m unittest tests.test_forge_mutante.PlacarDaRelease`: `Ran 6 tests` / `OK`.
- Mutantes declarados: `bin/forge-mutante -- tests/mutantes/v047-placar-mutacao.json` no 4b465b8c: M1 a M7 `morreu` (linhas 49, 55, 58, 92, 96, 57, 79), rc=0.
- M10 da spec v0457-escopo-ponto-2: o `de` novo casa com `bin/forge-check:2757` (comentário MP1311 que o PR 536 acrescentou); a catraca verde no CI cobre a rodada.

## O que está conforme
- Faz o que o item pede, nem mais: `aviso_do_desde` só imprime e não muda o rc (o placar segue medida, não portão; `R-DECISAO` do M-5); `falhas=` só aparece quando há falha, e a linha `placar:` sem falha fica idêntica à de antes (o teste antigo continua exigindo a linha exata).
- Conferi o comportamento no clone real (tags v0.45.5, v0.46.0, v0.47.0): `--desde v0.46.0 --versao 0.47.1` avisa `(v0.47.0)`; `--desde v0.47.0 --versao 0.47.1` e `--versao próxima` não avisam; `--desde develop` avisa que não é tag.
- `rev-parse` com `--end-of-options` e `refs/tags/` explícito; a validação de `--desde` como commit (R-3) continua antes do aviso, então nome com `-` já saiu com 2.
- Guardas do diff: uma linha por guarda com mutante (M1 a M7), cada uma com teste de comportamento do ramo de falha (salvo o ramo `not alvo`, ver A1); o teste roda o script em subprocesso com `-I` e ambiente filtrado.
- Docstring do script, `docs/engineering/placar-mutacao.md` e o fragmento `changelog.d/v047-placar-mutacao.md` atualizados na mesma entrega.
- Tamanho (M14): 54 linhas de código e teste contadas (script 28, teste 26; `tests/mutantes/` fica fora da conta); um comportamento só.
- Commits em Conventional Commits em português, uma mudança coerente cada; a develop entrou por merge, sem rebase (`R-VERIFY`).

## Achados
- A1 (recomendado) scripts/placar-mutacao.py:55 · O ramo `not alvo` (versão fora de semver, o padrão `próxima`) não tem teste: a troca por `False or` passa nos 6 testes de PlacarDaRelease (sondado), e quebraria com AttributeError no clone com tags semver. Sugestão: caso sem `--versao` com v0.1.0 e v0.2.0 no teste do aviso.

## Sondas

## Parecer
Aprovado. A1 é recomendado (`R-REVIEW`): o comportamento está correto hoje (conferido acima com `--versao próxima`), falta só o teste que trava o ramo; sem defeito provado, não devolve. Pode ir num cartão da 0.47.1 ou numa volta futura do placar.
