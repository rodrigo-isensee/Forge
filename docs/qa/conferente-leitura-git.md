---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/conferente-leitura-git
commit: dcfc75052a01d12cbea143d8c428710495adc53d
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# Parecer de QA - CONFERENTE-LEITURA-GIT (E8)
Base dc615c25a89cf801dbff0356ff3e07cf491e4567; código ce4409a e dcfc75052a01d12cbea143d8c428710495adc53d (head testado; só testes e este parecer depois). Execução só dos testes tocados (R-TETO).

## Escopo
O `forge:conferente` lê `git branch` (sem argumento, `--list [padrão]`, `-r`, `--contains <commit>`) e `git worktree list` (sem opção) por gramática exata (`forma_de_leitura_git`); o resto é recusado (R-CONFORMIDADE). Fora do escopo: outros papéis, que não mudam.

## Critério -> teste -> resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Leituras permitidas passam (`git branch`, `--list 'p'`, `-r`, `--contains` com espaço e `=`, `-C`/`--no-pager`, `worktree list`) | `test_passam_as_formas_de_leitura` | forma exata; global só `-C`/`--no-pager` | passa |
| Escrita recusada: `-D -d -m -f -u`, `--set-upstream-to`, `--unset-upstream`, `--edit-description`, `--del`, abreviação, `branch x` | `test_recusam_...` + `test_qa_...` (novo) | opção curta/longa/abreviada, argumento solto | passa (rc 2) |
| `worktree add/remove/prune/lock/unlock/move/repair`, `list -v`, `list --porcelain` | idem | só `list` sem opção | passa (rc 2) |
| Escape: `-c x=y`, `--git-dir`, `--work-tree`, `;`, `&&`, `\|`, `\|\|`, `$()`, crase, `>`, `>>`, `2>`, `--contains=-D`/`=$(pwd)` | `test_qa_encadeamento_e_escape_seguem_recusados` (novo, 26 entradas) | gramática da linha + valor de `--contains` | passa (rc 2) |
| Outro papel não ganha a leitura | `test_outro_papel_e_a_forca_de_leitura_nao_mudam` | `GIT_LEITURA` intacto | passa |

Nenhuma forma de escrita ou escape escapou da guarda.

## Execução real
- `python3 -m unittest tests.test_guarda_conferente`: `Ran 20 tests`, `OK`, rc=0 (incluem os 2 testes novos de QA e o teste de recusa já do autor).
- Vermelho: `forge-testes --vermelho dc615c2 --modulos test_guarda_conferente`: `contagem: não prova (passa na base)=19; prova (asserção)=1`, rc=0. Prova: `test_passam_as_formas_de_leitura` (base recusa, head libera). Os testes de recusa passam na base por desenho (a base recusa tudo); a prova deles é a mutação.
- Mutação: `forge-mutante --cobertura --base dc615c2` listou 14 condições sem mutante (o autor não declarou spec). Escrevi `tests/mutantes/versao-033-qa.json` (12 mutantes sobre `forma_de_leitura_git` e `git_so_leitura`): `bin/forge-mutante tests/mutantes/versao-033-qa.json --processos 3`, saída 0, Q1 a Q12 `morreu`. Linhas 403, 404, 406, 408 a 412, 414, 415, 417, 422, 1137, 1138 cobertas; 406 (`i < len(args)`) e 413 sem mutante próprio, o laço é exercitado por todos os casos.
- Acessibilidade e E2E: não se aplicam (hook sem tela).

## Achados
- A1 (recomendado) hooks/conformidade.py:417 · `git branch --show-current` e `git worktree list --porcelain` ficam recusados (documentado em docs/hooks.md); o pedido de QA os listava como leitura. Se o dono os quer, vira novo pedido; não é defeito.

## Parecer
Aprovado: as leituras passam, e as 50 variantes de escrita ou escape testadas seguem recusadas (R-CONFORMIDADE).
