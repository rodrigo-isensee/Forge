---
tipo: qa
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a4
commit: 8ece4aba1e244960910f40f340b9ac8643d2cef3
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-furo-hook-a, branch a4 (A4 FC-SUBCOMANDO-HOOK)

Revalidação sobre o head 8ece4ab (parecer anterior: 820043b, reprovado por A1 e A2). Diff total 234dbe0..8ece4ab: `hooks/conformidade.py` +42 (`args_do_forge_check`, `forge_check_grava`, tabelas), `tests/test_hooks.py` +19, 23 fixtures, spec `tests/mutantes/impl-furo-hook-a-a4.json`, `docs/hooks.md`. M14 (`agents/tech-lead.md:19`): 61 linhas de código e teste, uma classe em `hooks/`. Cumpre.

Delta lido (`forge-check delta --parecer`, 820043b..8ece4ab): a fixture nova `fc-anotar-por-interpretador-sem-forge-check-dev-libera.json` (+19) e a spec de mutantes (+41 -15, ids m2, m6, m7 reescritos e m14 novo). Nenhum código de produção mudou no delta.

## Achados
- A1 (recomendado) hooks/conformidade.py:77 · `--cobertura` ainda imprime "sem mutante" em :77 (a ferramenta olha a condição `achados`); o mutante A4-m14 existe e morre, e um mutante meu na condição (`if not achados`) também morre. Só a heurística da ferramenta, não é defeito da entrega

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A4: `forge-check anotar` fora do papel só de leitura não forja a decisão do dono nem a linha conferida | fixtures `fc-anotar-*-dev-bloqueia` (direto, caminho, interpretador, `-X`, `-W`, env, `=`, abreviada, raiz antes do subcomando, opaco); `fc-anotar-jarvis-libera` | todas as formas de chamar; jarvis libera | passou |
| A4: interpretador sem forge-check na linha não é lido como forge-check | `fc-anotar-por-interpretador-sem-forge-check-dev-libera` | mutante `else args` (A2 anterior) | passou, mutante m14 morreu |
| A4: `brief --gravar` (também abreviado) e saída do `transcricao anonimizar` seguem a política de caminhos | fixtures `fc-brief-gravar-*`, `fc-anonimizar-saida-*`, `fc-brief-sem-gravar-dev-libera`, `fc-pr-dev-libera`, `fc-sem-subcomando-dev-libera` | só grava com `--gravar`; destino livre libera | passou |
| A4: todo subcomando que grava está classificado | `test_a4_todo_subcomando_do_forge_check_que_grava_esta_classificado` | piso de 4 subcomandos; prefixo recusado | passou |
| A4: spec de mutantes cobre cada linha de guarda | `bin/forge-mutante tests/mutantes/impl-furo-hook-a-a4.json` | linhas 72, 74, 76, 77, 78, 80 e as de `forge_check_grava` | passou, rc=0 |

## Cenários e resultado real
- Mutação (head 8ece4ab, rc=0): m1 :72, m2 :76, m3 :78, m4 :1012, m5 :1015, m6 :74, m7 :76, m8 :80, m9 :938, m10 :1005, m11 :1007, m12 :1008, m13 :1009, m14 :77, todos "morreu". Mutante extra do QA em `$TMPDIR` (`if achados else None` para `if not achados else None`): morreu, rc=0.
- Conferência da lista contra o diff: `--cobertura --base 234dbe0` marca como coberta toda condição mudada, exceto o :77 (ver A1, recomendado).
- Vermelho antes do verde (do parecer anterior, mantido, código de produção inalterado no delta): com `hooks/conformidade.py` da base e os testes do head, `test_fixtures_do_lote_furo_hook_a` falha em várias fixtures; no head, OK. A fixture nova é contraprova de liberação, provada pelo mutante m14.
- Suíte: `python3 -m unittest tests.test_hooks` no head: 54 testes, OK (212 s). `scripts/validar-plugin.sh`: Validation passed.
- Sem interface de usuário: acessibilidade e E2E não se aplicam.
- Parecer: aprovado; A1 e A2 do parecer anterior estão corrigidos.
