---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-folga-jarvis
commit: ebeb9161070e947fe03a1a6d8de630cee47be833
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 (E1.167, folga do texto do Jarvis P1 a P4 e FOCO-NAS-DECISOES)

## Achados
- A1 (recomendado) agents/agile-coach.md:13 · "Métricas de fluxo do time ... pelas convenções da skill `kanban-scrum`": as métricas foram para `kanban-metricas` (P1). Sem perda, porque as duas estão no `skills:` do agile-coach, mas o ponteiro ficou errado; trocar o nome da skill, como já foi feito na linha 23.
- A2 (recomendado) agents/jarvis.md:14 · "Leia falar-com-o-dono ... diante de ordem ampla": "Ordem ampla não confirma" foi para `fluxo-do-pedido`, e a falar-com-o-dono só aponta para ela, sem "leia" (a description perdeu "resolva, acabe tudo, pode fazer"). Sem perda (fluxo-do-pedido é lida antes de todo pedido); corrigir o ponteiro.
- A3 (recomendado) skills/fluxo-do-pedido/SKILL.md:8 · o cabeçalho diz que a skill foi "movido inteiro e sem mudar palavra", mas a seção `## Versão` (linha 46) é texto novo, o resumo da diretriz 21 (decisão do dono de 14/11 08:16). Ressalvar a seção, para o próximo leitor não a tratar como trecho movido.
- A4 (recomendado) tests/apoio_jarvis.py:73 · ordem de leitura conferida por linha: skill passa com "leia" de outra skill. Reproduzido: sem o "Leia `fluxo-do-pedido`" da jarvis.md:42, `contribuir-com-o-forge` reprova; modo-iniciante e novo-projeto passam assim na :14. Segue a proposta P4.

## Sondas

## Parecer
Aprovado no head ebeb9161 (classe C pelo `forge-check classe`: review ∥ QA ∥ segurança, gatilho `tests/config.json`). São dois commits, um por item (P1 a P4; FOCO-NAS-DECISOES), em Conventional Commits, com o fragmento `changelog.d/v047-folga-jarvis.md`.

**Diretriz 25: só movido, nenhuma palavra mudada.** Script sobre `git diff -U0 origin/develop...ebeb9161 -- agents skills templates`: das 57 linhas removidas não vazias, 54 existem literais no head (agents/*.md e skills/*/SKILL.md). As 3 que não existem são:
- agile-coach.md:23: só o ponteiro `kanban-scrum` → `kanban-metricas` muda, porque a "Retrospectiva" mudou de skill;
- a `description:` da falar-com-o-dono, que é cabeçalho e não regra; ver A2;
- templates/projeto/CLAUDE.md:30: o texto antigo fica inteiro como prefixo e a frase da diretriz 29 vem depois.

Os resumos novos do Jarvis (linhas 13, 15, 18, 24, 27, 32 e 42) são texto novo, que a decisão do dono (a) de 13/11 19:52 autoriza. Os invariantes de `tests/config.json` só mudam de chave: os 21 que saem de `agents/jarvis.md` e os 3 de ordem ampla que saem de `skills/falar-com-o-dono/SKILL.md` estão todos sob `skills/fluxo-do-pedido/SKILL.md`. Os dois invariantes novos (diretriz 29) e o ponteiro novo entram com regra e motivo. Nenhum invariante sumiu. `LEGADO_TRECHOS_MAXIMO` desce de 284 para 225 e `invariantes_sem_motivo` do jarvis desce de 49 para 28: os dois apertam.

**Mudanças fora do previsto, julgadas:**
- `agents/agile-coach.md` (P1): a skill nova entra no `skills:` e a linha da retrospectiva da 0.42 vai, palavra por palavra, para `kanban-metricas`, que o agile-coach carrega. Só muda de lugar: aceita. Os testes que a liam (`test_medidas_m14b` e `test_forge.PraticasDeEspecificacao`) leem agora o agente mais a skill e exigem o ponteiro. Fica A1.
- `skills/falar-com-o-dono`: custo e origem, resposta curta, ordem ampla e ritmo vão inteiros para `fluxo-do-pedido`, e o espaço que sobra recebe o detalhe da diretriz 29, que o dono mandou pôr nessa skill (ordem de 14/11 08:09). É o caminho da diretriz 25: aceita. Fica A2.
- Testes de texto: `test_forge.Agentes`, `test_reval_delta` e `test_metricas_texto` seguem o texto para o arquivo novo, e a mensagem da catraca passa a mandar mover (P3), com teste das duas mensagens. Nenhuma asserção ficou mais frouxa: aceita.
- Diretrizes 26 a 28 como `pendente`: a decisão do dono de 14/11 08:38 classificou só a 2, a 11, a 23 e a 24. A 26, a 27 e a 28 nasceram depois da proposta, valem "no Forge e em todos os projetos" e ainda não têm texto na fábrica. `pendente` é a única classe honesta para elas: exige cartão (INTEGRACAO-EM-LOTE, RELEASE-EM-1H e SESSAO-AUTOMATICA, todos no `KANBAN.md`), reprova quando o texto já existe e só desce (`MAX_PENDENTES` = 7). Aplica o mesmo critério da decisão e não afrouxa nada: aceita. Recomendo uma linha `técnico` no pedido.

**Teste de presença (P4)** em `tests/test_jarvis_nucleo.py` com `tests/apoio_jarvis.py`:
- o conjunto do Jarvis é calculado, não lista fixa: 30 arquivos neste head;
- os IDs vêm da tabela do índice das regras (≥ 17) e as diretrizes da fixture neutra, de 1 a 29, sem buraco;
- há 11 mutantes numa árvore sintética, um para cada caso da proposta (AR-1);
- os mínimos de itens estão afirmados (checklist 11).

A4 é recomendação. Foram rodados (ambiente limpo):
- `test_jarvis_nucleo test_metricas_texto test_reval_delta test_clareza test_forge.{Agentes,RegrasInviolaveis,PraticasDeEspecificacao} test_medidas_m14b.MedidaM2b`: 80 testes OK, 1 pulado (arquivo do dono);
- o mesmo subteste com `FORGE_DIRETRIZES_DONO` apontando o arquivo do dono: OK, cada número de 1 a 29 tem entrada;
- `test_forge.{Skills,Neutralidade,NeutralidadeDoNucleo,AntiDuplicacao,Orcamento} test_orcamento_instrucao`: 20 OK.

Também rodei um mutante: com "uma vez por dia" trocado por "uma vez por semana" na seção Versão, a diretriz 21 reprova, e a mensagem diz onde procurar e "não apague (diretriz 25)". A suíte inteira fica para o CI do PR; ainda não há PR.

**Pendências para o PR (não são do código):**
- Tamanho (M14): 390 linhas de `tests/*.py` e `tests/config.json`. O corpo do PR precisa trazer `teto: excedido, 390 linhas, <motivo>`; o motivo é o lote que o dono decidiu (P1 a P4 num PR), quase todo teste de presença e invariante movido de chave.
- Este parecer cobre o review. Segurança (gatilho `tests/config.json`) e QA são portões à parte (E1.168 e E1.169).
