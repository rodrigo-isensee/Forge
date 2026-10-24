# lote-leitura-hook-2 - sem o marcador, `env` com `-iu`, `-iC`, `-iS'…'` e `-vS'…'` deixa de ser lido (regressão contra a develop)
- Severidade: alta (segredo e apagar o `.git` passam; o `env` real lê e apaga)
- Responsável sugerido: forge:tech-lead (hooks do Forge; caminho do `software-architect` e do dono, pela decisão de 2026-10-22: 2.ª volta seguida da classe)
- Ambiente: 1b4b0d8b060379d6e078d5ef15c2c63676e41b87 contra a base d150ec87b004f6f5561a65aa130bb16cf454473c, Python 3.14.4, `/usr/bin/env` uutils 0.8.0

## Passos para reproduzir
1. Cópias limpas por `git archive` da base e do head em `$TMPDIR/qa-engineer-lote-leitura-hook/v13/{base,lote}`.
2. Montar o repositório temporário com o `Fixture` do corpus (`tests/test_hooks.py`, modelo do `conformidade`) e alimentar `python3 hooks/conformidade.py` com a entrada JSON do Claude Code, só trocando `tool_input.command` (sonda `v13/s4.py`).

## Resultado esperado
Sem o marcador crítico, as regras que não dependem dele (ler `.env`, apagar o `.git` da raiz) continuam vendo o comando atrás do `env`: rc 2, como na develop. A decisão do dono diz "nada disto é regressão".

## Resultado obtido
| Comando (`conformidade`, sem marcador) | develop | lote |
|---|---|---|
| `env -iu X cat .env` | 2 | 0 |
| `env -iu X rm -rf .git` | 2 | 0 |
| `env -iC / cat .env` | 2 | 0 |
| `env -iS'cat .env'` | 2 | 0 |
| `env -vS'cat .env'` | 2 | 0 |
| `env -u X cat .env` (controle) | 2 | 2 |
| `env -S'cat .env'` (controle) | 2 | 2 |

Sem os hooks, `env -iu X echo OK` imprime `OK` aqui: o `env` real roda o comando depois do valor da opção.

## Evidência
`$TMPDIR/qa-engineer-lote-leitura-hook/v13/s4.py` (saída reproduzida no parecer). Confirma o A1 e o A2 do review (`docs/reviews/lote-leitura-hook.md`, revalidação 13). Causa: `separar_lancadores` (`hooks/_comum.py:1848`) lê o grupo curto `-iu` como opção sem valor, e o `-iS…` (`:2030`) não é mais dividido sem o marcador.

## Contorno
Nenhum para o usuário. Para o hook: o review sugere, sem decidir, ler as duas leituras possíveis (palavra seguinte como valor e como comando; resto do grupo com `S` como texto) ou recusar o lançador com opção fora da tabela também sem o marcador.
