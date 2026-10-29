---
tipo: review
contrato: 1
pedido: vel-p1p10
branch: melhoria/vel-p1p10
commit: 0b4585f172afa6ba0c1e535da996938711ada03e
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Code review: entrega menor e verificadores do autor (VEL-P1P10, P1 e P10)

Escopo: primeira rodada (`R-REVIEW`) do pedido VEL-P1P10-REV, E1.1. Diff lido inteiro: `git diff 3b94791a8e96771c061eabb8e2b77381151289d1...0b4585f172afa6ba0c1e535da996938711ada03e` (5 commits, `d7eda57` a `0b4585f`). O revisor é uma instância que não implementou o lote. Segurança (E2.1) e QA (E3.1) rodam em paralelo, em `docs/security/` e `docs/qa/`; não os refaço.

## Achados
- A1 (bloqueante) skills/qa-testing/SKILL.md:85 · requisito (E2 e decisão técnica (c) de 2026-10-28 22:06), classe contradição: a frase diz 3 a 16 mutantes e, na mesma linha, "Pedido com mais de 8 mutantes divide"; a ferramenta divide acima de 16. Trocar 8 por 16 e travar com teste
- A2 (recomendado) bin/forge-mutante:559 · spec só com mutantes equivalentes sai rc 0 ("todos morreram") sem rodar nenhum mutante; sugestão: sem mutante rodado, rc 2, ou a linha 37 dizer que o 0 exclui os equivalentes. Vira cartão ao security-engineer
- A3 (recomendado) bin/forge-mutante:466 · na `--cobertura`, o equivalente declarado cobre a condição e sai como `coberta` igual ao mutante com teste; sugestão: marcar `coberta (equivalente)` para o review e o QA verem a guarda que ninguém prova
- A4 (recomendado) tests/test_forge.py:4951 · nenhum teste confere o número de divisão da spec em skills/qa-testing/SKILL.md; o A1 passou com os testes verdes. Sugestão: assertNotIn("mais de 8 mutantes") nessa skill

## Parecer
**Reprovado** pelo A1. O resto da entrega cumpre o escopo.

- **A1:** a decisão técnica (c) põe no lote a troca de 3 a 8 para 3 a 16 na `skills/qa-testing/SKILL.md`. A troca entrou no começo da linha 85, mas a frase seguinte, na mesma linha, manda dividir a spec acima de 8. A skill fica com dois limites, e o de 8 contradiz o `MAXIMO_DE_MUTANTES = 16` (`bin/forge-mutante:66`) e o objetivo do E2 (o limite cabe num lote). É a mesma classe da volta 1 deste pedido (o 400 que ficou em `agents/jarvis.md:48`), e o review `lote-mutante` já tinha um achado nessa linha (A1 do `8c6975c`): por isso grava a linha AR-2 em `docs/engineering/achados-recorrentes.md`. A correção é de uma palavra e mais um teste (A4); volta ao autor.
- **A2 e A3:** o campo `equivalente` faz o que o E2 pede: não roda, não dá rc 1, a justificativa é obrigatória (20+ caracteres) e o trecho `de` tem que aparecer uma vez no arquivo do commit. O que falta é ver o caso de borda. Uma spec feita só de equivalentes devolve 0, o "provado", sem ter rodado nada, e a `--cobertura` não separa equivalente de mutante com teste. A justificativa aparece na saída e o QA confere a lista contra o diff (`skills/qa-testing/SKILL.md:87`), então não é defeito provado. Mas o rc 0 é o sinal que os portões leem, e por isso esse ponto vira cartão ao `security-engineer` (controle do Forge).

## Conferência por item do Entregar
- **Teto (E1):** 150 linhas, com a conta no commit `d7eda57`: a maior entrega sem volta da linha de base é o #350 (117 linhas), mais cerca de 30% de folga; as outras sem volta são o #347 (3), o #337 (0) e o #354 (0). Mais estreito que 400, não afrouxa. O número aparece em `agents/tech-lead.md:19`, `skills/engineering-practices/SKILL.md:62` e `agents/jarvis.md:48`, a única linha do Jarvis que muda, como manda a decisão técnica (a). A regra de um comportamento por PR fica em `agents/tech-lead.md:19`, como bloqueante pelo requisito M14, e na skill.
- **Teto aplicado a este PR:** pelo `git diff --numstat --no-renames 3b94791a...0b4585f`, contam `bin/forge-mutante` 36, `tests/test_forge.py` 28 e `tests/test_forge_mutante.py` 55, o que dá 119 linhas, abaixo de 150. Ficam fora da conta o `tests/mutantes/vel-p1p10.json` (128), o `changelog.d/` e o `.md`. O lote junta P1 e P10 por decisão do dono (2026-10-28 20:59), antes de a regra de um comportamento por PR existir; fica só registrado, sem achado.
- **Campo `equivalente` (E2):** `CHAVES_DO_EQUIVALENTE` troca `testes` por `equivalente`, e mandar as duas chaves juntas é recusado (é testado). A justificativa curta, vazia, só com espaços, `None` ou numérica é recusada antes de rodar (rc 2, "nada foi executado"). Na rodada, `linha_do_equivalente` imprime `equivalente: <id> · <justificativa>`, e o trecho ausente ou repetido sai como `inválido` com rc 2.
- **Limite de 16:** `MAXIMO_DE_MUTANTES = 16`, com o docstring e a skill atualizados (fora o A1). Os testes de borda passaram a usar 16 e 17, também com várias specs.
- **Verificadores do autor (E3):** o Entregar do `agents/tech-lead.md:22` e o item 5 do `node-backend.md` e do `react-frontend.md` listam a mutação no diff com a spec, o `shellcheck` no shell tocado e a suíte do item, antes do push; o `agents/jarvis.md` fica de fora. O projeto tem uma stack só (`node-react`), e os dois agentes dela estão cobertos.
- **Testes novos (E4):** `TetoPorPr.test_teto_de_150_linhas_tambem_no_jarvis`, `test_teto_de_150_linhas_e_um_comportamento_por_pr_no_tech_lead_e_na_skill`, `VerificadoresDoAutor`, mais três testes de validação e três de execução do equivalente em `tests/test_forge_mutante.py`. O teste antigo deixou de exigir o "400" e os novos exigem o "150" nos três arquivos, então o teste não afrouxou. A spec `tests/mutantes/vel-p1p10.json` tem 12 mutantes, cada um com o teste que o mata. A rodada é evidência do QA e não a refiz.
- **Fragmento:** `changelog.d/vel-p1p10.md`, com `### Alterado`.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_forge_mutante tests.test_forge.TetoPorPr tests.test_forge.VerificadoresDoAutor` na `0b4585f`: `Ran 73 tests`, `OK`.
- `bin/forge-mutante --cobertura --base 3b94791a...`: rc 0. Saem 7 condições `coberta` (linhas 225, 226, 242, 243, 271, 559 e 562), nenhuma `sem mutante`.
- `shellcheck`: o diff não toca nenhum shell.
- PA-7 (`docs/engineering/achados-recorrentes.md`): o AR-1 (máscara do shell) não se aplica, porque o diff não toca nenhum shell. Este parecer grava o AR-2.
