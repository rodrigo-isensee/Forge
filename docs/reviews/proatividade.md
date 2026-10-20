---
tipo: review
contrato: 1
pedido: proatividade-melhoria
branch: melhoria/proatividade
commit: 640f304da65c32375ea1d9cedac3fac0db06405a
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

## Recomendações (não bloqueiam; viram cartão)
- `agents/agile-coach.md:21`: "Melhorias você mesmo implementa, sem aprovação prévia" segue listando só "decisões de produto e mudanças nas regras invioláveis" como dependentes do usuário. Faltam custo, controle e tokens/tempo. A linha 19 e o R-DECISAO prevalecem, mas a frase lida sozinha contradiz o limite do dono. Sugestão: trocar a lista por "o que não passa no critério de entrada direta (`R-DECISAO`)". Fica fora de D1 a D8 e por isso não bloqueia.
- `bin/forge-check:2755`: a linha começa com espaço e sai como linha própria (`"\n".join`), não no fim da frase anterior. O efeito é cosmético no brief. Sugestão: tirar o espaço inicial.
- `docs/melhoria-continua.md:7`: "junta as respostas" ficou desatualizado, já que não há mais pergunta por papel. Sugestão: "junta as linhas `MELHORIA:`".

## Achados
