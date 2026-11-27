---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-g3-parte2
commit: 91e3d5fe4cbfae0a7e99bdb6e1e6bd6a1aebd23f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 g3 parte 2 (#927, E28.6)

Obrigações (E28.6, sem especificação de UX): CA-1 o brief de código no Forge não pede D2 nem bateria local, só afetados, e a prova é o CI do PR; CA-2 a `prova_do_ci` exige em pass os 8 jobs do agregador (A1 do #923); CA-3 a `prova_do_ci` confere o título do PR (PR-TITULO-DO-BRIEF); CA-4 o brief do QA lê o CI do head e o `pr --previo` só avisa a conferência que falta; CA-5 o `pr` sem `--previo` segue exigindo a conferência.

- ci: 91e3d5fe4cbfae0a7e99bdb6e1e6bd6a1aebd23f verde

CI lido por `gh api .../commits/91e3d5fe.../check-runs` e `gh pr checks 927`: concluídos e verdes bateria (passos), (verificações longas), (python 3.14), instalação, as 10 suítes (3.12 e 3.14, partes 1 a 5), teto de pulados 3.12 e 3.14, árvore já provada; fora da linha do CI (esperam parecer ou rótulo) `bateria`, `bateria (pareceres)` e `catraca`. Os commits seguintes na branch (f93a309c, 6d89d684) só tocam docs/reviews e docs/security.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 | `test_pre_envio_brief.Gerar.test_codigo_do_forge_prova_pelo_ci_sem_o_d2_e_fora_do_forge_nao` | fora do Forge sem a linha; D2 ausente do brief | passou; vermelho na base (API ausente) |
| CA-2 | `test_forge_pronto.ProvaDoCi.test_job_do_agregador_ausente_ou_pulado_reprova` e `test_os_jobs_do_agregador_sao_os_needs_do_job_bateria_do_ci` | cada um dos 8 jobs ausente e pulado; lista presa ao ci.yml (mínimo 8) | passou; mutantes M1, M2 mortos |
| CA-3 | `test_forge_pronto.ProvaDoCi.test_titulo_do_brief_reprova_e_o_de_conventional_commits_passa` | título do brief, Conventional Commits, `None`, não-str | passou; M3, M4 mortos |
| CA-4 | `QaLeOCiSemEsperarAConferencia.test_o_brief_do_qa_nao_espera_a_conferencia`, `test_no_previo_a_conferencia_que_falta_so_avisa` | previo com e sem linhas | passou; vermelho na base; M6 morto |
| CA-5 | `QaLeOCiSemEsperarAConferencia.test_fora_do_previo_a_conferencia_que_falta_reprova`, `test_o_pr_passa_o_previo_a_conferencia_com_e_sem_base` | `pr` com e sem `--base`, com e sem previo | passou; M5, M7, M8, M29, M30 mortos |
| regressão | `test_selo_e_entrega.Entrega` (ajustado para os 8 jobs) | gh falso com o agregador completo | passou |

## Cenários e resultado real
Vermelho antes do verde, `forge-testes --vermelho 346a7860515c --modulos test_forge_pronto,test_pre_envio_brief` (head 91e3d5fe4cbf):
```
vermelho: base=346a7860515c head=91e3d5fe4cbf módulos=test_forge_pronto,test_pre_envio_brief (restrito por --modulos)
revertidos à base: bin/forge-check, changelog.d/v0481-g3-parte2.md, skills/briefs-e-conferencia/conferencia-da-entrega.md
test_forge_pronto · sem veredito (prazo, sinal ou executor sem registro em B)
Gerar.test_codigo_do_forge_prova_pelo_ci_sem_o_d2_e_fora_do_forge_nao · H=ok · B=erro · prova (API ausente)
QaLeOCiSemEsperarAConferencia.test_fora_do_previo_a_conferencia_que_falta_reprova · H=ok · B=erro · prova (API ausente)
QaLeOCiSemEsperarAConferencia.test_no_previo_a_conferencia_que_falta_so_avisa · H=ok · B=erro · prova (API ausente)
QaLeOCiSemEsperarAConferencia.test_o_brief_do_qa_nao_espera_a_conferencia · H=ok · B=falha · prova (asserção)
QaLeOCiSemEsperarAConferencia.test_o_pr_passa_o_previo_a_conferencia_com_e_sem_base · H=ok · B=erro · prova (API ausente)
contagem: não prova (passa na base)=29; prova (API ausente)=4; prova (asserção)=1; sem veredito=1
rc=2
```
O rc 2 vem de `test_forge_pronto`: na base o módulo nem carrega (`AGREGADOS` usa `fc.JOBS_DO_AGREGADOR` no import). Prova à mão, cópia em `$TMPDIR` com os testes do head e `bin/forge-check` da base: `python3 -m unittest tests.test_forge_pronto.ProvaDoCi` termina em `AttributeError: module 'forge_check_pronto_d2' has no attribute 'JOBS_DO_AGREGADOR'`, ou seja, falha na base e passa no head (CI verde). O `test_selo_e_entrega` passa do prazo de 590 s no `--vermelho`; coberto pelo CI.

Mutantes (`bin/forge-mutante tests/mutantes/v0481-g3-parte2.json --processos 2`, rc=0, rev=91e3d5fe4cbf):
```
M1 · morreu · bin/forge-check:1590
M2 · morreu · bin/forge-check:10755
M3 · morreu · bin/forge-check:10752
M4 · morreu · bin/forge-check:10751 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
M5 · morreu · bin/forge-check:1803
M6 · morreu · bin/forge-check:1803
M7 · morreu · bin/forge-check:1659
M8 · morreu · bin/forge-check:1677
```
Specs editadas (lote-l08 M29, M30; v0481-d2-no-brief M8) rodadas com `--ids`: todos morreram (1659, 1677, 10202). `forge-mutante --cobertura --base 346a7860...`: as linhas de guarda mudadas (1803, 10751, 10752) saem cobertas por M3 a M6; o resto do diff são `mais`/chamadas cobertas por M1, M2, M7, M8; sem condição sem mutante.

Testes locais afetados no head (`ProvaDoCi`, `test_pre_envio_brief`, `test_selo_e_entrega.Entrega`) sob a trava: 57 testes, OK em 26 s.

Observações sem achado: `JOBS_DO_AGREGADOR` não inclui `teto de pulados (python 3.14)` nem as suítes 3.14, o que bate com os `needs` do agregador (o teste de paridade com o ci.yml o prende). O `--previo` só avisa, e o merge e o `forge-fechar` seguem exigindo a conferência (CA-5 provado).
