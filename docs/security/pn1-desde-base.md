---
tipo: revisao-seguranca
contrato: 1
pedido: pn1-desde-base
branch: melhoria/pn1-desde-base
commit: 23a66bb075998d91fd4ca94642ad9f32d0ec6180
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-29
---
# Review de segurança: pn1-desde-base

Escopo: `git diff 99315cfb42c6852c7d7959cd6dca8161e2bd5c08...23a66bb075998d91fd4ca94642ad9f32d0ec6180`. Revalidação por delta do parecer `123bafd` (head anterior `ee49b7e`): `forge-check delta` sobre `4749f3e..23a66bb` lista só `bin/forge-check` (`base_sha_como_desde`, `desde_e_a_base`, `mensagem_de_entrega`, ajuda e docstring), `tests/mutantes/pn1-desde-base.json` (M7 a M10) e `tests/test_mensagem_conferente.py` (`DesdeNaBranchNova`). Volta 1: a mensagem de entrega emite o Base-sha em `Desde:` quando a última conferida está fora do head da worktree.

## Gatilhos
Controle do Forge (`R-SEGURANCA`): `bin/forge-check entrega` decide o intervalo que o conferente lê (`R-PROVA`), e `brief mensagem --entrega` gera o `Desde:` que o conferente usa.

## Achados
- A1 (recomendado) bin/forge-check:840 · conferida antiga ancestral do Base-sha (branch anterior integrada por merge, não por squash) segue recusando o Desde igual ao Base-sha; lado seguro, só usabilidade, fora da P-N1 (mantido de 123bafd)
- A2 (recomendado) bin/forge-check:4688 · com conferida fora do head e base fixada pelo dono mais recente no Histórico, a mensagem emite o Base-sha e não a base do dono; confere a branch inteira (mais, nunca menos); lado seguro, fidelidade à decisão do dono

## Detalhe dos achados
**Refatoração (`bin/forge-check:834-846`):** `base_sha_como_desde` é a condição antiga sem o `desde == base_sha`, que passou para `desde_e_a_base`; a conjunção é a mesma (última conferida não ancestral do head e Base-sha ancestral do head). O `cmd_entrega` (`bin/forge-check:1082`) chama `desde_e_a_base` como antes; a invariante do parecer anterior (ramo novo com `valido = None`, intervalo idêntico ao da chamada sem `--desde`) não mudou. M10 guarda a ancestralidade da conferida no `entrega`.

**Mensagem (`bin/forge-check:4686-4692`):** o `Desde:` é só um insumo; o portão continua sendo o `forge-check entrega` sobre a branch real (`--branch`), que reconfere tudo com o seu próprio head, e o conferente (`agents/conferente.md:85`) confere o `Desde:` contra o Histórico e a ancestralidade na branch. Uma mensagem errada, portanto, só pode levar a recusa ou a intervalo maior, nunca a conferir menos. Sondas (cenário de `DesdeNaBranchNova`, em `$TMPDIR`):
- Worktree com HEAD de outra branch (destacado no Base-sha, conferida da branch real fora desse HEAD): a mensagem emite o Base-sha; no `entrega`, a conferida é ancestral do head da branch real, `desde_e_a_base` é falso e sai `escopo: --desde sem conferência anterior` (rc 1, a recusa de hoje; `test_com_conferida_no_historico_o_base_sha_segue_recusado`). Lado seguro.
- `--worktree` que não é repositório: `git merge-base` falha, `e_ancestral(base_sha, HEAD)` é falso e a mensagem cai na conferida antiga (comportamento de hoje). Lado seguro.
- Base-sha fora do HEAD da worktree: `squash` falso, conferida antiga. Lado seguro.
- Sem conferida no Histórico: `squash` falso (M7); a base fixada pelo dono segue emitida.
- Entradas do git: o Base-sha passa pela expressão de 40 hex (`bin/forge-check:868`) e as conferidas pela `CONFERIDA` (sha40); sem injeção de opção. `--worktree` exige caminho absoluto existente; o `git()` tira as variáveis `GIT_*` e tem limite de tempo; quem a passa é o Jarvis.

**A1, detalhe.** Evidência: `bin/forge-check:840` (condição mantida na refatoração). Caminho de ataque: nenhum (a falha é recusar). Severidade: informativa. Correção mínima, se o dono quiser o caso: tratar como "sem conferida na branch" também a última conferida ancestral do Base-sha. Esforço: P. Dono: `tech-lead`. Não devolve.

**A2, detalhe.** Evidência: `bin/forge-check:4688` (`squash` olha só as linhas `conferida`) e `bin/forge-check:4692`. Sonda: Histórico com `DECISÃO DO DONO`, conferida da branch anterior fora do head e depois `base do delta fixada pelo dono <c1>`: sai `Desde: <Base-sha>`, não `<c1>`; o conferente aplica a exceção do squash e o `entrega` confere a branch inteira. Caminho de ataque: nenhum (o intervalo cresce). Severidade: informativa. Correção mínima: `squash` só quando a linha mais recente (`bases[-1]`) é `conferida` (`bases[-1][1] == "conferida"`), com o teste do caso. Esforço: P. Dono: `tech-lead`. Não devolve.

**PA-7 (`docs/engineering/achados-recorrentes.md`):** AR-1 conferido (M7 a M10 cobrem a condição `squash`, a escolha do Base-sha, a pasta do git e a guarda do `entrega`); AR-2: o ramo de falha (worktree que não é repositório) não tem teste próprio, mas cai no comportamento antigo (sonda acima), assunto do QA; AR-3 e AR-5 não se aplicam (sem lista negativa nem python novo em hook); AR-7 conferido: o git da mensagem roda com `-C <--worktree>` explícito, e M9 guarda a pasta; AR-8 a AR-10 não se aplicam (texto de ajuda e docstring atualizados; `agents/conferente.md` já descrevia a exceção).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff e do delta (`forge-check delta`), `python3 -m unittest tests.test_mensagem_conferente tests.test_conferencia_base_dono` (42 testes, OK) e três sondas da mensagem. `gitleaks` e `semgrep` não estão no PATH (lacuna registrada; o diff não traz credencial nem configuração).
