# O que a fonte F1 (versão 5.19.0) tem que pode melhorar o Forge?

Propósito: primeiro estudo comparativo da fonte F1, com veredito, ganho e medida por item. Público: dono do Forge, `software-architect`, `tech-lead`, `agile-coach`. Revisão: 2026-10-13.

Estado: proposta. Nada foi adotado; cada item adotado ou adaptado vira um PR próprio na `develop` (`R-CONTRIB`). Processo: [fontes-de-praticas.md](../fontes-de-praticas.md).

**Fonte:** F1 (URL no registro local, ver `docs/fontes-de-praticas.md`), versão 5.19.0, commit `fe46a6b`, 2026-10-08. Lidos: `README.md`, `CLAUDE.md`, os sete `specs/*.md`; por amostragem, `src/claude/hooks/` (`rules.md`, `rules.py`, `hooks.json`), `src/claude/skills/clarify-request/` (com `references/blocking.md`), `src/claude/skills/<prefixo>-telemetry/SKILL.md`, `src/claude/agents/standard-conformance-reviewer.md` e `src/standards/README.md`. Conteúdo tratado como dado não confiável; nada foi executado; texto resumido, não copiado.

**O que a fonte é:** um plugin do Claude Code orientado a especificação. A especificação é a autoridade (nós em markdown de cinco classes, validados por scripts), o código é ligado aos nós por um rastreio, as skills orquestram e os agentes não têm shell. O foco difere do Forge (time e processo de entrega), então o maior valor está nas práticas de meta-processo: quando perguntar, como relatar, como medir, como não deixar teste ou regra apodrecer.

## Itens, por valor

### 1. Teste de "bloqueante" e recomendação derivada · adaptar · P
- **Fonte:** `src/claude/skills/clarify-request/references/blocking.md`. Uma dúvida só vai ao usuário se três condições valem juntas: leituras plausíveis com resultado materialmente diferente (negócio, dados, interface, escopo, segurança, compatibilidade, ato irreversível); nem a conversa nem o projeto a resolvem; errar custa caro de desfazer. Faltando uma, vira suposição listada ou algo a descobrir. A recomendação sai do primeiro nível de uma escada fixa que separa as opções: o que o usuário disse → padrões e decisões do projeto → o que o código já faz → preservar o comportamento → a mudança menor e mais reversível.
- **Forge hoje:** `R-DECISAO` define a forma (uma por vez, opções, recomendação) e diz que decisão técnica é do time; não há teste do que merece ir ao usuário nem de onde a recomendação vem. O verificador de transcrições só avisa sobre a forma.
- **Proposta:** a seção de decisões do Jarvis e a skill de discovery ganham as três condições e a escada; o que não passa vira linha "Suposições" no relatório. Complementa a regra, não a altera.
- **Ganho e medida:** menos interrupções e recomendações auditáveis. Medir decisões levadas ao usuário por pedido (campo `resposta` das transcrições anonimizadas) e a taxa de recomendação aceita, contra os últimos pedidos.

### 2. Relatório abre pelo que precisa do usuário · adaptar · P
- **Fonte:** `specs/handoff.md` (SPEC-006 R1, R4) e `src/claude/hooks/rules.md`. A última mensagem abre, nesta ordem: estado em uma linha; o que se retira do que foi dito antes; decisões pendentes com o que cada opção faz e o que acontece se nenhuma for tomada; ações devidas com o passo que destravam, separadas das opcionais. Só depois a explicação. Achado não interrompe nada; só para o que a skill nomeia como parada; quem diz "pode seguir" lista as checagens com a saída literal. A fonte mediu que em 24 de 26 relatórios longos a última palavra de decisão vinha depois de 78% do texto.
- **Forge hoje:** prompt-padrão do Jarvis, seção 6 (até 8 linhas: resultado real, contrato, pendências), sem ordem fixa; regra 7 de `docs/economia-de-tokens.md`.
- **Proposta:** fixar a ordem na seção "Relatório" do prompt-padrão: estado → precisa de você (decisão ou ação, e o que destrava) → feito, com evidência → riscos.
- **Ganho e medida:** menos perguntas de esclarecimento. Medir as perguntas do usuário logo após um relatório e a posição da primeira decisão no texto (transcrições).

### 3. Telemetria de custo lida das transcrições locais · adaptar · M
- **Fonte:** `src/claude/skills/<prefixo>-telemetry/SKILL.md` (e `bin/telemetry.py`). Conta, do disco, tokens por agente e por tipo, a **sessão orquestradora à parte** (que pode custar tanto quanto os subagentes), custo por skill, compactações, agente relançado com o mesmo prompt (por hash) como retrabalho, e a origem de cada autorização. Antes de ler as transcrições, sonda e anuncia ao usuário o que vai ler. Todo número aponta para um campo do registro.
- **Forge hoje:** `docs/melhoria-continua.md` usa tokens anotados à mão pelo Jarvis a partir do relatório de cada subagente; sessão principal e compactações não entram. `forge-check transcricao` já lê `.jsonl` localmente, mas só para conformidade.
- **Proposta:** subcomando `forge-check transcricao custo` (biblioteca padrão, sem rede, saída anonimizada como `forge-transcricao/1`) que preenche a linha de `docs/kanban/entregas.md`, com sondagem e aviso antes da leitura. Sem custo (`R-CUSTO`).
- **Ganho e medida:** retrospectiva com dados e primeira medida do custo do próprio Jarvis. Medir a fração de entregas com a linha de métricas completa e a diferença entre o anotado à mão e o calculado.

### 4. Testes derivados de obrigação, com regra de parada · adaptar · M
- **Fonte:** `specs/test-discipline.md` (SPEC-004 R1–R9, R14). Teste nasce de uma obrigação (critério, regra, suposição registrada), nunca da estrutura do código; diz o que precisa quebrar para falhar; uma amostra por classe de equivalência mais cada fronteira; no máximo um teste por comportamento distinto; parar quando toda obrigação tem evidência e nada é redundante; cobertura dita por obrigação, não em percentual. Medição da fonte: a cobertura auditada foi de 60% para 83% de um para dois testes por critério e estagnou a partir de três, com código de teste chegando a 3,6 vezes o código provado.
- **Forge hoje:** skill `qa-testing`: cada critério de aceite tem ao menos um teste, bordas, mutação só no diff, cobertura de linha não é meta. Existe o piso, falta o teto (redundância e parada).
- **Proposta:** seção curta na `qa-testing` (obrigação → teste, regra de parada, redundante não entra); a tabela critério → teste do parecer ganha a coluna "fronteira protegida". A mutação continua como contraprova. A skill está perto do limite de linhas: talvez um arquivo de referência.
- **Ganho e medida:** menos teste escrito e mantido sem perder detecção. Medir testes por critério e linhas de teste por linha de código do diff; o escore de mutação no diff e os escapes não podem piorar.

### 5. Toda regra e decisão nasce com o fato que a reverte · adotar · P
- **Fonte:** `CLAUDE.md` (seção "Determinism and state": proposta recusada guarda o motivo e o critério que a reabriria; mudança justificada por custo cita a medição e o estimador) e cada `specs/*.md`, que termina com a validação exigida e "Readings" datadas, com veredito pendente e o critério que reverte a regra.
- **Forge hoje:** ADRs têm alternativas e consequências; experimentos têm métrica, linha de base e sucesso, e terminam em manter, ajustar ou reverter. Nenhuma ADR ou regra diz o que a reverteria; rejeições não ficam com critério de reabertura.
- **Proposta:** o formato de ADR e de experimento ganha "Critério de reversão" (um fato observável) e "Leituras" (data, medida, veredito). Este estudo já usa "reabre se" nas rejeições.
- **Ganho e medida:** decisões reavaliadas por dado, sem rediscutir ideia já recusada. Medir a fração de ADRs e experimentos com critério de reversão e de leituras feitas no prazo.

### 6. Mecanismo novo só depois de mostrar por que o existente não basta · adotar · P
- **Fonte:** `CLAUDE.md` ("Determinism and state"): proposta de campo, checagem, canal ou agente nomeia antes o que já existe para a mesma necessidade e mostra, pelo que aquilo registrou ao rodar (saídas, histórico), e não pela descrição, por que não basta.
- **Forge hoje:** a skill `contribuir-com-o-forge` e este processo não pedem isso. O Forge já tem seis hooks, `forge-check`, verificador de transcrições e vigia: há risco real de um segundo mecanismo para a mesma necessidade.
- **Proposta:** um campo no modelo de PR de melhoria e na skill: "o que já existe para isso e por que não basta (evidência de execução)".
- **Ganho e medida:** menos código a manter e menos contexto. Medir PRs de melhoria com o campo preenchido e mecanismos fundidos ou removidos por ciclo.

### 7. Guardas contra teste que passa em silêncio · adotar · P
- **Fonte:** `src/standards/README.md` ("What the suite reads": teste que percorre um glob afirma que o glob não está vazio) e `CLAUDE.md` (teste preso a palavras que a mudança reescreveu é reancorado, nunca afrouxado; teste de ausência é relido quando o texto que procura muda, porque "não achei" também vale para um trecho que deixou de existir).
- **Forge hoje:** os testes estruturais percorrem agentes, skills, stacks, regras e fixtures de hooks; `Neutralidade`, `AntiDuplicacao` e `termos_proibidos_hash` são testes de ausência. Afrouxar invariante já exige destaque no PR, mas nada impede um conjunto vazio de passar.
- **Proposta:** todo teste que percorre pasta ou lista afirma um mínimo de itens; o checklist do review relê teste de ausência cujo alvo mudou.
- **Ganho e medida:** a suíte deixa de ficar verde por falta do que testar. Medir com mutação simples (renomear a pasta varrida deve derrubar o teste) e contar os testes com guarda.

### 8. Regra do padrão marcada "ferramenta" ou "leitura"; revisor só lê · adaptar · M
- **Fonte:** `src/standards/README.md`, `src/claude/schemas/standard.json`, `src/claude/agents/standard-conformance-reviewer.md`. Cada regra do padrão do projeto diz quem a decide; as de ferramenta rodam na suíte do projeto, e o revisor recebe só as de leitura que alcançam os arquivos do diff. O revisor é só leitura e devolve achados, sem veredito nem severidade. Revisão sem padrão declara que não rodou, nunca sai "limpa".
- **Forge hoje:** regra 5 de `docs/economia-de-tokens.md` (a máquina testa) e o `praticas.md` do projeto; o review do `tech-lead` lê o diff contra todas as práticas; o `tech-lead` tem Write/Edit sem restrição de caminho além de `docs/reviews/`.
- **Proposta:** em `templates/projeto/docs/engineering/praticas.md`, coluna "decidida por" (comando ou leitura); o review lê só as de leitura e cita a saída das ferramentas. Depois, avaliar no `hooks/conformidade.json` que o `tech-lead`, ao revisar, não grave fora de `docs/reviews/` (escritor e revisor separados, pesquisa seção 5.6).
- **Ganho e medida:** review mais barato e sem achado que a ferramenta já dá. Medir tokens do review por entrega e achados que uma ferramenta apontaria.

### 9. Decisão do usuário só vale gravada; resumo de compactação não autoriza · adaptar · P
- **Fonte:** `src/claude/hooks/rules.md` (autorização vem das palavras do usuário na sessão; resumo de contexto anterior não autoriza; rota retomada após compactação pergunta de novo) e a seção 15 da telemetria, que classifica cada commit pela origem da autorização.
- **Forge hoje:** agentes commitam em branch por desenho, protegidos por `R-FLUXO` e `R-MAIN`; a retomada (`docs/retomada-de-sessao.md`) reconcilia o estado com o git. Mas a resposta do usuário a uma decisão pode existir só no resumo de compactação do Jarvis.
- **Proposta:** a resposta do usuário a uma decisão é gravada no arquivo do pedido ou no diário de retomada no mesmo turno; após compactação, decisão que não está no disco é perguntada de novo. A parte de commit não é adotada (item 12).
- **Ganho e medida:** nenhuma ação apoiada em decisão parafraseada. Medir decisões com registro em arquivo sobre decisões levadas, e ações pós-compactação sem registro.

### 10. Pedido vago vira instrução com suposições e descobertas explícitas · adaptar · M
- **Fonte:** `src/claude/skills/clarify-request/SKILL.md`. Sem executar nem escrever, lê o projeto só para resolver referências, pergunta só o bloqueante (item 1) em até duas rodadas e devolve uma instrução com modo, tarefa, suposições (cada uma com caminho e linha de base) e o que o executor deve descobrir. Linha sem fonte é apagada; o modo nunca sobe (pedido de olhar não vira pedido de mudar).
- **Forge hoje:** `R-DISCOVERY` e o prompt-padrão de seis seções; não há passo de entrada que fixe o modo do pedido e liste as suposições antes do discovery.
- **Proposta:** primeiro passo do discovery: o Jarvis grava no arquivo do pedido o modo (analisar, planejar, implementar), o escopo e as suposições com a base. Sem skill nova.
- **Ganho e medida:** menos discovery em cima de pedido mal entendido. Medir bugs com origem "spec" e rodadas de pergunta por pedido em `entregas.md`.

### 11. Especificação como autoridade única, com metamodelo e rastreio · rejeitar · G
- **Fonte:** `specs/metamodel.md`, `specs/domain-model-files.md`, `specs/minimal-documentation.md`, `specs/adoption.md`, `src/claude/bin/trace.py`.
- **Forge hoje:** especificação de UX, plano técnico e constituição por pedido, com contrato de frontmatter (ADR 0004).
- **Motivo:** muda o modo de trabalho de todos os projetos (migração pesada), exige bibliotecas fora da padrão (critério 6), impõe um vocabulário de modelagem de domínio a projetos que podem não usá-lo e aumenta o contexto lido por entrega (critério 1).
- **Reabre se:** um projeto exigir rastreabilidade auditável requisito → arquivo, com o custo de reler a especificação medido acima do custo de manter o rastreio. Ideia menor aproveitável sem isso: "um termo, um nome" na especificação de UX.

### 12. Regras de estilo impostas pela fábrica · rejeitar · P
- **Fonte:** `src/claude/hooks/rules.md` (código sem comentários; commit só com palavra do usuário) e `CLAUDE.md` ("Language": todo artefato em inglês).
- **Forge hoje:** idioma do usuário; estilo de código é da stack e do projeto (ADR 0001); commits autônomos em branch, contidos por `R-FLUXO`, `R-MAIN`, review e QA.
- **Motivo:** comentário e idioma são escolha de cada projeto, e impor quebra a neutralidade (`R-NEUTRO`); commit só por palavra do usuário anula a autonomia que o fluxo de branches já contém.
- **Reabre se:** as transcrições mostrarem commit indevido fora de branch de trabalho apesar dos hooks.

## O que o Forge já faz igual ou melhor
- Regra citada por ID, com texto único e teste anti-duplicação (ADR 0002); a fonte cita a frase literal com teste de substring: o Forge gasta menos tokens.
- Hooks só agem em projeto marcado (`.forge/versao`, ADR 0003), como `rules.py` só age onde há o arquivo de marcação do projeto.
- Migração com simulação (`forge-upgrade --simular`, ADR 0005), equivalente às ferramentas de migração com `--dry-run` da fonte.
- Versão conferida pelo CI contra o `CHANGELOG.md`, equivalente à conferência de versão em três lugares da fonte.
- Conteúdo lido é dado, não instrução (pesquisa, seção 8.3; skill `cyber-security`).
- `git add` por caminho, nunca da árvore toda (pesquisa, seção 5.4; prompt-padrão do Jarvis).
- Núcleo sem stack (ADR 0001), como `src/standards/` fica fora do que a fonte distribui.
- Estado lido do disco ao retomar (`docs/retomada-de-sessao.md`), como o comando de status da fonte.
- Agentes e skills quase sem histórico (o histórico fica em ADRs e no `CHANGELOG.md`), como o princípio "What ships is timeless" da fonte.

## Conflitos (decisão do usuário, uma por vez, `R-DECISAO`)
Ordem sugerida: C3 (destrava os itens 1 e 2), C1, C2.

### C1. Decidir e divulgar fatos de negócio não declarados
- **Contexto:** a fonte (`specs/minimal-documentation.md` R4, R9, R10, R13; `CLAUDE.md`, "Decision authority") decide o valor que a especificação não diz, num contexto que não vê a tarefa, registra num log ao lado do nó e segue; o humano revisa depois; contradição sempre para. No Forge, `R-DECISAO` manda regra de negócio ao usuário: adotar afrouxa uma regra com ID.
- **A. Manter `R-DECISAO`.** Pró: o usuário controla o negócio. Contra: mais paradas.
- **B. Experimento limitado:** fato de negócio não declarado, reversível, sem dado pessoal, sem custo e sem contradição é decidido pelo time e listado num log do projeto que o usuário revisa na entrega; reverte se mais de 1 em cada 5 for corrigida. Pró: menos paradas. Contra: afrouxa `R-DECISAO` (destaque no título do PR).
- **C. Adotar integral.** Pró: fluxo sem paradas. Contra: muda o papel do usuário; regra de negócio errada pode chegar à produção.
- **Recomendação: A.** O item 1 já transforma em suposição listada o que é reversível e barato, sem afrouxar a regra. Reabre B se as transcrições mostrarem que mais da metade das decisões de negócio levadas ao usuário são aceitas como recomendadas.

### C2. Regras da fábrica injetadas por hook em toda sessão e subagente
- **Contexto:** a fonte (`src/claude/hooks/hooks.json`, `rules.py`; `README.md`, seção 4) põe as regras de sessão como contexto em `SessionStart` e `SubagentStart`, só em projeto marcado; nada vai para a raiz e a atualização chega com o plugin, sem migração. No Forge, a lista de IDs fica no `CLAUDE.md` do projeto (modelo) e muda por `forge-upgrade`; a ADR 0003 (vigente) proíbe hook de injetar contexto, com a retomada como única exceção.
- **A. Manter.** Pró: nenhum token a mais, ADR intacta. Contra: mudar a lista pede migração.
- **B. Mover a seção "Regras da fábrica" do `CLAUDE.md` do projeto para um hook `SessionStart`.** Pró: atualização sem migração, mesmo custo na sessão principal. Contra: emenda a ADR 0003; os subagentes, que leem o `CLAUDE.md`, perdem a lista.
- **C. B mais `SubagentStart`.** Pró: todos recebem a lista atualizada. Contra: custo multiplicado pelo número de agentes (critério 1).
- **Recomendação: A.** O ganho é só evitar a migração de um bloco de oito linhas que muda pouco, e o `forge-upgrade` já resolve isso. Reabre se a lista mudar em duas releases seguidas.

### C3. Quando o time não recomenda
- **Contexto:** a fonte (`specs/handoff.md` R2, R3) só recomenda com um critério de lista fechada (pré-condição não atendida, regra violada, já feito, leitura paga duas vezes), o fato no disco que decide e o que reverteria; nunca recomenda sobre escopo do pedido, contradição, duas leituras da mesma evidência, peso de um achado ou custo. No Forge, `R-DECISAO` exige recomendação em toda decisão, inclusive escopo, prioridade e custo.
- **A. Manter como está.** Pró: o usuário sempre recebe uma opinião. Contra: preferência e fato chegam com o mesmo peso.
- **B. Adotar a fonte.** Pró: recomendação só onde um fato decide. Contra: afrouxa `R-DECISAO`; o usuário perde a opinião do time onde mais pesa.
- **C. Recomendar sempre, com a base declarada:** o nível da escada do item 1 que decidiu; em escopo, prioridade ou custo, a marca "preferência do time", separada dos fatos.
- **Recomendação: C.** Preserva o que `R-DECISAO` garante, acrescenta a transparência que motiva a fonte e só reforça a regra. Esforço P; medida: fração de recomendações com base declarada (verificador de transcrições).

## Riscos observados
- **Sem licença declarada** na raiz da fonte: vale todos os direitos reservados. Adotamos ideias, nunca texto; cada PR de adoção escreve com palavras próprias.
- **A fonte cita nomes de projetos consumidores** nos `specs/` (seções de medição): nada disso pode passar para o Forge (`R-NEUTRO`; a catraca de termos não conhece esses nomes).
- **Números da fonte não se transferem:** foram medidos nos projetos dela; cada adoção mede a própria linha de base antes.
- **Ritmo alto de versões** (5.x com 19 versões menores): a triagem fica nos caminhos de interesse do processo para não virar custo de leitura.
