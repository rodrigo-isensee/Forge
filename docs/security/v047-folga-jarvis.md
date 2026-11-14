---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-folga-jarvis
commit: ebeb9161070e947fe03a1a6d8de630cee47be833
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (folga do texto do Jarvis e FOCO-NAS-DECISOES, E1.168)

Intervalo `origin/develop..ebeb9161` (base e60183d0, 2 commits, 17 arquivos). Suíte: sem PR, sem CI; vale a entrega conferida ebeb9161 (histórico do v047, 09:52). Rodei só o que tirava dúvida: `tests.test_jarvis_nucleo`, `tests.test_metricas_texto`, `tests.test_forge.RegrasInviolaveis` e `tests.test_forge.Agentes`, todos verdes.

## Gatilhos
`R-SEGURANCA`: controles do Forge (invariantes de `tests/config.json` movidos de arquivo, legado sem motivo encolhido, teste novo de presença das regras com ID e das diretrizes, mensagem da catraca de texto).

## Achados
- A1 (bloqueante) tests/apoio_jarvis.py:82 · checagem de presença das regras com ID é vazia na árvore real: o índice docs/regras/README.md entra no conjunto (pela R-WIP) e a tabela dele cita todo ID entre crases; tirar `R-SEGURANCA` do Jarvis e de todas as skills dá [] (S1). Requisito da decisão do dono de 13/11 19:52
- A2 (recomendado) tests/fixtures/diretrizes-do-dono.json:164 · diretrizes 26, 27 e 28 entram como pendente (MAX_PENDENTES = 7, test_jarvis_nucleo.py:27); a decisão de 14/11 08:38 nomeia só 2, 11, 23 e 24, e a de 13/11 19:52 pede presença de 1 a 26: levar ao dono pelo Jarvis (`R-DECISAO`)

## Sondas
- S1 · cópia por git archive de ebeb9161; trocar `R-SEGURANCA` por texto sem crases em agents/jarvis.md e skills/*/SKILL.md; problemas_das_regras(raiz, conjunto_do_jarvis(raiz)) · espera: ["R-SEGURANCA: não aparece no Jarvis nem nas skills citadas"] · obtido: [] (README.md no conjunto: True)

## Detalhe dos achados
**Foco do brief (nada sumiu nem afrouxou):** conferido por máquina contra a base e60183d0.
- Invariantes: nenhum padrão sumiu de `tests/config.json`; 24 mudaram de arquivo (21 de `agents/jarvis.md` e 3 de `skills/falar-com-o-dono/SKILL.md` para `skills/fluxo-do-pedido/SKILL.md`); 3 novos (o ponteiro `skills/fluxo-do-pedido/SKILL\.md` no Jarvis e dois da diretriz 29 na `falar-com-o-dono`). Todo padrão casa no arquivo-alvo no head. Os IDs do bloco de regras do Jarvis (`R-MAIN` ... `R-SEGURANCA`, `R-PROVA`, `R-BRIEF`) seguem invariantes em `agents/jarvis.md`.
- Texto movido sem mudar palavra (diretriz 25): toda linha removida de `agents/jarvis.md`, `skills/kanban-scrum/SKILL.md` e `skills/falar-com-o-dono/SKILL.md` aparece inteira no head (nas skills novas ou no próprio arquivo), com duas exceções que são edição de ponteiro, não de regra: a `description:` da `falar-com-o-dono` e o nome da skill no "Ciclo de evolução" do `agents/agile-coach.md` (`kanban-scrum` → `kanban-metricas`, que entra no `skills:` dele). A linha do Telegram ("sem segredo; não mude a allowlist") foi inteira para `skills/fluxo-do-pedido/SKILL.md:13`; não era invariante antes nem depois.
- Legado: `invariantes_sem_motivo` do Jarvis 49 → 28 e `LEGADO_TRECHOS_MAXIMO` 284 → 225 só descem; os 21 movidos ganham motivo pelo `invariantes_motivo` da skill nova (R-DECISAO). Aperta, não afrouxa.
- Catraca de texto: nenhum teto de `tests/fixtures/metricas-texto.json` subiu; só entram as duas skills novas. `estouros()` reprova igual; muda só a mensagem (mover, não reduzir), conforme a decisão de 14/11 08:14.
- Testes alterados (`test_forge`, `test_medidas_m14b`, `test_reval_delta`, `test_metricas_texto`): seguem as frases para o arquivo novo, sem tirar asserção.

**A1.** Evidência: `tests/apoio_jarvis.py:80-90` (`problemas_das_regras` junta todo o conjunto), `:41` (a R-WIP tem texto só em `docs/regras/README.md`, que por isso entra no conjunto). Caminho: um autor tira um ID do Jarvis e das skills para caber no teto; o teste novo, vendido como a prova da decisão do dono, passa. Hoje o invariante de `tests/config.json` ainda pega os IDs do bloco do Jarvis, então não há perda de proteção nesta entrega; o defeito é o controle novo não provar o que diz, e o mutante `test_id_fora_do_conjunto_reprova` não pega porque a árvore sintética não põe o índice no conjunto. Severidade: média (controle de guarda vazio). Correção mínima: em `problemas_das_regras`, procurar o ID só em `agents/jarvis.md` e nas `skills/*/SKILL.md` do conjunto (fora de `docs/regras/`), e um mutante cuja árvore sintética tenha um ID só de índice citado pelo Jarvis (o índice entra no conjunto) e outro ID tirado do Jarvis, que precisa reprovar. Esforço: P. Dono: `tech-lead` (autor da E1.137).

**A2.** Evidência: `tests/fixtures/diretrizes-do-dono.json:164` em diante (26 INTEGRACAO-EM-LOTE, 27 RELEASE-EM-1H, 28 SESSAO-AUTOMATICA como `pendente`) e `tests/test_jarvis_nucleo.py:27`. A proposta aprovada (`docs/propostas/folga-texto-jarvis.md`, mapa) e a decisão de 08:38 fixam os pendentes em 2, 11, 23 e 24; 4, 5 e 22 como sessão vêm do mapa aprovado e 3 e 21 da decisão de 08:16. Sem caminho de ataque: é decisão de escopo, não defeito de segurança, por isso recomendado; vai ao dono pelo Jarvis (`R-DECISAO`): aceitar 26 a 28 como pendentes com cartão ou exigir o texto delas antes do merge. Dono: Jarvis.

Informativo: `test_cada_numero_do_arquivo_do_dono_tem_entrada` pula sem `FORGE_DIRETRIZES_DONO`; o arquivo do dono fica fora do git por neutralidade (`R-NEUTRO`), e a tabela neutra cobre o CI.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: git, a biblioteca padrão do Python e os testes do repositório. `gitleaks` ausente no PATH (lacuna; a entrega é texto e testes, sem credencial).
