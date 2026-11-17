---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-folga-jarvis
commit: 2a95b1630df4dbf2fa45d39c916393e4423d6c44
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047 (folga do texto do Jarvis, revalidação E2.655)

Revalidação por delta `16b7ca74..2a95b163` (`forge-check parecer delta`, sem o que veio da develop pelo merge `2712bc2f`). No domínio: `tests/config.json` (o gatilho), `agents/jarvis.md`, `skills/falar-com-o-dono/` (SKILL.md e os três arquivos novos), `skills/kanban-metricas/SKILL.md`, `skills/kanban-scrum/SKILL.md`, `templates/projeto/CLAUDE.md`; fora: `tests/test_forge.py`, `tests/test_jarvis_n_jar_a.py`, `tests/test_jarvis_nucleo.py`, `tests/test_medidas_m14b.py`, `tests/test_reval_delta.py`. Li por commit os quatro da branch (`61b82395`, `733a1f45`, `ae01c4fa`, `2a95b163`).

Gatilhos: `R-SEGURANCA`, controles do Forge (`tests/config.json`, invariantes trocadas e acrescentadas por decisão do dono de 17/11, opção 1).

**Invariantes (`733a1f45`).** As 8 da versão curta da diretriz 29 saem e entram 8 trechos da versão longa, cada um contendo ou mais estrito que o anterior: `**Pedido das decisões**` passa a `**Pedido de decisões \(diretriz 29\):**` (`tests/config.json:270`); `` `forge-check anotar` `` fica dentro de "Uma a uma, cada resposta por `forge-check anotar`…"; "Não há decisão sua pendente" fica, com "numa linha"; "só ler as perguntas abertas", "O time segue…" e "entre as perguntas, nenhum aviso" viram frases maiores com o mesmo conteúdo. Só "foco total" deixa de ser trecho próprio; segue na `description` da skill e o comportamento ("faça só isso, sem disparo, cartão, registro, conferência nem andamento antes") é invariante. Nenhuma checagem fica mais fraca.

**Arquivos novos (`ae01c4fa`, `2a95b163`).** Q2, "toda mensagem" e "conferir a develop" mudam inteiros para `pergunta-pendente.md`, `toda-mensagem.md` e `conferir-develop.md`, com ponteiro `${CLAUDE_PLUGIN_ROOT}` na SKILL.md protegido por invariante e com motivo (`R-DECISAO`) em `invariantes_com_motivo`. A exceção de Q2 (risco, gasto `R-CUSTO`, `afrouxa-regra`, main, ato destrutivo, `R-CONFORMIDADE`) fica inteira como invariante; `tests/test_jarvis_n_jar_a.py` passa a exigir `R-CUSTO` e `R-CONFORMIDADE` no arquivo novo (antes só `R-CUSTO` na SKILL.md). `invariantes_sem_motivo` de `agents/jarvis.md` desce de 28 para 27 (a frase ganhou motivo; a catraca só desce).

Suíte: sem PR nem CI neste head; rodei `tests.test_jarvis_n_jar_a`, `tests.test_jarvis_nucleo` (45, OK, 1 skip de ambiente pré-existente: `FORGE_DIRETRIZES_DONO` fora do git) e `tests.test_forge.RegrasInviolaveis` (3, OK). O CI do PR continua obrigatório para o merge.

## Achados
- A1 (recomendado) tests/apoio_jarvis.py:84 · corrigido no 8a223677 (presença do ID só em agents/jarvis.md e skills/*/SKILL.md); o delta não toca o arquivo. Sem pendência
- A2 (recomendado) tests/fixtures/diretrizes-do-dono.json:164 · diretrizes 26 a 28 como pendente (MAX_PENDENTES = 7); sem mudança no delta; decisão de escopo sem caminho de ataque, ao dono pelo Jarvis (`R-DECISAO`)

## Sondas
- S1 · cópia por `git archive` do 2a95b163; em pergunta-pendente.md "Nunca vale para aceite de risco, gasto" trocado por "Vale para gasto"; `tests.test_forge.RegrasInviolaveis` · espera: FAIL · obtido: FAIL no trecho "Nunca vale para aceite de risco… `R-CONFORMIDADE`"
- S2 · mesma cópia; apagada da SKILL.md a linha do ponteiro `**Pergunta pendente (Q2):**` · espera: FAIL · obtido: FAIL no trecho `skills/falar-com-o-dono/pergunta-pendente\.md`

## Detalhe dos achados
A1 e A2 sem mudança desde o parecer do 16b7ca74 (`8069afdd`). Nenhum achado novo no delta; nenhum bloqueante.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: git, a biblioteca padrão do Python e os testes do repositório. `gitleaks` ausente no PATH (lacuna); busca por credencial nas linhas acrescentadas do domínio da branch sem ocorrência (o delta é texto de skill, de agente e de teste).
