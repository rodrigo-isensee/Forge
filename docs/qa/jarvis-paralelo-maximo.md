---
tipo: qa
contrato: 1
pedido: jarvis-paralelo-maximo
branch: melhoria/jarvis-paralelo-maximo
commit: 7fd503451ad679f2b9aa93984dc0af132e69f7b2
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# QA: jarvis-paralelo-maximo

Commit testado (código): `7fd5034`; HEAD da branch `3569626` só acrescenta pareceres de review e segurança (docs).

## Critério → teste → resultado
| Critério | Teste | Resultado | Fronteira protegida |
|---|---|---|---|
| Regra do dono de paralelo máximo em `agents/jarvis.md`, dentro de `R-TETO` e `R-WIP` | Leitura da linha 44 + invariante "toca sempre o máximo de itens ao mesmo tempo" | OK; apagada a frase numa cópia em `$TMPDIR`, `test_trechos_obrigatorios` falhou | teto de agentes (`R-TETO`, `R-WIP`) |
| Melhoria vale para o Forge e todos os projetos | Leitura da linha 76 + invariante "vale para o Forge e para todos os projetos que o usam" | OK; apagada a frase na cópia, o teste falhou | n/a |
| Nada contradiz a série por arquivo em comum nem os portões | Leitura das linhas 44 a 47 | OK: "espera só por dependência real ou série por arquivo em comum"; `R-TETO`/`R-WIP` citados; portões intactos | série por arquivo em comum |
| Suíte e plugin | `unittest discover -s tests -q`; `scripts/validar-plugin.sh` | 1194 testes OK; validação passou | n/a |

## Vermelho antes do verde
Os dois invariantes novos foram vistos falhando ao remover cada frase de `agents/jarvis.md` (cópia de `git archive HEAD` em `$TMPDIR`) e passam com o texto presente.

## Achados
