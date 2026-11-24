# Relato dos agentes: o que falta (FILA-25, E131.1)

- **Pedido:** `docs/pedidos/relato-dos-agentes.md` (forge-contrib), aprovado pelo dono em 16/11 (`v047.md:1312`); conferido contra a develop 0e59c446 (cópia `wt/v0480-relato-desenho`).
- **Veredito:** quase tudo já está em vigor. Faltam três coisas pequenas: a ordem do resumo (decisão pendente no topo), o formato do resumo único escrito num lugar só e uma medida que conte as falas ao dono. O cartão **não fecha** como "nada falta".
- **Afrouxa?** Não: nenhuma linha de `docs/regras/` nem de `tests/config.json` sai ou muda; só se acrescenta texto.
- **Proposta de origem:** `~/.forge-contrib/propostas/relato-dos-agentes.md` não existe (a leitura falha). A decisão de 06/11 (`decisoes-estudos.md:108`) manda trazê-la das transcrições só se ela trouxer algo além da seção Relatório dos briefs. Este desenho não precisa dela: o pedido lista as quatro regras.

## Pedido × em vigor
| Parte do pedido | Em vigor (arquivo:linha) | Falta |
|---|---|---|
| Interromper só por bloqueio, falha de portão ou ação do dono | `agents/jarvis.md:15` (decidir ou agir, algo que muda prazo ou risco, marco fechado); `tests/config.json:234-236` e `:895-897` protegem o texto | nada |
| Relatos não vão crus ao dono | `agents/jarvis.md:15` ("relatório de agente, ao histórico do pedido"); relatório de até 8 linhas no brief (`bin/forge-check:9562`); `docs/economia-de-tokens.md:12` | nada |
| Resumo único | `agents/jarvis.md:15` ("no máximo um resumo a cada 30 min, estado em uma linha por item que mudou; nada mudou, nada a dizer") | **o formato** (campos e ordem) não está escrito, e `skills/fluxo-do-pedido/SKILL.md:12` ainda manda contar o andamento "ao fim de cada etapa", sem dizer que isso vai no resumo ou no marco |
| Decisão pendente no topo | Só no pedido de decisões: `skills/falar-com-o-dono/SKILL.md:18` e `agents/jarvis.md:17`; recibo antes de tudo: `skills/falar-com-o-dono/toda-mensagem.md:9-11` | **no resumo e no aviso de marco**, a ordem não está escrita |
| R-DECISAO mantida | `agents/jarvis.md:14`; `skills/falar-com-o-dono/SKILL.md:10` | nada |
| Medir antes e depois | Dados: `hooks/meta.py:344-351` grava `em` e `caracteres` por Stop em `.forge/run/mensagens.jsonl`; meta "até 4 por hora" em `docs/arquitetura/visao-de-foco.md:167`; 40 por hora em 13/11 (`tests/config.json:895`) | **nenhum comando lê isso**: `bin/forge-check` não cita `mensagens.jsonl`, e `transcricao decisoes` (`bin/forge_transcricao.py:332-342`) mede a forma das opções, não o volume |

## Texto das regras que faltam
1. **`skills/falar-com-o-dono/resumo-unico.md`** (arquivo novo, como `toda-mensagem.md`; o ponteiro numa linha da `SKILL.md`):
   > **Resumo único (FILA-25):** o que chega dos agentes fora de marco fica no histórico do pedido e sai num resumo só, no máximo a cada 30 min. Ordem: recibo, se houver (`toda-mensagem.md`); depois "Precisa de você", com o número de decisões pendentes e a mais pesada numa linha; depois uma linha por item que mudou; riscos só se mudaram. A pergunta completa vai na mensagem seguinte, uma a uma (`R-DECISAO`). Nada mudou e nada pendente: nada a dizer. O aviso de marco segue a mesma ordem.
2. **`agents/jarvis.md:15`**: depois de "no máximo um resumo a cada 30 min", acrescentar "(formato e ordem: `falar-com-o-dono/resumo-unico.md`)". O invariante `tests/config.json:236` continua casando.
3. **`skills/fluxo-do-pedido/SKILL.md:12`**: depois de "ao fim de cada etapa", acrescentar ", no resumo único ou no aviso de marco (`agents/jarvis.md`, Falar só no marco)". Nada se apaga (diretriz 25, `fluxo-do-pedido/SKILL.md:8`).

## Formato do resumo único
```
Resumo 14:30 (desde 14:00)
Precisa de você: 2 · a mais pesada: <decisão em linguagem fácil> (pergunto a seguir)
- <item em linguagem fácil>: <antes> → <agora>; próximo: <passo>
- <item>: <antes> → <agora>
Risco: <só se mudou prazo ou risco>
```
- Sem decisão pendente: "Precisa de você: nada". Sem nome de branch, pasta ou agente técnico (`agents/jarvis.md:16`); o agente a quem passou só no recibo e no aviso de marco (`agents/jarvis.md:23`).
- Teto: 1200 caracteres (`hooks/meta.py:40`, `TETO_DA_MENSAGEM`). Item que não mudou fica fora.
- **Origem de cada linha (R-BRIEF, R-PROVA, conferente):** nada muda nesses três. `Provas:` e veredito do conferente vão ao `## Histórico`. `Melhoria vista:` vai à retrospectiva (`fluxo-do-pedido/SKILL.md:31`). Achado bloqueante ou portão vermelho vira marco só se mudar prazo ou risco; senão vira uma linha do resumo.

## Medida antes e depois
- **Comando:** `forge-check transcricao falas`. É uma entrada nova em `MEDIDAS` (`bin/forge_transcricao.py:369-371`) e em `TRANSCRICAO_DO_MODULO` (`bin/forge-check:7253`). Reaproveita `ler_respostas_do_jarvis` (`forge_transcricao.py:305`) e o mesmo anúncio (`cmd_transcricao_medida`, `forge_transcricao.py:345`).
- **Campos por sessão:**
  - `respostas`: falas finais do turno;
  - `sem_dono`: turno aberto por mensagem que não é do dono, como o aviso de agente terminado;
  - `rajadas`: janelas de 30 min com 2 ou mais falas `sem_dono`;
  - `taxa` = `rajadas`/`sem_dono`.
  A saída só traz números, como as outras medidas (T-14).
- **Antes:** a mesma medida sobre as transcrições dos 7 dias anteriores ao merge da F1. Fica gravada no `## Histórico` do pedido antes do merge.
- **Depois:** 7 dias depois do merge da F1.
- **Meta:** `rajadas` = 0 e falas `sem_dono` por hora ativa ≤ 4 (`visao-de-foco.md:167`).
- **Critério de reversão:** se a medida "depois" não cair e o dono disser que deixou de saber de algo de que precisava, volta o texto da F1.
- **Suposição (a confirmar na F2):** o aviso de agente terminado aparece na transcrição como mensagem de usuário sem `tool_result`, com o texto começando por `<task-notification>`. Se a forma for outra, o oráculo da F2 se ajusta à forma real, vista numa transcrição real e anonimizada.

## Corte da implementação (tech-lead, uma branch por fatia)
| Fatia | O que | Arquivos | Pronto quando (oráculo) |
|---|---|---|---|
| F2 (primeiro: grava o "antes") | medida `falas` | `bin/forge_transcricao.py`, `bin/forge-check` (só o nome na tupla), `tests/test_transcricao*.py` | `python3 -m unittest` dos testes da medida verde com fixture de 3 sessões (sem rajada, com rajada, aviso de agente dentro e fora da janela); `forge-check transcricao falas <pasta>` imprime só `chave=número`; linha "antes" gravada no pedido |
| F1 | texto das regras 1 a 3 | `skills/falar-com-o-dono/resumo-unico.md` (novo), `skills/falar-com-o-dono/SKILL.md`, `agents/jarvis.md`, `skills/fluxo-do-pedido/SKILL.md`, `tests/config.json` (invariante novo "Precisa de você" em `resumo-unico.md`, só acrescenta) | `.githooks/pre-push --suite` verde; invariantes de `tests/config.json:234-238` intactos; `grep -n "resumo-unico.md" agents/jarvis.md skills/falar-com-o-dono/SKILL.md` acha as duas linhas; teto de caracteres do `jarvis.md` respeitado (teste existente) |
| F3 (7 dias depois da F1) | medida "depois" | só o pedido (`## Histórico`) | linha "depois" gravada ao lado da "antes"; meta atingida, ou cartão com o número e a decisão de manter ou reverter (`R-DECISAO`) |

- **Paralelo:** F2 e F1 não dividem arquivo e podem andar juntas. A F1 só entra na develop depois da linha "antes" (o "antes" precisa ser anterior ao texto novo).
- **Classe e portões:** a F1 é texto de agente e skill (review e QA). A F2 lê transcrições locais: passar pelo `security-engineer` para conferir `R-SEGURANCA`. O padrão (só disco local, sem rede, saída só números) já é o das medidas `lastro`, `vereditos` e `decisoes`.
- **Por que o existente não basta (F2):** `hooks/meta.py` grava uma linha por Stop, mas não diz o que abriu o turno, só cobre o que rodou desde a 0.44.2 e nenhum comando a lê (grep de `mensagens.jsonl` em `bin/`: 0 ocorrências). `transcricao decisoes` não conta volume nem hora.

## Critério de parada (F2, analisador)
- bloqueia: nada; só mede.
- rajada · 2 ou mais falas `sem_dono` na mesma janela de 30 min da sessão principal · oráculo: fixture "com rajada" no teste da F2
- sem_dono · turno aberto por mensagem que não é do dono · oráculo: fixture "aviso de agente" no teste da F2
- gatilho · oráculo: `forge-check transcricao falas tests/fixtures/<pasta-da-F2>` sai 0 e imprime só números
