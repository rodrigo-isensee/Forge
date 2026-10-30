---
tipo: review
contrato: 1
pedido: mutante-casa-espaco
branch: melhoria/mutante-casa-espaco
commit: 572c025c8c6e5078f1f78127b4f864a3b6b42b6e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: mutante-casa-espaco

Pedido MUTANTE-CASA-ESPACO (FM1, PR 1), etapa E1.1 do MUTANTE-CASA-ESPACO-REV, rodada 2. Revalidação por delta sobre o parecer 490ff93 (que valia para 16beca1); head revisado 572c025.

## Achados

## Revalidação por delta (rodada 2)
- **Delta lido** (`forge-check delta --parecer docs/reviews/mutante-casa-espaco.md`, intervalo 16beca1..572c025; conferido também `git diff 9829a70..572c025`, só o commit 572c025): `bin/forge-mutante`:415-416, `tests/mutantes/mutante-casa-espaco.json`:63-65, `tests/test_forge_mutante.py`:667-671.
- **Já lido** (rodada 1, sem mudança): a lógica de `casa` (bin/forge-mutante:411-430), o portão que não afrouxa, os outros três asserts do teste novo, C1-C3, C5, C6, o fragmento de changelog.
- **A1 resolvido.** O C4 passa de `equivalente` a `testes` com `test_de_e_para_que_dividem_o_espaco_junto_da_condicao_casam`; `bin/forge-mutante tests/mutantes/mutante-casa-espaco.json` (rev 572c025c8c6e) dá `C4 · morreu · bin/forge-mutante:420`, rc 0. Classe da rodada 1 (equivalente declarado que o teste mata) registrada aqui, sem linha AR nesta rodada (DECISÃO TÉCNICA 2026-10-29 15:28 do T1-CONF-ESCOPO-REV).
- **A2 resolvido.** A docstring diz "basta um alinhamento em que o trecho mudado inteiro fique dentro do nó", que é o que o código faz.
- **4º assert (tests/test_forge_mutante.py:667-671).** Mudança só de teste: o `SyntaxError` vira `self.fail` com mensagem, e o `assertFalse` segue sobre o mesmo caso. O comportamento verificado continua: `casa` devolve False sem aplicar a troca fora do nó; com o C4 aplicado, o teste falha (agora como falha, não erro), e é isso que mata o C4.
- **Teto M14.** `git diff --numstat --no-renames 042e5d8...572c025`: `bin/forge-mutante` 8+3, `tests/test_forge_mutante.py` 12+0 = 23 de 150; spec em `tests/mutantes/`, fragmento e `.md` ficam fora. Um comportamento só.

## O que foi conferido (rodada 1, sobre 16beca1)
- **Função `casa`, portão, teste novo, changelog, neutralidade, custo:** ver parecer 490ff93; nada disso mudou no delta.

## Saída das ferramentas (citada, rev 572c025)
- `python3 -m unittest tests.test_forge_mutante`: 68 testes, OK.
- `bin/forge-mutante tests/mutantes/mutante-casa-espaco.json`: C1, C2, C3, C4, C5 e C6 morreram; rc 0.
- `bin/forge-mutante --cobertura --base 042e5d8f73fc659615a4313c7213a661dfc32ce0`: a condição de bin/forge-mutante:425 coberta por C5; rc 0.
- shellcheck: sem shell no diff.

## Parecer
Aprovado. Os dois achados da rodada 1 foram resolvidos no delta; nada novo.
