---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0474-pos-merge-631
commit: 01b4e8aec3cd625f9a0bcf8359b88673d1e15d0b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E1.41, depois do merge do #631)

Escopo: o delta 9fd5d771..56559cfd do #631, que entrou na `develop` no squash 01b4e8ae sem portão depois dos pareceres no 9fd5d771. Os commits do delta (lidos de `refs/pull/631/head`): 875d5b15 (ponteiro do ritmo e corte, troca de invariantes) e 56559cfd (description sem dois-pontos). Os merges da `develop` no meio não mexem em `agents/tech-lead.md`, `tests/config.json` nem `skills/`. `git diff 56559cfd 01b4e8ae -- agents/tech-lead.md tests/config.json` sai vazio: o que está na `develop` é o que se revisa aqui.

## O que mudou e se alguma regra sumiu ou afrouxou
1. **description do `agents/tech-lead.md`:** sai a lista "granularidade, mensagens, branches, envio das branches"; a lista segue no item 4 do corpo, e a main continua do usuário (`R-MAIN`). Nenhuma regra sai.
2. **Item 5:** a lista da descrição do PR sai e vira ponteiro para a skill `engineering-practices`, que o tech-lead carrega no frontmatter. A lista de lá (seção "Pull request e a main") cobre a antiga e acrescenta o link do pedido e as pendências. Nada afrouxa.
3. **Ritmo e corte:** a linha virou só ponteiro para `skills/trabalho-em-paralelo/ritmo-e-corte.md`. Tudo o que a linha antiga dizia está no arquivo da skill: lote de até 3 sem arquivo em comum, nada de juntar sem teste verde nem pela exceção do GitHub, PR da manhã para a `main`, corte por arquivo, lote de 3 a 5, 12 branches e 20 agentes dentro do `R-TETO`, e o agente livre que termina o que está aberto. O texto da skill é igual ou mais estrito: acrescenta o CI vermelho e "branch nova só quando uma entra na develop". Nenhuma regra some. O que diminui é o alcance: o tech-lead não carrega mais o texto no próprio contexto, e o ponteiro não diz quando ler (A1).
4. **Invariantes:** sai do tech-lead "No máximo 12 branches abertas e 20 agentes", que tinha `porque` em `R-TETO`. No lugar entra o caminho do ponteiro, em `R-FLUXO`. A skill passa a proteger "Até 20 agentes ao mesmo tempo" e "Agente livre termina o que está aberto", ao lado de "no máximo 12 branches com trabalho aberto", que já existia. O teto saiu do tech-lead, mas segue protegido onde está escrito, e o `porque` da skill cita o teto do H6. Não é afrouxamento de conteúdo. Mesmo assim, foi a remoção de um invariante, e o título do #631 só destaca o MAX_PENDENTES (A2).
5. **Processo:** os dois commits entraram depois do último parecer, sem portão (`R-REVIEW`, "Correção antes dos portões"). Este review fecha esse buraco depois do fato. O conteúdo não pede volta.

## Achados
- A1 (recomendado) agents/tech-lead.md:38 · o ponteiro do ritmo e corte não diz quando ler e a skill trabalho-em-paralelo não está no frontmatter; usar o gatilho do jarvis.md:37 (ler antes de planejar lote ou juntar na develop)
- A2 (recomendado) tests/config.json:361 · o invariante do teto de 12 branches e 20 agentes saiu do tech-lead sem destaque no título do PR (CLAUDE.md, regras protegidas por teste); o conteúdo segue protegido na skill, falta só o registro

## Sondas

## Parecer
Aprovado. Nenhuma regra sumiu e nenhuma afrouxou no conteúdo. O texto que saiu do `agents/tech-lead.md` está inteiro, e protegido por invariante, em `skills/trabalho-em-paralelo/ritmo-e-corte.md` e em `skills/engineering-practices/SKILL.md`. Os dois achados são recomendados e não devolvem o item: A1 é o alcance do ponteiro, A2 é o registro da troca de invariante. Suíte: não rerrodada; o CI do #631 é o do head mesclado.
