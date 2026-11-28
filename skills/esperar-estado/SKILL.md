---
name: esperar-estado
description: Espera pelo estado de um objeto (o PR, com saída em MERGED ou CLOSED; o envio em segundo plano, com saída na linha rc= do log), com teto de 170 s por chamada. Use ao esperar um PR ou um comando em segundo plano.
---

# Esperar pelo estado

Espere o PR, não os checks. Um check antigo pode seguir "em andamento" depois do PR integrado, e um laço sobre os checks (`gh pr checks --watch`) não termina.

## Regras
1. **Espere o estado do objeto, não o processo.** O PR fica `MERGED` ou `CLOSED`; o envio grava a linha `rc=` no log. O laço sai no primeiro estado terminal que ler.
2. **Uma chamada do Bash, em primeiro plano, de no máximo 170 s** (aos 180 s a ferramenta a manda ao segundo plano): 5 voltas de 30 s. Não use `timeout` com `sh -c`, nem `--watch`, nem `run_in_background` para esperar, salvo a regra 6. Se o teto chega antes do estado terminal, a chamada imprime `fim=teto` e sai com código 1; repita-a, que relê o estado.
3. **PR:** a cada volta, leia o estado (`gh pr view <n> --json state --jq .state`); fora de `OPEN`, saia. Em `OPEN`, leia `gh pr checks <n>`: o código 8 quer dizer checks pendentes (`gh pr checks --help`, "Additional exit codes"), e `no checks reported` (código 1, PR recém-aberto) também; outro código encerra a espera com ele.
4. **Envio longo (ou comando de mais de 170 s) num subagente:** o segundo plano morre quando o turno acaba. Lance-o com o `run_in_background`, com log de caminho literal que termina na linha `rc=`; no mesmo turno, espere com o laço da regra 2 sobre `grep -q '^rc=' <log>`. **Nunca encerre o turno nem devolva o relatório com um processo em segundo plano pendente.**
5. **Trava `pesado` (R-TETO):** espere o sumiço de `.forge/run/pesado.json` ou o `desde` gravado nele mais o teto da trava, lendo o arquivo; nunca por `kill -0` no pid gravado (o pid de outro namespace não aparece e a espera acaba cedo).
6. **CI longo (uns 20 min) na sessão principal:** lance o laço sem teto de `envio-longo.md` nesta skill com o `run_in_background` e siga com outro trabalho; o aviso chega quando o laço sai. O subagente não tem essa saída (regra 4): segue a regra 2 e repete a chamada de 170 s até o estado terminal.

## O laço do PR
Troque `123` pelo número do PR e rode na pasta do repositório:

```bash
n=123; fim=""; for i in $(seq 1 5); do e=$(gh pr view "$n" --json state --jq .state 2>/dev/null) || { fim=erro; break; }; [ "$e" = OPEN ] || { fim="$e"; break; }; s=$(gh pr checks "$n" 2>&1); c=$?; case $s in *"no checks reported"*) c=8;; esac; [ "$c" -eq 8 ] || { fim="checks:$c"; break; }; sleep 30; done; echo "fim=${fim:-teto}"; [ -n "$fim" ]
```

## O que a saída quer dizer
| Saída | Código | O que fazer |
|---|---|---|
| `fim=MERGED` | 0 | Integrado: siga para a limpeza e o relatório; não espere check. |
| `fim=CLOSED` | 0 | Fechado sem integrar: relate; não reabra por conta própria. |
| `fim=checks:0` | 0 | PR aberto com todos os checks verdes. |
| `fim=checks:<outro>` | 0 | Check reprovado (1) ou outro erro: leia `gh pr checks <n>`. |
| `fim=erro` | 0 | O `gh` não leu o estado (rede, credencial, número): relate. |
| `fim=teto` | 1 | Teto com o PR aberto e checks pendentes: repita. |

Cache do `gh` só de leitura: `XDG_CACHE_HOME` em pasta gravável (por exemplo, `${TMPDIR:-/tmp}`).

## O envio longo
Lance com o `run_in_background`, trocando `<envio>` pelo comando e `<log>` pelo caminho absoluto de um log próprio (sem `$TMPDIR` nem `$?`, que a `conformidade` recusa ao lado do envio):

`<envio> > <log> 2>&1 && echo rc=0 >> <log> || echo rc=1 >> <log>`

No mesmo turno, em primeiro plano, espere o log, com o caminho literal 3 vezes (`envio-longo.md`):

```bash
for i in $(seq 1 5); do grep -q '^rc=' <log> 2>/dev/null && break; sleep 30; done; echo "fim=$(grep -m 1 '^rc=' <log> 2>/dev/null || echo teto)"; test -f <log> && grep -q '^rc=' <log>
```

`fim=rc=0` é sucesso; `fim=rc=1` é falha: leia o log. `fim=teto` (código 1) é o comando ainda rodando: repita, sem encerrar o turno. O `bin/forge-fechar <pedido> --ref <branch> --espera <s>` com espera longa: `envio-longo.md` nesta skill.
