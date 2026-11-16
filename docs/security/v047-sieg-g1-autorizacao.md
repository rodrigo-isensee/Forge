---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-sieg-g1-autorizacao
commit: a87f0a6f84340873491da2257360b8c4effc1b71
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 ADR 0018, autorização do dono gravada (E2.485, head a87f0a6f)

Gatilhos: hook, autorização, CI (`R-SEGURANCA`). Revisão de desenho: a ADR 0018 é a única mudança do head (sem código, sem teste novo; nada a rodar). Parecer completo, sem parecer anterior. Os oráculos que a ADR cita ainda não existem.

## Resumo
- Só aperta: confirmado. O `exigir_dono` (`hooks/conformidade.py:2299`) e a catraca por conteúdo ficam; entram condições a mais (ADR itens 9, 10, 11). Nenhum caminho novo libera o que hoje barra; `retirar` livre (item 8) e a falha fechada (item 7) só estreitam.
- A prova de autoria resiste a subagente: só a sessão principal grava (item 3), o transcript é protegido (`hooks/conformidade.json:50-53`, `quem: []`), classificador positivo e falha fechada (item 4). Não resiste ao que a ADR quer vencer, a leitura larga feita pela sessão principal: o trecho contíguo (item 3) deixa o agente recortar a frase do dono (A1).
- Os limites que a ADR declara (CI prova forma e não origem; palavra colada conta como do dono) estão certos; faltam os que os achados A5, A3 e A6 descrevem.
- Reprovado por um bloqueante (A1). O resto é recomendado e entra nas etapas G1.2 a G1.5.

## Achados
- A1 (bloqueante) docs/adr/0018-autorizacao-do-dono-gravada.md:14 · Palavras = "trecho contíguo" escolhido pelo agente: recortar tira negação, condição e prazo ("não mescle a main 0.47.3 ainda" vira "mescle a main 0.47.3"), e ato, alvo e validade saem do recorte. A mensagem inteira tem de ser o corpo.
- A2 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:16 · "Palavra inteira" aceita número solto como alvo ("às 5", "3 PRs" cobrem pr:5, pr:3): exija marcador (`PR`, `#`, `versão`) colado ao número, e alvo só com ato na mesma frase.
- A3 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:66 · Proteção de `.forge/autorizacoes/` na G1.2 sem lista: o modelo é `.forge/recados/`, com três grafias (relativa, `~/.forge-contrib/` e `~/.forge-contrib/*/`). Reproduzo as três no detalhe.
- A4 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:20 · O `U-<n>` sequencial com `x` não faz o uso único atômico: dois hooks em paralelo leem "sem uso" e gravam `U-1` e `U-2`. O nome do uso tem de derivar do Id da concessão (`x` falha no segundo).
- A5 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:22 · Job `autorizacao-main` verde lê corpo de PR que o agente escreve: o dono pode ler "verde" como prova de origem. A saída do job e da catraca deve dizer "forma conferida; origem só local".
- A6 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:17 · Validade sem fuso: o transcript grava UTC e o dono fala em horário local, então "hoje 23:59" e "esta noite 08:00" mudam de dia. Fixe o fuso do dono no desenho e grave-o na concessão.
- A7 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:20 · O analisador do rótulo (PR legível por `pr edit`, `api`, `graphql`, URL, `xargs`, remoção) pede a matriz de dimensões, o gerador, o corpus de legítimos e o orçamento antes da G1.3; hoje só há o critério de parada.
- A8 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:18 · Autorização presa ao PR e não ao conteúdo: com `ate:` o agente empurra afrouxamento novo ao mesmo PR e reaplica o rótulo. É o "motivo novo" do Contexto. Decisão D4 ao dono (head, ou motivo nas palavras).

## Sondas

## Detalhe dos achados
**A1.** Evidência: item 3 (linha 14), "as palavras são trecho contíguo, byte a byte, da mensagem"; itens 5 e 6 derivam ato, alvo e validade só dessas palavras. Caminho: a sessão principal (o Jarvis, quem lê o dono; as três leituras largas do Contexto são dele) passa `--palavras` com um recorte de uma mensagem em que o dono nega, condiciona ou adia. A conferência byte a byte passa, o `Sha256` bate, a concessão fica `ativa` e libera o rótulo no PR. Também escolhe o recorte que traz "hoje" e some com "só se". Não precisa de agente malicioso: basta o agente que lê largo, que é o problema de origem. Severidade: alta (anula o requisito "palavras exatas do dono"). Correção mínima: o corpo é a mensagem inteira do dono (`--palavras` deixa de existir; `--mensagem <uuid>` basta); ato, alvos e validade saem do texto todo; mensagem com mais de um ato, alvo ou termo de validade em conflito, ou com marca de negação ou condição (`nao`, `nunca`, `ainda`, `antes`, `depois`, `so se`, `se`, `exceto`, sem acento e minúsculas), fica `pendente-confirmacao` e só `C-<n>` a ativa. Esforço P. Dono: software-architect (ADR), tech-lead (G1.2).

**A2.** Evidência: item 5, "cada alvo ... que aparece como palavra inteira". Caminho: "pode aplicar o rótulo às 5, são 3 PRs" torna `pr:5` e `pr:3` ativos sem confirmação, e o agente pede o rótulo num PR que o dono nunca nomeou. Severidade: média. Correção: número só conta com marcador colado (`PR`, `#`, `pull`, `versao`); versão só no formato `X.Y.Z`. Esforço P. Dono: tech-lead.

**A3.** Evidência: linha da G1.2 na tabela (linha 66), "protegida em `hooks/conformidade.json`"; precedente em `hooks/conformidade.json:60-61`, que lista a pasta de recados em duas grafias porque a sessão da contribuição roda num clone sob `~/.forge-contrib/wt/`. Caminho: lista curta deixa o registro do clone principal gravável por Write ou Bash do agente, e o `Gravado-por` e o `Sha256` são públicos (detectam acidente, não autenticam; a barreira é só o caminho protegido). Correção mínima, as entradas com `quem: []`: `.forge/autorizacoes/`, `~/.forge-contrib/.forge/autorizacoes/`, `~/.forge-contrib/*/.forge/autorizacoes/`; o teste `escrita-direta` cobre Write, Edit e Bash nas três. Esforço P. Dono: tech-lead.

**A4.** Evidência: item 9, "uso gravado pelo hook na liberação" e item 1, `n` sequencial; o pedido corre com dezenas de agentes em paralelo. Caminho: dois comandos de rótulo concorrentes com a mesma concessão `uso-unico` passam ambos. Impacto baixo (o rótulo é reaplicado ao mesmo PR), mas viola o "usada" do item 7. Correção: arquivo do uso nomeado `U-<Id>` para `uso-unico` (a abertura com `x` é o cadeado); o teste dispara dois hooks juntos. Esforço P. Dono: tech-lead.

**A5.** Evidência: itens 10 e 11 e o Limite conhecido (linha 53); a ADR já declara que o CI não prova origem. Falta a consequência: o job é obrigatório e verde, e o dono o vê como "autorizado". Correção: texto fixo na saída do job e da catraca, e `D3` registra que o job é aviso de forma; nenhuma mudança de lógica. Esforço P. Dono: devops-engineer.

**A6.** Evidência: item 2 (`Hora-da-fala`, carimbo da transcrição) e item 6 (mapa de validade). Caminho: fala às 21:00 locais já é o dia seguinte em UTC; "hoje 23:59" e "esta noite 08:00" mudam de dia conforme o fuso lido (erro para o lado estreito ou para o largo). Correção: gravar `Fuso` na concessão e converter na leitura. Esforço P. Dono: tech-lead.

**A7.** Evidência: item 9; o analisador atual já trata como "aplica" o que não consegue ler (`hooks/conformidade.py:2192`, `2206`, `2209`) e AR-11 e AR-5 mostram a leitura divergente do `gh api` como defeito recorrente. Dimensões a fechar, com gerador: mecanismo (`pr edit`, `issue edit`, `api` REST, `graphql`, `alias`, `xargs`, URL no lugar do número), posição do número, remoção do rótulo (hoje conta como aplicação; exigir autorização para tirar o rótulo aperta além do desejado, decida), vários PRs num comando (`pr:N` de cada um), e um corpus de legítimos (comandos de rótulo que não tocam `afrouxa-regra`). Orçamento de tempo do hook. Esforço M. Dono: tech-lead com qa-engineer.

**A8.** Evidência: item 5 e Contexto ("lida também para motivo novo"). A concessão cobre PR e validade, não o conteúdo; a catraca já exige o rótulo depois do último envio, e `uso-unico` limita a um envio. Com `ate:` o agente reaplica após cada push. Não é defeito do que a ADR declara, é decisão que falta: a) `ate:` só vale para o head visto na concessão (custo: reconceder a cada envio, o que a decisão de 13/11 evitou); b) manter e registrar o limite em Consequências; c) o motivo entra nas palavras e o `declarar` o copia. Recomendo c) ou b). Dono: usuário (`R-DECISAO`).

## Itens conferidos sem achado
- Só aperta (itens 8, 9, 10, 11): ver Resumo. A trava `R-MAIN` fica (item 11) e a autorização nunca destrava o merge do agente (Alternativas, última linha).
- Escrita do registro: `x`, sem seguir link, precedente em `bin/forge_dono.py:54-68`; vínculo com o transcript do evento, precedente em `hooks/agentes.py:275-283`.
- Falha fechada nos itens 4 e 7; a deriva do formato do transcript é custo declarado (Consequências), não brecha.
- A fala de `pedido fala --gravar` não amplia autorização (`bin/forge_dono.py:360`): a rejeição da alternativa está correta.
- PA-7 (`docs/engineering/achados-recorrentes.md`), conferido: AR-1 e AR-2 viram requisito da G1.3 e já estão na ADR; AR-3 não se aplica (vocabulário em lista positiva); AR-5 vale para os subcomandos novos (só entram com `-I`); AR-7 vale para a "raiz principal do clone" (A3); AR-11 vale para A7.

## Condição para aprovar
Corrigir A1 na ADR (o texto muda, o desenho fica); a revalidação lê `forge-check parecer delta`. Os recomendados A2 a A8 entram nas etapas G1.2 a G1.5 como requisito de cada uma. O parecer de G1.2 a G1.5 pede o modelo de ameaças com os casos de abuso (`fala-forjada`, `forma-opaca`, `escrita-direta`, `escopo-largo`, `inativa`, `rotulo-sem-autorizacao`, `ci-sem-declaracao`, mais o recorte com negação do A1 e o número solto do A2).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: nenhuma varredura aplicável (documento, sem código nem dependência); `gitleaks`, `osv-scanner`, `semgrep`, `zizmor` e `actionlint` não estão no PATH deste ambiente (lacuna registrada). Suíte: não roda neste head (sem código); CI do PR não consultado.
