---
tipo: qa
contrato: 1
pedido: pn3-pr-contra-main
branch: melhoria/pn3-pr-contra-main
commit: 34e3c1b5849fe59cfce45ae5560766381539d3d7
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: pn3-pr-contra-main

Escopo: P-N3, o `scripts/promover-homolog.py` roda `forge-check pr release-<versão> --ref <ref> --base main` na release e para antes de abrir o PR. Sem especificação de UX nem gatilho de segurança; os critérios vêm do pedido (E1, E2). Base 31257c1, head 34e3c1b.

## Achados
- A1 (bloqueante) scripts/promover-homolog.py:153 · o ramo de falha da conferência (forge-check que não roda ou estoura o prazo) é guarda nova sem mutante declarado e sem teste: o mutante QA Q2 sobreviveu; classe AR-2 (R-QA)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 parecer da release desatualizado contra a main para antes do PR | ContraMain.test_parecer_da_release_desatualizado_para_antes_de_abrir_o_pr (M1, M2) | código depois do parecer; nenhuma chamada gh | passou |
| E1 parecer da release faltando para | ContraMain.test_parecer_da_release_faltando_para (M1) | parecer ausente | passou |
| E1 release válida passa, base main e pedido release-<versão> | ContraMain.test_release_valendo_contra_a_main_passa_e_diz_o_comando (M3, M4) | base e pedido exatos | passou |
| E1 sem versão nova não roda a conferência | Versao.test_sem_versao_nova_nao_e_release_e_nao_confere_changelog (M2) | versão igual à da homolog | passou |
| E1 forge-check não roda ou estoura o prazo (falha fechada) | nenhum | prazo, executável ausente | SEM TESTE (A1) |
| E2 spec de mutantes M1 a M4 e vermelho antes do verde | forge-mutante, forge-testes --vermelho | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_promover_homolog` sobre 34e3c1b: 32 testes, OK (ContraMain: 3 OK).
- `bin/forge-mutante tests/mutantes/pn3-pr-contra-main.json`: M1 a M4 morreram, rc=0.
- `bin/forge-mutante --cobertura --base 31257c1`: coberta 154 (M1) e 233 (M2), rc=0; "declarado, não provado".
- Conferência da lista contra o diff: guardas mudadas são `if r.returncode`, `if versao != versao_de(base)`, `--base main`, o pedido e o ramo `except (TimeoutExpired, OSError)`; este último não tem mutante nem teste. Mutantes meus (spec em $TMPDIR): Q1 (`--ref` omitido) morreu, Q3 (sem `-I`) morreu, Q2 (ramo do except vira passa, a conferência seria ignorada) SOBREVIVEU.
- Vermelho, `bin/forge-testes --vermelho 31257c14c8d245d66e7806edb7cd65e22b3aeb04 --modulos test_promover_homolog`, rc=0:
  `vermelho: base=31257c14c8d2 head=34e3c1b5849f módulos=test_promover_homolog`; revertidos à base: changelog.d, docs/promocao-integrador.md, scripts/promover-homolog.py; os 3 testes de ContraMain e Versao.test_sem_versao_nova... H=ok B=falha, prova (asserção); contagem: não prova=28, prova=4.
- Documentação (docs/promocao-integrador.md, docstring) bate com o comportamento; fragmento do changelog presente.
- Itens de PA-7 (achados-recorrentes.md) conferidos: AR-2 se aplica (A1); AR-1 não, a lista cobre as guardas condicionais; AR-5 ok (`-I` no comando, Q3 morre).
