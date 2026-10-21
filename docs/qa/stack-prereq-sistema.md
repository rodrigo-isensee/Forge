---
tipo: qa
contrato: 1
pedido: stack-prereq-sistema
branch: melhoria/stack-prereq-sistema
commit: 399e4f8107be134eb54b2c7aba6f20a977461bc1
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA - pré-requisitos do sistema (stack node-react, M15)

Links: `docs/reviews/stack-prereq-sistema.md`, pedido `stack-prereq-sistema`. Sem UX nem API; as obrigações são E1 e E2 do pedido. Offline, nada instalado, sem `sudo` (`R-CONFORMIDADE`, `R-CUSTO`). A árvore testada (HEAD c38ecb9) só soma o review sobre o código 399e4f8.

## Resultados
| ID | Obrigação / cenário | Fronteira protegida | Resultado |
|---|---|---|---|
| CT-01 | E1: seção, comando de instalação e pré-voo presentes em `stacks/node-react/pronto.md` | n/a | Passou: seção "Pré-requisitos do sistema", `npx playwright install --with-deps chromium`, `ldd ... \| grep 'not found'`, frase de pedido ao usuário |
| CT-02 | E2 e teste novo `tests/test_stack_prereq_sistema.py` + Neutralidade | n/a | Passou: `python3 -m unittest discover -s tests -q`, 1086 testes, OK (276 s) |
| CT-03 | `scripts/validar-plugin.sh` | n/a | Passou: `Validation passed` (tentativas de rede do sandbox negadas; sem efeito no resultado) |
| CT-04 | Pré-voo, cache vazio (`PLAYWRIGHT_BROWSERS_PATH` apontando para pasta vazia em `$TMPDIR`) | vazio | Sem linha `not found`; sai `ldd: ./: not regular file` no stderr, rc=1 (mesmo rc do sucesso). Distingue só pela mensagem do `ldd` |
| CT-05 | Pré-voo, binário `chrome` presente e completo (cópia de `/bin/true`) | n/a | Nenhuma linha, rc=1: sucesso |
| CT-06 | Pré-voo, binário com biblioteca ausente (cópia de `/bin/true` com o nome da lib trocado por `libnspr4.`) | lib faltando | Saída `libnspr4. => not found`, rc=0: falha detectada |
| CT-07 | Clareza para quem não conhece a stack | n/a | Passou: diz o que é, quem roda, por que, o que esperar e a frase pronta; o texto tem passo único |

Cache real do Playwright não existe nesta máquina (nenhum `chrome-linux` em `/`): o caso "cache presente" foi montado com binários sintéticos, não com o Chromium real.

## Vermelho antes do verde e mutação
Sem código de produção; o teste novo é estrutural sobre texto. Vermelho não reexecutado (o review registra). Mutação: sem ferramenta na stack do Forge; não executada.

## Observações não bloqueantes
- Cache vazio: o pré-voo não imprime `not found` e o `ldd` reclama de `./`; quem lê só "nenhuma linha" pode tomar por sucesso (já no review, `pronto.md:39`). Sugestão: citar a mensagem `not regular file` como sinal de "navegador ainda não baixado".
- O texto usa `npx` numa stack que usa `pnpm`; funciona, só vale alinhar numa próxima edição.

## Achados

## Veredito
Aprovado sobre 399e4f8: zero bugs abertos; recomendações acima não bloqueiam.
