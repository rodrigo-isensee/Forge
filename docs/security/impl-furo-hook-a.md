---
tipo: revisao-seguranca
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a4
commit: 59c53536717189520afd72c24340f1066fa1c274
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-furo-hook-a, branch a4

Etapa E1.3 do pedido `impl-furo-hook-a` (brief `impl-furo-hook-a-security-engineer-2`). Diff lido: `234dbe0..59c5353`, incluindo a volta 1 (`4b67f82`, `ddf8bf3`). Modelo de ameaças: `~/.forge-contrib/docs/security/ameacas/furo-hook.md`, §4.5. Não sou o autor.

## Item entregue e M14
- **Item:** E4, A4 FC-SUBCOMANDO-HOOK. O `conformidade` lê o que o `forge-check` grava em todo papel (`args_do_forge_check`, `forge_check_grava`, `FORGE_CHECK_ESCRITAS`).
- **M14 (decisão M14, `agents/tech-lead.md:19` na develop):** contam `hooks/conformidade.py` (42) e `tests/test_hooks.py` (19): 61 linhas, abaixo de 150. As fixtures de `tests/hooks/`, `tests/mutantes/`, `docs/hooks.md`, `changelog.d/` e os pareceres ficam fora. Uma classe de comportamento em `hooks/` (o destino da escrita do `forge-check` passa pela política de caminhos), com corpus próprio (22 fixtures `fc-*`). **Cumpre.**

## Gatilhos
R-SEGURANCA, controles do Forge: o hook `conformidade` (R-CONFORMIDADE), que protege o registro de decisão (R-DECISAO) e o brief aprovado (R-BRIEF).

## Achados
- A1 (recomendado) hooks/conformidade.py:69 · forge-check não reconhecido grava o pedido pelo dev: `find . -exec forge-check anotar …`, `echo anotar … | xargs forge-check`, `bin/forge-chec? anotar`, `{forge-check,anotar} …`, `python3 - anotar … < bin/forge-check`, cópia renomeada. Cartão.
- A2 (recomendado) hooks/conformidade.py:78 · com o nome opaco, `--t decisao` sai 0: o argparse aceita prefixo de 1 letra, e `abreviacao_de` exige mais de 3 caracteres. Conte qualquer prefixo de `--tipo`, ou `anotar` sozinho, como a forma do anotar. É o A2 do review.

## Detalhe dos achados
Sondas: cada uma monta a fixture `fc-anotar-dev-bloqueia` (papel dev) pelo `Fixture`/`rodar` da própria worktree e roda o hook real. Nada rodou contra repositório real, rede ou produção.

**O que a branch fecha (saem 2 pelo dev):** `forge-check anotar` com `--tipo decisao` e com `--tipo historico` (a linha `conferida`), `--raiz`/`--raiz-pedidos` antes do subcomando (com `=` e separados), `xargs` com o subcomando na linha, `xargs -I{}`, `timeout 5`, `sh -c '…'`, o nome entre aspas ou escapado (`"forge-check"`, `forge-chec\k`, `an\otar`, `"anotar"`), `F=forge-check; $F anotar`, `$(command -v forge-check) anotar --tipo=…`, `brief gerar --grav` e `--gr`, e `transcricao anonimizar a.jsonl docs/pedidos/p1.md`. O corpus de legítimos sai 0: `forge-check pr p1` e `conferencia registrar` pelo dev, e as contraprovas do jarvis nas fixtures. O destino é conferido nas duas raízes (`.` e `~/.forge-contrib`), qualquer que seja o `--raiz-pedidos`. Para o dev, isso é mais estrito que o destino real e cobre o C-A4-1 sem depender do nome do pedido. Rodei `test_fixtures_do_lote_furo_hook_a` e `test_a4_todo_subcomando_do_forge_check_que_grava_esta_classificado` no HEAD revisado, os dois com `OK`.

**A1, recomendado.** Evidência: `args_do_forge_check` (`hooks/conformidade.py:69-80`) reconhece o programa pelo nome-base, por uma palavra `forge-check` entre os argumentos do interpretador ou pelo `$`/crase no nome. Sondas com saída 0, do dev, todas gravariam a linha `DECISÃO DO DONO` em `docs/pedidos/p1.md`:
- `find . -maxdepth 0 -exec forge-check anotar --pedido p1 --tipo decisao --literal sim \;`;
- `echo anotar --pedido p1 --tipo decisao --literal sim | xargs forge-check`;
- `bin/forge-chec? anotar …` e `python3 bin/forge-chec* anotar …` (glob no nome);
- `{forge-check,anotar} --pedido p1 …` (chaves do bash);
- `python3 - anotar … < bin/forge-check` e `python3 /dev/stdin anotar … < bin/forge-check` (o programa pela entrada padrão);
- `python3 -c "exec(open('bin/forge-check').read())" anotar …`;
- `cp bin/forge-check /tmp/fc && /tmp/fc anotar …`.

Caminho: só deliberado. A sessão, por injeção, escolhe uma forma que esconde o programa ou o subcomando. A mesma intenção já grava o pedido pelo N6 (interpretador que monta o caminho), limite aceito no modelo e no [B] de `docs/hooks.md`. Por isso não bloqueia. Severidade média, pelo ativo (o registro de decisão do dono). Correção mínima (cartão, com a do N6): falhar fechado pelo texto. Fora do jarvis, a linha cujo texto cita `forge-chec` (sem o `k`, para pegar o glob), ou que tem `find` com `-exec`/`-execdir`/`-ok`/`-okdir`, ou `xargs`, antes de um `forge-check` sem subcomando legível recusa, a menos que o subcomando lido seja um dos que só leem. Isso pede uma lista positiva dos subcomandos de leitura do `forge-check`, mantida pelo mesmo teste estrutural do A4. Esforço M. Dono: tech-lead. O texto de `docs/hooks.md:41` ("atrás de lançador") promete mais do que o hook faz no `find` e no `xargs` com o subcomando na entrada. Restrinja o texto aos lançadores lidos, como pede o A3 do review.

**A2, recomendado.** Evidência: `hooks/conformidade.py:78` usa `abreviacao_de(a, ("--tipo",))`, que exige mais de 3 caracteres. `$(command -v forge-check) anotar --pedido p1 --t decisao --literal sim` sai 0 (`--t` é prefixo único de `--tipo` no subparser `anotar`). Caminho: deliberado, e exige o nome opaco junto com a opção abreviada. Severidade baixa. Correção mínima: na forma opaca, `anotar` como palavra livre já basta para recusar fora do jarvis, sem exigir o `--tipo`. Esforço P. Dono: tech-lead.

**Cartões do review (pergunta do brief):** nem o A2 nem o A3 do review bloqueiam. Os dois pedem contorno deliberado, da mesma classe do N6, já aceito como limite. O A1 acima amplia o A3 do review com as formas glob, chaves, entrada padrão e cópia, para o cartão sair com a família inteira.

Dimensão nova para a matriz do modelo (§8, Mecanismo): **programa por glob, por chaves, pela entrada padrão ou copiado com outro nome**. A expansão do shell aparece também nas branches a2, a3 e a5.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sondas locais pelo harness de fixtures, execução das fixtures do lote e do teste estrutural. `gitleaks`, `semgrep`, `osv-scanner`, `zizmor`, `actionlint` e `bandit` não estão no PATH (lacuna registrada; o diff não traz segredo, dependência nem workflow).
