---
name: esperar-estado
description: Padrão único de espera pelo estado de um objeto (o PR no GitHub), com saída no primeiro estado terminal - MERGED ou CLOSED - e teto de 540 s por chamada do Bash. Use sempre que um agente precisar esperar um PR ou os checks dele.
---

# Esperar pelo estado

Quem espera um PR espera o PR, não os checks. Um check antigo da branch pode seguir "em andamento" depois que o PR já foi integrado, e um laço só sobre os checks (como `gh pr checks --watch`) não termina nunca.

## Regras
1. **Espere pelo estado do objeto, não pelo processo.** Cada objeto tem estado terminal: o PR fica `MERGED` ou `CLOSED`. O laço sai no primeiro estado terminal que ler.
2. **Uma chamada do Bash, em primeiro plano, de no máximo 540 s**, contados por voltas: 17 voltas de 30 s. Não use `timeout` com `sh -c`, nem `--watch`, nem `run_in_background` para esperar. Se o teto chega antes do estado terminal, a chamada imprime `fim=teto` e sai com código diferente de 0; repita a mesma chamada, que relê o estado do zero.
3. **PR:** a cada volta, leia primeiro o estado (`gh pr view <n> --json state --jq .state`); fora de `OPEN`, saia. Em `OPEN`, leia `gh pr checks <n>`: o código 8 quer dizer checks pendentes (conferido em `gh pr checks --help`, "Additional exit codes"); qualquer outro código encerra a espera com ele.

## O laço do PR
Troque `123` pelo número do PR e rode da pasta do repositório dele:

```bash
n=123; fim=""; for i in $(seq 1 17); do e=$(gh pr view "$n" --json state --jq .state) || { fim=erro; break; }; [ "$e" = OPEN ] || { fim="$e"; break; }; gh pr checks "$n" >/dev/null 2>&1; c=$?; [ "$c" -eq 8 ] || { fim="checks:$c"; break; }; sleep 30; done; echo "fim=${fim:-teto}"; [ -n "$fim" ]
```

## O que a saída quer dizer
| Saída | Código | O que fazer |
|---|---|---|
| `fim=MERGED` | 0 | O PR foi integrado: siga para o passo seguinte (limpeza, relatório); não espere mais nenhum check. |
| `fim=CLOSED` | 0 | O PR foi fechado sem integrar: relate; não reabra por conta própria. |
| `fim=checks:0` | 0 | PR aberto com todos os checks verdes. |
| `fim=checks:<outro>` | 0 | PR aberto com check reprovado (1) ou outro erro do `gh`: leia `gh pr checks <n>` e relate. |
| `fim=erro` | 0 | O `gh` não leu o estado (rede, credencial, número errado): relate a mensagem dele. |
| `fim=teto` | 1 | Passaram 540 s com o PR aberto e checks pendentes: repita a mesma chamada. |

No sandbox, se o `gh` reclamar do cache, rode o laço com `XDG_CACHE_HOME` apontando para uma pasta gravável (por exemplo, `$TMPDIR`).
