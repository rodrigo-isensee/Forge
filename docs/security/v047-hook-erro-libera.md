---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-hook-erro-libera
commit: 9666b6bf53214ef46d9069cd1a38b5809b88c72a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v047-hook-erro-libera

Pedido v047, etapa E3.40: segurança por delta `4c350b2f..9666b6bf` (junção da develop com conflito resolvido em `tests/test_hooks.py`), sobre o parecer aprovado da E3.36. Lido: `forge-check parecer delta` (no domínio: `bin/forge-testes` e `tests/test_hooks.py`; `tests/apoio_volta_unica.py` fora do domínio) e `git diff 4c350b2f HEAD -- hooks` (vazio: `hooks/conformidade.py`, `_comum.py`, `agentes.py` e `hooks.json` idênticos aos do parecer anterior). Rodado no head: `tests.test_hook_erro_libera` (11 testes, verdes). Sem PR, sem CI do head: suíte inteira não rodada (carga da máquina, diretriz 15).

## Delta
- Nenhum controle de segurança mudou: o código do hook é byte a byte o da E3.36, então A1 e A2 seguem fechados e C1 a C8 seguem cumpridos.
- `tests/test_hooks.py`: `nucleos_do_processo` passa a morar em `tests/apoio_volta_unica.py` e volta por import no fim do módulo (ciclo resolvido; importado e chamado no head, devolve 12). A resolução do conflito não perdeu a função nem o teste de segurança do `gh` que não responde.
- `test_hooks.py` (teste do `gh` pendurado): o teto passa a `(limite-1) * fator_de_carga()`, com fator preso em 2. Timeout do hook é 10, teto máximo 18 s, abaixo do `sleep 30` do teste: uma regressão que prenda o hook ainda falha, então o teste não perde poder de detecção.
- `bin/forge-testes`: uma linha de mapa (`templates/projeto/.forge/config.json` roda `test_ritmo`); só seleciona teste, não afrouxa controle.

## Achados
- A3 (recomendado) hooks/conformidade.py:2878 · Sem mudança: termo só literal, `cp x docs//pedidos/v1.md` e formas ofuscadas passam com erro ou prazo (S7 a S9 da E3.36); exige ofuscação deliberada.
- A4 (recomendado) hooks/_comum.py:2791 · Sem mudança: declarar no PR o número medido na E3.17 e a limitação do erros.log (C5).
- A5 (recomendado) hooks/conformidade.py:2831 · Sem mudança: cartão para a guarda normal sobre troca de base por opção ou variável (`env -C`, `git --work-tree`, `GIT_WORK_TREE`, `git -C <dir> apply`, `git apply --directory`).
- A6 (recomendado) hooks/conformidade.py:2874 · Sem mudança: `git reset --hard origin/x` na develop passa com erro ou prazo; pre-push e proteção do remoto seguram o envio.

## Sondas
Nenhum bloqueante neste delta; as sondas S1 a S10 da E3.36 valem, pois `hooks/` não mudou.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Risco declarado antes (configuração corrompida recusa escrita na raiz, disponibilidade) segue igual e vai ao dono pelo Jarvis. `gitleaks`, `zizmor` e `actionlint` não aplicáveis (sem segredo, workflow ou dependência no delta).
