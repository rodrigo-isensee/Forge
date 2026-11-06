---
tipo: qa
contrato: 1
pedido: versao-034
branch: melhoria/lote-estoque-b
commit: fb390efc8e6e3b27c4a1f18b5a22bfc997231cb3
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-06
---
# QA: lote-estoque-b (E2.5, junção de 7 itens de CI e catraca)

Base do parecer: o log da suíte inteira do push do lote (/tmp/push-lote-b2.log, head enviado 84472bf, o commit julgado), sem rodar a suíte de novo, pela decisão do dono de 2026-11-05 14:59. Resultado do log: processo 1 com 969 testes (rc 0), processo 2 com 1663 testes (rc 0), 2632 testes em 92 módulos, `OK (skipped=30)`, `push_rc=0`. Os pareceres de cada item (QA, review e segurança) seguem valendo e não foram revistos.

## Achados
- A1 (recomendado) .github/workflows/ci.yml:56 · o passo `env com -a` (CI-ENV-ARGV0, nos jobs de teste e bateria) não tem teste local que confira o conteúdo; só a execução no CI o prova. Cobrir com asserção de texto em test_ci_local.
- A2 (recomendado) tests/apoio_volta_unica.py:438 · o `env_gnu` de fb390ef (parcial reprova, total passa) não tem teste com `env` falso no `PATH`; só o uso indireto no T9b o exercita. Cobrir com dois testes e `cache_clear`.

## Critério → teste → resultado
| Critério (o que mudou na junção) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| catraca-ramo-cmd-pr: o parecer é o da branch do PR (E11) | tests/test_catraca.py, os três `test_e11_*` | parecer de outra branch no desempate; tipo exigido só em outra branch | passou (suíte do push) |
| catraca-fork: head de outro repositório é recusado | test_catraca.py: fork com nome de branch já mesclada, fork sem arquivo sensível e nas promoções, CI sem BASE_REPO, workflow declara as duas variáveis, mesmo repositório, CLI por env | `head.repo` nulo; CI sem `BASE_REPO`; mesmo repositório | passou |
| catraca-fork somado ao catraca-ramo (junção em tests/catraca.py, `violacoes_de_pareceres` com `repo_head` e `repo_base` e `ramo` passado ao `cmd_pr`) | os mesmos dois grupos, no mesmo módulo, rodados juntos no processo 1 | assinatura nova com padrões vazios | passou |
| ci-comentario-rapida: texto do topo do ci.yml | `test_comentario_do_topo_diz_que_a_rapida_roda_a_suite` | texto do comentário | passou |
| ci-ubuntu-26: runner fixado em todo job (ci, catraca, release) | `test_todo_job_roda_no_ubuntu_26_04` | job novo sem runner fixado | passou |
| ci-env-argv0: passo do uutils em dois jobs | só execução no CI; sem teste de texto local | n/a | sem teste local (A1) |
| lote-cilista-v2: lista fechada antes do lint | `test_passo_novo_antes_do_lint_reprova` e os testes de lista de env em test_ci_local | passo ou env fora da lista | passou |
| release-pr-so-parecer: PR só de parecer sem fragmento | sete testes novos em tests/test_changelog.py (só parecer, modelo e `ameacas`/`aceites`, renomeação, `_modelo.md` e pasta `_x`, fragmento malformado, fragmento válido, outro arquivo da fábrica) | modelo `_*`, renomeação, fragmento malformado | passou |
| Soma: um só `changelog.d/lote-estoque-b.md` com o nome da branch (volta da E2.1) | tests.test_changelog FragmentoTemONomeDaBranch | mais de um fragmento novo | passou |

## Cenários e resultado real
- Leitura do diff d9b26bb..84472bf: 7 merges first-parent, nenhum com conflito no resultado final (`git show --remerge-diff` sem conteúdo), e o commit 84472bf junta os 7 fragmentos de changelog num só (8 arquivos, 10 linhas a mais, 14 a menos). Todo o código novo (bin/forge-changelog, tests/catraca.py, ci.yml, catraca.yml, release.yml) tem teste no mesmo lote, exceto o passo do uutils (A1).
- A ordem dos merges (catraca-ramo antes de catraca-fork) foi a que o pedido registrou; a combinação dos dois em `violacoes_de_pareceres` é coberta porque os dois grupos de teste vivem em test_catraca.py e passaram juntos.
- Vermelho antes do verde e mutação (R-QA): não repetidos aqui; são dos pareceres de cada item (bin/forge-changelog e tests/catraca.py têm os mutantes declarados nos pedidos de origem), conforme o brief, que veta rever o que cada item já teve aprovado.
- Aviso do log: `catraca: a API do GitHub não respondeu por inteiro (OSError); vale como sem rótulo` é saída da rede do push, não falha de teste.
- Nenhum bug aberto; nada a devolver ao autor da junção.

## Avisos do log (/tmp/push-lote-b2.log)
- linha 5: AVISO: job 'j' pulado por falta de suporte: condição sem suporte (token inesperado): __import__('os').system('touch /tmp/forge-suite-syznibix/p1/tmp4al5vw9n/executou')
- linha 9: AVISO: --confiar: o código do PR de fork de 'dona' vai rodar nesta máquina com o seu ambiente e com a credencial do gh em disco; ela fica exposta a esse código.
- linha 10: AVISO: j/lint pulado: actionlint ausente no PATH
- linha 18: AVISO: j/lint pulado: actionlint ausente no PATH

## Revalidação das voltas do CI
Sobre fb390ef (os commits 7ec3a35, 83b3e55 e fb390ef, mais os pareceres de devops, segurança e review revalidados), sem rodar a suíte de novo. O diff 237c130..fb390ef tem 4 arquivos (`.github/actionlint.yaml`, `ci.yml`, `tests/apoio_volta_unica.py`, o fragmento de changelog).

### Suíte inteira do push de fb390ef (/tmp/push-lote-b8.log, 58 linhas)
Resumo final, copiado (linhas 50 a 58):
- linha 50: processo 1: rc 0, 969 testes, 1401.1 s, 50 módulos
- linha 51: processo 2: rc 0, 1663 testes, 867.3 s, 42 módulos
- linha 53: Ran 2632 tests in 1401.341s (2 processos)
- linha 55: OK (skipped=30)
- linha 58: push_rc=0 05:10:02

Falha, pulo ou aviso do log (nenhuma linha de falha ou erro de teste; o grep por FAIL e ERROR só acha o que está abaixo):
- linha 5: AVISO: job 'j' pulado por falta de suporte: condição sem suporte (token inesperado): __import__('os').system('touch /tmp/forge-suite-qksno4og/p1/tmpgcismzuh/executou')
- linha 9: AVISO: --confiar: o código do PR de fork de 'dona' vai rodar nesta máquina com o seu ambiente e com a credencial do gh em disco; ela fica exposta a esse código.
- linha 10: AVISO: j/lint pulado: actionlint ausente no PATH
- linha 18: AVISO: j/lint pulado: actionlint ausente no PATH
- linhas 46, 47 e 48: `catraca: a API do GitHub não respondeu por inteiro` (KeyError, OSError, OSError), saída da rede do push, não falha de teste.
- pulos: 30 (`skipped=30`), os mesmos 30 do parecer anterior sobre 84472bf; o log não os lista um a um.

### CI do #455 em 83b3e55 (run 42180421859, /tmp/ci-455b-full.log, ubuntu-26.04)
- linha 17: Image: ubuntu-26.04 (job bateria); linha 688: o mesmo no job bateria (python 3.14).
- linha 229: HEAD_SHA: 83b3e5578ea551093e894e7e23a7f62b25288518.
- linhas 624 e 626: Ran 2645 tests in 734.213s (4 processos), depois OK (job bateria).
- linhas 996 e 998: Ran 2645 tests in 1176.666s (4 processos), depois OK (job bateria, python 3.14).
- Os passos `env com -a` com o `gnuenv` rodaram antes dos testes nos dois jobs (linhas 521 a 523 e 899 a 901) e não reprovaram.
- O único `##[error]` do log é na linha 470, no passo dos pareceres (`Process completed with exit code 1`), o vermelho que o brief já descreve; nenhum teste falhou.
- Limite: o CI rodou 83b3e55, não fb390ef. A diferença entre os dois é só o `env_gnu` (fb390ef), coberta pela suíte do push local acima (2632 testes, OK), que roda no `env` desta máquina, não no do 26.04.

### As voltas têm teste? (por leitura)
- 7ec3a35 (`.github/actionlint.yaml` com o label do runner): sem teste de texto; a prova é o passo do actionlint no CI, verde no run acima (o passo não aparece como falha).
- 83b3e55 e fb390ef (`env_gnu` e o `gnuenv` do CI): não há teste com `env` falso no `PATH`, nem o parcial nem o total; `grep` por `env_gnu` acha só `tests/apoio_volta_unica.py` e o uso em `tests/test_hooks_volta_corpus.py:313` (`test_divisao_esta_na_classe`) e em `apoio_volta_unica.py:485` e `:564`. É o achado A2 (recomendado, não bloqueante): o ramo de reprovar é falha fechada por construção, e o passo do CI confere o `gnuenv` com `--s` nos dois jobs.
- Falha fechada, lida em `apoio_volta_unica.py:438-460`: numa máquina com `env` parcial (divide o `-S` separado e recusa alguma grafia de `OPCOES_DE_DIVISAO`) e sem `gnuenv` ou `genv` que divida tudo, `env_gnu` levanta `AssertionError` com a grafia recusada e o caminho. Os testes que o chamam (o T9b: `test_divisao_esta_na_classe` e a montagem dos textos do corpus) reprovam em vez de cair no skip. Só sem nenhum `env` que divida o `-S` separado o retorno é None e o teste pula. Isto é leitura do código; não executei o cenário.
- Parecer: aprovado mantido. Nenhum bug aberto; A2 é recomendação.
