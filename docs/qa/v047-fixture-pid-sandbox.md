---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-fixture-pid-sandbox
commit: 32f1628aae7bffa63a590a218b88c18ed4c73738
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047 (fixtures de pid puladas fora do CI, E1.90 / E1.110)

Head testado: b47610cc. Diff contra a base afba389e: `tests/test_hooks.py`, `tests/mutantes/v047-fixture-pid-sandbox.json` e o fragmento de changelog; o hook `hooks/agentes.py` não muda. Sem PR e sem check-run no sha no momento do parecer; a máquina estava com carga ~21 em 12 CPUs, então a execução local ficou nos testes leves e afetados.

## Achados
- A1 (recomendado) tests/mutantes/v047-fixture-pid-sandbox.json:1 · o M1 só dá veredito onde o ns de pid se lê (CI): local sai 2 (controle vermelho, o teste pula). Cite o check-run `bateria` do mesmo sha como prova da morte do M1 antes do merge.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Sem ns de pid do pai legível e sem CI, as 4 fixtures de pid/sessão saem puladas com motivo | test_sem_ns_de_pid_do_pai_as_fixtures_de_pid_e_sessao_saem_puladas_com_motivo | ns ilegível (PermissionError) x legível; só as 4 da lista pulam; motivo no skip | passou |
| Com ns legível (ou CI) as 4 rodam e gravam | test_com_ns_de_pid_do_pai_legivel_as_fixtures_de_pid_e_sessao_rodam_e_gravam | CI definido nunca pula | sandbox sem CI: pulou (esperado); com CI=1: passou |
| Nunca pula com CI ou GITHUB_ACTIONS | mesmo teste, ramo `sinais_de_ci()` | CI definido | passou com CI=1 |
| Hook inalterado; M1 mata a perda da gravação de pid e sessão | M1 em tests/mutantes | linha `return {"pid"...}` | sem veredito local (rc 2); só no CI |

## Cenários e resultado real
- Os dois testes novos: sem CI, 1 ok e 1 skipped com motivo; com `CI=1`, o segundo roda as 4 fixtures sob mock e passa.
- `tests.test_apoio_sandbox`: 22 testes, OK.
- `test_fixtures` completo (com e sem CI): não concluiu em 550 s por causa da carga; fica para o CI do PR.
- `forge-testes --vermelho afba389e`: estourou o prazo (rc 124), sem veredito; a base não tem os helpers nem os dois testes, então eles falham por ausência (vermelho por inspeção, não por saída da ferramenta).
- `forge-mutante`: rc 2, `M1 · controle vermelho · hooks/agentes.py` (sem veredito, nunca "morreu"). Há um mutante para a única guarda de código ligada ao diff (o hook não mudou).

## Delta E1.124 (QA por delta até b645e83c, E1.120)
Head da branch: dc39fbd5 (só soma o parecer de segurança sobre b645e83c). Delta desde e812e844: `bin/forge-testes` (`REAPROVEITAM_O_LOTE`, `JUNTO_DO_MODULO`, `modulos_sem_mapa`), `tests/test_hooks.py` (`pular_sem_ns_de_pid` vira função do módulo), `tests/test_testes_tocados.py` (teste novo), mutante M2. Carga ~13 em 12 CPUs; o PR #547 (rascunho) tinha a suíte do CI pendente na hora do parecer.

### Achados
- A2 (recomendado) docs/qa/v047-fixture-pid-sandbox.md:1 · a suíte inteira só roda no CI do PR #547; cite o check-run `bateria` do mesmo sha antes de integrar. Aqui valeu a execução local dos módulos afetados.

### Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Os módulos que reaproveitam `executar_em_lote` rodam sem AttributeError | test_esperar_estado, test_hook_ansi_c, test_hook_git_comum, test_hooks_fila27, test_hooks_parecer_pasta, test_hooks_volta_{corpus,lancador,propriedades} | quem não herda de `Hooks` (a função saiu do método) | 8 módulos OK, 0 AttributeError (lancador: 25 puladas, sandbox sem CI) |
| Pulo só sem /proc legível e nunca com CI | test_sem_ns_..._puladas_com_motivo e test_com_ns_..._rodam_e_gravam | ns ilegível x legível; CI definido | 2 testes, OK (1 skipped esperado, sem CI) |
| O mapa lista esses módulos ao pedir tests/test_hooks.py | CaminhoFiltroEAviso.test_test_hooks_pelo_caminho_roda_quem_reaproveita_o_lote_dele | mínimo de 8 reaproveitadores (guarda de suíte vazia); outro módulo não leva extra | OK |

### Mutação
`forge-mutante tests/mutantes/v047-fixture-pid-sandbox.json`: M1 controle vermelho (sem veredito local, só no CI; A1 anterior), M2 morreu em `bin/forge-testes:104`. A guarda de código mudada (`JUNTO_DO_MODULO`) tem o M2; `modulos_sem_mapa` é coberta pelo mesmo teste.

Vermelho antes do verde: não rodei `forge-testes --vermelho` (carga); o M2 morto prova que o teste novo cai sem o mapa.

## Delta E1.153 (QA por delta b645e83c..edac705c)
`forge-check parecer delta` lista só `tests/test_fechar.py` e `tests/test_prepush_so_docs.py` (commit de código 32f1628a; edac705c só soma pareceres). Nenhum código de produção mudou; os dois são ajustes de teste contra corrida (CI do PR 547, Python 3.14, parte 2/3).
- `test_fechar`: a parada passa a ser lida pela última linha `[err]` (stdout e stderr não têm ordem entre si). Fronteira mantida: `erros` vazio ou parada ausente falha, e a última linha ainda é `fim: código 1`.
- `FilaDaChecagem.primeiro_aviso`: espera a linha inteira "aguardando a vez" com teto de 20 s; se estourar, mata o grupo (`killpg`) e falha com mensagem. Sem espera fixa nem corrida entre senha e contagem. Os avisos lidos entram em `fins`, então a conferência de ordem e de "quem está na frente" segue intacta.

Execução local (carga 9 a 14 em 12 CPUs): `python3 -m unittest tests.test_prepush_so_docs.FilaDaChecagem tests.test_fechar` · Ran 106 tests in 343.971s · OK (uma rodada; as seguintes interrompidas por tempo). No PR 547 as partes da suíte 3.14 (1/3, 2/3, 3/3) e 3.12 (2/3, 3/3) estavam `pass` na consulta; 3.12 parte 1/3 pendente, e o head do PR era c5e635c5, não edac705c.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A fila conta quem está na frente em ordem de chegada | test_tres_esperam_em_ordem_de_chegada_contando_quem_esta_na_frente | linha de aviso inteira lida antes de lançar o próximo; teto de 20 s | OK |
| O fechamento para no passo que falhou e registra o código | test_fechar, parada no passo 1 | stderr sem ordem com stdout; sem `[err]` falha | OK |

Vermelho antes do verde: não se aplica (estabilidade de teste existente, sem regra nova; a falha anterior é a do CI citado). Mutação: sem arquivo de produção no delta.

### Achados
- A3 (recomendado) tests/test_prepush_so_docs.py:520 · a suíte inteira só vale pelo check-run `suíte` do mesmo sha; cite-o antes do merge (3.12 parte 1/3 pendente e head do PR diferente do revisado).

Parecer do delta: aprovado, sem bug aberto.
