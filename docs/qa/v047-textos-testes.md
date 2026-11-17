---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-textos-testes
commit: 219c3c50ae76ef60bded7b6337ad6803673485d9
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047-textos-testes (E1.255, parecer E1.270)

Intervalo `origin/develop..219c3c50`: três skills (`qa-testing`, `briefs-e-conferencia`, `contribuir-com-o-forge`), o fragmento de changelog e a classe `RodarUmModuloComIsolamento` em `tests/test_forge.py`. Sem especificação de UX nem contrato de API (pedido de texto): as obrigações são as regras nomeadas no pedido, CONTRIB-TESTE-NICE (Q6 do dono), UNITTEST-I-NAO-IMPORTA e BRIEF-UNITTEST-DISCOVER, lidas no changelog e no teste.

## Achados
- A1 (recomendado) skills/briefs-e-conferencia/SKILL.md:8 · o diff apara texto alheio ao pedido (sandbox suja a raiz, worktree compartilhada, clone sem refs, Texto do Jarvis, pre-push barram) e o fragmento de changelog só cita rodar testes. Registre ou separe.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CONTRIB-TESTE-NICE (nice e um arquivo por vez na contribuição) | `test_cada_skill_traz_a_forma_e_a_contribuicao_em_nice_um_por_vez` | forma única por skill (exatamente 1), seção 5 com a frase | passou; vermelho na base |
| UNITTEST-I-NAO-IMPORTA (`tests.<mod>` falha sob `-I`) | `test_tests_ponto_modulo_com_menos_i_nao_importa` | `No module named 'tests'` | passou; passa também na base (documenta o fato de Python, não regressão) |
| BRIEF-UNITTEST-DISCOVER (a forma das skills roda sob `-I`) | `test_a_forma_das_skills_roda_com_menos_i` | projeto mínimo sem `__init__.py`, ambiente limpo, 3 skills | passou; vermelho na base |

## Cenários e resultado real
- Classe nova no head: `python3 -I -m unittest discover -s tests -p test_forge.py -k RodarUmModuloComIsolamento` → `Ran 3 tests ... OK`.
- Vermelho antes do verde, à mão (o `forge-testes --vermelho` do módulo `test_forge` não terminou: estourou o prazo da sessão e as tentativas foram encerradas sem veredito, que não vale como vermelho; o CI refaz). Cópia do head com as 3 skills da `origin/develop`: `FAILED (failures=1, errors=1)` (`test_a_forma_das_skills_roda_com_menos_i` ERROR, `test_cada_skill_traz_a_forma_...` FAIL). O terceiro teste passa na base, como esperado.
- Mutação no diff (cópia em `$TMPDIR`, classe rodada após cada mutante; os 4 morreram):
  - M1 tira `-I` da forma em `qa-testing`: `FAILED (failures=1, errors=1)`.
  - M2 tira `nice -n 19` da contribuição: `FAILED (failures=1)`.
  - M3 tira "um arquivo por vez": `FAILED (failures=1)`.
  - M4 troca a forma por `tests.test_x` em `briefs-e-conferencia`: `FAILED (failures=1, errors=1)`.
- Módulos que leem as skills, no head: `test_jarvis_nucleo`, `test_aq1_texto`, `test_modelos_projeto`, `test_orcamento_instrucao`, `test_clareza`, `test_citacao`, `test_textos_034`, `test_textos_dono_f7`: todos OK.
- `forge-check docs`: rc=0.
- Suíte completa: não rodada aqui (`R-QA`); a prova é o check-run `bateria` do PR. O branch ainda não tem PR e a API não devolveu check-runs para o sha, então fica pendente para o tech-lead conferir no PR.
- Fora do diff do pedido: nenhum controle (`bin/`, hooks, `.githooks/`) mudou; `forge-mutante` não se aplica. Acessibilidade e E2E: n/a (texto).
- Remoto avançou (`24af617e`, só pareceres de review e segurança); trazido por merge, sem tocar código.
