---
tipo: qa
contrato: 1
pedido: bateria-shellcheck-prepush
branch: melhoria/bateria-shellcheck-prepush
commit: c6fc94683001f5f8db2e94b2fa2152f0c34da167
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
revisor: qa-engineer
data: 2026-10-22
---
# QA: bateria-shellcheck-prepush

Entrega testada: diff a3dbe22..c6fc946 (8afd7b3 e c6fc946). Depois dele só entraram os pareceres de segurança e de review, sem código.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 (hook passa no shellcheck do CI) | CT-01: shellcheck 0.10.0 sobre a lista de arquivos do passo do ci.yml | todos os 11 arquivos do passo, incluindo o hook do modelo | passou: rc=0 no HEAD; rc=1 no hook de a3dbe22 (SC2015 linha 58, SC2317 linhas 243 a 246) |
| E1 (sem mudar comportamento) | CT-02: fila_vivas das duas versões em cópia com arquivo vivo travado, morto, link simbólico, diretório e fila vazia | fila vazia (glob sem arquivo), link simbólico, arquivo ausente | passou: saídas idênticas nas duas versões |
| E1 (parar continua pelo trap) | CT-03: diff do hook limita-se a 2 linhas (58 e a diretiva) | corpo de parar e `trap parar TERM INT HUP` intactos | passou |
| E2 (teste vermelho antes, verde depois, sem rede) | CT-04: tests/test_pre_push_shellcheck.py contra o hook de a3dbe22 e contra o HEAD | hook antigo; shellcheck ausente | passou: vermelho (3 falhas) com o hook antigo e shellcheck no PATH; vermelho (2 falhas) sem shellcheck; verde no HEAD; sem rede |
| E2 (fragmento de changelog) | CT-05: changelog.d/bateria-shellcheck-prepush.md existe no diff | n/a | passou |
| Aviso quando o shellcheck falta | CT-06: teste sem shellcheck no PATH | PATH sem a ferramenta | passou: o teste principal pula com "AVISO: shellcheck fora do PATH; o CI roda este passo" e os outros dois rodam |

## Cenários e resultado real
- Ferramenta: shellcheck 0.10.0, binário já baixado em $TMPDIR (sem custo, R-CUSTO). Comando: `shellcheck <lista do passo do ci.yml>`.
- Vermelho antes do verde: `python3 -m unittest tests.test_pre_push_shellcheck` numa cópia com o hook de a3dbe22: `FAILED (failures=3)` com shellcheck no PATH; `FAILED (failures=2, skipped=1)` sem ele (a regex acusa `&& [ ! -L "$f" ] || continue`). No HEAD: `OK` (3 testes) com shellcheck e `OK (skipped=1)` sem.
- Comportamento: a função fila_vivas extraída das duas versões, com fila de arquivo vivo (flock preso), morto, link simbólico e diretório, e com fila vazia: mesma saída, mesmo rc. O link simbólico é pulado como antes.
- `python3 -m unittest tests.test_forge.NeutralidadeDoNucleo`: OK. A suíte completa roda no pre-push do envio.
- Mutação: não se aplica (a mudança é uma reescrita equivalente de uma condição e um comentário; a stack de scripts não tem ferramenta de mutação no `pronto.md` usado aqui).

## Recomendações (não bloqueiam)
- tests/test_pre_push_shellcheck.py:31: a regex só pega `A && B || continue` na mesma linha; outra forma `A && B || C` em fila_vivas passaria, e vale ampliar para `&&.*\|\|` se voltar (como o review disse).
- tests/test_pre_push_shellcheck.py:24: o teste que roda a ferramenta é pulado sem shellcheck no PATH; a garantia real é o job do CI. O aviso está claro, mas a estação não traz a ferramenta (sugestão ao `devops-engineer` para `scripts/preparar-estacao.sh`, cartão à parte).
- A diretiva de parar cobre a função inteira; código inalcançável futuro dentro dela não seria apontado (R1 da segurança).
