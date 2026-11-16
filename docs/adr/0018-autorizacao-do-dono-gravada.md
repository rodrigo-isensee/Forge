# 0018 - Autorização do dono gravada: escopo, palavras exatas e validade

Estado: proposta (vale depois do parecer do `security-engineer` sobre este desenho e das decisões D1 a D3 do dono; o número segue a 0017, da `melhoria/v047-forge-sempre-atual`, e é tomado na integração, em ordem). Data: 2026-11-16.
Propósito: definir o registro das autorizações do dono e a conferência dele pelas ferramentas antes do rótulo `afrouxa-regra` e do merge na `main` (cartão G1 do pedido v047, E2.483). Público: quem mantém o Forge, o `tech-lead`, o `security-engineer` e o `devops-engineer`. Revisão: 2026-11-16.

## Contexto
Ordem do dono (16/11 15:40): registrar as autorizações com escopo, palavras exatas e validade; o rótulo de exceção e o merge na `main` só passam com uma autorização ativa que os cubra; nada afrouxa, só aperta. A ideia vem do estudo de 16/11 sobre um projeto externo de código aberto (anexo do clone de contribuição, fora do repositório); só a ideia, nenhum código.

Três leituras largas da fala do dono, de 06/11 a 16/11: "Pode aplicar os rótulos também" (validade de um fim de semana, escrita à mão no pedido); "pode aplicar o rótulo do afrouxa, está liberado para este plano" (v047, decisão de 16/11 05:13), lida também para motivo novo; "pode mesclar a main esta noite" (13/11 20:42), sem versão nem hora de fim gravadas. Em nenhuma delas uma ferramenta conferiu escopo nem validade antes do ato.

## Decisão
1. **Registro.** Um arquivo por evento, só acréscimo, em `<raiz principal do clone>/.forge/autorizacoes/`, aberto com `x` e sem seguir link (como as falas de `bin/forge_dono.py`). Quatro tipos: concessão `A-<n>`, confirmação `C-<n>`, uso `U-<n>` e retirada `R-<n>`, com `n` sequencial curto, fácil de digitar. Nada se edita nem se apaga: a retirada e o uso são eventos novos.
2. **Campos da concessão** (cabeçalho `Campo: valor`, linha vazia, corpo): `Id`, `Ato` (`rotulo-afrouxa-regra` ou `merge-main`), `Alvos` (`pr:<N>` em lista, ou `versao:<X.Y.Z>`), `Validade` (`uso-unico` ou `ate:<AAAA-MM-DD HH:MM>`), `Origem-da-validade` (o termo literal ou `sem termo`), `Estado-inicial` (`ativa` ou `pendente-confirmacao`), `Mensagem` (uuid da mensagem do dono na transcrição), `Hora-da-fala` (carimbo da transcrição, não do relógio do agente), `Sessao`, `Sha256` (das palavras), `Gravado-por` (sha256 do `forge-check`, como o registro de autoria dos pareceres), `Autoriza: só o ato e os alvos acima, até a validade; não amplia outra regra (R-DECISAO)`. O corpo são as palavras do dono, byte a byte.
3. **Quem grava: só a palavra do dono, literal.** Só a sessão principal (o Jarvis; evento do hook sem `agent_id`) roda `forge-check autorizacao gravar --palavras '<literal>' --mensagem <uuid> --transcricao <caminho> --ato <ato> --alvos <alvos>`. O hook `conformidade` (PreToolUse) aceita só essa forma, com o literal entre aspas simples (gramática positiva, ADR 0011); expansão, heredoc, variável ou subcomando barram. Ele confere que `--transcricao` é o `transcript_path` do próprio evento (como `transcript_da_sessao` de `hooks/agentes.py`) e que as palavras são trecho contíguo, byte a byte, da mensagem `--mensagem` digitada pelo dono. O `forge-check` repete a conferência antes de gravar (duas leituras independentes).
4. **O que conta como mensagem do dono:** classificador positivo, falha fechada. Só a entrada de usuário digitada na sessão principal; ficam fora resultado de ferramenta, notificação de tarefa, retorno de subagente, mensagem entre agentes, lembrete do sistema, resumo de compactação, comando expandido e qualquer forma que o classificador não conheça. As fixtures saem de transcrições reais do Claude Code.
5. **Escopo estreito, ancorado nas palavras.** O ato exige um termo do vocabulário fechado nas palavras (sem acento, minúsculas): `rotulo` ou `afrouxa` para o rótulo; `main` para o merge. Cada alvo (número do PR, versão) que aparece como palavra inteira nas palavras deixa a concessão `ativa`. Alvo que não aparece (ex.: "este plano", enumerado pelo Jarvis) a deixa `pendente-confirmacao`. Ela só fica ativa com uma confirmação `C-<n>`: mensagem posterior do dono com o `Id` e uma palavra de `PALAVRAS` de `bin/forge_dono.py`, conferida pelo hook como no item 3. Não existe alvo genérico ("todos", "qualquer", pedido inteiro): PR novo é alvo novo.
6. **Validade, sempre explícita e com teto.** Mapa fechado do termo das palavras: sem termo, `uso-unico`; "hoje" ou "hj", 23:59 do dia da fala; "esta noite", 08:00 do dia seguinte; "até amanhã", 23:59 do dia seguinte; data e hora escritas ("até 18/11 12:00"), essa data e hora (23:59 sem hora). Termo fora do mapa vale `uso-unico`, e o Jarvis pergunta a data. Toda validade para no teto (D1; até a decisão, 48 h desde a fala).
7. **Ativa** quer dizer: concessão íntegra (o `Sha256` bate com o corpo, `Gravado-por` igual ao `forge-check` do plugin carregado, arquivo comum sem link), confirmada quando nasceu pendente, agora antes da validade e do teto, sem retirada, e, se `uso-unico`, sem uso. Erro ao ler qualquer evento vale como "não há autorização" (falha fechada).
8. **Retirar é livre; conceder, não.** `forge-check autorizacao retirar <Id>` não precisa da palavra do dono, porque só aperta. Ela grava `R-<n>` e marca `Retirada:` na declaração dos PRs que a citam (item 10).
9. **Rótulo (local).** Em `gh_rotulo` de `hooks/conformidade.py`, depois do `exigir_dono` de hoje (fica igual), entra `exigir_autorizacao("rotulo-afrouxa-regra", pr=N)`. Sem o número do PR legível no comando, ou sem concessão ativa que cubra `pr:N`, barra com `R-CONTRIB` e diz o que falta: o ato, o PR e o comando `forge-check autorizacao gravar`. O uso (`U-<n>`) é gravado pelo hook na liberação, antes do comando rodar: comando que falha consome a autorização assim mesmo, o lado mais estreito.
10. **Rótulo (CI).** `forge-check autorizacao declarar --pr N` escreve no corpo do PR o bloco `Autorização: <Id> sha256 <64> · ato · alvos · validade`, com as palavras entre aspas. A catraca só aceita o rótulo do dono (`rotulo_do_dono` de `tests/catraca.py`) se esse bloco cobre o PR, com o evento `labeled` antes da validade e sem `Retirada:`. Na promoção (S-16) vale a declaração do PR onde o rótulo foi posto. No CI, a camada confere forma e coerência; a origem das palavras é conferida só na camada local (Consequências).
11. **Merge na `main`.** A trava de hoje fica como está: nenhum agente mescla na `main` (`R-MAIN`, `gh pr merge` com base `main`, `gh api` de merge, `bin/forge-fechar`), com ou sem autorização. A autorização não destrava nada. Entra um job obrigatório `autorizacao-main` nos PRs com base `main`: exige no corpo a declaração de uma concessão `merge-main` cuja `versao:` é a do `plugin.json` do head, dentro da validade e sem `Retirada:`. Sem ela, o job fica vermelho e o merge não passa, nem pela interface (D2). Pôr o job na proteção da `main` é acesso: o dono aplica (D3).
12. **Leitura.** `forge-check autorizacao ler` lista cada concessão com estado (ativa, pendente, vencida, retirada, usada), integridade e palavras; o Jarvis a lê antes de perguntar de novo (`R-DECISAO`).
13. **Neutro.** O código vale para qualquer raiz e não cita projeto. Levar isso aos projetos (`R-MAIN` deles, ADR 0014) é decisão à parte, pela migração da ADR 0005.

### Corte em etapas (cada uma deixa a suíte verde sozinha)
| Etapa | Quem | O quê | Depende de |
|---|---|---|---|
| G1.1 | tech-lead | Formato, leitura e `autorizacao ler` (só leitura, nada barra); testes de integridade, link e evento adulterado | — |
| G1.2 | tech-lead + security-engineer | `gravar`, `confirmar`, `retirar`; conferência na transcrição no hook e no `forge-check`; `.forge/autorizacoes/` protegida em `hooks/conformidade.json` (escrita só pelos subcomandos e pelo hook) | G1.1 |
| G1.3 | tech-lead | `exigir_autorizacao` no rótulo e o `U-<n>` na liberação; mutantes nos ramos de falha (AR-1, AR-2) | G1.2 |
| G1.4 | tech-lead + devops-engineer | `declarar` e a declaração na catraca (rótulo e promoção) | G1.3 |
| G1.5 | devops-engineer | Job `autorizacao-main`; o dono o põe na proteção da `main` (D3) | G1.4 |
| G1.6 | tech-lead | Texto: `R-CONTRIB`, `R-DECISAO` e `R-MAIN` citam o registro; skill `falar-com-o-dono` e `agents/jarvis.md`; só acréscimo em `invariantes` de `tests/config.json` | G1.3 |

QA em todas as etapas (`qa-engineer`); parecer de segurança em G1.2 a G1.5 (gatilhos: hook, autorização, CI).

### Decisões em aberto, ao dono (`R-DECISAO`)
- **D1, teto da validade.** a) 48 h desde a fala (recomendada: cobre "esta noite" e "até amanhã", e o caso de 06/11 seria regravado no segundo dia); b) 7 dias; c) sem teto, só o termo. Até a resposta vale a), a mais estreita.
- **D2, a `main` mesclada pelo dono na interface também precisa da declaração?** a) sim (recomendada: é a ordem literal, e o CI não distingue a conta do dono usada por um agente da conta usada pelo próprio dono; custo: uma frase por versão); b) não, e o job vira só aviso.
- **D3, o job `autorizacao-main` na proteção da `main`:** é acesso e só o dono aplica; `comando: —`.

## Alternativas
- **Só texto nas regras** ("leia a decisão antes"): é o estado de hoje e deixou passar as três leituras do Contexto.
- **Estender a fala do `pedido fala --gravar`** com escopo e validade: ela é gravada pelo agente a partir do que ele diz que o dono falou, sem conferência de origem; pôr o ato nela faria a fala ampliar autorização, o contrário do que ela promete (`bin/forge_dono.py:360`).
- **Hook `UserPromptSubmit` novo** que guarda o hash de toda mensagem do dono: dá a origem sem ler a transcrição, mas acrescenta um hook em todo turno de todo projeto e grava texto do dono sem necessidade. A transcrição já é lida e protegida (`hooks/agentes.py`, `hooks/conformidade.json`). Reabre se a leitura da transcrição falhar mais de 2 vezes por mês com formato novo do Claude Code.
- **Registro versionado no repositório** (para o CI conferir a origem): a conta do `gh` usada pelos agentes é a do dono, então o CI não distingue quem escreveu; o registro no repositório daria a mesma prova que a declaração no corpo, com um commit a mais por autorização.
- **A autorização destravar o merge do agente na `main`:** afrouxa `R-MAIN`; fora deste desenho, só por decisão do dono.

## Consequências
- Melhora: o rótulo e o merge na `main` passam a depender de um registro com as palavras exatas, alvo nomeado e prazo; o "liberado para este plano" deixa de cobrir PR ou motivo novo sem confirmação.
- Piora: o dono escreve uma frase com o número do PR ou a versão, ou confirma um `Id`, por ato; mensagem de recusa a mais quando falta a autorização.
- Limite conhecido: no CI, a declaração no corpo do PR prova forma e coerência, não origem; quem tem a conta do `gh` do dono pode escrevê-la fora do Forge. A origem só se prova na camada local. Um token separado para os agentes fecharia isso; é acesso e fica para o dono.
- Limite conhecido: palavras coladas pelo dono contam como dele. É a regra de hoje para qualquer fala.
- A manter: o classificador da transcrição acompanha o formato do Claude Code (fixtures reais); o mapa de validade e o vocabulário do ato só crescem por ADR.
- Afrouxa? Não. Nada sai de `docs/regras/`, de `tests/config.json` nem de controle: o `exigir_dono`, a catraca por conteúdo e a trava da `main` ficam; tudo aqui é condição a mais.

## Por que o existente não basta
- **Conta do dono:** `exigir_dono` (`hooks/conformidade.py:2299`) compara a conta do `gh` com a dona do repositório, e `rotulo_do_dono` (`tests/catraca.py:1057`) compara o `actor` do evento `labeled`. Na sessão do Forge o `gh` dos agentes está na conta do dono, então os dois passam para qualquer papel. Evidência: as decisões de 06/11 21:51 (`versao-04x`) e de 16/11 05:13 (v047) entregaram ao Jarvis a aplicação do rótulo, e os dois portões conferem só a conta; escopo e validade ficaram no texto do pedido, sem ferramenta que os leia.
- **Fala literal:** `forge-check pedido fala --gravar` (`bin/forge_dono.py:348`) guarda as palavras com sha256 e declara que não amplia autorização. Nenhum hook a lê: a busca por `fala-` e `autoriza` em `hooks/` dá 0 ocorrências.
- **Decisões no pedido:** as linhas `DECISÃO DO DONO` são texto escrito pelo Jarvis com a leitura dele. A leitura "liberado para este plano" virou motivo novo (estudo de 16/11, linha G1), e nenhuma ferramenta a confrontou com o ato.

## Critério de parada
- bloqueia: rótulo `afrouxa-regra` aplicado por agente, ou PR para a `main` com o job verde, sem concessão ativa gravada da palavra literal do dono que cubra o PR ou a versão; e concessão gravada com palavras que não estão numa mensagem digitada pelo dono
- fala-forjada · palavras que não são trecho contíguo de uma mensagem do dono na transcrição do evento, ou mensagem que não é do dono (ferramenta, subagente, notificação, resumo) · oráculo: python3 -m unittest tests.test_autorizacao_gravar
- forma-opaca · `autorizacao gravar` ou `confirmar` com expansão, variável, heredoc, subcomando, abreviação ou fora da sessão principal · oráculo: python3 -m unittest tests.test_conformidade_autorizacao
- escrita-direta · escrita em `.forge/autorizacoes/` por Write, Edit ou Bash fora dos subcomandos · oráculo: python3 -m unittest tests.test_conformidade_autorizacao
- escopo-largo · alvo fora das palavras sem confirmação `C-<n>`, alvo genérico ou ato sem termo do vocabulário · oráculo: python3 -m unittest tests.test_autorizacao_gravar
- inativa · concessão vencida, além do teto, retirada, usada (uso único), adulterada ou gravada por outro `forge-check` · oráculo: python3 -m unittest tests.test_autorizacao_ler
- rotulo-sem-autorizacao · `gh` que aplica o rótulo sem concessão ativa para o PR, ou sem PR legível · oráculo: python3 -m unittest tests.test_conformidade_autorizacao
- ci-sem-declaracao · catraca ou `autorizacao-main` verde sem declaração que cubra o PR ou a versão · oráculo: python3 -m unittest tests.test_catraca tests.test_autorizacao_main
- gatilho · oráculo: python3 -m unittest tests.test_autorizacao_ler tests.test_autorizacao_gravar tests.test_conformidade_autorizacao tests.test_catraca tests.test_autorizacao_main

## Critério de reversão
Se, nos 30 dias depois da G1.3 entrar na `develop`, houver mais de 3 recusas indevidas (autorização dita pelo dono, gravada e recusada pela ferramenta), registradas no `## Histórico` dos pedidos como `autorizacao: recusa indevida`, o vocabulário do ato e o mapa de validade voltam ao desenho para ajuste, sem tirar a conferência.

## Leituras
| Data | Medida | Veredito (manter, ajustar, reverter) |
|---|---|---|
| AAAA-MM-DD | recusas indevidas em 30 dias; atos de rótulo ou `main` sem concessão ativa (meta 0) | pendente |
