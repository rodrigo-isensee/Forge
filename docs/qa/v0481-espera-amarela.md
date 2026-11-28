---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-espera-amarela
commit: 054d4103ddb0c0364136575a4b36bbd3a2708164
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 (E47.5, #948, espera amarela, 1.ª rodada completa)

Diff `319a968d..054d4103` lido contra os critérios do brief (F1-ESPERA-NAO-E-VERMELHO): faltando só parecer ou rótulo, `bateria (pareceres)` e `catraca` ficam pendentes (amarelos) e seguem barrando a junção; vermelho só por defeito real. Não há `docs/ux` para este pedido; os critérios são os do brief (CE-1 a CE-4 abaixo). Clone de revisão `/root/.forge-contrib/wt/v0481-espera-amarela-qa-engineer`.

- ci: 054d4103ddb0c0364136575a4b36bbd3a2708164 verde
  - `gh pr checks 948` no head: verdes os jobs `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação (python 3.14)`, `árvore já provada na develop`, `teto de pulados` e as 5 partes da suíte 3.12. Vermelhos só `bateria (pareceres)` (faltam os pareceres do head, esperado) e `catraca (conferência)`, o job interno do `catraca` (R-CONFORMIDADE por mudar workflow e catraca, título com `[afrouxa-regra`; o script da base ainda sai 1, e o rc 3 só vale depois de mesclado, dito em `docs/protecao-de-branch.md`; falta o rótulo do dono). Os agregadores `bateria` e `catraca` herdam esses dois e ficam fora da conta (G3).

## Critério → teste → resultado

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CE-1 parecer ausente: espera (rc 3), não vermelho | `EsperaNaoEVermelho.test_so_falta_o_parecer_sai_3_e_diz_espera`, `test_desatualizado_segue_espera` | parecer ausente; parecer de commit anterior | passou (vermelho na base) |
| CE-2 rótulo ausente: espera só com `[afrouxa-regra` no título | `test_regra_com_titulo_afrouxa_sem_rotulo_sai_3`, `test_regra_sem_titulo_afrouxa_e_defeito_sai_1`, `EsperaDoRotuloSoComAApiRespondendo.test_com_tudo_respondendo_sai_3` | título com e sem a marca | passou |
| CE-3 defeito junto com espera fica vermelho | `test_parecer_reprovado_e_defeito_sai_1`, `test_review_ausente_com_outro_parecer_reprovado_sai_1`, `test_custo_e_defeito_mesmo_com_o_titulo`, `test_sonda_s1`, `test_sonda_s2` | reprovado, custo, nome de arquivo que imita a linha de espera | passou; lacuna em 2 ramos (A1) |
| CE-4 falha da API/git não vira espera | `test_cada_consulta_que_falha_sai_1` (execuções, fonte, PR, git), `test_sonda_s3`, `test_sem_eventos_sai_1...`, `test_sem_eventos_da_api_e_vermelho_mesmo_com_o_titulo` | API sem resposta, git estoura prazo, sem eventos | passou |
| CE-5 workflow: rc 3 grava o sufixo; rc 1, verde velho, API fora ficam vermelhos | `EsperaAmarelaNosWorkflows.test_espera_grava_o_sufixo_e_defeito_ou_verde_velho_fica_vermelho` (lista fechada de 5 estados mais 6 recusados) | estado do último check do head | passou; lacuna no rc 1 com a API respondendo (A3) |
| CE-6 sufixo só com todos os `needs` verdes; agregador da catraca exige a conferência | `test_sufixo_so_com_todos_os_needs_verdes`, `test_check_exigido_tem_o_sufixo...` | cada `needs` em failure, cancelled, skipped | passou |

## Vermelho antes do verde (`forge-testes --vermelho 319a968d --modulos test_catraca,test_ci_local`, rc=2)

```
vermelho: base=319a968df760 head=054d4103ddb0 módulos=test_catraca,test_ci_local (restrito por --modulos)
revertidos à base: .github/workflows/catraca.yml, .github/workflows/ci.yml, ..., scripts/ci-local, tests/catraca.py
contagem: não prova (passa na base)=496; prova (API ausente)=10; prova (asserção)=4; sem veredito=3
sem veredito: volta ao autor; não vale como vermelho nem como já falhava.
```

- Provam: `EsperaNaoEVermelho` (8 testes novos, API ausente), `EsperaDoRotuloSoComAApiRespondendo.test_com_tudo_respondendo_sai_3` e `test_cada_consulta_que_falha_sai_1`, `PrazoTotalDaApi`, `Workflows.test_gate_do_ci...`, `LeituraDosWorkflowsTest` (2).
- Passam na base de propósito (guardas negativas: o comportamento vermelho já existia; quem as prova é o mutante): `test_sonda_s3`, `test_sem_eventos_sai_1_com_o_resto_respondendo`.
- Sem veredito (A4): os 3 testes de `EsperaAmarelaNosWorkflows` caem na base com `ValueError`/`KeyError` de desempacotar o job ou o passo que a base não tem; a ferramenta só classifica `API ausente` e asserção. Conferi à mão numa cópia com os 4 arquivos de produção na base: os 3 erram ali (`not enough values to unpack`, `KeyError: 'conferencia'`) e passam no head; os mutantes M5-M11, M21-M23 os matam por comportamento.

## Mutantes (`bin/forge-mutante` das 4 specs `tests/mutantes/v0481-espera-amarela*.json`, rc=0)

```
M1..M25 · morreu (25 de 25; M18 morreu por erro do teste declarado sob o mutante, controle verde)
```

`--cobertura --base`: toda condição Python mudada tem mutante (M13-M20, M24, M25 e M1-M4); os dois workflows saem `não coberto` pela ferramenta (só lê Python), mas têm M5-M11 e M21-M22.

Lista do QA (spec fora do repositório, 7 mutantes sobre as linhas do diff), rc=1:

```
Q1 · sobreviveu · tests/catraca.py:2149   (sem arquivo sensível: return nao_aprovam, True)
Q2 · sobreviveu · tests/catraca.py:2157   (pedido sem achado: return nao_aprovam, True)
Q3 · sobreviveu · tests/catraca.py:156    (tira "da branch" do padrão de espera)
Q4 · morreu · tests/catraca.py:2326
Q5 · sobreviveu · .github/workflows/catraca.yml:58   (rc 1 passa adiante junto com o 3)
Q6 · morreu · .github/workflows/catraca.yml:74
Q7 · morreu · .github/workflows/ci.yml:619
```

Nenhum dos 4 sobreviventes é equivalente: Q1 e Q2 fazem um PR com parecer reprovado (sem arquivo sensível, ou de QA reprovado com review aprovado) sair do CLI com rc 3 (espera) em vez de 1, porque os testes lêem só `violacoes_de_pareceres(...)[0]` ou o caso com `hooks/novo.py` e review ausente; Q5 faz o rc 1 do script com a API devolvendo `nenhum` ou `failure` gravar `espera=` (o teste usa `gh` falho para o rc 1 e mascara); Q3 deixa a linha `sem parecer da branch` sem teste.

## Achados
- A1 (bloqueante) tests/catraca.py:2150 · mutantes Q1 e Q2 sobrevivem (linhas 2150 e 2158, `return nao_aprovam, False` virando True): nenhum teste dirige o CLI `--modo pareceres` com parecer reprovado sem arquivo sensível, nem QA reprovado com review aprovado e arquivo sensível; esperado rc 1, não 3. Defeito virar espera é o risco do #948.
- A2 (bloqueante) tests/catraca.py:156 · mutante Q3 sobrevive: tirar `da branch` de `LINHA_DE_ESPERA` não derruba teste; falta caso da linha `sem parecer da branch` (espera, rc 3) e de seu vizinho que casa só no começo e não é espera.
- A3 (bloqueante) .github/workflows/catraca.yml:58 · mutante Q5 sobrevive: com rc 1 do script e `gh` respondendo `nenhum` ou `failure`, o passo grava `espera=` e a catraca vira pendente com defeito. Em `test_espera_grava_o_sufixo...` o caso rc 1 usa `gh` que sai 9; precisa de rc 1 com `gh` devolvendo `nenhum`, nos dois workflows (mesmo ramo em ci.yml:618).
- A4 (recomendado) tests/test_ci_local.py:1131 · `forge-testes --vermelho` sai 2 para os 3 testes de `EsperaAmarelaNosWorkflows` (erro de desempacotar na base, não asserção); provados à mão e pelos mutantes. Abrir com `assertIn("conferencia", jobs)`/asserção explícita faz a ferramenta dar veredito.

## Outras observações
- Acessibilidade e E2E de navegador: n/a (workflow e script de catraca, sem tela).
- Bugs de produto em `docs/qa/bugs/`: nenhum; os achados são lacunas de teste.
- Na volta: reteste o que `forge-check parecer delta docs/qa/v0481-espera-amarela.md` listar, mais Q1, Q2, Q3, Q5 (spec da lista do QA acima) e o `--vermelho` com os testes novos.
