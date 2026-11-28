---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-f3-develop-no-fim
commit: 7de82a022ae4c7b51479a7fdc87646b580153e03
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 (E30.7, F3 develop só no fim, #924)

- ci: 7de82a022ae4c7b51479a7fdc87646b580153e03 verde

Leitura do `gh pr checks 924`: tudo `pass` ou `skipping` no head, fora `bateria (pareceres)`, `bateria` e `catraca`, que esperam parecer ou rótulo (runs 45938144589 e 45938223566, mesmo sha); suíte 3.12 e 3.14, partes 1 a 5, verdes.

## Escopo
Critérios (do E30.1 e da volta E30.4, sem especificação de UX): CA-1 o `forge-check pronto` com base velha só avisa e confere contra o ponto de partida; CA-2 o merge que descarta a base (`-s ours`, conflito resolvido com a branch) desatualiza o parecer; CA-3 merge simulado que falha não vale (falha fechada); CA-4 a 3ª volta compara os testes com o início com a base trazida; CA-5 texto (`R-FLUXO`, fechamento, ritmo-e-corte) alinhado; CA-6 o D2 (`v0481-d2-no-brief`) segue valendo com o teste renomeado. Fora: a suíte inteira (vem do CI, `R-QA`).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 | `test_forge_pronto.BaseVelha.test_marca_depois_do_nascimento_so_avisa_e_confere_contra_o_ponto_de_partida`; `..test_com_a_base_trazida_nao_ha_linha_de_base_velha` | base velha vs base trazida (`--base` de cada checagem) | passou; vermelho na base (asserção); F3-1, F3-2 morreram |
| CA-2 | `test_forge_check_base_igual.MergeQueDescartaABase.test_merge_s_ours_desatualiza_review_e_seguranca`, `..test_conflito_resolvido_com_o_lado_da_branch_desatualiza`; `test_fechar_forge_check_real.DevelopSoNoFim.test_merge_que_descarta_a_base_desatualiza_o_parecer` (forge-fechar real) | head com a base trazida e `fora` vazio | passou; vermelho na base (asserção); F3-3 morreu |
| CA-3 | `test_forge_check_base_igual.MergeQueDescartaABase.test_merge_simulado_que_falha_desatualiza` | merge simulado sem resultado (git falha) | passou; vermelho na base (API ausente); F3-4, F3-5 morreram |
| CA-4 | `test_volta_alinhada.TerceiraVoltaComABaseTrazida` (5 testes: base que tirou teste cumpre; tirar teste depois de trazer a base não cumpre; conflito compara com o início; sem base compara com o início; ref da base num commit da branch não esconde) | base ausente, conflito, ref forjada | passou; 4 de 5 vermelhos na base (o 5º é regressão e passa na base por desenho); F3-6 a F3-9 morreram |
| CA-5 | `test_comando_pronto.TestComandoPronto.test_skills_tocadas_citam_comando_pronto` (A1 do review) e a suíte do CI | citação do comando de pronto em skill tocada | passou no CI do head |
| CA-6 | specs `v0481-d2-no-brief` (M1 a M8) e `v0481-voltas-alinhada-2` (VA-M9 a VA-M15, VA-M11 realinhado) | guardas do D2 e da conferência da entrega | todos morreram |

## Vermelho antes do verde (`forge-testes --vermelho`)
`vermelho: base=ee05ee8439f8 head=7de82a022ae4 módulos=test_forge_check_base_igual,test_fechar_forge_check_real,test_volta_alinhada,test_forge_pronto,test_reval_delta,test_comando_pronto (restrito por --modulos)` · rc=0 · `contagem: não prova (passa na base)=70; prova (API ausente)=4; prova (asserção)=5`. Os 9 que provam são os de CA-1 a CA-4; o que passa na base é regressão preexistente.

## Mutantes (`forge-mutante`)
Specs F3 numa rodada (`pedido=v0481-f3-develop-no-fim rev=7de82a022ae4`, rc=0): F3-1 a F3-9 todos `morreu` (F3-5 e F3-9 por erro do teste declarado, que passa sem o mutante, veredito de morte da ferramenta). D2: M1 a M8 `morreu` (rc=0). `voltas-alinhada-2`: VA-M9 a VA-M15 `morreu` (rc=0). `--cobertura --base ee05ee84`: `bin/forge-check` linhas 920, 950, 957, 4630, 4633, 4636 `coberta`; `spec editada` para d2-no-brief e voltas-alinhada-2 (rodadas acima); `não coberto: bin/forge-fechar` é só comentário no diff, sem linha de guarda. As linhas 1252/1255 e 10892 estão nas specs F3-1/F3-2/F3-8 e D2/VA-M11, que morreram.

## Bordas conferidas
- Base ausente, git que falha e conflito levam ao início ou a `desatualizado` (falha fechada); a ref local da base apontada para commit da própria branch não afrouxa o teste da 3ª volta.
- Merge da base sem conflito e sem byte à mão continua válido (não pede parecer novo, objetivo do F3), coberto por testes de `reval_delta` e `base_igual` que passam no head e na base.
- `forge-check pronto` com base velha deixa de reprovar e avisa em stderr; a marca passa a ser conferida no fechamento e no CI (decisão do E30.1).

## Resultado da execução
2026-11-27, local sob `flock` da trava A: vermelho em 6 módulos (2 min 34 s), mutantes F3 (1 min 3 s), D2 e voltas-alinhada-2. Nenhum bug aberto; `docs/qa/bugs/` sem entrada.
