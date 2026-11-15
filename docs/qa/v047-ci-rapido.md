---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-ci-rapido
commit: 0237a1bcdad85dca462d34aa0426a328f6af78c0
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047 (CI-RAPIDO: matriz de 5 partes, agregadores de nome fixo, teto de pulados em job próprio, tempos por anotação)

Instância que não fez a entrega. Intervalo `origin/develop..88fe9ff4` (o remoto trouxe depois só `docs/devops/v047-ci-rapido.md`, trazido por merge sem conflito; o código testado é o do `commit:`). Sem especificação de UX: os critérios vêm de `docs/propostas/ci-rapido.md` (decisão do dono de 2026-11-14, leitura b; ameaças S1 a S12) e do brief; CA-1 a CA-8 abaixo são essa leitura. A develop avançou (`c5c3a449`); `git merge-tree` de `HEAD` com `origin/develop` sai limpo.

## Achados
- A1 (bloqueante) tests/test_suite_partes.py:499 · R-QA: resolvido: antes sem veredito na base; agora os testes falham por asserção (`self.job`/`self.casar`). Vermelho rc=0, sem `sem veredito` (ver Cenários).
- A2 (recomendado) tests/mutantes/v047-ci-rapido-2.json:84 · resolvido: M20 declarado `equivalente` com justificativa; `forge-mutante` o lista `equivalente`, rc=0.
- A3 (bloqueante) stacks/node-react/pronto.md:65 · R-QA: resolvido em 0237a1bc: o texto agora diz que o `--shard` divide por arquivo, sem pesos, e manda quebrar o arquivo grande.
- A4 (recomendado) tests/test_suite_partes.py:609 · resolvido em 0237a1bc (docstring com 5 partes; AR-9 com vezes 4). Antes dizia "as 3 partes de cada versão"; são 5 (AR-9, limite antigo no texto, 4ª vez); a linha AR-9 sobe no PR do review.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 PR e develop em 5 partes por Python, N único (S2) | `FiacaoDoCI.test_o_n_das_matrizes_e_o_mesmo_nos_tres_lugares`, `test_partes_por_versao_rodam_o_script_em_cinco`; M25-M28 | 4 matrizes, `--parte K/N`, `--somar-pulados N`; N=4 reprova | passou (sem veredito no vermelho, A1) |
| CA-2 divisão por unidade, completude por ID, falha fechada (S9) | `DivisaoPorUnidade.*` (completude, unidade fora de toda parte ou em duas, ID sem unidade, mais partes que unidades); M1-M14 | partes > unidades, unidade duplicada ou perdida | passou |
| CA-3 agregador de nome fixo só passa com 5 pernas + teto; perna vermelha, pulada ou cancelada reprova (S1, A1) | `test_agregador_da_develop_exige_as_cinco_pernas_e_o_teto_sem_rodar_codigo`, `test_agregadores_tem_o_nome_exigido_e_exigem_todas_as_partes`; M29-M31 | `always()`, nunca `skipped` | passou |
| CA-4 teto de pulados em job próprio, artefato do run corrente (S5, A4) | `test_pernas_da_develop_publicam_os_pulados_e_o_download_so_le_o_run_corrente`, `test_parte_faltando_repetida_ou_adulterada_reprova`, `test_soma_acima_do_teto_ou_teto_ilegivel_reprova`; M32-M34 | parte faltando, repetida, outro N, teto ilegível | passou (sem veredito no vermelho, A1) |
| CA-5 anotação de tempos só no CI, só parte verde, alfabeto seguro (S6) | `test_anotacao_de_tempos_so_no_ci_e_so_com_a_parte_verde`, `test_nome_fora_do_alfabeto_valor_invalido_e_formato_ruim_ficam_de_fora`, `test_muitas_unidades_viram_blocos_e_acima_do_limite_nenhuma`, `test_escapar_dado` | `::`, `%`, CR/LF, mais de 8 blocos | passou |
| CA-6 `pesos-do-ci.py` lê só a API, descarta anotação fora do formato, nunca grava no repositório nem chama git/gh (S10) | `tests/test_pesos_do_ci.py` (14 testes); M15-M24 | conjunto parcial de pernas, segundos acima de TETO_S, token só no cabeçalho | passou (M20 equivalente) |
| CA-7 sem `pull_request_target`, sem cache novo, `contents: read` por job (S3, S4, S7, S8) | `test_ci_local.LeituraDosWorkflowsTest`, `PortoesDeSegurancaTest`; leitura do diff | permissões, interpolação em `run:` | passou |
| CA-8 PR sem afrouxar: passo barato vermelho pula as partes e reprova agregadores (A18, S12) | `MatrizNeedsEAgregadorTest.test_passo_barato_vermelho_pula_a_suite_e_reprova_os_agregadores` | `needs` e `if` | passou (sem veredito no vermelho, A1) |

## Cenários e resultado real
- Suíte dirigida local (`test_suite_partes`, `test_pesos_do_ci`, `test_ci_local`): `Ran 134 tests ... OK` no head. A suíte inteira e o check-run `bateria` do sha ficam para o CI do PR (não há PR ainda, sem `run` a citar; I5).
- Vermelho antes do verde, base do brief (`forge-testes --vermelho 067b2a9f8d287ef24a2ee878f6c56db2d6a71d66 --modulos test_suite_partes,test_pesos_do_ci,test_ci_local`), rc=2:
  `vermelho: base=067b2a9f8d28 head=a77f2eeceee9 módulos=test_suite_partes,test_pesos_do_ci,test_ci_local (restrito por --modulos)`
  `contagem: não prova (passa na base)=90; prova (API ausente)=28; prova (asserção)=9; sem veredito=7`
  `sem veredito: volta ao autor; não vale como vermelho nem como já falhava.` Nenhum teste cai no HEAD (`H=ok` em todos). Os 7 sem veredito: `FiacaoDoCI` (n das matrizes, partes por versão, pernas da develop, rápidas como prova), `LeituraDosWorkflowsTest` (bateria/ferramenta, comentário do topo) e `MatrizNeedsEAgregadorTest` (passo barato vermelho). A rodada restrita aos 3 módulos novos; a suíte inteira foi inviável localmente (carga da máquina).
- Mutação (spec do autor, 34 mutantes em 3 arquivos, conferida contra as linhas de guarda do diff; `bin/forge-mutante tests/mutantes/v047-ci-rapido-{1,2,3}.json --processos 4`, `rev=88fe9ff40c95`): M1 a M34 `morreu`, exceto `M20 · sobreviveu · scripts/pesos-do-ci.py:85` (equivalente, A2). Nenhuma linha de guarda mudada sem mutante encontrada na leitura do diff de `ci.yml` e `suite-partes.py`.
- Simulação de merge com `origin/develop` (`c5c3a449`): sem conflito.
- `forge-check docs`: rc=0 antes deste arquivo.
- Fora do alcance local: tempo real das 5 partes (meta de 5 e 8 min) e `pesos-d4` sem recalibrar, por desenho; a medida pós-merge é do `devops-engineer`.
- Acessibilidade e permissão de usuário: não se aplicam (mudança de CI, sem interface).

## Revalidação por delta 88fe9ff4..5b632a48 (`forge-check parecer delta`)
- Domínio lido: `docs/economia-de-tokens.md`, `scripts/suite-partes.py` (3 funções sem uso removidas: `esperado_da_parte`, `pesos_por_modulo`, `dividir`; o teste que as cobria saiu junto, sem perda de obrigação: o fora-da-divisão e o módulo-do-ID seguem testados), `skills/ci-cd/SKILL.md`, `pronto.md` (node-react, python), spec de mutantes, `test_ci_local.py`, `test_forge.py:335` (3 para 5 partes; a base 067b2a9f tem "3 partes" no README, então falha por asserção lá, conferido), `test_suite_partes.py`.
- Vermelho (`forge-testes --vermelho 067b2a9f8d287ef24a2ee878f6c56db2d6a71d66 --modulos test_suite_partes,test_pesos_do_ci,test_ci_local`), rc=0:
  `vermelho: base=067b2a9f8d28 head=5b632a48bbce módulos=test_suite_partes,test_pesos_do_ci,test_ci_local (restrito por --modulos)`
  `contagem: não prova (passa na base)=87; prova (API ausente)=27; prova (asserção)=17` (antes: 7 sem veredito; agora 0).
  Com `test_forge` no `--modulos` o módulo inteiro estoura o prazo (`sem veredito`, rc 2 por tamanho do módulo); o teste de `test_forge:335` foi provado à parte (passa no head, README da base diz "3 partes").
- Mutação do delta: `bin/forge-mutante tests/mutantes/v047-ci-rapido-{1,2,3}.json --base 88fe9ff40c95a8cae5565c6ea7105117f0a8f4dc --processos 4`: `base=88fe9ff40c95… rev=5b632a48bbce`; M1 a M34 `morreu`, M20 `equivalente`; nenhum sobrevivente.
- Suíte dirigida local (`test_suite_partes`, `test_pesos_do_ci`, `test_ci_local`) no head: `Ran 131 tests ... OK` (os 134 antes menos os 3 testes das funções removidas). Suíte inteira e check-run `bateria`: CI do PR (sem PR ainda; I5).
- Merge com o remoto (pareceres de review e segurança, `1f1214be`) sem conflito.
- `forge-check docs`: rc=0.

## Revalidação por delta 5b632a48..0237a1bc (`forge-check parecer delta`, rc=0)
- Domínio lido: só textos. `stacks/node-react/pronto.md` (A3: `vitest --shard` por arquivo, sem pesos; consistente com a skill), `skills/ci-cd/SKILL.md` (overhead medido pelo projeto, sem número do Forge: neutro), docstring de `tests/test_suite_partes.py:609` ("5 partes", igual à matriz `parte: [1..5]` do `ci.yml`), `docs/engineering/achados-recorrentes.md` (AR-9 vezes 4).
- Nenhuma linha de guarda mudada: a mutação do delta não se aplica (a mudança de código é uma docstring); M1 a M34 seguem os da rodada anterior.
- Suíte dirigida local (`test_suite_partes`, `test_pesos_do_ci`, `test_ci_local`) no head: `Ran 131 tests ... OK`. Vermelho: sem teste novo no delta. Suíte inteira e `bateria`: CI do PR (sem PR ainda; I5).
- Remoto avançou (`79eae902`, só `docs/security/v047-ci-rapido.md`), trazido por fast-forward.
- Bugs abertos: nenhum. Aprovado.
