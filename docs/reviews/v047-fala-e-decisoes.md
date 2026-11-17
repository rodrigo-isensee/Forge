---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-fala-e-decisoes
commit: 1c330fe64c8687225e4847f84cf17b030c2a4353
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047-fala-e-decisoes

Revalidação (E2.395) no head 1c330fe6, por delta: correção de A1 da passada E2.332 (head 14a29d8f, reprovado).

## Delta lido
`forge-check parecer delta docs/reviews/v047-fala-e-decisoes.md` → intervalo `14a29d8f9399b00c1785434af6e9a69fcd3ab826..1c330fe64c8687225e4847f84cf17b030c2a4353`; no domínio só `tests/config.json` (uma linha trocada, uma acrescentada). Fora do domínio: pareceres de QA e de segurança e `docs/qa/bugs/v047-legado-jarvis-contagem.md`. O resto da branch não foi relido.

## Conferência de A1
- `tests/config.json`:756 dá ao trecho devolvido "diga sempre ao usuário para qual agente passou" regra (`R-DECISAO`) e porque, citando a decisão do dono de 16/11 09:52.
- `invariantes_sem_motivo["agents/jarvis.md"]` (`tests/config.json`:696) fica em 48, abaixo dos 49 da base `5e74c70e`: o legado encolhe, como pedia A1. A sugestão do bug do QA (subir para 49) não foi seguida, e não precisava ser: com o motivo, a conta fecha em 48.

## Saída das ferramentas (sem refazer)
- `python3 -m unittest tests.test_forge.RegrasInviolaveis tests.test_forge.Orcamento tests.test_orcamento_instrucao tests.test_jarvis_nucleo` → 33 testes OK.
- `python3 -m unittest tests.test_forge -k nvariante -k Neutral -k Regra` (os passos do bug do QA) → 15 testes OK.
- Mutante numa cópia do head (`git archive`): tirar a entrada de motivo do trecho devolvido faz `test_invariante_traz_regra_e_porque_e_o_legado_so_encolhe` falhar (morto).
- Tamanho (M14): 3 linhas de `tests/config.json`; sem guarda de código, sem mutante a declarar.
- Suíte inteira: fica para o CI do PR.
- `docs/engineering/achados-recorrentes.md` conferido: A1 não se repetiu neste pedido; sem linha `AR-<n>` nova.

## Achados

## Sondas

## Parecer
Aprovado. A1 resolvido sem achado novo. O commit 1c330fe6 segue Conventional Commits em português e muda só `tests/config.json`.

## Passada anterior (E2.332, head 14a29d8f, reprovado por A1, resolvido)
Revalidação (E2.332) no head 14a29d8f, por delta: volta E2.315, decisão do dono de 16/11 09:52 (pedido v047:947), que mantém o invariante "diga sempre ao usuário para qual agente passou" e muda só o momento (recibo e aviso de marco, nunca em mensagem extra).

### Delta lido
`forge-check parecer delta docs/reviews/v047-fala-e-decisoes.md` → intervalo `fd0a0172774f2744dbfbba81ca10064d4f98ec41..14a29d8f9399b00c1785434af6e9a69fcd3ab826`, sem o que veio da base; no domínio: `agents/jarvis.md`, `changelog.d/v047-fala-e-decisoes.md`, `tests/config.json`, `tests/test_jarvis_nucleo.py`. O resto da branch foi lido nas passadas anteriores e não foi relido.

### Conferência com a decisão de 16/11 09:52
- `agents/jarvis.md`:34 devolve o trecho "diga sempre ao usuário para qual agente passou" e acrescenta "no recibo e no aviso de marco, nunca em mensagem extra", nas palavras do dono. O trecho de 15/11 ("só nos marcos, num resumo") sai do texto e dos invariantes; sobra só em pareceres antigos de QA e segurança (histórico).
- `tests/config.json`: o trecho devolvido volta a `invariantes` e o momento entra como invariante novo, com motivo em `invariantes_motivo_trecho` (`R-DECISAO`).
- `tests/test_jarvis_nucleo.py`: `RETIRADOS_047` sai, então o teste volta a exigir o trecho do dono. Isso aperta, não afrouxa.
- O changelog e o `description` do Jarvis mudam só o texto; nenhuma outra regra sai (diretriz 25). O `agents/jarvis.md` tem 7954 bytes e `test_orcamento_instrucao` passa.

### Saída das ferramentas (sem refazer)
- `python3 -m unittest tests.test_jarvis_nucleo` → 20 testes OK.
- `python3 -m unittest tests.test_forge.RegrasInviolaveis tests.test_forge.Orcamento tests.test_orcamento_instrucao tests.test_jarvis_nucleo` → 33 testes, 1 falha: `test_invariante_traz_regra_e_porque_e_o_legado_so_encolhe` (A1). O mesmo teste passa em `fd0a0172` e na base `5e74c70e`, nas duas cópias feitas com `git archive`.
- Mutantes numa cópia do head: trocar ", nunca em mensagem extra." por " e nunca em mensagem extra." e tirar o "sempre" do trecho devolvido fazem `test_trechos_obrigatorios` falhar nos dois casos (mortos).
- Tamanho (M14): poucas linhas de `tests/config.json` e `tests/test_jarvis_nucleo.py` no delta; sem guarda de código, sem mutante a declarar.
- Suíte inteira: fica para o CI do PR (`tests/config.json` muda).

### Achados
- A1 (bloqueante) tests/config.json:223 · o trecho devolvido não tem motivo e `agents/jarvis.md` passa a ter 49 sem motivo (58-9) contra o legado 48 (:696). `test_invariante_traz_regra_e_porque_e_o_legado_so_encolhe` falha. Ponha o motivo em `invariantes_motivo_trecho` (R-DECISAO); não suba o legado.

### Sondas

### Parecer
Reprovado por A1. O texto faz o que a decisão do dono pede (a regra fica e muda só o momento), mas o head quebra um teste estrutural que passava em fd0a0172. A correção é do autor e cabe numa linha de `tests/config.json`. Depois dela, a revalidação é por delta.

## Passada anterior (E1.347, head fd0a0172, aprovado)

Code review da E1.282 (E1.292) no head 05797223, intervalo `origin/develop..05797223` (base c5c3a449): diretriz 24 (falar só no marco) em `agents/jarvis.md` e `skills/modo-iniciante/SKILL.md`, diretriz 29 (pedido das decisões) em `skills/falar-com-o-dono/SKILL.md`, 15 invariantes novos em `tests/config.json`.

Revalidação (E1.347) no head fd0a0172, por instância que não fez a entrega: decisão 2 do dono de 15/11 (pedido v047, 06:34), que tira o invariante "diga sempre ao usuário para qual agente passou" e o troca pelo resumo nos marcos; o PR leva o destaque de afrouxa-regra. As passadas anteriores (E1.306, head a4a47661, aprovado; E1.292, head 05797223, reprovado) seguem no fim.

### Delta lido
`forge-check parecer delta docs/reviews/v047-fala-e-decisoes.md` → rc 0, intervalo `a4a476617e6aae4b418e2a97df2839f84500942a..fd0a0172774f2744dbfbba81ca10064d4f98ec41`, no domínio: `agents/jarvis.md`, `changelog.d/v047-fala-e-decisoes.md`, `tests/config.json`, `tests/test_jarvis_nucleo.py`. Fora do domínio: pareceres de QA e de segurança. O resto da branch já foi lido nas passadas anteriores e não foi relido.

### Conferência com a decisão 2
- `agents/jarvis.md`:34 troca só a oração final da triagem: "diga sempre ao usuário para qual agente passou" → "diga qual agente faz o quê só nos marcos, num resumo", nas palavras do dono ("Diga qual agente faz o quê só nos marcos, num resumo").
- `tests/config.json`: o trecho velho sai de `invariantes` e o novo entra no mesmo lugar, com motivo em `R-DECISAO`; por isso `invariantes_sem_motivo` de `agents/jarvis.md` cai de 49 para 48. A conta bate.
- `tests/test_jarvis_nucleo.py`: `RETIRADOS_047` registra o trecho retirado com a data e a decisão, no padrão de `RETIRADOS_046`.
- O fragmento do changelog diz em negrito que afrouxa um invariante, com a decisão e o trecho. O destaque no título do PR (CLAUDE.md, "Regras da fábrica protegidas por teste") e o rótulo `afrouxa-regra` da catraca ficam para quando o PR for aberto. Isso é pendência do PR, não achado deste delta.
- Restos do trecho velho: só no retrato `tests/fixtures/jarvis-invariantes-b2580c6.json`, em `tests/fixtures/afrouxamentos/218.json` (histórico) e nos pareceres. Nenhum agente, skill ou modelo segue mandando avisar a cada agente acionado.

### Diretriz 25 (nada apagado nem resumido)
O delta tira um único trecho, por decisão expressa do dono. Nenhuma outra regra sai nem é resumida: `agents/jarvis.md` muda uma linha, os outros três arquivos só acrescentam ou trocam o mesmo trecho.

### Saída das ferramentas (sem refazer)
- Suíte inteira: fica para o CI do PR (`tests/config.json` muda), sem PR aberto agora.
- Afetados com `env -i` e `python3 -I -m unittest discover -s tests`: `test_jarvis_nucleo` (20 testes) OK; `test_forge` -k RegrasInviolaveis/Orcamento OK; `test_orcamento_instrucao` OK.
- Mutante numa cópia do head (`git archive`): devolver o trecho velho em `agents/jarvis.md`:34 faz `test_trechos_obrigatorios` falhar (morto). O novo invariante protege o texto.
- Tamanho (M14): 9 linhas de código e teste no delta (`tests/config.json` e `tests/test_jarvis_nucleo.py`); sem guarda de código, sem mutante a declarar.

### Achados

### Sondas

### Parecer
Aprovado. O delta faz o que a decisão 2 do dono pede, sem nada a mais. O afrouxamento está registrado em três lugares: no invariante novo com motivo, no `RETIRADOS_047` e no fragmento do changelog. A diretriz 25 foi cumprida. O commit fd0a0172 segue Conventional Commits em português e diz no assunto que afrouxa um invariante.

### Passada anterior (E1.306, head a4a47661, aprovado)
`bin/forge-check parecer delta docs/reviews/v047-fala-e-decisoes.md` → rc 0, intervalo `05797223ac8b884b8d44874803878cfb356eedbc..a4a476617e6aae4b418e2a97df2839f84500942a`, no domínio: `changelog.d/v047-fala-e-decisoes.md`, `skills/falar-com-o-dono/SKILL.md`, `skills/falar-com-o-dono/resposta-curta.md` (novo), `skills/kanban-scrum/SKILL.md`, `skills/kanban-scrum/experimentos.md` (novo), `skills/modo-iniciante/SKILL.md`, `skills/modo-iniciante/numeros.md` (novo), `tests/config.json`. Já lido (passada anterior, não relido): `agents/jarvis.md` e o resto da branch.

### Achados anteriores
- **A1 (resolvido):** `resposta-curta.md`:7 traz a linha O4 idêntica, caractere a caractere, à da develop (`c5c3a449`, `skills/falar-com-o-dono/SKILL.md`:16), com `decisoes --resposta` e `origem:`, `procurado:`, `seguir:`, `não seguir:`. A skill aponta o arquivo (SKILL.md:18-19).
- **A2 (resolvido):** a frase do técnico do `tech-lead` e do aprendizado com os erros do `agile-coach` está inteira em `skills/kanban-scrum/SKILL.md`:132, skill que o Jarvis manda ler (jarvis.md:49).
- **A3 (resolvido):** a skill volta a "regra 12 de `docs/economia-de-tokens.md`" (SKILL.md:25), igual à develop.
- **A4 (resolvido):** o exemplo C devolve "não dá para dizer se é maior ou menor" (modo-iniciante SKILL.md:44).

### Diretriz 25 (nada apagado nem resumido)
- `experimentos.md` e `numeros.md` levam o texto movido sem mudança (a tabela de colunas e "Uma mudança por vez..."; as três marcas `medido`, `estimado`, `não medido` com a regra inteira). O que fica na SKILL.md é ponteiro e o resumo de uma linha, sem perder regra: o texto completo está no arquivo apontado.
- Os três arquivos novos têm o cabeçalho que diz que valem como a skill (`R-DECISAO`) e o porquê da mudança de arquivo, e entram em `invariantes` com motivo; os ponteiros também são invariantes. Nada foi apagado no delta.

### Saída das ferramentas (sem refazer)
- `bin/forge-testes --listar` → suíte completa (`tests/config.json` muda): fica para o CI do PR.
- Afetados, ambiente limpo e `python3 -I`: `test_forge` (RegrasInviolaveis, Orcamento, Neutralidade) 11 OK; `test_orcamento_instrucao` 8 OK; `test_skills*` 4 OK; `test_jarvis*` 22 OK.
- Mutantes numa cópia do head (`git archive`): "corte recomendado leva" → "corte leva" em `resposta-curta.md` e "Uma mudança por vez em cada parte" → "Uma mudança por vez" em `experimentos.md`; `RegrasInviolaveis.test_trechos_obrigatorios` falhou nos dois (mortos).
- Tamanho (M14): só `tests/config.json` conta (59 linhas na branch), abaixo de 150; sem guarda de código, sem mutante a declarar.

### Achados

### Sondas

### Parecer
Aprovado. A1 a A4 resolvidos, sem achado novo; a diretriz 25 foi cumprida: o que não coube no teto mudou para arquivo ao lado com ponteiro e invariante. Commit a4a47661 em Conventional Commits em português; o fragmento do changelog registra os três arquivos novos.

### Passada anterior (E1.292, head 05797223, reprovado por A1)
- A1 (bloqueante) skills/falar-com-o-dono/SKILL.md:18 · o corte tirou o formato do corte recomendado e `decisoes --resposta`; diretriz 25.
- A2 (recomendado) agents/jarvis.md:19 · frase do técnico e do aprendizado cortada em vez de movida.
- A3 (recomendado) skills/falar-com-o-dono/SKILL.md:24 · perdeu o caminho `docs/economia-de-tokens.md`.
- A4 (recomendado) skills/modo-iniciante/SKILL.md:44 · exemplo C perdeu "não dá para dizer se é maior ou menor".

Reprovado por A1. Diff de 5 arquivos (52 inserções, 26 remoções), só texto e `tests/config.json`; nenhuma guarda de código, sem mutante a declarar.

- **Diretriz 24:** o "Falar só no marco" do Jarvis cobre os três gatilhos (decidir ou agir, problema que muda prazo ou risco, marco fechado), o resumo de no máximo 30 min com uma linha por item que mudou, sem nome de branch ou pasta, "nada mudou, nada a dizer", relatório de agente ao histórico e recibo e perguntas completos. O "à pessoa, só decisão, rótulo, merge na `main` e comando em arquivo travado" foi absorvido nos parênteses do gatilho, sem perda. No modo iniciante, "e o que já foi feito depois" sai por decisão do dono (diretriz 24), não é corte de regra. O modo foco entra só no caminho do perfil iniciante; o resto do cartão FALA-SO-NO-MARCO (forge-init, novo-projeto, README, métrica de mensagens) o autor declarou fora: o cartão fica aberto.
- **Diretriz 29:** o "Pedido das decisões" bate com o texto do dono: nada antes da resposta além de ler as perguntas abertas numa consulta, lista curta por peso, primeira pergunta completa, cada resposta pelo `forge-check anotar`, o time segue no que não depende (Q2), nenhum aviso entre as perguntas, resumo no fim e a linha "Não há decisão sua pendente.". O Jarvis manda ler a skill também "ao pedido das decisões" (resumo no Jarvis, detalhe na skill, diretriz 25).
- **Cortes (diretriz 25):** "Custo e origem" e "a seguinte, depois da resposta" saíram da skill, mas seguem na `R-DECISAO` (linha 14) e no "Como perguntar" do modo iniciante, que a skill cita: não há perda. O formato do corte recomendado (A1) não tem outra cópia em texto; só o `bin/forge_dono.py` o cobra na recusa, e a diretriz 25 pede o texto no Jarvis ou numa skill. O `agents/jarvis.md` está em 7951 bytes (develop: 7954); se o trecho não couber na skill, a folga da diretriz 25 é mover, não cortar.
- **Invariante "diga sempre ao usuário para qual agente passou"** (jarvis.md:34) contra a diretriz 24: o autor não o tirou e registrou a PERGUNTA AO DONO no pedido (14/11 23:14). Correto (`R-CONFORMIDADE`); não é achado.
- **Invariantes:** os 15 padrões novos casam e têm motivo com `R-DECISAO`. Mutantes rodados numa cópia do head (`git archive`): trocar "recibo e perguntas, sempre completos" por "recibo e perguntas completos" no Jarvis e "nenhum aviso" por "sem aviso" na skill; `RegrasInviolaveis.test_trechos_obrigatorios` falhou nos dois (mortos).
- **Execução** (sem PR aberto, só os afetados, ambiente limpo): `test_jarvis_nucleo`, `test_jarvis_n_jar_a`, `test_forge.Neutralidade`: 25 testes OK; `test_forge.RegrasInviolaveis` e `test_forge.Orcamento`: 5 testes OK. O `forge-testes --listar` aponta a suíte completa (o diff toca `tests/config.json`): fica para o CI do PR.
- Commit único, Conventional Commits em português, fragmento `changelog.d/v047-fala-e-decisoes.md` presente.
