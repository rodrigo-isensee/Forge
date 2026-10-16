---
tipo: qa
contrato: 1
pedido: ta-5
branch: melhoria/ta-5-fechamento
commit: 24883170f8fd067b5ba1efff2f3180a98707e4d1
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-16
---
# QA - TA-5 (`bin/forge-fechar`, passos mecânicos de fechamento)

Sem UX nem API. Código testado: 2488317 (implementação 27f3868 + volta do autor) sobre a base 15660a3. O HEAD da branch (c95761b) só acrescenta as revalidações de review e segurança sobre 2488317 (2 arquivos em `docs/reviews/` e `docs/security/`, ambos `parecer: aprovado`, `commit: 2488317`); não há código diferente do testado. Pré-condição conferida: ambos aprovados.

## Obrigação -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| PQ-1 | Suíte verde | `python3 -m unittest discover -s tests -q` | n/a | 722 testes, OK (258 s) |
| PQ-2 | Plugin válido | `scripts/validar-plugin.sh` | n/a | "Validation passed" |
| PQ-3 | Pareceres de review e segurança antes do QA | `grep ^parecer` nos dois arquivos | portão R-REVIEW/R-SEGURANCA | ambos `aprovado`, em 2488317 |
| EX-a | `--dry-run` não muda nada | repo temporário, fakes de gh e forge-check; `for-each-ref` + `status` antes/depois; registro das chamadas | nada executado | imprime os 7 passos, rc=0, refs e árvore idênticas, registro de chamadas com 0 bytes |
| EX-b | Para no primeiro erro, mensagem clara | (b1) forge-check rc=1; (b2) head local difere do remoto | passos 1 e 2 | b1: "parou no passo 1 ... nada foi aberto nem mesclado", rc=1, só `forge-check` registrado; b2: "parou no passo 2: o head local (..) difere do remoto (..)", rc=1, nenhum `gh` chamado |
| EX-c | Base main recusada | `--base origin/main`, `--base main`, `--base origin/homolog`, `--ref main` | base main/fora do fluxo | as quatro: rc=1 com a regra citada (R-MAIN/R-FLUXO), nenhuma chamada ao fake |
| EX-d | Check vermelho ou pendente para | check `fail`; check `pending` com `--espera 0` | vermelho; pendente no limite | rc=1 nos dois, "há check vermelho" / "ainda pendentes após 0s"; 0 chamadas `pr merge` |
| EX-e | Rótulo pedido e não aplicado para | texto do PR cita `afrouxa-regra`, sem rótulo | rótulo ausente | rc=1 "o dono ainda não o aplicou; o script nunca aplica rótulo"; 0 `pr merge`. Rótulo já aplicado segue: coberto por `test_rotulo_pedido_e_aplicado_pelo_dono_segue` (não repetido) |
| EX-f | Tudo verde mescla pelo método certo e limpa | fluxo completo com os fakes | método de R-FLUXO | `gh pr merge melhoria/x --squash --match-head-commit <sha do remoto>`, estado MERGED, branch remota e local apagadas, rc=0; nunca `--force`, `--no-verify`, `label` |
| EX-g | Dry-run contra o GitHub real (só leitura) | `bin/forge-fechar ta-5 --ref melhoria/ta-5-fechamento --dry-run` | n/a | rc=0, 7 passos impressos, árvore da worktree limpa; por desenho o dry-run não consulta o GitHub (nem gh nem git remoto), então "contra o real" só confirma que não executa nada. Com `FORGE_CHECK` sem `FORGE_FECHAR_TESTE=1`: aviso em stderr e comandos reais |
| EX-h | `forge-check pr ta-5 --ref HEAD --base origin/develop` | rodado depois de commitar este parecer | parecer QA presente | rc=0, sem achados |

## Mutação manual no arquivo alterado
Sem ferramenta de mutação para o Bash da fábrica; mutei à mão, em cópia temporária, seis pontos de `bin/forge-fechar` e rodei `python3 -m unittest tests.test_fechar -q` (base: 22 testes, OK).
| Mutante | Resultado |
|---|---|
| M1 remove `--match-head-commit` do merge | morto (5 falhas) |
| M3 aceita check `fail` | morto (1 falha) |
| M4 aceita base main (`alvo=main`) | morto (1 falha) |
| M5 ignora o rótulo | morto (1 falha) |
| M6 ignora `--dry-run` | morto (1 falha) |
| M2 remove só a recusa explícita de base main no passo 6 | **sobrevive**, justificado: a linha seguinte (`[ base = $alvo ]`) recusa qualquer base diferente da develop, inclusive main; o mutante é equivalente em comportamento (só muda a mensagem). A defesa em profundidade fica |

Vermelho antes do verde: os testes de `tests/test_fechar.py` são do autor; os mutantes M1, M3, M4, M5 e M6 mostram cada obrigação falhando sem o código que a guarda, o que cumpre o papel (não houve stash do código de produção, porque o script é arquivo novo).

## Bugs
Nenhum. Observações (não são bugs, já documentadas em `docs/fechamento-integrador.md` ou no review): o passo 5 lê texto livre do PR, e o controle real do rótulo é a Catraca no passo 4; shellcheck não está instalado nesta máquina e roda na bateria do CI.

## Veredito
Aprovado: nenhum bug aberto, todas as obrigações com evidência. Não declara segurança; o parecer de segurança é de `docs/security/ta-5.md`.
