---
tipo: review
contrato: 1
pedido: vel-p1p10
branch: melhoria/vel-p1p10
commit: 9e191c78b4dbed14aa439122ade1f86bcb955a57
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Code review: entrega menor e verificadores do autor (VEL-P1P10, P1 e P10)

Escopo: pedido VEL-P1P10-REV, E1.1 (`R-REVIEW`). Rodada 2: revalidação por delta, a partir do parecer `8757265`, até o head `9e191c7` (seção abaixo). Rodada 1, diff lido inteiro: `git diff 3b94791a8e96771c061eabb8e2b77381151289d1...0b4585f172afa6ba0c1e535da996938711ada03e` (5 commits, `d7eda57` a `0b4585f`). O revisor é uma instância que não implementou o lote. Segurança (E2.1) e QA (E3.1) rodam em paralelo, em `docs/security/` e `docs/qa/`; não os refaço.

## Achados
- A2 (recomendado) bin/forge-mutante:559 · spec só com mutantes equivalentes sai rc 0 ("todos morreram") sem rodar nenhum mutante; sugestão: sem mutante rodado, rc 2, ou a linha 37 dizer que o 0 exclui os equivalentes. Vira cartão ao security-engineer
- A3 (recomendado) bin/forge-mutante:466 · na `--cobertura`, o equivalente declarado cobre a condição e sai como `coberta` igual ao mutante com teste; sugestão: marcar `coberta (equivalente)` para o review e o QA verem a guarda que ninguém prova

## Revalidação por delta (rodada 2, head 9e191c7)
Parecer anterior: `8757265` (reprovado sobre `0b4585f`, A1 bloqueante, A2 a A4 recomendados). Delta lido:
- `git diff 8757265..9e191c7` tem dois commits na primeira linha: `cf04778` (volta 2) e `9e191c7` (atualização com a develop `a55ec03`, release 0.30.6).
- **`cf04778`, lido inteiro:** `skills/qa-testing/SKILL.md:85` passa a "Pedido com mais de 16 mutantes divide", igual ao `MAXIMO_DE_MUTANTES = 16`. **A1 resolvido.** O teste `TetoPorPr.test_a_skill_de_qa_divide_a_spec_no_mesmo_limite_que_a_ferramenta` (`tests/test_forge.py:5076`) exige "3 a 16 mutantes" e "Pedido com mais de 16 mutantes divide" e recusa "mais de 8 mutantes"; o alvo do assertNotIn existia antes e foi lido (checklist 11). **A4 resolvido.**
- **`9e191c7`, atualização com a develop:** o patch do lote sobre a develop (`git diff a55ec03...9e191c7`) é, arquivo por arquivo, igual ao `3b94791...cf04778` (linhas `+`/`-` iguais nos 11 arquivos de código, teste, skill, agente e spec). O único conflito ficou nas linhas AR de `docs/engineering/achados-recorrentes.md`: a linha `limite-antigo-no-texto` que este review gravou como AR-2 agora é a **AR-9** (a develop já trazia AR-1 a AR-8), com a mesma classe, contagem 2 e `skills/qa-testing/SKILL.md:85`. A antiga AR-1 (`mascara-do-shell-esconde-codigo`) é a AR-6 da develop, com a mesma contagem.
- **Já lido:** o conteúdo da develop que entra pela atualização (`.githooks/pre-push`, `bin/forge-check`, `hooks/parecer.py`, pareceres, corpus e specs dos lotes AQ1, HK3, LOTE-PREPUSH e a release 0.30.6) tem review próprio nos PRs que o levaram à develop; o `forge-check delta --parecer` o lista porque o intervalo parte de `0b4585f`, e não o revisei de novo. Conferi só o encontro com este lote: a develop mexeu em `agents/tech-lead.md:17` e `agents/jarvis.md:65`, outras linhas, e nenhum texto fora dos pareceres ficou com "400 linhas", "8 mutantes" ou "3 a 8" (`grep` em `agents/`, `skills/`, `stacks/`, `docs/regras/`, `templates/` e `README.md`).
- Nenhuma regressão do que o `8757265` aprovou: os itens da conferência abaixo seguem valendo no head novo.

## Parecer
**Aprovado** no head `9e191c7`. O A1 (bloqueante da rodada 1) e o A4 foram resolvidos na volta 2 (`cf04778`). O A2 e o A3 seguem como recomendações, que não devolvem a entrega.

- **A1 (rodada 1, resolvido):** a skill tinha dois limites na mesma linha, e o de 8 contradizia o `MAXIMO_DE_MUTANTES = 16` (`bin/forge-mutante:66`). É a mesma classe da volta 1 deste pedido (o 400 que ficou em `agents/jarvis.md:48`) e do A1 do review `lote-mutante` (`8c6975c`); por isso a linha AR-9 (`limite-antigo-no-texto`, antes gravada como AR-2) fica em `docs/engineering/achados-recorrentes.md`.
- **A2 e A3:** o campo `equivalente` faz o que o E2 pede: não roda, não dá rc 1, a justificativa é obrigatória (20+ caracteres) e o trecho `de` tem que aparecer uma vez no arquivo do commit. O que falta é ver o caso de borda. Uma spec feita só de equivalentes devolve 0, o "provado", sem ter rodado nada, e a `--cobertura` não separa equivalente de mutante com teste. A justificativa aparece na saída e o QA confere a lista contra o diff (`skills/qa-testing/SKILL.md:87`), então não é defeito provado. Mas o rc 0 é o sinal que os portões leem, e por isso esse ponto vira cartão ao `security-engineer` (controle do Forge).

## Conferência por item do Entregar
- **Teto (E1):** 150 linhas, com a conta no commit `d7eda57`: a maior entrega sem volta da linha de base é o #350 (117 linhas), mais cerca de 30% de folga; as outras sem volta são o #347 (3), o #337 (0) e o #354 (0). Mais estreito que 400, não afrouxa. O número aparece em `agents/tech-lead.md:19`, `skills/engineering-practices/SKILL.md:62` e `agents/jarvis.md:48`, a única linha do Jarvis que muda, como manda a decisão técnica (a). A regra de um comportamento por PR fica em `agents/tech-lead.md:19`, como bloqueante pelo requisito M14, e na skill.
- **Teto aplicado a este PR:** pelo `git diff --numstat --no-renames a55ec03...9e191c7`, contam `bin/forge-mutante` 36, `tests/test_forge.py` 34 e `tests/test_forge_mutante.py` 55, o que dá 125 linhas, abaixo de 150 (eram 119 na rodada 1; a volta 2 somou 6 linhas de teste). Ficam fora da conta o `tests/mutantes/vel-p1p10.json` (128), o `changelog.d/` e o `.md`. O lote junta P1 e P10 por decisão do dono (2026-10-28 20:59), antes de a regra de um comportamento por PR existir; fica só registrado, sem achado.
- **Campo `equivalente` (E2):** `CHAVES_DO_EQUIVALENTE` troca `testes` por `equivalente`, e mandar as duas chaves juntas é recusado (é testado). A justificativa curta, vazia, só com espaços, `None` ou numérica é recusada antes de rodar (rc 2, "nada foi executado"). Na rodada, `linha_do_equivalente` imprime `equivalente: <id> · <justificativa>`, e o trecho ausente ou repetido sai como `inválido` com rc 2.
- **Limite de 16:** `MAXIMO_DE_MUTANTES = 16`, com o docstring e a skill atualizados (a frase da divisão também, desde a volta 2). Os testes de borda passaram a usar 16 e 17, também com várias specs.
- **Verificadores do autor (E3):** o Entregar do `agents/tech-lead.md:22` e o item 5 do `node-backend.md` e do `react-frontend.md` listam a mutação no diff com a spec, o `shellcheck` no shell tocado e a suíte do item, antes do push; o `agents/jarvis.md` fica de fora. O projeto tem uma stack só (`node-react`), e os dois agentes dela estão cobertos.
- **Testes novos (E4):** `TetoPorPr.test_teto_de_150_linhas_tambem_no_jarvis`, `test_teto_de_150_linhas_e_um_comportamento_por_pr_no_tech_lead_e_na_skill`, `VerificadoresDoAutor`, mais três testes de validação e três de execução do equivalente em `tests/test_forge_mutante.py`. O teste antigo deixou de exigir o "400" e os novos exigem o "150" nos três arquivos, então o teste não afrouxou. A spec `tests/mutantes/vel-p1p10.json` tem 12 mutantes, cada um com o teste que o mata. A rodada é evidência do QA e não a refiz.
- **Fragmento:** `changelog.d/vel-p1p10.md`, com `### Alterado`.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_forge_mutante tests.test_forge.TetoPorPr tests.test_forge.VerificadoresDoAutor` na `9e191c7`: `Ran 74 tests`, `OK` (eram 73 na rodada 1; o teste novo é o do A4).
- `bin/forge-mutante --cobertura --base a55ec03...` na `9e191c7`: rc 0. Saem 7 condições `coberta` (linhas 225, 226, 242, 243, 271, 559 e 562), nenhuma `sem mutante`.
- `shellcheck`: o patch do lote não toca nenhum shell; o `.githooks/pre-push` que aparece no delta veio da develop.
- PA-7 (`docs/engineering/achados-recorrentes.md`): a AR-6 (máscara do shell) não se aplica, porque o lote não toca nenhum shell. A AR-9 (`limite-antigo-no-texto`) é a classe do A1, já resolvido, e não reaparece no head: nenhum texto fora dos pareceres guarda o 400 ou o 8. A AR-7 e a AR-8 tratam de `hooks/parecer.py`, que o lote não toca.
