---
tipo: qa
contrato: 1
pedido: versao-034
branch: melhoria/lote-estoque-b
commit: 84472bfa6c63406c46a6c86ce6353939a39a53dc
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
