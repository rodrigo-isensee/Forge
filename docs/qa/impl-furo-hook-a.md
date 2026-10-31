---
tipo: qa
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a2
commit: 7b5f5aa36d90f6368325dfd53d514ebafa545040
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-furo-hook-a, branch a2 (A2 PARECER-LANCADOR)

Diff lido: 234dbe0..45f6c15 (parecer original) e, na revalidação, 6b77146..7b5f5aa. Item do pedido: E2/A2, o parecer lê o comando atrás dos lançadores com `separar_lancadores`, e `timeout`, `env`, `xargs` e `find -exec` antes do merge de PR deixam de passar sem parecer. Código: `hooks/parecer.py` (+32/-3, uma classe de comportamento), `tests/test_hooks.py` +5, 9 fixtures novas em `tests/hooks/parecer/`, uma fixture de corpus ajustada (CO5, parecer 0 para 2, sem `nao_promete`), a spec `tests/mutantes/impl-furo-hook-a-a2.json` e `docs/hooks.md`. M14 (`agents/tech-lead.md:19`): 40 linhas de código e teste, uma classe em `hooks/`, com corpus próprio. Cumpre.

## Revalidação no head 7b5f5aa (delta 45f6c15..7b5f5aa)
- O `forge-check delta` lista o que a develop trouxe nos dois merges (412abf7 e 7b5f5aa). Li só o que toca a entrega: `git diff 6b77146 7b5f5aa` em `hooks/parecer.py`, `docs/hooks.md`, `tests/test_hooks.py`, `tests/fixtures/heredoc-volta-unica.json` e a spec de mutantes. O diff da branch contra a base atual segue sendo só o A2; a mudança de `hooks/parecer.py` entre 45f6c15 e o head (K-164, `base_do_delta`) veio da develop, sem conflito, e não está no diff da branch.
- `docs/hooks.md` (resolução do merge): o diff contra a base atual tem 4 linhas. A linha "Palavra crítica só no texto" ficou com o texto do A2 (lançadores seguidos, `xargs`, `find -exec` e demais recusam) e a outra linha mexida só acrescenta o `find -exec`; nada da develop se perdeu.
- M14 (`agents/tech-lead.md:19`): a branch cumpre. Uma classe de comportamento (lançador no parecer), `hooks/parecer.py` +35/-3, `tests/test_hooks.py` +5, 9 fixtures, spec e `docs/hooks.md`.
- Suíte completa no head (`python3 -m unittest discover -s tests`): `Ran 2344 tests in 936.046s`, `OK (skipped=27)`, rc=0. Uma rodada anterior, igual, terminou com `FAILED (failures=1, skipped=27)`; a saída foi cortada por `tail` e o teste não foi identificado; a repetição passou inteira sem mudança de código (a primeira rodava junto com a mutação). Fica registrada como instabilidade não explicada; nenhum teste foi pulado.
- Vermelho antes do verde repetido no head (cópia em `$TMPDIR`, `hooks/parecer.py` de 6b77146 com os testes do head): `test_fixtures_do_lote_furo_hook_a` falha em 7 fixtures (`env`, `find-exec`, `flock`, `lancador-encadeado`, `timeout-reprovado`, `xargs`, `nice`), cada uma com `AssertionError: 0 != 2`.
- Mutação sobre 7b5f5aa: `A2-m1 · morreu · hooks/parecer.py:284`, `A2-m2 · :279`, `A2-m3 · :279`, `A2-m4 · :282`, `A2-m5 · :287`; rc=0. `bin/forge-mutante --cobertura --base 6b77146`: `:279`, `:284` e `:287` com mutante declarado; nenhuma guarda sem mutante.
- Parecer mantido: aprovado, sem achados. Depois deste teste a branch ganhou só o parecer do review (4a3ef0d, `docs/reviews/`).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A2: merge reprovado atrás de `timeout`, `env`, `flock` ou lançador encadeado bloqueia | fixtures `forge-clone-pr-merge-{timeout,env,flock,lancador-encadeado}-reprovado-bloqueia`, por `test_fixtures_do_lote_furo_hook_a` | lançador com e sem opção, encadeado | passou |
| A2: `find -exec` e `xargs` no merge bloqueiam | fixtures `...-find-exec-bloqueia` e `...-xargs-branch-atual-aprovada-bloqueia` | alvo vindo da entrada padrão, mesmo com parecer aprovado | passou |
| A2: merge com parecer aprovado atrás de `timeout` libera | fixture `...-timeout-aprovado-libera` | o lançador não vira falso positivo | passou |
| A2: `cd` e `nice` de lançador não valem como pasta nem como parecer | fixtures `merge-na-develop-cd-de-lancador-nao-vale-bloqueia` e `merge-na-develop-nice-sem-parecer-bloqueia` | `cd` roda noutro processo | passou |

## Cenários e resultado real
- Vermelho antes do verde (manual, cópia em `$TMPDIR` com `hooks/parecer.py` da base e os testes do head): `test_fixtures_do_lote_furo_hook_a` falha em 7 fixtures (`env`, `find-exec`, `flock`, `lancador-encadeado`, `timeout-reprovado`, `xargs`, `nice`), `Ran 1 test in 23.7s`, FAILED. Verde no head: OK. O `forge-testes --vermelho` sobre a suíte inteira estourou o prazo aqui (sem veredito), por isso a prova é manual.
- Mutação (`bin/forge-mutante tests/mutantes/impl-furo-hook-a-a2.json`): `A2-m1 · morreu · hooks/parecer.py:284`, `A2-m2 · morreu · :279`, `A2-m3 · morreu · :279`, `A2-m4 · morreu · :282`, `A2-m5 · morreu · :287`. Nenhum sobrevivente, nenhum inválido.
- `bin/forge-mutante --cobertura --base 234dbe0`: as condições mudadas (`:279`, `:284`, `:287`) têm mutante declarado; nenhuma linha de guarda sem mutante.
- Sem interface de usuário: acessibilidade e E2E não se aplicam.
- Risco: o ramo `except (LancadorDemais, TextoDivididoAberto)` não é condição e não tem mutante; se falhasse, cairia na falha fechada do hook, que também recusa, então o efeito observável é o mesmo.
