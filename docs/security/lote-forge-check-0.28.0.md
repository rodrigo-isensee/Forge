---
tipo: revisao-seguranca
contrato: 1
pedido: lote-forge-check-0.28.0
branch: melhoria/lote-forge-check-0.28.0
commit: 389096eaea742a6a26ecb3b29f6de842400ad49a
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: lote-forge-check-0.28.0

Entrega revisada: `26f71895c37f16628d8ff914aec564fa336546f6..389096eaea742a6a26ecb3b29f6de842400ad49a` (11 commits), item a item contra os desenhos de `docs/propostas/aq/` citados no pedido. Leitura estática e sondas locais em `$TMPDIR` (repositório temporário, o hook `conformidade` rodado pelo `Fixture` de `tests/test_hooks.py`, segredo de teste com valor falso). Dois achados bloqueantes, ambos em subcomandos novos que contornam proteções que o hook `conformidade` já garante.

## Gatilhos
- Controles do Forge: `docs/regras/R-BRIEF.md` e `tests/config.json` no diff (gatilho do `forge-check pr`).
- Portões: `hooks/parecer.py` (isenção do M13) e `bin/forge-check` (`pr`, `brief`, conferência do conferente), marcados no pedido.
- Leitura de caminho vindo de texto (P3, conferência de citação e `--citar`) e escrita nova em pastas de outro papel (P4 `anotar`, P6 `--gravar`).
- Rede: `gh pr view` no `brief gerar` (P5), gratuito (`R-CUSTO`).

## Achados
- A1 (bloqueante) bin/forge-check:1468 · `forge-check anotar` grava em qualquer arquivo (`caminho_do_pedido`, :701, aceita caminho) e o hook conformidade não o barra: um agente forja `DECISÃO DO DONO` em docs/pedidos/ ou escreve em docs/security/aceites/ (R-DECISAO).
- A2 (bloqueante) bin/forge-check:3945 · `brief gerar --citar .env:1` imprime a linha do `.env` (e de outro arquivo de segredo na raiz), e a citação conferida (:3560) é oráculo de substring dele; o hook barra `cat .env`, mas libera isto a todo papel, o conferente inclusive.

## Detalhe dos achados
**A1, P4 (`c23ea30`).** Evidência: `cmd_anotar` (`bin/forge-check:1457-1494`) resolve o alvo por `caminho_do_pedido` (`:701`: `if Path(pedido).is_file(): return Path(pedido)`), recusa só link simbólico e reescreve o arquivo com a seção `## Decisões do usuário (registro literal)` e a linha `DECISÃO DO DONO (<hora do relógio>): <contexto> → "<literal>"`. O hook `conformidade` só inspeciona o `forge-check` do papel só de leitura (`hooks/conformidade.py:897`); para os outros, o comando passa sem checar escrita. Sondas: com `agent_type` `forge:tech-lead` e `forge:qa-engineer`, o hook libera (rc 0) `forge-check anotar --pedido p1 ...`, `--pedido docs/security/aceites/p1.md ...`, `--pedido docs/regras/R-X.md ...` e `--pedido ~/.claude/CLAUDE.md ...`, enquanto `echo ... >> docs/pedidos/p1.md` é barrado (`docs/pedidos/` é só do jarvis). Executado num repositório temporário, o `anotar` gravou a linha de decisão num aceite de segurança e um bloco `## Histórico` num `.json`. Caminho de ataque: um subagente com Bash (instruído por conteúdo do projeto, ou por erro) grava uma decisão do dono com hora real e formato idêntico ao legítimo; o `forge-check brief` passa a cobrá-la nos briefs e o Jarvis a trata como do dono (rótulo afrouxa-regra, risco aceito, corte de escopo); ou acrescenta texto a arquivo protegido (`quem: []`). Severidade: alta (falsifica o registro em que as regras de decisão se apoiam e fura a lista de caminhos protegidos). Correção mínima: (1) no `cmd_anotar`, aceitar só o id do pedido resolvido por `dentro_da_raiz(..., ("docs/pedidos",))` na raiz, na cópia principal ou em `~/.forge-contrib`, sem o atalho de caminho arbitrário; (2) no hook `conformidade`, tratar `forge-check anotar` como escrita em `docs/pedidos/` e `forge-check brief gerar --gravar` como escrita em `docs/briefs/` (os dois só do jarvis), com fixtures `*-bloqueia` para tech-lead e qa e `*-libera` para o jarvis. Esforço: P. Dono: tech-lead (código e `hooks/`, em `melhoria/*`).

**A2, P3 (`8f8fa3c`).** Evidência: `bloco_de_citacoes` (`bin/forge-check:3927-3946`) imprime a linha literal da fonte; `linhas_da_fonte` (`:3541-3563`) confina o caminho à raiz, à cópia principal e a `~/.forge-contrib` e limita a 1 MiB, mas não recusa arquivo de segredo. Na conferência (`conferir_citacoes`), `citação: ok` contra `citação: trecho fora da fonte` responde se um prefixo escolhido está no arquivo. Sondas com valor falso: `brief gerar --citar .env:1` imprimiu a linha inteira; um brief com `"API_TOKEN=s3" (.env:1)` saiu `citação: ok` e com `s4` saiu `trecho fora da fonte`. O hook libera `forge-check brief gerar ... --citar .env:1` para `forge:conferente` e `forge:tech-lead` (rc 0), e barra `cat .env` (`ler .env expõe segredos`). O desenho (`p3-p6.md`, P3 b) promete que o conteúdo do arquivo nunca é impresso; o `--citar` o imprime por desenho e sem filtro. Caminho de ataque: num projeto com credenciais reais no `.env` (a skill manda guardá-las ali), qualquer agente, inclusive o conferente só de leitura, põe o segredo no contexto do modelo e na transcrição com um comando liberado. Severidade: alta (vazamento de segredo). Correção mínima: em `linhas_da_fonte`, recusar como `fonte não verificável` o nome que casa com o padrão de `.env` do hook (`hooks/conformidade.py:77`, fora os de exemplo) e, de preferência, aceitar só arquivo `.md` rastreado pelo git (citação é de documento); teste com `.env` de valor falso para o `--citar` e para a conferência. Esforço: P. Dono: tech-lead.

**Item a item:**
- M16 (`5f3ae67`): aprovado. A marca deixa de ser exigida na etapa do mesmo papel, como na decisão do dono (afrouxa na letra, com rótulo); a etapa sem menção de qualquer papel e a junção de delegações passam a reprovar; `tests/config.json` só ganha invariantes.
- P2 (`84db057`): aprovado. `--cobre` validado contra `## Etapas` e o papel; saída passa por `sem_controle`.
- M13 (`8ccff9f`): aprovado. `isencoes_do_diff` segue a D-M13 "A" ao pé da letra; diff vazio ou base ausente não isenta (falha fechada); o hook `parecer` deixa de liberar PR só de `.md` sem parecer (endurece) e a catraca herda a mesma regra.
- M4 (`9921db8`): aprovado. O PQ `cmd` só conta como prova do conferente quando `comando_do_conferente` o aceita.
- M5 e P2, tabela (`3101c0d`): aprovado. `avisos_da_etapa` só informa e roda sem rede; a recusa do `gerar` usa a mesma fonte (`pr_da_cli`).
- P6 (`bfed7d5`, `9ffd14c`): aprovado no que entrega: `open(..., "xb")` não sobrescreve nem segue link, nome validado por lista fechada, `docs/briefs/` link simbólico recusado, `chmod` confinado a `docs/briefs/` por `realpath`. A escrita por papel que não é o jarvis entra na correção do A1.
- P4 (`c23ea30`): A1.
- P3 (`8f8fa3c`): A2. A D1 (PQ `pr` e `merge` como prova do conferente) está conforme a decisão do dono e é conferível por ele.
- P5 (`158af43`): aprovado. O `Base-sha` fora da branch passa de aviso a reprovação: endurece e falha fechado. Brief antigo em volta: a conferência roda só sobre o brief novo (o anterior entra como `--anterior`), e o `gerar --volta` mantém o `Base-sha` anterior enquanto ele for ancestral da entrega; sem `--force` (`R-VERIFY`) a branch não é reescrita, então o anterior segue ancestral. O que sobra é disponibilidade (brief gerado de uma develop local atrasada), e o remédio é gerar de novo. Sem objeção de segurança.
- Testes (`389096e`): aprovado.

**Recomendações (não bloqueiam):**
- R1. `bin/forge-check:3854`: passe `--` antes da branch no `gh pr view` (uma branch que começa com `-` vira opção do `gh`). Baixa.
- R2. P6: a hipótese do `0444` foi refutada (a ferramenta Write sobrescreve); o texto novo da `R-BRIEF` diz que o brief aprovado fica `0444`, o que é verdade, mas não é trava. Abra o cartão da P6b (hook `conformidade`, com parecer de segurança) e não cite o `0444` como proteção até lá.
- R3. M13: `stacks/*/seguranca.md`, `stacks/*/pronto.md`, `templates/projeto/**` e `CLAUDE.md` também são instrução que chega aos projetos e ficam isentos de QA (o review continua). A lista segue a decisão do dono; ampliá-la é decisão dele, pelo Jarvis.
- R4. `CONTROLES_DO_FORGE` (`bin/forge-check:128`) não inclui `hooks/`, `bin/forge-check` nem `agents/`: o gatilho de segurança deste lote veio da marcação no pedido, não do diff. Anterior ao lote; vale um cartão.
- R5. `cmd_anotar` reescreve o pedido inteiro (`write_text`) depois de checar o link simbólico; prefira escrever em arquivo temporário e renomear, para não truncar o pedido numa falha.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner` e `shellcheck` não estão no PATH deste ambiente (lacuna registrada; nada foi instalado). O diff não toca workflow, dependência nem contêiner. Revisão por leitura do diff e sondas locais com valor falso; nenhum segredo real foi lido nem exibido.
