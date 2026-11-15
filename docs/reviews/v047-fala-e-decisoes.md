---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-fala-e-decisoes
commit: 05797223ac8b884b8d44874803878cfb356eedbc
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047-fala-e-decisoes

Code review da E1.282 (E1.292) no head 05797223, intervalo `origin/develop..05797223` (base c5c3a449): diretriz 24 (falar só no marco) em `agents/jarvis.md` e `skills/modo-iniciante/SKILL.md`, diretriz 29 (pedido das decisões) em `skills/falar-com-o-dono/SKILL.md`, 15 invariantes novos em `tests/config.json`.

## Achados
- A1 (bloqueante) skills/falar-com-o-dono/SKILL.md:18 · o corte tirou "`decisoes --resposta` a lê; corte recomendado leva `origem:`, `procurado:`, `seguir:`, `não seguir:`", regra que só estava aqui (grep em agents/, skills/ e docs/regras/ vazio); a diretriz 25 (DECISÃO DO DONO 13/11 19:37) proíbe apagar ou resumir regra: devolva o trecho.
- A2 (recomendado) agents/jarvis.md:19 · saiu "O técnico (desenho, portões, integração, versão) é do `tech-lead`; o aprendizado com os erros, do `agile-coach`"; quase tudo segue na tabela (L24, L30) e nos passos 3 e 9, mas pela diretriz 25 o caminho é mover para skill citada, não cortar.
- A3 (recomendado) skills/falar-com-o-dono/SKILL.md:24 · "(economia, regra 12)" e jarvis.md:47 "(política, regras 9 a 11)" perderam o caminho `docs/economia-de-tokens.md`; no Jarvis ele segue no L9, na skill não: devolva o caminho na skill.
- A4 (recomendado) skills/modo-iniciante/SKILL.md:44 · o exemplo C perdeu "não dá para dizer se é maior ou menor", que mostra o item 4 do "Como perguntar" (custo maior ou menor, em palavras) no caso `não medido`.

## Sondas

## Parecer
Reprovado por A1. Diff de 5 arquivos (52 inserções, 26 remoções), só texto e `tests/config.json`; nenhuma guarda de código, sem mutante a declarar.

- **Diretriz 24:** o "Falar só no marco" do Jarvis cobre os três gatilhos (decidir ou agir, problema que muda prazo ou risco, marco fechado), o resumo de no máximo 30 min com uma linha por item que mudou, sem nome de branch ou pasta, "nada mudou, nada a dizer", relatório de agente ao histórico e recibo e perguntas completos. O "à pessoa, só decisão, rótulo, merge na `main` e comando em arquivo travado" foi absorvido nos parênteses do gatilho, sem perda. No modo iniciante, "e o que já foi feito depois" sai por decisão do dono (diretriz 24), não é corte de regra. O modo foco entra só no caminho do perfil iniciante; o resto do cartão FALA-SO-NO-MARCO (forge-init, novo-projeto, README, métrica de mensagens) o autor declarou fora: o cartão fica aberto.
- **Diretriz 29:** o "Pedido das decisões" bate com o texto do dono: nada antes da resposta além de ler as perguntas abertas numa consulta, lista curta por peso, primeira pergunta completa, cada resposta pelo `forge-check anotar`, o time segue no que não depende (Q2), nenhum aviso entre as perguntas, resumo no fim e a linha "Não há decisão sua pendente.". O Jarvis manda ler a skill também "ao pedido das decisões" (resumo no Jarvis, detalhe na skill, diretriz 25).
- **Cortes (diretriz 25):** "Custo e origem" e "a seguinte, depois da resposta" saíram da skill, mas seguem na `R-DECISAO` (linha 14) e no "Como perguntar" do modo iniciante, que a skill cita: não há perda. O formato do corte recomendado (A1) não tem outra cópia em texto; só o `bin/forge_dono.py` o cobra na recusa, e a diretriz 25 pede o texto no Jarvis ou numa skill. O `agents/jarvis.md` está em 7951 bytes (develop: 7954); se o trecho não couber na skill, a folga da diretriz 25 é mover, não cortar.
- **Invariante "diga sempre ao usuário para qual agente passou"** (jarvis.md:34) contra a diretriz 24: o autor não o tirou e registrou a PERGUNTA AO DONO no pedido (14/11 23:14). Correto (`R-CONFORMIDADE`); não é achado.
- **Invariantes:** os 15 padrões novos casam e têm motivo com `R-DECISAO`. Mutantes rodados numa cópia do head (`git archive`): trocar "recibo e perguntas, sempre completos" por "recibo e perguntas completos" no Jarvis e "nenhum aviso" por "sem aviso" na skill; `RegrasInviolaveis.test_trechos_obrigatorios` falhou nos dois (mortos).
- **Execução** (sem PR aberto, só os afetados, ambiente limpo): `test_jarvis_nucleo`, `test_jarvis_n_jar_a`, `test_forge.Neutralidade`: 25 testes OK; `test_forge.RegrasInviolaveis` e `test_forge.Orcamento`: 5 testes OK. O `forge-testes --listar` aponta a suíte completa (o diff toca `tests/config.json`): fica para o CI do PR.
- Commit único, Conventional Commits em português, fragmento `changelog.d/v047-fala-e-decisoes.md` presente.
