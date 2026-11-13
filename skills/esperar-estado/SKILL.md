---
name: esperar-estado
description: Padrão único de espera pelo estado de um objeto (o PR no GitHub, com saída em MERGED ou CLOSED; o envio longo lançado em segundo plano, com saída na linha rc= do log), com teto de 170 s por chamada do Bash. Use sempre que um agente precisar esperar um PR, os checks dele ou um comando lançado em segundo plano.
---

# Esperar pelo estado

Quem espera um PR espera o PR, não os checks. Um check antigo da branch pode seguir "em andamento" depois que o PR já foi integrado, e um laço só sobre os checks (como `gh pr checks --watch`) não termina nunca.

## Regras
1. **Espere pelo estado do objeto, não pelo processo.** Cada objeto tem estado terminal: o PR fica `MERGED` ou `CLOSED`; o envio grava a linha `rc=` no log. O laço sai no primeiro estado terminal que ler.
2. **Uma chamada do Bash, em primeiro plano, de no máximo 170 s** (aos 180 s a ferramenta a passa para segundo plano): 5 voltas de 30 s. Não use `timeout` com `sh -c`, nem `--watch`, nem `run_in_background` para esperar. Se o teto chega antes do estado terminal, a chamada imprime `fim=teto` e sai com código diferente de 0; repita a mesma chamada, que relê o estado do zero.
3. **PR:** a cada volta, leia primeiro o estado (`gh pr view <n> --json state --jq .state`); fora de `OPEN`, saia. Em `OPEN`, leia `gh pr checks <n>`: o código 8 quer dizer checks pendentes (conferido em `gh pr checks --help`, "Additional exit codes"); qualquer outro código encerra a espera com ele.
4. **Envio longo (ou qualquer comando de mais de 170 s) num subagente:** o segundo plano morre quando o turno do subagente acaba. Lance o comando com o `run_in_background` da ferramenta, gravando num log de caminho literal que termina com a linha `rc=`; no mesmo turno, espere com o laço da regra 2 sobre `grep -q '^rc=' <log>`. **Nunca encerre o turno nem devolva o relatório com um processo em segundo plano pendente.**
5. **Trava `pesado` (R-TETO):** espere pelo sumiço de `.forge/run/pesado.json` ou pelo `desde` gravado nele mais o teto da trava, lendo o arquivo (só leitura); nunca por `kill -0` no pid gravado (o pid de outro namespace não aparece e a espera acaba antes da hora).
6. **CI longo (e2e de uns 20 min) na sessão principal:** lance o laço do PR sem teto, o segundo bloco de "O laço do PR", com o `run_in_background` da ferramenta e siga com outro trabalho; o aviso de término chega quando o laço sai (`fim=MERGED`, `fim=CLOSED`, `fim=checks:<código>` ou `fim=erro`), sem prazo de 170 s e sem repetir chamadas. O subagente não tem essa saída (regra 4): segue a regra 2 e repete a chamada de 170 s até o estado terminal.

## O laço do PR
Troque `123` pelo número do PR e rode da pasta do repositório dele:

```bash
n=123; fim=""; for i in $(seq 1 5); do e=$(gh pr view "$n" --json state --jq .state) || { fim=erro; break; }; [ "$e" = OPEN ] || { fim="$e"; break; }; gh pr checks "$n" >/dev/null 2>&1; c=$?; [ "$c" -eq 8 ] || { fim="checks:$c"; break; }; sleep 30; done; echo "fim=${fim:-teto}"; [ -n "$fim" ]
```

Sem teto, só para o segundo plano da sessão principal (regra 6); a saída é a mesma, sem `fim=teto`:

```bash
n=123; while :; do e=$(gh pr view "$n" --json state --jq .state) || { echo "fim=erro"; break; }; [ "$e" = OPEN ] || { echo "fim=$e"; break; }; gh pr checks "$n" >/dev/null 2>&1; c=$?; [ "$c" -eq 8 ] || { echo "fim=checks:$c"; break; }; sleep 30; done
```

## O que a saída quer dizer
| Saída | Código | O que fazer |
|---|---|---|
| `fim=MERGED` | 0 | O PR foi integrado: siga para o passo seguinte (limpeza, relatório); não espere mais nenhum check. |
| `fim=CLOSED` | 0 | O PR foi fechado sem integrar: relate; não reabra por conta própria. |
| `fim=checks:0` | 0 | PR aberto com todos os checks verdes. |
| `fim=checks:<outro>` | 0 | PR aberto com check reprovado (1) ou outro erro do `gh`: leia `gh pr checks <n>` e relate. |
| `fim=erro` | 0 | O `gh` não leu o estado (rede, credencial, número errado): relate a mensagem dele. |
| `fim=teto` | 1 | Passou o teto com o PR aberto e checks pendentes: repita a mesma chamada. |

No sandbox, se o `gh` reclamar do cache, rode o laço com `XDG_CACHE_HOME` apontando para uma pasta gravável (por exemplo, `${TMPDIR:-/tmp}`).

## O envio longo
Lance com o `run_in_background` da ferramenta, trocando `<envio>` pelo comando e `<log>` pelo caminho absoluto, escrito por extenso, de um log próprio da tarefa (sem `$TMPDIR` nem `$?`, que a `conformidade` recusa ao lado do envio):

`<envio> > <log> 2>&1 && echo rc=0 >> <log> || echo rc=1 >> <log>`

No mesmo turno, em primeiro plano, espere pelo log, trocando `<log>` pelo mesmo caminho:

```bash
log=<log>; fim=""; for i in $(seq 1 5); do fim=$(grep -m 1 '^rc=' "$log" 2>/dev/null) && break; sleep 30; done; echo "fim=${fim:-teto}"; [ -n "$fim" ]
```

`fim=rc=0` é sucesso; `fim=rc=1` é falha: leia o log e relate. `fim=teto` (código 1) quer dizer o comando ainda rodando: repita a mesma chamada, sem encerrar o turno. Vale para o `bin/forge-fechar` com `--espera` acima de 170 s: lance-o no lugar de `<envio>` e, com `fim=rc=1`, leia no log a linha `fim: código <n>` dele (3 é integrado com limpeza pendente).
