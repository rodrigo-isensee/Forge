---
tipo: revisao-seguranca
contrato: 1
pedido: impl-catraca-2
branch: melhoria/impl-catraca-2-c3
commit: 4bed4549a3133a12bb407c0ae0784f80a5008ad5
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-catraca-2 (branch c3)

## Gatilhos
R-SEGURANCA, gatilho de controles do Forge: a mudança é na isenção que tira a catraca da leitura estática do ambiente git (`tests/test_ambiente_git.py`). O controle em si (`tests/catraca.py`) não muda.

Item entregue: E3 do pedido (CATRACA-ISENCAO-AMBIENTE, C3 do desenho com a correção da seção 3.3 do modelo de ameaças `docs/security/ameacas/catraca-2.md`). Diff lido: `234dbe0..4bed454`, commits `7ef13bc` (teste), `2d9ff06` (fragmento) e `4bed454` (parecer do review).

M14 (`agents/tech-lead.md:19`): cumpre. `git diff --numstat --no-renames 234dbe0 4bed454` conta 28 linhas de teste (`tests/test_ambiente_git.py`, 26+2); o fragmento de `changelog.d/` e o parecer `.md` ficam fora. Abaixo de 150, um comportamento só (o motivo da isenção da catraca e a guarda dele), sem arquivo de `hooks/`, `.githooks/`, `bin/`, `.github/` nem de `PROTEGIDOS`.

## Achados
- A1 (recomendado) tests/test_ambiente_git.py:294 · C3-3 do modelo (lista positiva dos subcomandos do git da catraca) não entrou, e a guarda só acha `fetch` como argumento direto de chamada: um `subprocess.run(["git", ..., "fetch"])` em lista, como o de `tests/catraca.py:465`, escaparia.

## Detalhe dos achados
Conferido contra o modelo de ameaças, 3.3:
- C3-1: o motivo novo (`tests/test_ambiente_git.py:30-33`) cita o `merge-tree --write-tree` pelo forge-check, o `fetch` para `refs/catraca/pull/<n>` com `maintenance.auto=false` e `gc.auto=0` na própria chamada, e não diz mais que só lê. Bate com o fonte (`tests/catraca.py:912`).
- C3-2: `test_todo_fetch_da_catraca_leva_a_manutencao_desligada_na_propria_chamada` (`:291`) lê pela árvore de sintaxe, por chamada, com piso de um `fetch` achado (a guarda não passa vazia).
- C3-4 e T3-1: `test_motivo_da_excecao_cita_o_que_o_arquivo_escreve` (`:279`) exige `fetch` e proíbe "só lê" no motivo de quem faz `fetch`, e exige `merge-tree --write-tree` de quem chama o forge-check.
- Provas por mutação, refeitas numa cópia do head em `$TMPDIR`: tirar os dois `-c` do `fetch` de `tests/catraca.py:912` deixa T3-2 vermelho (falha de asserção, subteste `linha=912`); voltar o motivo ao texto de `234dbe0` deixa T3-1 vermelho (2 falhas). No head, os 17 testes de `tests.test_ambiente_git` passam.

A1: severidade baixa, sem caminho de ataque hoje. Quem acrescentasse à catraca um subcomando que escreve, ou um `fetch` em lista sem os `-c`, mexeria num arquivo de `PROTEGIDOS`, com review, segurança e o rótulo do dono; o risco é a isenção ficar falsa sem nenhum teste vermelho, não uma liberação. O pedido (E3) pede o motivo e a guarda do fetch, e a branch entrega os dois; por isso não devolve. Correção mínima: a guarda C3-3, que lê os subcomandos das chamadas `git(...)` e das listas `["git", ...]` de `tests/catraca.py` e exige que estejam contidos em {`show`, `ls-tree`, `diff`, `merge-base`, `log`, `rev-list`, `rev-parse`, `cat-file`, `fetch`}, e que estende a guarda do `fetch` às listas. Esforço P; dono: tech-lead, numa próxima mexida.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodei `python3 -m unittest tests.test_ambiente_git` no head revisado (17 testes, OK). `gitleaks`, `semgrep` e `zizmor` não estão no PATH: lacuna registrada; o diff é só de teste e não traz credencial, workflow nem configuração.
