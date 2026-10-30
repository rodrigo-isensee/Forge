---
tipo: review
contrato: 1
pedido: pn1-desde-base
branch: melhoria/pn1-desde-base
commit: ee49b7ef07337f4abf940b5da94036fbba641028
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Code review: o Base-sha do brief como Desde na branch nova (P-N1)

Escopo: `git diff 99315cfb42c6852c7d7959cd6dca8161e2bd5c08...ee49b7ef07337f4abf940b5da94036fbba641028` (7 commits): `bin/forge-check` (+15 -2), `tests/test_conferencia_base_dono.py` (+48), `tests/mutantes/pn1-desde-base.json` (+54), `agents/conferente.md` (+1 -1), `changelog.d/pn1-desde-base.md` (+2). Primeira rodada: sem parecer anterior, sem delta.

## Conferido
- `desde_e_a_base` (`bin/forge-check:834`) segue as DECISÕES TÉCNICAS de 20:28 e 20:42 do PN1-DESDE-BASE: vale com `--desde` igual ao Base-sha, Base-sha ancestral do head e o Histórico sem `conferida` ou com a última fora do head; a última `conferida` ancestral do head segue sendo o Desde (cai no `desde_valido` e reprova o Base-sha); branch que não nasce do Base-sha cai no ramo antigo e reprova.
- Não afrouxa `R-PROVA`: no ramo novo `valido` fica `None`, então o intervalo, a contagem, o corte da integração e a exigência dos pareceres na `merge-integracao` são os mesmos de rodar sem `--desde` (branch inteira). A linha `escopo: Base-sha fora da branch` continua independente do ramo.
- Linha `base: Base-sha do brief (sem conferida na branch)` informativa (não reprova), coberta por `assertEqual` da saída inteira; texto de uso no topo do `bin/forge-check` atualizado.
- Testes (`DesdeNoBaseSha`, 4 casos): sem conferida, com conferida no head, conferida de branch anterior fora do head (e a linha do dono não conta como conferida), branch que não nasce do Base-sha. `python3 -m unittest tests.test_conferencia_base_dono`: 28 testes, OK.
- Mutação (ferramenta): `bin/forge-mutante tests/mutantes/pn1-desde-base.json` rc 0, M1 a M6 `morreu` (`bin/forge-check:1076`, `:839`, `:839`, `:840`, `:839`, `:838`). A spec cobre cada guarda da expressão (AR-1 conferido).
- Teto M14: contam `bin/forge-check` (17) e `tests/test_conferencia_base_dono.py` (48) = 65 linhas, abaixo de 150; um comportamento só; sem `hooks/`. `bin/forge-check` está em `PROTEGIDOS` (`tests/catraca.py:43`): o PR precisa do rótulo `afrouxa-regra` do dono depois do último push (decisão do dono 2026-10-29 20:41, item A), para a etapa do PR.
- `agents/conferente.md`: 110 linhas; a frase nova cabe na regra de volta por delta. Changelog: fragmento novo em `changelog.d/`, sem edição do `CHANGELOG.md`.
- Segurança e QA: pareceres próprios em paralelo (E2.1, E3.1), não refeitos aqui.

## Achados
- A1 (bloqueante) agents/conferente.md:85 · requisito (objetivo do PN1-DESDE-BASE): o caminho novo é inalcançável pelo canal canônico; a mensagem de entrega põe em Desde a última conferida (bin/forge-check:4681), nunca o Base-sha, e a exceção só vale com Desde igual ao Base-sha; a conferência segue travando.

## Parecer
Reprovado, por um achado de requisito; o código do `forge-check entrega` em si está correto e bem testado.

A1 · `agents/conferente.md:85` e `bin/forge-check:4681` · classe: caminho novo inalcançável pelo canal canônico (o comando aceita, mas a mensagem que alimenta o conferente nunca o produz). O conferente usa o `Desde:` da mensagem do Jarvis, que vem de `forge-check brief mensagem --entrega` e é enviada sem edição (`agents/jarvis.md:65`). Esse comando grava `Desde: {bases[-1][0]}`, a última linha do Histórico, mesmo fora do head. No caso do squash, o conferente recebe a conferida velha, ela bate com o Histórico, roda `--desde <velha>` e sai `escopo: --desde sem conferência anterior`; a exceção nova (`Desde:` igual ao Base-sha) nunca chega. Sugestão, à escolha do autor: (a) no `conferente.md`, com a última `conferida` da mensagem fora do head (`merge-base --is-ancestor` rc 1), rodar com `--desde <Base-sha>` e copiar a linha `base:`; ou (b) o `mensagem_de_entrega` emitir o Base-sha como `Desde:` nesse caso, com teste. Severidade: bloqueia.

Sem linha AR nova nesta rodada (DECISÃO TÉCNICA 2026-10-29 15:28 do T1-CONF-ESCOPO-REV); a classe fica citada acima.
