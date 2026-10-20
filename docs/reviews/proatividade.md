---
tipo: review
contrato: 1
pedido: proatividade-melhoria
branch: melhoria/proatividade
commit: 3a8e376866ccdcd4e49176f3b9531080e217dd95
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-19
---
# Code review: proatividade (melhoria vista, retrospectiva que vira cartão, entrada direta)

Rodada 1 (E1.3): `e9c81e0..640f304`, 2 commits, 10 arquivos, 36+/14-. Revisor é outra instância, não o autor da E1.2 (D-ETAPAS-INST).

Ferramentas rodadas em 640f304: `python3 -m unittest tests.test_forge.Neutralidade tests.test_forge.NeutralidadeDoNucleo tests.test_forge.RegrasInviolaveis tests.test_forge.RegrasComId tests.test_changelog` dá `Ran 33 tests ... OK`; `git diff e9c81e0 640f304 -- tests/config.json | grep -c '^-[^-]'` dá `0`. Não refiz a suíte inteira nem `scripts/validar-plugin.sh` (R-TETO): o autor relatou 865 OK e o conferente deu "cumpriu", e o QA (E1.4) roda os dois no head. A segurança tem parecer próprio do `security-engineer` (E1.3 em paralelo), que eu não refiz.

## Conferência contra o desenho
- D1: `docs/regras/R-DECISAO.md` ganha a seção "Complemento: melhoria vista e entrada direta" com os itens (a) a (e), fiel ao desenho. Também mudam a lista do 1º item (", aumento de tokens ou de tempo de entrega"), `verificada_por`, a data de Revisão e a linha do `docs/regras/README.md`. Conforme.
- D2: `agents/jarvis.md:62`, a "Última linha: `Melhoria vista:`" fica no fim do item 6. Conforme.
- D3: `bin/forge-check:2755`, a linha nova vai no fim do bloco `## Relatório` do `brief gerar`, sem checagem que reprove brief e com fixtures intactas (o diff não toca `tests/fixtures/`). Conforme.
- D4: `docs/melhoria-continua.md:6` traz o "Registro por papel" no texto do desenho, e a tabela (b) ganha a linha M4. Conforme.
- D5: `agents/jarvis.md:41` (passo 9), `agents/agile-coach.md:14` e `skills/kanban-scrum/SKILL.md:123`. Conforme.
- D6: `agents/jarvis.md:87` e `:92`, e `agents/agile-coach.md:19`. A contradição antiga com o item de autonomia está resolvida. Conforme.
- D7: `templates/projeto/CLAUDE.md:29`. Conforme.
- D8: os 10 trechos do desenho entram como invariantes, e a chave nova `bin/forge-check` também. Nenhum item sai nem muda (0 linhas removidas). Conforme.

## Limites do dono
- Dinheiro real nunca, sem exceção: está em R-DECISAO (c), "não custa dinheiro real, sem exceção (`R-CUSTO`)", e em (d), "melhoria que custa dinheiro real não entra na fila". O trecho virou invariante.
- O aumento de tokens ou de tempo de entrega vai ao dono: R-DECISAO (c) põe a condição "não aumenta tokens nem tempo de entrega" (também invariante), (d) manda ao usuário "com o aumento estimado", e o 1º item da regra inclui esse aumento entre as decisões do usuário. Em `agents/jarvis.md:92` ele está entre os "Continuam sendo do usuário".

## Texto único e neutralidade
- O texto completo fica só em `R-DECISAO.md`. Os outros arquivos citam o ID com no máximo um resumo de uma oração, como prescrevem D6 e D7, sem repetir as condições. Isso está de acordo com a ADR 0002.
- R-NEUTRO: não há nome, regra de negócio nem stack de projeto no diff, e o teste `Neutralidade` passa.
- Fragmento `changelog.d/proatividade.md` presente, e o `CHANGELOG.md` não foi tocado. Commits seguem Conventional Commits em português, um por camada (a regra, depois quem a cita).
- Critério de reversão: está no pedido (Desenho, "Custo"). Não exijo "por que o existente não basta", porque o passo 9 e o "Registro por papel" já existiam e a mudança os reforça, sem criar mecanismo novo.

## Revalidação por delta (volta 1)
Delta `eb45334..3a8e376`: 4 arquivos, 4+/5-. Revisor é outra instância, não o autor da volta (D-ETAPAS-INST). O restante do parecer da rodada 1 (conferência contra o desenho, limites do dono, texto único e neutralidade) vale, pois o delta só toca os pontos abaixo.

| Recomendação | Correção | Resultado |
|---|---|---|
| `agents/agile-coach.md:21` (limites do dono ausentes) | "sem aprovação prévia só para o que passa no critério de entrada direta (`R-DECISAO`, "Melhoria vista")" | Resolvida |
| `bin/forge-check:2755` (espaço inicial) | a frase "Última linha" foi para o fim da linha anterior, sem espaço | Resolvida |
| `docs/melhoria-continua.md:7` ("junta as respostas") | "junta as linhas `MELHORIA:` do pedido" | Resolvida |
| Segurança R1 (`R-DECISAO.md`, parêntese de (c)) | "por exemplo, passo, rodada, agente ou texto..." | Resolvida |
| Segurança R2 (`controle` sem fonte) | "não afrouxa controle (`R-CONFORMIDADE`)" | Resolvida |

Ferramentas: `git diff eb45334 3a8e376 -- tests/config.json | grep -c '^-[^-]'` dá `0` (nenhum invariante saiu ou mudou; o arquivo nem aparece no delta); `python3 -m unittest tests.test_forge.RegrasInviolaveis tests.test_forge.RegrasComId tests.test_forge.Neutralidade` dá `Ran 6 tests ... OK`. Suíte inteira e `validar-plugin.sh` não refeitos (R-TETO): o autor relatou 865 OK, o conferente deu "cumpriu" e o QA (E1.4) roda no head. O ajuste em `bin/forge-check` só junta duas strings do brief, sem mudar a lógica.

## Achados
