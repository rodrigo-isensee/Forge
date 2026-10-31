---
tipo: qa
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a2
commit: 45f6c15bf0bcc9000b85d8f240c9d05f0f26c2a7
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

Diff lido: 234dbe0..45f6c15. Item do pedido: E2/A2, o parecer lê o comando atrás dos lançadores com `separar_lancadores`, e `timeout`, `env`, `xargs` e `find -exec` antes do merge de PR deixam de passar sem parecer. Código: `hooks/parecer.py` (+32/-3, uma classe de comportamento), `tests/test_hooks.py` +5, 9 fixtures novas em `tests/hooks/parecer/`, uma fixture de corpus ajustada (CO5, parecer 0 para 2, sem `nao_promete`), a spec `tests/mutantes/impl-furo-hook-a-a2.json` e `docs/hooks.md`. M14 (`agents/tech-lead.md:19`): 40 linhas de código e teste, uma classe em `hooks/`, com corpus próprio. Cumpre.

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
