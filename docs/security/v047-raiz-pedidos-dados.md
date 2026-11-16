---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-raiz-pedidos-dados
commit: ccd65b30e4075f293df74851fa5ab09919c105e2
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047-raiz-pedidos-dados

Intervalo revisado: `develop` (bf475209) até `ccd65b30` (E2.73 do pedido v047; etapa E2.100). Arquivos: `bin/forge-check`, `bin/forge-placar`, `tests/test_voltas.py`, `tests/evals/test_placar.py`, `tests/mutantes/v047-raiz-pedidos-dados.json`, `changelog.d/v047-raiz-pedidos-dados.md`.

## Gatilhos
Mudança em `bin/forge-check` e `bin/forge-placar`, ferramentas de fábrica que leem o quadro, os briefs e os pedidos (`R-SEGURANCA`). Os dois comandos tocados (`voltas` e o placar) são só leitura; nenhum controle de bloqueio foi afrouxado (`R-CONFORMIDADE`).

## Achados

## Sondas

## Detalhe dos achados
Sem achado bloqueante nem recomendação. O que foi verificado:

- `bin/forge-check:9690-9691`: `voltas` passa a usar `--raiz-pedidos` como raiz de leitura, igual ao `dora` (`:9693`). O valor já passou pela trava de confinamento em `:9606-9614` (só `~/.forge-contrib`, a raiz do repositório ou a raiz principal, comparadas após `resolve()`). Sondas: `voltas --raiz-pedidos /etc` e `--raiz-pedidos /root/.forge-contrib/../../etc` saem com rc=2 e a mensagem de fora do confinamento, sem ler nada.
- `bin/forge_voltas.py`: sem escrita em arquivo nem subprocesso; a troca de raiz não abre caminho de gravação.
- `bin/forge-placar:469,499-500`: `--raiz-pedidos` substitui o `--raiz` e não tem confinamento, mas o `--raiz` também nunca teve: o placar é só leitura, sem rede, e o único subprocesso (`git -C`, `:145`) usa o `--git`, não a raiz. O argumento vem do próprio operador local: sem caminho de ataque realista, não é achado.
- Testes: ambiente reduzido a `PATH` e `HOME` temporário, `python -I` e `cwd` no clone falso (AR-4 e AR-5 conferidos); só fixtures em diretório temporário. Mutantes RP-M1 e RP-M2 cobrem as duas linhas novas e morrem (AR-1, AR-12 conferidos). Sem segredo, rede nem caminho pessoal no diff.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: fica com o CI do PR (`R-REVIEW`); rodei localmente `tests.test_voltas.VoltasComRaizDePedidos` e `tests.evals.test_placar.Medir.test_raiz_pedidos_fora_do_clone_vale_sobre_o_raiz` (2 testes, OK) e `forge-mutante tests/mutantes/v047-raiz-pedidos-dados.json` (RP-M1 e RP-M2 morreram). Ferramentas de varredura de segredos e SAST não estão no PATH deste ambiente (lacuna registrada; o diff foi lido inteiro e não traz credencial).
