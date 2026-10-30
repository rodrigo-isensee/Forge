---
tipo: review
contrato: 1
pedido: pn1-desde-base
branch: melhoria/pn1-desde-base
commit: 23a66bb075998d91fd4ca94642ad9f32d0ec6180
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Code review: o Base-sha do brief como Desde na branch nova (P-N1)

Escopo: `git diff 99315cfb42c6852c7d7959cd6dca8161e2bd5c08...23a66bb075998d91fd4ca94642ad9f32d0ec6180`. Segunda rodada (volta 1), revalidação por delta sobre o parecer anterior (`98ca200`, reprovado, head `ee49b7e`).

## Delta lido
`bin/forge-check delta --parecer docs/reviews/pn1-desde-base.md`: intervalo `ee49b7ef07337f4abf940b5da94036fbba641028..23a66bb075998d91fd4ca94642ad9f32d0ec6180`; lidos `bin/forge-check` (+20 -9: linhas 79, 834-848, 4673-4692, 5321), `tests/mutantes/pn1-desde-base.json` (+32: 52-83) e `tests/test_mensagem_conferente.py` (+41 -1: 9, 100-139). Os pareceres de segurança (`123bafd`) e de QA (`4749f3e`) do intervalo não foram relidos. Já lido na rodada anterior e fora do delta: `tests/test_conferencia_base_dono.py`, `agents/conferente.md`, `changelog.d/pn1-desde-base.md`.

## Conferido
- A1 resolvido pela opção (b), conforme a DECISÃO TÉCNICA de 2026-10-29 21:18: `mensagem_de_entrega` (`bin/forge-check:4686-4692`) emite `Desde: <Base-sha>` quando há `conferida` no Histórico, a última está fora do head da worktree e o Base-sha é ancestral dele; com a última `conferida` ancestral do head, segue ela; sem `conferida`, o comportamento de antes (ausente ou a base fixada pelo dono). O conferente recebe o Base-sha e cai na exceção já descrita em `agents/conferente.md:85`; o caminho novo do `entrega` passa a ser alcançável pelo canal canônico.
- Regra numa função só: `base_sha_como_desde` (`bin/forge-check:834`) guarda a condição; `desde_e_a_base` só acrescenta `desde == base_sha`. Sem duplicação da expressão.
- A ancestralidade na mensagem roda no git da worktree (`a.worktree`, `HEAD`), não na raiz (classe AR-7 conferida; o M9 a guarda). Worktree que não é repositório: `e_ancestral` sai falso nos dois lados e a mensagem fica como antes (os testes antigos de `MensagemPelaEtapaDoBrief` passam).
- Texto de uso (`bin/forge-check:79`) e `--help` do `--entrega` (`:5321`) atualizados (AR-9 conferido).
- Testes `DesdeNaBranchNova` (3 casos, repositório real na worktree): conferida fora do head dá o Base-sha; conferida ancestral do head segue sendo o Desde; sem conferida, ausente ou a base do dono. `python3 -m unittest tests.test_mensagem_conferente tests.test_conferencia_base_dono`: 42 testes, OK.
- Mutação (ferramenta): `bin/forge-mutante tests/mutantes/pn1-desde-base.json` rc 0, M1 a M10 `morreu` (M7 `:4688`, M8 `:4692`, M9 `:4689`, M10 `:846`). Cada guarda nova tem mutante (AR-1 conferido).
- Teto M14: `bin/forge-check` (36), `tests/test_conferencia_base_dono.py` (48), `tests/test_mensagem_conferente.py` (42) = 126 linhas, abaixo de 150; um comportamento só (o Base-sha como Desde, no comando e no gerador da mensagem); sem `hooks/`. `bin/forge-check` está em `PROTEGIDOS`: o PR espera o rótulo `afrouxa-regra` do dono depois do último push (decisão do dono 2026-10-29 20:41, item A), na etapa do PR.
- Segurança e QA: pareceres próprios (E2.1, E3.1) sobre este head, em paralelo; não refeitos aqui. `forge-check pr` aponta hoje o QA desatualizado (`bin/forge-check` mudou), a ser renovado na rodada paralela.

## Achados
- A2 (recomendado) bin/forge-check:4688 · com a conferida velha fora do head e uma base fixada pelo dono mais recente, a mensagem troca a base do dono pelo Base-sha; o intervalo fica mais largo (seguro), mas ignora a base escolhida pelo dono; sugestão: só aplicar o Base-sha quando a última linha do Histórico for `conferida`.

## Parecer
Aprovado. O A1 da rodada anterior (classe: caminho novo inalcançável pelo canal canônico) está resolvido no delta, com teste e mutante. Sem bloqueante nesta rodada; o A2 é recomendação e não devolve.

Sem linha AR nova nesta rodada (DECISÃO TÉCNICA 2026-10-29 15:28 do T1-CONF-ESCOPO-REV); a classe do A1 fica citada acima.
