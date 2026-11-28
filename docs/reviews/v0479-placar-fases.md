---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-placar-fases
commit: c08aee63c9d6161a53a2ead78cf2af20551a1221
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 E20.6 (melhoria/v0479-placar-fases, head 94728c4f), revalidação por delta

Escopo: só o delta lido em `forge-check parecer delta docs/reviews/v0479-placar-fases.md`, intervalo 23431487..94728c4f, domínio código e testes: `bin/forge-placar`, `tests/evals/test_placar.py`, `tests/mutantes/v0479-placar-fases-{2,4,6}.json`, `changelog.d/v0479-placar-fases.md`, `docs/melhoria-continua.md`.

## Sondas
- S1 · `bin/forge-placar fases --git . --ref origin/develop --dia 2026-11-18` no clone (origin/develop 2904a68a), sem `refs/pull/*` · espera: os 4 merges medidos e os squashes contados à parte · obtido: 4 itens e `itens sem fases (squash): 28 (...; fora da média)`
- S2 · o mesmo, depois de `git fetch origin refs/pull/N/head:refs/pull/N/head` dos 28 PRs do dia · espera: os 32 itens da linha principal do dia · obtido: `total do dia: 32 itens · ... média 283 min por item (meta 85 min) · primeira rodada aprovada 19/32`, rc 0

## Parecer
Aprovado. O A1 do parecer anterior está resolvido: o squash do `forge-fechar` (um pai, assunto `(#N)`) é medido pelos commits de `refs/pull/N/head` a partir do pai na linha principal (`pais[0]..ponta`, sem merges, o que tira a develop trazida pela branch), e sem a ref conta na linha `itens sem fases (squash): N` e em `sem_fases` do `--json`, fora da média; o dia só com squash sem ref diz "nenhum item medido" em vez de "nenhum mesclado". Commit direto de um pai sem `(#N)` fica fora. Na develop real de 18/11 os 32 itens do dia entram (eram 4). O `--prs` com JSON aninhado fundo (`RecursionError`) e com `mergedAt` de dia inexistente sai com 2, sem traceback (A1 da segurança). Texto de ajuda, changelog e `docs/melhoria-continua.md` acompanham o comportamento.

Teto H1: a branch soma 160 linhas de código (`bin/forge-placar`, 158+2 contra a base 0c47762a). Aceito o excesso de 10: vem das correções que os portões exigiram (A1 deste review e A1 da segurança), e tirá-las deixa vermelhos os testes `test_squash_mede_pelos_commits_do_pr_e_conta_a_parte_sem_eles` e `test_arquivo_ausente_ou_invalido_sai_com_2`; o PR leva a linha `teto: excedido, 160 linhas, <motivo>`.

Ferramentas e provas: `Fases` e `SemTeste` rodados no head, 15 OK; `bin/forge-mutante` no `-6.json`: M34 a M41 morreram; M13, M14 (`-2.json`) e M26 (`-4.json`), reescritos no delta, morreram. Suíte inteira: fica no CI do PR (sem suíte local, pelo brief).

## Revalidação E20.14 (head c08aee63, delta 94728c4f..c08aee63)
Lido só `forge-check parecer delta`, domínio código e testes: `bin/forge-placar`, `tests/evals/test_placar.py`, `tests/mutantes/v0479-placar-fases-{6,7}.json`, `changelog.d/v0479-placar-fases.md`. O `RecursionError` deixa de depender da versão do Python: `fundo_demais` (`TETO_ANINHAMENTO = 64`) conta `[` e `{` fora das strings antes do `json.loads` e sai com 2, sem traceback. O teste novo cobre o teto exato (64 passa), 65 recusado e colchete em string ignorado. Guardas do delta com mutante: M34 (reescrito, `-6.json`) e M42 a M44 (`-7.json`); os quatro morreram, e M35 a M41 seguem mortos. `SemTeste` rodado no head: 5 OK. Suíte inteira fica no CI do PR. Sem achado novo; o teto H1 e a justificativa acima seguem valendo (o delta mexe no mesmo comportamento; o `teto:` do PR deve refletir a contagem final). Aprovado.
