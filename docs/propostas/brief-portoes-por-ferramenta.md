# Como os briefs dos portões saem da ferramenta e deixam de segurar as vagas?

Propósito: desenhar o subcomando que gera e sela os briefs dos portões (review, segurança, QA, devops) a partir do pedido e do head, e a fila que o Jarvis dispara quando uma vaga abre (cartão BRIEF-NAO-SEGURA-VAGAS, ORDEM DO DONO de 14/11 15:53, pedido v047, etapa E1.224). Público: dono do Forge, Jarvis, `tech-lead`, `security-engineer`, `software-architect`. Revisão: 2026-11-14.

Estado: proposta, só desenho, para o parecer de segurança antes de qualquer código. Marcas: **[COD]** confirmado no código da `develop` 7fff73e4; **[INF]** decisão de desenho a verificar na implementação.

## 1. Problema e evidência

- A ordem do dono (14/11 15:53): "Hoje você escreve cada brief, um por vez, e as vagas ficam vazias enquanto isso. [...] os briefs dos portões (review, segurança, QA, devops) passam a ser gerados por ferramenta a partir do pedido e do head; você escreve à mão só os briefs de autor; quando um agente termina, o próximo brief já está pronto. [...] O selo continua obrigatório."
- Vagas ociosas: ORDEM DO DONO de 14/11 14:03 registra 4 agentes e 46% do processador parado com teto 16.
- Volume: dos 338 briefs do v047 em `docs/briefs/`, 198 (59%) têm `Etapa:` review, seguranca ou qa, e outros 12 do `devops-engineer` são portão com `Etapa: review` (contagem de 14/11 por `grep '^Etapa:'`). É trabalho repetido, quase todo derivável do pedido e do git.
- Erro de digitação que a ferramenta não comete: o `## Histórico` do v047 (14/11 15:53) registra ERRO-JARVIS "os briefs de portão não mandavam pedido: v047 no frontmatter e os pareceres saíram com o nome da branch". Campo derivado escrito à mão errou quatro vezes no mesmo dia.

## 2. O que já existe e por que não basta

Existe [COD]:
- `forge-check brief gerar --pedido P --destino forge:<x>... --branch B --etapa review|seguranca|qa --gravar`: cabeçalho, `Base-sha`, `Revisar-sha` (`sha_a_revisar`, AQ-5), decisões por referência, `## Fora do escopo`, PQ de `forge-check docs` e do CI; aceita vários destinos e grava um arquivo por destino (`docs/briefs/<pedido>-<papel>-<n>.md`, aberto com `x`).
- `forge-check classe --json` (classe, portões, pareceres exigidos e gatilhos de segurança do diff), `forge-check parecer delta`, `forge-check brief selar` (corrige derivados, roda `avaliar_brief`, grava o selo no `## Histórico`), o hook `agentes` (recusa brief sem selo ou com hash diferente; avisa brief vencido).

Não basta, com evidência:
- O `gerar` deixa `PREENCHER` no `## Entregar`, no `arquivos:` e nos PQ (`montar_brief`), e o selo reprova enquanto restar um. O Jarvis escreve à mão, a cada portão, o mesmo Entregar: pasta do parecer, `pedido:` e `commit:` do frontmatter, clone de trabalho, envio, formato dos achados, revalidação pelo delta. É esse texto que segura a vaga e que errou o `pedido:`.
- O `gerar` não lê a classe: o Jarvis roda `forge-check classe`, escolhe os destinos e repete o comando por portão.
- O `Fora do escopo` lista uma linha por etapa do pedido (`linha_de_outra_etapa`); no v047, com 360 etapas, só a parte fixa passa de 9 KB e se aproxima do teto de 10.000 caracteres do `R-BRIEF`.
- Nada liga "o autor terminou" a "o brief do portão está pronto": o `forge-check entrega --pedido` grava `entrega conferida <sha40>` e para aí; a fila do `forge-check fila` é de cartões, não de briefs.
- O portão de devops não tem etapa própria: `ETAPAS_DE_PARECER = ("review", "seguranca", "qa")`, e os briefs de devops do v047 saíram com `Etapa: review`.

O mecanismo novo reaproveita `montar_brief`, `sha_a_revisar`, `cmd_classe`, `parecer_delta` e `cmd_brief_selar`; nada disso é duplicado.

## 3. O subcomando

```
forge-check brief portoes --pedido P --branch B [--head H] [--classe auto|T|N|C] [--so-mostrar] [--sem-selar]
```

- `--head` padrão: `origin/B` (o que foi enviado, nunca a árvore local). Recusa (rc 1, nada gravado) se `origin/B` não existe ou se o head local da branch não é igual ao remoto.
- Pré-condição: a última linha `entrega conferida <sha40>` do `## Histórico` do pedido para a branch `B` tem o sha igual ao `Revisar-sha` calculado. Sem entrega conferida nesse código, recusa: portão não roda sobre entrega não conferida (`R-PROVA`).
- `--classe auto` (padrão): a mesma função do `forge-check classe` (`classe_da_entrega`, `gatilhos_do_diff`, `pareceres_exigidos`) sobre `base...head`. `--classe T|N|C` só pode **subir** a classe (T < N < C); pedir classe abaixo da calculada recusa. Catraca que não carrega dá C (falha fechada, já é assim em `catraca_da_classe`).
- Portões e destinos, tirados de `pareceres_exigidos` somados ao que o plano técnico do pedido marca (a mesma soma do `forge-check pr`, uma só fonte):

| Parecer exigido | Destino | `Etapa:` | Pasta do parecer |
|---|---|---|---|
| `review` | `forge:tech-lead` | `review` | `docs/reviews/` |
| `qa` | `forge:qa-engineer` | `qa` | `docs/qa/` |
| `revisao-seguranca` | `forge:security-engineer` | `seguranca` | `docs/security/` |
| `revisao-devops` | `forge:devops-engineer` | `devops` (nova) | `docs/devops/` |

- Portão já feito no mesmo código (parecer na `origin/B` com `commit:` igual ao `Revisar-sha`) não gera brief: sai a linha `portão em dia: <tipo> <arquivo>`.
- Saída: uma linha por brief, `brief na fila: docs/briefs/<pedido>-<papel>-<n>.md sha256 <hash> · <tipo> · <novo|revalidação> · Revisar-sha <sha12>`, e uma linha de resumo. `--so-mostrar` imprime os briefs sem gravar nem selar (para o review do gerador e para depuração). rc 0 com todos selados; 1 com qualquer recusa (nenhum arquivo fica gravado sem selo: o que reprova é apagado na mesma execução, porque foi aberto com `x` por ela); 2 erro de uso.

### 3.1 O que sai do pedido e do head (sem `PREENCHER`)

| Campo | Origem |
|---|---|
| `Agente destino`, `Etapa`, pasta do parecer | tabela acima |
| `Pedido:` | o `id:` do pedido |
| `Branch`, `Base`, `Base-sha` | `base_sha_real` / `base_sha_esperado` [COD] |
| `Revisar-sha:` | `sha_a_revisar(origin/B)` [COD] |
| `Cobre:` | a etapa do pedido do papel do destino, aberta, que cita `[branch B]` (seção 3.3) |
| `pedido:` do frontmatter | o slug que o `forge-check pr` e o `forge-fechar` procuram para a branch `B` (a mesma função; no v047 é `v047`, na release é `release-X.Y.Z`) [INF: extrair a função que hoje resolve o slug em `cmd_pr`] |
| `commit:` do frontmatter | igual ao `Revisar-sha:`, escrito literal no Entregar |
| Revalidação | parecer do mesmo tipo já na `origin/B` com `commit:` ancestral do `Revisar-sha`: o Entregar manda ler só `forge-check parecer delta <arquivo>` e registrar no parecer o delta `<commit12>..<revisar12>`; parecer com `commit:` que não é ancestral recusa (história reescrita) |
| `Fora do escopo` | compacto (seção 3.2) |
| `Ler` | `forge-check proximo P`, as seções do pedido e, no QA das classes N e C, o pedido sem o código (aceite em paralelo, `skills/qa-testing`) |
| Pronto quando | `forge-check docs`, a linha do CI (`linha_do_ci_do_parecer`), o PQ (push) da branch e o PQ (arquivo) do parecer |

O Entregar é um modelo fixo por tipo, no código (constante versionada `MODELO_PORTOES = 1`), com só valores calculados interpolados por `interpolacao_segura` [COD] e `nome_seguro`. Do texto do pedido entra uma única coisa: a linha da etapa coberta, citada entre aspas como já faz `montar_brief`, sem controle (`sem_controle`) e reprovada por `caractere_disfarcado`. Nenhuma frase do pedido vira instrução fora das aspas.

### 3.2 Fora do escopo compacto

Hoje cada outra etapa leva o trecho literal (`R-BRIEF`). Proposta: as outras etapas vão por faixa de id, `- E1.1–E1.223, E2.1–E2.30 · outras etapas do pedido, sem a marca; continuam no pedido`. O `conferir_corte` passa a expandir a faixa contra `## Etapas` (cada id da faixa existe no pedido; faixa com buraco ou id inexistente reprova). Isso muda o texto de `R-BRIEF` ("com o trecho literal" → "por id ou faixa de ids"), e por isso vai num PR próprio, antes do subcomando, com destaque no título por mexer numa regra protegida. Enquanto não entra, o gerador usa a forma de hoje.

### 3.3 Etapa no pedido

O selo exige `Cobre:` de uma etapa do pedido do papel do destino. Duas saídas:
- (a) o Jarvis abre a etapa do portão no pedido e o subcomando só a acha (recusa sem ela, com a linha pronta para colar);
- (b) o subcomando grava a etapa com texto fixo, `- E<n>.<m> (<papel>): [branch B] parecer de <tipo> no código <sha12> (gerado)`, sob a mesma trava de arquivo do `gravar_no_historico`.

Recomendo (b): sem ela a vaga continua esperando o Jarvis escrever uma linha. O texto é fixo e só leva valores calculados. Ponto para a segurança: é a ferramenta escrevendo em `## Etapas`, que hoje só o Jarvis escreve (ameaça T4).

## 4. O selo continua obrigatório

- O subcomando chama o `cmd_brief_selar` de hoje, com todas as checagens (`avaliar_brief`, decisões E8, teto, caractere disfarçado, corte, PQ). Não existe selo novo nem atalho: a linha `brief selado docs/briefs/<x>.md <sha256>` e o hook `agentes` ficam como estão.
- Linha nova no cabeçalho do brief, dentro do conteúdo selado: `Gerado-por: forge-check brief portoes modelo 1`.
- **Selo de reprodução** [INF]: brief com `Gerado-por:` só é selado se o `selar` o regenera com as mesmas entradas (pedido, branch, `Revisar-sha`, classe) e obtém os mesmos bytes. Brief gerado e depois editado à mão perde o `Gerado-por:` ou não sela. Assim o que o Jarvis não leu é exatamente o que o modelo revisado em PR produz.
- Pendência de decisão do dono (E8) reprova como hoje: o gerador não decide nada que o dono não decidiu.
- `--sem-selar` grava sem selo, para o Jarvis ler e selar à mão (o caminho de hoje), e é o caminho de reversão.

## 5. A fila de briefs prontos

- Gatilho: o `forge-check entrega --pedido P --branch B --etapa codigo` (e o da volta), depois de gravar `entrega conferida <sha40>`, imprime o comando `forge-check brief portoes --pedido P --branch B`. Com `--portoes`, roda-o na mesma execução. A geração não espera vaga: o brief fica pronto quando o autor termina.
- `forge-check brief fila [--pedido P]` (só leitura): lista, em ordem de chegada (a hora do selo), os briefs selados com `Gerado-por:` que ainda valem e não foram disparados, até o número de vagas (`teto_calculado` menos `agentes_vigentes`, carga alta zera; a mesma conta do `forge-check fila`). Uma linha por brief: destino, caminho, sha256 e a linha pronta da delegação.
- **Ainda vale**: o `Revisar-sha` do brief é o `sha_a_revisar(origin/B)` de agora e `brief_vencido` não devolve nada. Brief que perdeu a validade sai como `vencido: rode brief portoes de novo`, nunca como pronto.
- **Já disparado**: o hook `agentes` passa a gravar `brief` (caminho e sha256) no registro do agente em `agentes.json` [INF: hoje grava `branches` e `escrita`, não o brief]; a fila também tira o brief cujo parecer já está na `origin/B` com `commit:` igual ao `Revisar-sha`.
- A fila não lança agente: só o Jarvis delega (ferramenta `Agent`), e o hook `agentes` confere selo, teto e Z10 como hoje. Os portões da mesma branch rodam juntos (Z10: leem a branch, gravam só o próprio parecer).
- No Jarvis: "a cada agente que termina, `forge-check brief fila` e dispare o que ela mostra" (uma linha em `agents/jarvis.md` e na skill `briefs-e-conferencia`).

## 6. O que fica à mão

- Briefs de autor (`codigo`), de volta (`gerar --volta`, que já tira os achados dos pareceres), de PR e de integração (`gerar --etapa merge-integracao` já sai quase completo), e o do `forge:conferente`.
- Portão com pedido especial do dono (por exemplo, parecer só de um trecho): `--sem-selar` e edição à mão, que perde o `Gerado-por:`.
- O texto do parecer e o veredito: o gerador escreve o pedido do trabalho, não o resultado.

## 7. O que vale para os projetos

- O subcomando mora no `bin/forge-check` do plugin e vale em todo projeto sem configuração: pastas de parecer do modelo (`templates/projeto/docs/reviews`, `qa`, `security`, `devops` já existem), classe pela catraca do projeto (sem catraca, C).
- Clone de trabalho: no Forge, a linha do clone em `~/.forge-contrib/wt/<slug>-<papel>`; no projeto, a worktree da sessão (a mesma regra do `checagem-do-brief`). [INF: a regra do caminho vem da função que o `gerar` já usa para avisar worktree de outra sessão.]
- Mudam: `agents/jarvis.md` (uma linha), skill `briefs-e-conferencia` (passo "portões: `brief portoes`, depois `brief fila`"), `docs/regras/R-BRIEF.md` (faixa de ids, seção 3.2) e o `CHANGELOG` por fragmento. Nada específico de projeto (`R-NEUTRO`).

## 8. Ameaças para a segurança avaliar

| # | Ameaça | Desenho | Risco residual |
|---|---|---|---|
| T1 | Brief gerado sem leitura humana | Modelo fixo no código, revisado por PR (classe C: `bin/`); só valores calculados; selo de reprodução; `MODELO_PORTOES` versionado | Defeito no modelo vale para todos os briefs até a correção; mitigado pelo teste de ouro (seção 9) |
| T2 | Injeção pelo texto do pedido | Só a linha da etapa coberta entra, entre aspas, com `sem_controle` e `caractere_disfarcado`; ids e branch passam por `NOME_SEGURO_DE_BRIEF` e `interpolacao_segura`; nada do pedido fora das aspas | Texto entre aspas ainda chega ao modelo do agente; o agente lê o pedido de qualquer forma hoje |
| T3 | Selo de brief que o Jarvis não leu | O selo deixa de valer "o Jarvis leu" e passa a valer "a ferramenta reproduz byte a byte"; o Jarvis vê a linha de resumo de cada brief na fila; decisão E8 pendente ainda reprova | Quem confia no selo como prova de leitura humana perde essa garantia; o dono decide se aceita (está na ordem de 15:53) |
| T4 | Ferramenta escrevendo em `## Etapas` (opção 3.3 b) | Texto fixo, trava de arquivo, uma linha por portão, só valores calculados | Erro de numeração de etapa; recusa se o id já existe |
| T5 | Brief de portão sobre código que mudou depois | Pré-condição de entrega conferida no mesmo sha; fila tira o vencido; hook já avisa `brief_vencido` | Push entre a fila e o disparo: o parecer grava `commit:` do brief, e o `forge-check pr` aponta o delta |
| T6 | `--classe` para baixo | Só sobe; pedir abaixo recusa | Nenhum conhecido |
| T7 | Branch ou head forjado | `--head` padrão no remoto; local diferente do remoto recusa | Credencial do remoto fora do escopo |

## 9. Testes e mutantes previstos

Testes de comportamento (subprocesso com ambiente limpo e `python3 -I`, `AR-4`, `AR-5`), em `tests/test_brief_portoes.py`:
- ouro: repositório de fixture com pedido, branch e entrega conferida; classe N gera review e QA, classe C gera review, segurança e QA; gatilho de infraestrutura soma devops; saída sem `PREENCHER`, selada, `pedido:` e `commit:` corretos.
- revalidação: parecer anterior com `commit:` ancestral gera brief com o `parecer delta`; com `commit:` não ancestral recusa; com `commit:` igual imprime `portão em dia`.
- recusas: sem entrega conferida; local diferente do remoto; `--classe` abaixo; pedido com caractere disfarçado na etapa; decisão E8 pendente (nada gravado, nenhum arquivo sobra).
- selo de reprodução: brief gerado e editado em um byte não sela.
- fila: ordem de chegada; brief vencido não sai como pronto; brief disparado some; vagas zero não lista.
- `conferir_corte` com faixa: faixa com id inexistente reprova (PR da seção 3.2).

Mutantes declarados, um por guarda (`tests/mutantes/v047-brief-portoes.json`, AR-1): entrega conferida no sha; local igual ao remoto; classe só sobe; portão em dia; `commit:` ancestral; caractere disfarçado; reprodução no selo; vencido na fila; apagar o que reprovou. São 9 guardas: abre também `v047-brief-portoes-2.json`.

## 10. Entrega em partes (M14, um comportamento por PR)

1. `conferir_corte` com faixa e o texto de `R-BRIEF` (destaque no título: muda regra protegida).
2. Etapa `devops` em `ETAPAS_DE_PARECER` e o `brief` no registro do hook `agentes` (classe C, `hooks/`, corpus próprio).
3. `brief portoes` com selo de reprodução.
4. `brief fila` e o `--portoes` do `entrega`; linha do Jarvis e da skill.

## 11. Medida, reversão e o que sai

- Medida: tempo entre `entrega conferida` e o disparo do primeiro portão (do `## Histórico` e do `agentes.json`), antes e depois, nos dois pedidos seguintes à entrada; e a fração de briefs de portão com `Gerado-por:`. Meta: mediana abaixo de 2 minutos e nenhum erro de `pedido:` ou `commit:` em parecer.
- Critério de reversão: se em 30 dias um parecer sair com campo errado vindo do modelo, ou a mediana não cair, os briefs voltam a sair por `--sem-selar` com leitura do Jarvis (o caminho de hoje), sem remover código.
- O que sai: o passo manual "preencher o Entregar do portão" da skill `briefs-e-conferencia`; o `gerar --etapa review|seguranca|qa` continua só para o caso da seção 6.

## 12. Riscos

- Modelo de Entregar errado se repete em todos os briefs: teste de ouro e `MODELO_PORTOES` versionado.
- A função do slug do `pedido:` diverge do `forge-fechar`: uma só função para os dois.
- Faixa no `Fora do escopo` esconde etapa nova acrescentada no meio: a expansão confere contra `## Etapas` no selo.
- O `agentes.json` é estado da sessão; perdido, a fila pode mostrar brief já disparado, e o parecer no remoto é a segunda prova. O hook Z10 recusa portão duplicado na mesma branch só se escreve; parecer duplicado é custo, não defeito.
