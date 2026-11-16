# Como os briefs dos portões saem da ferramenta e deixam de segurar as vagas?

Propósito: desenhar o subcomando que gera e sela os briefs dos portões (review, segurança, QA, devops) a partir do pedido e do head, e a fila que o Jarvis dispara quando uma vaga abre (cartão BRIEF-NAO-SEGURA-VAGAS, ORDEM DO DONO de 14/11 15:53, pedido v047, etapa E1.224). Público: dono do Forge, Jarvis, `tech-lead`, `security-engineer`, `software-architect`. Revisão: 2026-11-14.

Estado: proposta, só desenho, volta do parecer de segurança `docs/security/v047-brief-portoes.md` (E1.228: A1 na seção 3.4, A2 na 3.3, A3 na 4, A4 e A5 na 3, A6 na 3.2) e da revalidação E1.241 (A7 na 3.4, item do opaco, nos mutantes e na parte 0 da seção 10, volta E1.244), antes de qualquer código. Marcas: **[COD]** confirmado no código da `develop` 7fff73e4; **[INF]** decisão de desenho a verificar na implementação.

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

- `--head` padrão: o head do remoto **de agora** (A5). Antes de gerar, uma só função, `head_enviado(raiz, B)`, lê `git ls-remote origin refs/heads/B` e exige que ele seja igual a `origin/B` e ao head local da branch (se existir); se diverge, se falta o ref ou se a rede falha, recusa (rc 1, nada gravado). Dois refs igualmente velhos não passam, porque o `ls-remote` é a leitura de agora. A mesma função dá o head ao `selar` dos briefs com `Gerado-por:` (seção 4, A3).
- Pré-condição: a última linha `entrega conferida <sha40>` do `## Histórico` do pedido para a branch `B` tem o sha igual ao `Revisar-sha` calculado. Sem entrega conferida nesse código, recusa: portão não roda sobre entrega não conferida (`R-PROVA`).
- `--classe auto` (padrão): a mesma função do `forge-check classe` (`classe_da_entrega`, `gatilhos_do_diff`, `pareceres_exigidos`) sobre `base...head`. `--classe T|N|C` só pode **subir** a classe (T < N < C); pedir classe abaixo da calculada recusa. Catraca que não carrega dá C (falha fechada, já é assim em `catraca_da_classe`).
- Portões e destinos, tirados de `pareceres_exigidos` somados ao que o plano técnico do pedido marca (a mesma soma do `forge-check pr`, uma só fonte):

| Parecer exigido | Destino | `Etapa:` | Pasta do parecer |
|---|---|---|---|
| `review` | `forge:tech-lead` | `review` | `docs/reviews/` |
| `qa` | `forge:qa-engineer` | `qa` | `docs/qa/` |
| `revisao-seguranca` | `forge:security-engineer` | `seguranca` | `docs/security/` |
| `revisao-devops` | `forge:devops-engineer` | `devops` (nova) | `docs/devops/` |

- `ETAPAS_DE_PARECER` com uma fonte só (A4): hoje há três cópias (`bin/forge-check:2216` e `:8261`, `hooks/agentes.py:574`). As duas do `forge-check` viram uma constante; o hook `agentes` deixa a cópia dele e lê `forge_check().ETAPAS_DE_PARECER` (ele já carrega o módulo quando lê um brief, `hooks/agentes.py:618`). O `devops` entra nessa constante e em nenhum outro lugar. Teste: o hook `agentes` não tem literal da tupla, e o brief `Etapa: devops` é tratado como parecer (Z10) pelo hook e pelo gerador.
- O Entregar do portão de devops limita a escrita a `docs/devops/<pedido>.md` (linha `arquivos:` do modelo, um caminho só): a mesma fronteira dos outros portões, que gravam só o próprio parecer; workflow e infra ficam com o autor.

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

Hoje cada outra etapa leva o trecho literal (`R-BRIEF`). Proposta: as outras etapas vão por faixa de id, `- E1.1–E1.223, E2.1–E2.30 · outras etapas do pedido, sem a marca; continuam no pedido`. Semântica exata da expansão no `conferir_corte` (A6): seja `F` o conjunto dos ids que as faixas cobrem, intersectado com os ids de `## Etapas`; o corte passa só se `F` é igual aos ids do pedido menos o `Cobre:`, nem mais, nem menos. Id da faixa que o pedido não tem é ignorado (o v047 não tem `E1.102`: buraco no pedido não reprova); id do pedido fora de toda faixa reprova (etapa nova acrescentada no meio aparece); faixa cujo intervalo contém o `Cobre:` reprova, mesmo que ele saia de `F` (a etapa delegada nunca vai ao Fora do escopo). O gerador monta as faixas pela mesma função, então o que ele escreve é o que o corte aceita. Isso muda o texto de `R-BRIEF` ("com o trecho literal" → "por id ou faixa de ids"), e por isso vai num PR próprio, antes do subcomando, com destaque no título por mexer numa regra protegida. Enquanto não entra, o gerador usa a forma de hoje.

### 3.3 Etapa no pedido

O selo exige `Cobre:` de uma etapa do pedido do papel do destino. Duas saídas:
- (a) o Jarvis abre a etapa do portão no pedido e o subcomando só a acha (recusa sem ela, com a linha pronta para colar);
- (b) o subcomando grava a etapa com texto fixo, `- E<n>.<m> (<papel>): [branch B] parecer de <tipo> no código <sha12> (gerado)`.

Decisão: (b), aceita pela segurança (A2) com três condições, que entram no desenho como guardas:
1. **Id dentro da trava.** Uma função nova, `gravar_etapas_geradas(arq, pedidas)`, abre o pedido com `fcntl.flock(LOCK_EX)` (a trava do `gravar_no_historico`, `bin/forge-check:8510`) e, sob ela, lê `## Etapas`, calcula cada id e grava as linhas; nada da numeração é lido antes da trava. `n` é o grupo da última etapa de `## Etapas` que cita `[branch B]` (sem nenhuma, recusa: o portão não abre etapa de branch que o pedido não conhece); `m` é o maior `m` do grupo `n` mais 1, um por linha nova. Idempotência pela chave natural (branch, tipo, sha12): linha `(gerado)` igual já presente é reaproveitada, não duplicada, e a execução seguinte a uma recusa não abre id novo.
2. **Linha por expressão fechada.** Antes de gravar, cada linha passa por `^- E\d+\.\d+ \((tech-lead|qa-engineer|security-engineer|devops-engineer)\): \[branch <B>\] parecer de (review|qa|seguranca|devops) no código [0-9a-f]{12} \(gerado\)$`, com `<B>` já validado por `NOME_SEGURO_DE_BRIEF` e `git check-ref-format` e escapado com `re.escape`; o par papel e tipo tem de ser o da tabela da seção 3. Falhou uma: recusa sem gravar nenhuma.
3. **Todas as etapas antes do primeiro brief.** Numa execução com vários portões, `gravar_etapas_geradas` grava todas de uma vez (uma trava, uma escrita) e só depois o gerador relê o pedido e monta os briefs; assim o `Fora do escopo` de cada brief já lista as irmãs. Brief que reprova no selo é apagado (seção 3); a etapa gravada fica (o pedido é append-only) e é reaproveitada pela chave natural na próxima execução.

O texto é fixo e só leva valores calculados; só o dono do pedido roda o subcomando (seção 3.4), então a escrita em `## Etapas` continua do papel que já a escreve (ameaça T4).

### 3.4 Fronteira no hook `conformidade` (A1)

Hoje o hook só vê escrita do `brief` em `selar` e em `gerar --gravar` (`grava_no_pedido`, `hooks/conformidade.py:669`; `FORGE_CHECK_ESCRITAS`, `:480` e `:1601`), e a lista dos papéis só de leitura libera `forge-check brief` e `forge-check entrega` inteiros (`hooks/conformidade.json:111`). A sonda S1 da segurança e as desta volta (abaixo) mostram que `brief portoes` passaria em qualquer papel. Regra nova, falha fechada, no mesmo PR do subcomando (seção 10, parte 3):

- **Ações do `brief` numa fonte.** O `bin/forge-check` ganha `BRIEF_ACOES = ("gerar", "selar", "mensagem", "portoes", "fila")`, usada pelo despacho do `brief`; `alvo` fora dela sem `/` e sem terminar em `.md` sai com rc 2 (palavra solta não vira conferência de arquivo, então ação nova nunca se disfarça de leitura).
- **No hook, toda ação do `brief` grava, menos a lista fechada de leitura.** `BRIEF_NO_HOOK = {"fila": "le", "mensagem": "le", "gerar": "grava com --gravar", "selar": "grava", "portoes": "grava salvo --so-mostrar"}`; a conferência de arquivo (`alvo` com `/` ou `.md`) lê. O hook procura as ações em **todas** as palavras livres depois de `brief` (como o `"selar" in livres[1:]` de hoje), porque `livres_do_forge_check` também devolve o valor das opções: em `brief --pedido fila portoes` a ação é `portoes`, e basta uma palavra de escrita para a linha gravar. O inverso (`brief fila --pedido portoes`) é recusado ao papel sem escrita: falso positivo aceito, na dúvida recusa.
- **`--so-mostrar` pela leitura do argparse.** Conta como leitura só `abreviacao_de(a, ("--so-mostrar",))`, sem `=valor` e antes de um `--` (depois dele é posicional e o argparse recusa a linha). Abreviação que o argparse não aceita (`--s`, ambígua com `--sem-selar`) é escrita.
- **`entrega --portoes` grava** no pedido e em `docs/briefs/`, com qualquer `--sem-gravar` ou `--so-leitura` na linha: o hook ignora as duas quando `--portoes` (ou a abreviação aceita, `--po` em diante) está presente, e o argparse recusa a combinação (rc 2), para as duas leituras baterem.
- **Destinos.** `brief portoes` (sem `--so-mostrar`) e `entrega --portoes` passam pela política de caminhos em `docs/pedidos/` **e** `docs/briefs/` (`forge_check_grava`, nas duas raízes), então só o papel dono dessas pastas (`jarvis`, `hooks/conformidade.json:56-64`) os roda; papel de autor e papel só de leitura são recusados (`checar_so_leitura` já chama `forge_check_grava_no_pedido`, que passa a ver as formas novas).
- **Programa opaco e interpretador (A7, parte 0 da seção 10).** `args_do_forge_check` (`hooks/conformidade.py:97-108`) hoje só devolve os argumentos do programa opaco quando a linha tem `anotar --tipo` ou `--gravar`, e no interpretador só acha o script pelo nome literal `forge-check`; fora disso o `forge_check_grava` (`:1590`) não roda, e as sondas S2 e S6 a S11 mostram `brief selar`, `pausa` e `recado` passando no papel de autor pelo opaco, pela crase, pela variável e pelo interpretador [COD]. Regra nova, falha fechada, **sem lista de subcomandos no critério do opaco**:
  - programa opaco é o nome com `$` ou crase (`$(command -v forge-check)`, `"$(which forge-check)"`, `` `command -v forge-check` ``, `"$f"`); `args_do_forge_check` devolve **sempre** os argumentos dele, sem olhar o subcomando;
  - no interpretador (`INTERPRETES`), além do nome literal, **cada** palavra opaca devolve os argumentos que vêm depois dela e o hook confere cada fatia: a opção com valor (`-W ignore`, `-X "$v"`) não esconde o script opaco que vem depois, e a fatia que começa num script comum do usuário não casa subcomando e não grava nada;
  - quem decide é a política de destinos inteira do `forge_check_grava`: ela só confere destino quando o subcomando é de escrita (`grava_no_pedido`, `pausa` sem `--retomar`, `FORGE_CHECK_ESCRITAS`, `recado` sem `--confirmar`, `transcricao anonimizar`), então a leitura pelo opaco passa como hoje e o subcomando de escrita novo (o `brief portoes` e o `entrega --portoes` das partes 3 e 4) entra no opaco no mesmo dia em que entra no `forge_check_grava`, sem segunda lista a manter (`AR-3`). A condição `anotar --tipo` / `--gravar` de hoje sai, coberta pela regra geral;
  - envolvedor (`env`, `command`, `timeout`, `xargs`), `bash -c` e `eval` já chegam ao `args_do_forge_check` com o programa desembrulhado ou o texto reanalisado (sonda S11: `env forge-check pausa` dá rc 2), então valem pela mesma regra sem código próprio (`AR-8`, `AR-10`);
  - falso positivo aceito: outro programa opaco cujo primeiro argumento livre coincide com um subcomando de escrita (`"$editor" pausa`) é conferido como `forge-check` e recusado fora da política do papel; na dúvida, recusa.

Sondas desta volta (hook `conformidade` em `beb017bd`, papel pelo `agent_type`, subprocesso com `python3 -I` e ambiente limpo; só leitura):
- S2 · `$(command -v forge-check) brief selar --pedido v047 --arquivo docs/briefs/x.md`, papel de autor de stack · espera: recusa · obtido: rc 0 (a forma direta dá rc 2). Defeito já na `develop`, independente do subcomando: vai como correção própria (seção 10, parte 0).
- S3 · `forge-check brief portoes --pedido v047 --branch melhoria/x`, papel de autor de stack e `forge:conferente` · espera: recusa · obtido: rc 0 nos dois (confirma A1).
- S4 · `forge-check brief --pedido fila portoes --branch melhoria/x`, papel `forge:conferente` · espera: recusa · obtido: rc 0; `livres_do_forge_check` devolve `['brief', 'fila', 'portoes', 'melhoria/x']`, por isso a regra olha todas as palavras livres.
- S5 · `grava_no_pedido` com `entrega --pedido v047 ... --portoes --so-leitura` · espera: True · obtido: False (daí a regra de `--portoes` acima).

Sondas do parecer de segurança (A7, hook em `c8861f24`) e desta volta (hook em `0979cb63`, papel de autor de stack pelo `agent_type`, repositório temporário, ambiente limpo; só leitura):
- S6 · `$(command -v forge-check) pausa` · espera: rc 2 · obtido: rc 0 (a forma direta dá rc 2).
- S7 · `$(command -v forge-check) recado --para . oi` · espera: rc 2 · obtido: rc 0.
- S8 · `python3 -I "$(command -v forge-check)" pausa` · espera: rc 2 · obtido: rc 0.
- S9 · `f=$(command -v forge-check); "$f" pausa` e `` `command -v forge-check` recado --para . oi `` · espera: rc 2 · obtido: rc 0 nas duas.
- S10 · `python3 -W ignore "$(command -v forge-check)" pausa` · espera: rc 2 · obtido: rc 0 (opção com valor antes do script opaco; daí "cada palavra opaca").
- S11 · `env`, `command`, `timeout 5` e `xargs` antes de `"$(command -v forge-check)" pausa`, `bash -c '"$(command -v forge-check)" pausa'` e `eval "$(command -v forge-check) pausa"` · espera: rc 2 · obtido: rc 0 em todas; `env forge-check pausa` e `command forge-check pausa` dão rc 2 (o envolvedor já é desembrulhado; o furo é só o opaco).
- S12 · leituras pelo opaco: `pausa --retomar`, `recado --confirmar`, `pedido --ler v047`, `brief fila`, `entrega v047` · espera: rc 0 · obtido: rc 0 (têm de continuar assim depois da parte 0).

Corpus da parte 0 (`tests/hooks/conformidade/`, papel de autor de stack, e `forge:conferente` nas leituras; teste em subprocesso com ambiente limpo e `python3 -I`, `AR-4`, `AR-5`):
- **Recusa (rc 2)**: o produto das escritas pelas formas. Escritas: `brief selar --pedido v047 --arquivo docs/briefs/x.md`, `brief gerar ... --gravar`, `entrega --pedido v047`, `pausa`, `recado --para . oi`, `pedido` sem `--ler`, `rodar`, `meta`, `medida`, `anotar --tipo nota`, `transcricao anonimizar a.txt docs/pedidos/b.md`. Formas: `$(command -v forge-check)`, `"$(which forge-check)"`, crase, `f=$(command -v forge-check); "$f"`, `python3 "$(command -v forge-check)"`, `python3 -I "$(command -v forge-check)"`, `python3 -W ignore "$(command -v forge-check)"`, `env "$(command -v forge-check)"` e `eval "$(command -v forge-check) ..."`. O teste gera o produto (11 × 9) das duas listas, afirma o mínimo de 99 casos (checklist 11) e exige rc 2 em cada um.
- **Passa (rc 0)**: as leituras nas mesmas formas (`brief fila`, `brief mensagem`, `brief docs/briefs/x.md`, `entrega v047` pela forma antiga, `entrega --pedido v047 --so-leitura`, `pausa --retomar`, `recado --confirmar`, `pedido --ler v047`) e um programa opaco com subcomando que não é do `forge-check` (`"$f" --version`, `"$f" status`).
- **Sessão principal** (`jarvis`): as escritas pelo opaco passam, como a forma direta.

Limite registrado, fora da parte 0 (não é opaco, é outra classe): a cópia renomeada (`cp "$(command -v forge-check)" fc; ./fc pausa` e `python3 fc pausa`) dá rc 0 na sonda desta volta. O hook não modela binário da fábrica copiado para nome livre; vai como sugestão própria ao Forge, não neste PR (um comportamento por PR em `hooks/`).

Testes do hook (`tests/test_conformidade_brief_portoes.py`, subprocesso com ambiente limpo e `python3 -I`, `AR-4`, `AR-5`):
- **Cruzamento com o argparse** (`AR-11`, a leitura do hook igual à da ferramenta): carrega o `bin/forge-check` como módulo e exige `set(BRIEF_ACOES) == set(BRIEF_NO_HOOK)`, uma classificação por ação; ação nova sem classificação no hook reprova o CI. Do parser do `brief` e do `entrega` (`_option_string_actions`), gera todas as abreviações de `--so-mostrar` e `--portoes` e exige que o hook trate como leitura exatamente as que o argparse resolve para `--so-mostrar`, e como escrita todas as que resolve para `--portoes`; as que o argparse recusa por ambiguidade ficam como escrita.
- **Formas**, cada uma com o rc esperado: `portoes`; `portoes --so-mostrar`, `--so`, `--so-m`, `--so-mostrar=1`, `-- --so-mostrar`; `--pedido fila portoes`; `$(command -v forge-check) brief portoes` e `brief selar`; `python3 -I "$(command -v forge-check)" brief portoes`; `entrega --pedido ... --portoes`, `--po`, `--portoes --so-leitura`, `--portoes --sem-gravar`; `--raiz` e `--raiz-pedidos` antes e depois do subcomando.
- **Papéis**: `forge:conferente`, `forge:leitura` e um papel de autor recusam todas as formas de escrita; a sessão principal (`jarvis`) passa; `brief fila`, `brief mensagem`, `brief <arquivo>` e `portoes --so-mostrar` passam no `conferente`.

## 4. O selo continua obrigatório

- O subcomando chama o `cmd_brief_selar` de hoje, com todas as checagens (`avaliar_brief`, decisões E8, teto, caractere disfarçado, corte, PQ). Não existe selo novo nem atalho: a linha `brief selado docs/briefs/<x>.md <sha256>` e o hook `agentes` ficam como estão.
- Linha nova no cabeçalho do brief, dentro do conteúdo selado: `Gerado-por: forge-check brief portoes modelo 1`.
- **Selo de reprodução** [INF]: brief com `Gerado-por:` só é selado se o `selar` o regenera com as mesmas entradas (pedido, branch, `Revisar-sha`, classe) e obtém os mesmos bytes. Brief gerado e depois editado à mão perde o `Gerado-por:` ou não sela. Assim o que o Jarvis não leu é exatamente o que o modelo revisado em PR produz.
- **Uma fonte do head e nada de rede nos bytes (A3).** Para brief com `Gerado-por:`, o `selar` não usa `corrigir_revisar_sha` nem `corrigir_derivados` (que leem a branch local, `bin/forge-check:8663`): o head vem de `head_enviado(raiz, B)` (seção 3), a mesma função do gerador. O modelo não chama `linha_do_ci_do_parecer` nem outra leitura do `gh`: o PQ do CI sai de texto fixo com a branch e o `Revisar-sha` (o agente do portão lê o CI na hora). Os bytes reproduzidos dependem só do pedido, do git depois do `ls-remote` e do `MODELO_PORTOES`; reprodução que falha recusa (falha fechada) e devolve a vaga ao Jarvis com o motivo.
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
| T4 | Ferramenta escrevendo em `## Etapas` (opção 3.3 b) | Só o dono do pedido roda o subcomando (seção 3.4); id calculado e linha gravada sob a mesma trava; expressão fechada; todas as etapas antes do primeiro brief; chave natural (branch, tipo, sha12) | Nenhum conhecido |
| T5 | Brief de portão sobre código que mudou depois | Pré-condição de entrega conferida no mesmo sha; fila tira o vencido; hook já avisa `brief_vencido` | Push entre a fila e o disparo: o parecer grava `commit:` do brief, e o `forge-check pr` aponta o delta |
| T6 | `--classe` para baixo | Só sobe; pedir abaixo recusa | Nenhum conhecido |
| T7 | Branch ou head forjado ou velho | `ls-remote` de agora igual a `origin/B` e ao local, senão recusa; sem rede recusa (A5) | Credencial do remoto fora do escopo |
| T8 | Papel sem escrita no pedido roda `brief portoes` ou `entrega --portoes` (A1) | Hook em falha fechada: toda ação do `brief` grava salvo a lista fechada de leitura; `--portoes` grava sempre; opaco e interpretador pelo mesmo predicado; teste cruzado com o argparse (seção 3.4) | Ação nova do `brief` sem classificação no hook: o teste cruzado reprova o CI |

## 9. Testes e mutantes previstos

Testes de comportamento (subprocesso com ambiente limpo e `python3 -I`, `AR-4`, `AR-5`), em `tests/test_brief_portoes.py`:
- ouro: repositório de fixture com pedido, branch e entrega conferida; classe N gera review e QA, classe C gera review, segurança e QA; gatilho de infraestrutura soma devops; saída sem `PREENCHER`, selada, `pedido:` e `commit:` corretos.
- revalidação: parecer anterior com `commit:` ancestral gera brief com o `parecer delta`; com `commit:` não ancestral recusa; com `commit:` igual imprime `portão em dia`.
- recusas: sem entrega conferida; local diferente do remoto; `--classe` abaixo; pedido com caractere disfarçado na etapa; decisão E8 pendente (nada gravado, nenhum arquivo sobra).
- selo de reprodução: brief gerado e editado em um byte não sela.
- fila: ordem de chegada; brief vencido não sai como pronto; brief disparado some; vagas zero não lista.
- `conferir_corte` com faixa (PR da seção 3.2): id do pedido fora das faixas reprova; faixa que contém o `Cobre:` reprova; buraco no pedido (id da faixa que ele não tem) passa.
- etapas geradas (3.3): duas execuções em paralelo sobre o mesmo pedido, de branches diferentes, não repetem id; linha fora da expressão (papel fora da tabela, branch que o `check-ref-format` recusa) recusa sem gravar; com review e QA na mesma execução, o `Fora do escopo` de cada brief lista a etapa do outro; a segunda execução reaproveita a linha `(gerado)`.
- head (A5, A3): `ls-remote` diferente de `origin/B` recusa; remoto inacessível recusa; o `selar` de brief gerado, com a branch local atrasada, usa o head do remoto.
- `ETAPAS_DE_PARECER` (A4): uma fonte; `Etapa: devops` é parecer para o hook `agentes` e para o gerador.
- hook (seção 3.4): o cruzamento com o argparse e as formas e papéis listados lá.

Mutantes declarados, um por linha de guarda, por PR da seção 10 (`tests/mutantes/<pedido>.json`, AR-1; passou de 8, abre `-2.json`):
- parte 0 (opaco, A7): opaco passa pela política inteira (devolver `None` no ramo do opaco reprova o corpus de recusa); interpretador acha o script opaco (sem o ramo, S8 reprova); cada palavra opaca do interpretador, não só a primeira (só a primeira, S10 reprova).
- parte 1 (corte): id do pedido fora das faixas; faixa que contém o `Cobre:`.
- parte 2 (Z10): `devops` na constante única.
- parte 3 (subcomando e hook): entrega conferida no sha; `ls-remote` igual a `origin/B`; local igual ao remoto; classe só sobe; portão em dia; `commit:` ancestral; caractere disfarçado; reprodução no selo; apagar o que reprovou; expressão fechada da etapa; etapa da branch existe; chave natural da etapa; `alvo` solto recusa; ação do `brief` grava salvo leitura; `--so-mostrar` lê; destino `docs/briefs/` do `portoes`.
- parte 4 (fila e `--portoes`): vencido na fila; `--portoes` grava com `--so-leitura`; argparse recusa `--portoes` com `--sem-gravar` ou `--so-leitura`.

## 10. Entrega em partes (M14, um comportamento por PR)

0. Correção já na `develop` (sondas S2 e S6 a S11, A7): o programa opaco do `forge-check` e o interpretador com script opaco passam sempre pela política de destinos inteira do `forge_check_grava`, sem lista de subcomandos à parte (seção 3.4, item do opaco), com o corpus de recusa e de leitura de lá (`fix`, classe C, `hooks/`, corpus próprio). Não depende do resto e entra primeiro; o `brief portoes` e o `entrega --portoes` das partes 3 e 4 entram no opaco sem linha nova, pela regra do `forge_check_grava`.
1. `conferir_corte` com faixa e o texto de `R-BRIEF` (destaque no título: muda regra protegida).
2. `ETAPAS_DE_PARECER` com fonte única, a etapa `devops` nela e o `brief` no registro do hook `agentes` (classe C, `hooks/`, corpus próprio).
3. `brief portoes` com selo de reprodução e `gravar_etapas_geradas` e, no mesmo PR, a regra do hook `conformidade` da seção 3.4 com o teste cruzado (o subcomando não chega à `develop` invisível ao hook).
4. `brief fila` e o `--portoes` do `entrega`, com a regra do hook para `--portoes` no mesmo PR; linha do Jarvis e da skill.

## 11. Medida, reversão e o que sai

- Medida: tempo entre `entrega conferida` e o disparo do primeiro portão (do `## Histórico` e do `agentes.json`), antes e depois, nos dois pedidos seguintes à entrada; e a fração de briefs de portão com `Gerado-por:`. Meta: mediana abaixo de 2 minutos e nenhum erro de `pedido:` ou `commit:` em parecer.
- Critério de reversão: se em 30 dias um parecer sair com campo errado vindo do modelo, ou a mediana não cair, os briefs voltam a sair por `--sem-selar` com leitura do Jarvis (o caminho de hoje), sem remover código.
- O que sai: o passo manual "preencher o Entregar do portão" da skill `briefs-e-conferencia`; o `gerar --etapa review|seguranca|qa` continua só para o caso da seção 6.

## 12. Riscos

- Modelo de Entregar errado se repete em todos os briefs: teste de ouro e `MODELO_PORTOES` versionado.
- A função do slug do `pedido:` diverge do `forge-fechar`: uma só função para os dois.
- Faixa no `Fora do escopo` esconde etapa nova acrescentada no meio: a expansão confere contra `## Etapas` no selo.
- O `agentes.json` é estado da sessão; perdido, a fila pode mostrar brief já disparado, e o parecer no remoto é a segunda prova. O hook Z10 recusa portão duplicado na mesma branch só se escreve; parecer duplicado é custo, não defeito.
