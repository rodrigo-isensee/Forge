---
tipo: qa
contrato: 1
pedido: release-0.47.19
branch: melhoria/marca-0.47.19
commit: 9487d956120b90e783ef1462fcfe83c2b1df7230
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: release 0.47.19 (E12.24) (versão 0.47.19, head 9487d956)

QA da versão inteira para a promoção: `git diff b224ee09..9487d956` (`b224ee09` é a marca da 0.47.18 e ancestral do head; 109 arquivos, +4766 -139). Itens: #874, #877, #885, #886, #890, #892, #895, #896, #897, #898, mais a marca (#905). Cada item entrou na develop com os próprios pareceres (`docs/{reviews,qa,security}/v0481-<item>.md`; QA de cada um presente em `docs/qa/`: catraca-avisos, ci-descendente-parecer, copia-base, d6-resto, docs-ok, fechar-dryrun-branch, g4-f1-aviso, limpar-clone-parecer, pedido-arquiva, perfil-fifo). Aqui se confere a junção, a marca, o CHANGELOG e os manifestos. Modelo: `docs/qa/release-0.47.18.md`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão nos dois manifestos igual ao CHANGELOG | `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` = 0.47.19; `## [0.47.19] - 2026-11-26` | manifestos iguais | passou |
| CHANGELOG em português, `[Não publicado]` vazio | leitura: 11 itens (4 Adicionado, 2 Alterado, 5 Corrigido), todos em português, com id de origem | seção acima da 0.47.18 | passou |
| Os 10 fragmentos estão na seção | 21/21 linhas dos fragmentos da base `cc4376fe` achadas literal | 10 itens, nenhum a mais, nenhum a menos | passou |
| `changelog.d/` sem fragmentos | `bin/forge-changelog conferir-release` | sobra só `README.md` | passou |
| A marca é reprodutível | clone em `cc4376fe` + `forge-changelog release 0.47.19 2026-11-26`: árvore idêntica à de `9487d956` | n/a | passou (IDENTICO) |
| Junção | `git merge-base --is-ancestor b224ee09 HEAD`: ok; log `b224ee09..HEAD` traz os 10 PRs e a marca por cima | corte contém a marca anterior | passou |
| Sem teste pulado indevido | `git diff b224ee09..HEAD -- 'tests/*.py'`: 2 linhas com `skipUnless`, ambas em `tests/test_hooks.py`, condicionadas à capacidade (`os.mkfifo`, `signal.setitimer`), declaradas no #885 (pulos 38→41); nenhum `skip` incondicional nem `expectedFailure` | n/a | passou |
| Controle com mutantes declarados | `bin/forge-check`, `forge-copia`, `forge-fechar`, `forge_tamanho.py`, `hooks/` (`_comum`, `conformidade`, `salvar`, `hooks.json`) e `tests/catraca.py` mudaram | n/a | passou (prova no parecer de cada item; não rerrodei) |
| Pareceres dos itens | QA de cada item presente em `docs/qa/` | n/a | passou |
| Itens que afrouxam regra | #877, #895, #885 e #898 trazem `[afrouxa-regra: ...]` no título, com o motivo; #877 é exceção ao R-VERIFY à espera do dono (registrada no CHANGELOG) | destaque no título | passou; a decisão do dono fica com ele (`R-DECISAO`) |

## Execução
- CI do PR #905: run 45803496622, sha exato `9487d956`, `completed success` (suíte 3.12 e 3.14 em todas as partes, instalação, bateria, catraca).
- Sem código novo além dos 10 itens; a prova de cada um está no parecer do próprio pedido. Sem suíte local.
- Corte de 10 itens, abaixo dos 20, pela autorização fixa do dono (ordem de 25/11 07:52), citada no corpo do #905 com `teto: excedido, 522 linhas, marca de versão`.
- Segurança e acessibilidade: sem tela; a segurança tem parecer próprio (`docs/security/release-0.47.19.md`).
- ci: 9487d956120b90e783ef1462fcfe83c2b1df7230 verde
