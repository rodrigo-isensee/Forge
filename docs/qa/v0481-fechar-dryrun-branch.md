---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-fechar-dryrun-branch
commit: 1bf95225578a79532bae4ee99f3875af3a8bc007
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 forge-fechar --dry-run sem a branch local (#898)

Links: pedido v0481 (E14.32, QA E14.41), `docs/fechamento-integrador.md`, `bin/forge-fechar`. Sem UX nem API. Obrigações do brief: o teste removido não tira guarda, criar a ref local não muda o remoto nem outra branch, nada que barra hoje deixa de barrar. Offline, `gh` e `git` falsos (`R-CUSTO`). Clone criado com o `forge-copia` da develop, no head do remoto (1bf95225).

## Achados
- A1 (bloqueante) tests/mutantes/mp1311-fechar-cartao.json:26 · specs de mutante ficaram com o `de` fora da fonte: mp1311 M3 e M5, v0478-fechar-lote-2 FL-M11 e FL-M12 (linhas removidas do dry-run); falha test_forge_mutante.ConferirTodas (AR-12); alinhe no mesmo commit.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Sem a branch local, o dry-run cria a ref sem rastreio na origin/<b> e roda o 1c com o sha dela | `test_1c_no_dry_run_sem_a_branch_local_cria_da_origin_sem_rastreio_e_roda` | ref ausente; sem `branch.<b>.merge` | passou; prova (cai na base) |
| 1c que recusa (rc 1) para com 1 | `test_1c_no_dry_run_sem_a_branch_local_que_recusa_para_com_1` | recusa do 1c | passou; prova |
| Sem local nem origin/<b>: para com 1, manda `git fetch`, sem 1c e sem criar ref | `test_1c_no_dry_run_sem_a_branch_local_nem_a_origin_para_com_1_e_diz_como_destravar` | ambas ausentes | passou; prova; M3 morre |
| Ref que não se cria (lock) para com 1 | `test_1c_no_dry_run_que_nao_cria_a_branch_para_com_1` | falha de criação | passou; prova; M4 morre |
| `--limpar --dry-run` só descreve o passo 7, sem 1c e sem chamadas | `test_limpar_dry_run_sem_a_branch_so_descreve_o_passo_7` | branch e origin ausentes | passou; prova; M1 morre |
| Com a branch local, usa-a e não cria nada | `test_1c_no_dry_run_roda_o_conferir_ref_contra_a_homolog_local_sem_busca` (existente) | branch presente | passou; M2 morre |
| Teste ajustado: dry-run avisa "não consegui conferir" | `test_dry_run_avisa_quando_nao_consegue_ler_o_diff` (agora sem a origin/develop) | base ausente | passou; mesma obrigação |

## Conferências do brief
- Teste removido `test_dry_run_sem_branch_local_marca_o_sha_como_nao_lido`: o marcador existia só para o caso "sem branch local, sai 0". O caso agora cria a ref ou para com 1; nenhuma guarda sumiu, o que ele protegia (1c que não roda não sai 0) é provado pelos testes novos acima. O que ficou sem teste (marcador) deixou de existir no código.
- Criar a ref não toca o remoto nem outra branch: sonda em arquivo (servidor bare, clone separado, `git branch --no-track` como no script): refs do servidor iguais, refs remotas do clone iguais, `.git/config` igual, sem `branch.<b>.merge`, só `refs/heads/melhoria/x` nova. `--ref` passa antes por `git check-ref-format --branch` (linha 217), sem nome começando por `-`.
- Nada que barra hoje deixa de barrar: o diff só endurece (o caso "1c não rodou, sai 0" virou sai 1); a base ausente no `--limpar --dry-run` não pula checagem anterior ao bloco.
- Risco aceito, sem achado: a ref criada de uma origin/<b> velha fica atrás do servidor; o passo real compara com o `ls-remote` e para no passo 2.

## Provas
- Pacote `test_fechar.py` no head 1bf95225: 114 testes, OK (skipped=1; `shellcheck` ausente aqui, o CI cobre).
- `bin/forge-mutante tests/mutantes/v0481-fechar-dryrun-branch.json` (rev=1bf95225578a): M1 :1660, M2 :1671, M3 :1673, M4 :1674, todos `morreu`.
- `forge-testes --vermelho b224ee09e78032d99a9682d6ffd2da534ae6ae60 --modulos test_fechar`, rc=0: `vermelho: base=b224ee09e780 head=1bf95225578a módulos=test_fechar`; revertidos à base: bin/forge-fechar, changelog, doc; contagem: não prova (passa na base)=108; prova (asserção)=5; pulado=1. Os 5 que provam: os 4 `test_1c_no_dry_run_sem_a_branch_local_*`/`que_nao_cria_*` e `test_limpar_dry_run_sem_a_branch_so_descreve_o_passo_7`.
- `python3 -I -m unittest discover -s tests -p test_forge_mutante.py -k ConferirTodas`: FALHA (1 de 4), mesma falha do CI (suíte parte 4/5, 3.12 e 3.14: `test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes`). `bin/forge-mutante --conferir --todas` lista mp1311 M3, M5 e v0478-fechar-lote-2 FL-M11, FL-M12 com o trecho 0 vezes em bin/forge-fechar.
- CI: a run do sha 1bf95225 foi cancelada pelo push seguinte (pareceres); partes 4/5 vermelhas pela falha acima. Sem `- ci:` (as partes que contam não estão verdes).

## Bugs
- Alta (o A1, sem arquivo próprio: o brief limita o commit ao parecer): specs de mutante vencidas pela mudança.

## Veredito
Reprovado em 1bf95225: o comportamento novo está provado (5 provas, 4 mutantes mortos, sonda sem efeito no remoto), mas a mudança deixa 4 mutantes de outros pedidos sem o trecho e a suíte do CI cai. Revalidar com `forge-check parecer delta` depois de alinhar as specs.
