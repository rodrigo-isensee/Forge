---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/ci-env-argv0-v2
commit: 91055e7f82bb19884565ddc004d02c910bd3e80a
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: ci-env-argv0

Mudança: passo `env com -a` nos jobs `bateria-python-tres-quatorze` e `bateria` do `ci.yml` (o segundo atrás do gate `pesada`): instala `rust-coreutils` por apt, liga `/usr/lib/cargo/bin/coreutils/env` em `$RUNNER_TEMP/env-argv0/env`, põe no PATH e confere `-a`, para a prova viva de 20 formas do lançador voltar ao CI. Reempilhada sobre ci-comentario-rapida (8bcc469, que já está sobre a migração ao 26.04). HEAD de código: 91055e7; os commits seguintes só tocam `docs/`. Mudança só de workflow, sem teste Python novo: a prova do passo é o próprio passo. QA local, sem runner 26.04: a confirmação em runner real (pacote, caminho e `env --version` no 26.04) fica para o primeiro run do PR.

## Achados
- A1 (recomendado) .github/workflows/ci.yml:62 · o caminho `/usr/lib/cargo/bin/coreutils/env` e o nome `rust-coreutils` valem para o 24.04; no 26.04 só o primeiro run confirma, e o passo falha fechado se mudarem

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| O passo falha fechado se o uutils não for instalado | CT-02 | alvo ausente | passou (rc=1) |
| O passo falha fechado se o `env` achado não aceita `-a` | CT-03 | env GNU 9.4 como alvo | passou (rc=1) |
| O passo passa e põe o uutils no PATH com um `env` que aceita `-a` | CT-04 | caminho feliz | passou (rc=0) |

## Cenários e resultado real
| ID | Obrigação | Verificação | Resultado |
|---|---|---|---|
| CT-01 | O problema existe e o passo é necessário | `env -a x true` nesta máquina (GNU coreutils 9.4) | `invalid option -- 'a'`, rc=125 |
| CT-02 | Alvo ausente | o bloco `run` extraído do `ci.yml` por script, com `sudo` falso, `RUNNER_TEMP` e `GITHUB_PATH` em diretório descartável; `bash -n` e execução | sintaxe ok; `faltou /usr/lib/cargo/bin/coreutils/env depois da instalação`, rc=1 |
| CT-03 | `env` sem `-a` | mesmo bloco com `alvo=/usr/bin/env` | `env: invalid option -- 'a'` e `o env ... não aceita -a`, rc=1 |
| CT-04 | `env` com `-a` | mesmo bloco com alvo falso que aceita `-a x` e `--version` | `env (uutils coreutils) 0.fake`, rc=0 |
| CT-05 | Os dois blocos são iguais; o do job `bateria` tem o gate `if: ${{ !cancelled() && steps.gate.outputs.pesada == 'true' }}` | comparação dos dois blocos extraídos e leitura das linhas 56 e 258 | blocos idênticos; gate presente só no segundo; ambos antes do passo `Testes do Forge` do job |
| CT-06 | Nenhum `runs-on` mudou | `git diff 8bcc469 HEAD -- .github` filtrado por `runs-on` | 0 linhas |
| CT-07 | Testes dos workflows | `python3 -m unittest discover -s tests -p test_ci_local.py` | 54 testes, OK |

## Lacunas
- Sem PyYAML, sem actionlint e sem runner 26.04 aqui: instalação real do pacote, o caminho do binário e o `which` no PATH do runner ficam para o primeiro run do PR.
- Sem teste Python: o vermelho antes do verde aqui é o CT-01 mais CT-03 (sem o uutils, `-a` falha e o passo reprova); não há teste de unidade a reprovar sobre a base.
- Quem instala o `rust-coreutils` usa `sudo apt-get` com a rede do runner; falha de rede reprova o job (falha fechada, por desenho).

## Resultado
Aprovado, sem bugs abertos.
