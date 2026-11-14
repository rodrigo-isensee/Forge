---
tipo: review
contrato: 1
pedido: v0457
branch: melhoria/trava-agente-morto
commit: d0b8e6d26ffbfd8e9112a24fdf4a0baf79453a87
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: v0457 (TRAVA-AGENTE-MORTO, E23.70)

Diff `a1318e88..f77bb51d` (2 commits: `76bfc6ee` feat, `f77bb51d` mutantes), lido numa worktree destacada. Classe C. Instância que não fez o código.

## Achados
- A1 (bloqueante) docs/hooks.md:11 · requisito do pronto (R-REVIEW, engineering-practices "Definição de pronto"): o hook agentes passou a atender o PreToolUse do SendMessage e a liberar registro pela notificação terminal (lápide, liberacoes.log), e docs/hooks.md:11 e :70 não dizem nada disso; atualize as duas passagens na mesma entrega
- A2 (recomendado) bin/forge-testes:131 · o mapa não lista tests.test_trava_agente_morto para hooks/agentes.py: o envio local de quem mexer no hook não roda os 49 testes (só o CI); acrescente o módulo à lista da linha 134
- A3 (recomendado) hooks/hooks.json:19 · nenhum teste confere que o hooks.json liga o SendMessage ao agentes.py; sem esse gatilho a C8 morre calada (os testes chamam o script direto). Um teste estrutural que leia o hooks.json fecha o ramo
- A4 (recomendado) hooks/agentes.py:343 · cached_property não guarda exceção: com transcript ausente ou prazo estourado, cada registro candidato relê até 2 MB do transcript; guarde a falha (por exemplo, notas = {} depois do primeiro erro, mantendo os registros)

## Sondas
- S1 · grep -c SendMessage docs/hooks.md (head f77bb51d) · espera: >= 1 · obtido: 0
- S2 · grep -c 'liberacoes.log\|lapide\|lápide' docs/hooks.md (head f77bb51d) · espera: >= 1 · obtido: 0

## Desenho contra C1 a C12
- C1: `NOTIFICACAO` ancorada com `match`, lista positiva de status, nada lido depois do `<status>`; exige `type user`, `promptSource system`, `isSidechain is False` e `content` em texto (lista do tool_result cai em TypeError e é pulada). Conferi a forma contra uma notificação real do Claude Code (transcript local): cabeçalho, campos e `meta.json` com `toolUseId` batem com a regex e com `tool_use_do_meta`.
- C2: só notas depois do `desde`; qualquer nota com tool-use-id diferente do `meta.json` mantém o registro.
- C3: `session_id` por regex UUID, id por `a` + 16 hex, `sessao` do registro igual à do evento; transcript só do `transcript_path`, com `realpath` exigindo `~/.claude/projects/<p>/<sessao>.jsonl`; `O_NOFOLLOW`, `O_NONBLOCK` e `S_ISREG`; o meta.json recusa link no caminho.
- C4: 2 MB do fim, a partir da primeira linha inteira, e prazo monotônico de 2 s dentro do timeout de 10 s do hook.
- C5: a liberação é o `morto` de `vigentes()`, dentro do `hook.trava()`; o relançamento passa de novo por `lancar` (teste `test_c5_morto_libera_a_vaga_e_o_relancamento_passa_pelas_travas`).
- C6 e C7: sem variável, argumento nem mtime; só a notificação libera (testes `test_c6_*`, `test_c7_*`).
- C8: lápide com id, descrição e branches, vence com `expiracao_horas`, no máximo 64; `SendMessage` que cita o id com relançamento vigente sai com código 2, e o erro recusa (falha fechada). Depende do gatilho novo em `hooks/hooks.json` (A3).
- C9: registro com escrita só sai com `pesado.json` livre (mesma pasta do `pesado`, `hook.run()`, também no clone desde a FORGE-RUN-INERTE). A parte "sem filho vivo em segundo plano" ficou como o status terminal da notificação; o mérito é do parecer de segurança.
- C10: duas regras com `quem` vazio (`~/.claude/projects/*/*.jsonl` e `~/.claude/projects/*/*/subagents/`); o `casa` da conformidade aceita `*` por pasta. Mais estreita que a pasta inteira para não pegar a memória dos agentes, declarado pelo autor; cobre os dois arquivos que o hook lê, e o link trocado na pasta da sessão cai na conferência de `realpath` do código. Segue.
- C11: `liberacoes.log` com hora, id, status e motivo, sem a descrição; `anexar_ao_log` é o mesmo corpo do `registrar_recusa` extraído (o `hook._run or hook.run()` antigo equivale ao `hook.run()`).
- C12: 49 testes, uma classe por condição, mais o caminho pelo hook em subprocesso com ambiente limpo e `python3 -I` (AR-4, AR-5 conferidos).

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_trava_agente_morto`: 49 testes OK (rodado aqui, R-TETO: só este módulo).
- Mutação: 26 de 26 mortos, saída do autor (`bin/forge-mutante` sobre as 4 specs); não refeita.
- Suíte inteira, shellcheck e validação do plugin: CI do PR, que é o portão. As 4 fixtures de pid e sessão do test_hooks que o autor diz falharem no sandbox também na base ficam com o CI.

## Pendências do PR
- Tamanho: 773 linhas contadas (240 em hooks/agentes.py, 15 em hooks/hooks.json, 518 de teste); o corpo do PR traz `teto: excedido, 773 linhas, <motivo>` (M14). O risco é um comportamento só (liberação do agente morto) com corpus próprio; o volume é de teste.
- Achados recorrentes (PA-7) conferidos: AR-1 e AR-2 (um mutante por guarda, ramo de falha com teste de comportamento) atendidos; AR-9 (texto antigo) é a classe do A1, sem linha nova por ser a primeira vez neste pedido.

## Parecer
Reprovado só pelo A1. O código cumpre C1 a C12 como o parecer de segurança pediu, a forma lida bate com a notificação real do Claude Code e os testes cobrem cada condição pelo ramo de falha. O gatilho novo no hooks.json é necessário para a C8 e está certo (mesmo comando e timeout do `Agent|Task`). Das pendências declaradas, a do docs/hooks.md bloqueia: o pronto pede a documentação afetada na mesma entrega, e quem tiver o SendMessage recusado ou procurar o `liberacoes.log` não acha nada no guia dos hooks. A do mapa de testes (A2) pode seguir: o CI roda a suíte inteira. A volta é só texto em docs/hooks.md, e a revalidação lê o delta.

## Revalidação (E23.98, volta E23.74)
Delta lido: `forge-check parecer delta docs/reviews/trava-agente-morto.md`, intervalo `f77bb51d..31f2e643` (código e testes: docs/hooks.md, hooks/agentes.py, hooks/conformidade.json, 4 fixtures de C10, bin/forge-testes, testes e mutantes 4 e 5). Instância que não fez a entrega, worktree própria, sem PR (sem CI para citar).
- A1 resolvido: docs/hooks.md:11 traz o `SendMessage` no gatilho e a recusa pela lápide; :70 traz a notificação terminal, `liberacoes.log`, a lápide e a proteção de `~/.claude/projects/`. S1 e S2 repetidas no head: ambas passam de 0 para >= 1.
- A2 resolvido: `test_trava_agente_morto` na regra `hooks/.*` do mapa (bin/forge-testes).
- A3 resolvido: `C8Gatilho.test_hooks_json_liga_o_sendmessage_ao_agentes`; o mutante M28 (hooks/hooks.json:19) morre.
- A4 resolvido: `Liberacao.notas` guarda a falha (`_notas = {}` antes da leitura); `test_falha_da_leitura_nao_rele_o_transcript_a_cada_registro` afirma 1 leitura para 3 registros; M27 morre.
- C10 ampliada (segurança S1 a S4): regras `~/.claude/projects/*` e `~/.claude/projects/*/*`. Sonda: `escrita_barrada` devolve None para `projects/-p/memory/x.md` e `memory/MEMORY.md` (a memória segue livre, como o texto diz) e recusa a pasta do projeto, a da sessão, o transcript e o meta. O efeito colateral (outros arquivos soltos na pasta do projeto também barrados) é aceitável e não bloqueia.
- Provas do delta: `python3 -m unittest tests.test_trava_agente_morto` 51 testes OK; `bin/forge-mutante` nas specs `-4` (M25 a M30) e `-5` (M31, M32): todos mortos. A suíte inteira, shellcheck e a validação do plugin ficam com o CI do PR.

Parecer final: aprovado no head 31f2e643. Sem achados bloqueantes abertos; A2 a A4 (recomendados) atendidos. Pendência do PR: `teto: excedido` no corpo (M14), como já dito.

## Revalidação (E23.102, junção com a develop)
Delta lido: `forge-check parecer delta docs/reviews/trava-agente-morto.md`, intervalo `31f2e643..6e005f9b`. Instância que não fez a entrega, worktree própria, sem PR do CI a citar (o CI do PR #523 fica com a suíte e as 6 falhas locais de pid e sessão do sandbox em `tests.test_hooks`).
- O patch da branch não mudou: o diff de `hooks/agentes.py`, `hooks/hooks.json`, `hooks/conformidade.json`, `docs/hooks.md` e `tests/test_trava_agente_morto.py` contra a base antiga (`ee608198..31f2e643`) tem as mesmas linhas de `9b2c6474..6e005f9b` (contra a develop nova). A junção só trouxe o `.githooks/pre-push` do #506 e outros itens da develop; nenhum toca o código da trava (sem `agente` nem `trava` no diff do pre-push).
- Único arquivo do domínio na faixa: `bin/forge-testes`, e a parte da branch é só o mapa do `test_trava_agente_morto` (regra `hooks/.*` e o comentário), sem conflito com o mapa do forge-doutor do #518.
- Provas: `python3 -m unittest tests.test_trava_agente_morto tests.test_hook_git_comum` 52 testes OK; `bin/forge-mutante` na spec `-5` (M31, M32) mortos.

Parecer final: aprovado no head 6e005f9b. Sem achados bloqueantes; a junção não muda o comportamento da trava.

## Revalidação (E23.106, segunda junção com a develop)
Delta lido: `forge-check parecer delta docs/reviews/trava-agente-morto.md`, intervalo `6e005f9b..f3c614ea` (junção com o #522; conflito só em `bin/forge-testes`). Instância que não fez a entrega, worktree própria, sem PR (sem CI a citar).
- Nada da trava mudou: `git patch-id` do diff de `hooks/agentes.py`, `hooks/hooks.json`, `hooks/conformidade.json`, `docs/hooks.md` e `tests/test_trava_agente_morto.py` contra a develop nova (`origin/develop...HEAD`) é igual ao de `9b2c6474..6e005f9b` nos cinco arquivos; `git diff 6e005f9b..f3c614ea` neles é vazio. Os demais arquivos da faixa são do #522 (`test_pr_hook_prazo`, fixtures de parecer) e dos pareceres.
- `bin/forge-testes`: a resolução manteve as duas entradas (`test_pr_hook_prazo` e `test_trava_agente_morto` na regra `hooks/.*`; `test_pr_hook_prazo` em FORGE_CHECK), sem perda de nenhuma.
- Provas: `python3 -m unittest tests.test_trava_agente_morto tests.test_hook_git_comum tests.test_pr_hook_prazo` 70 testes OK; `bin/forge-mutante tests/mutantes/trava-agente-morto-5.json` M31 e M32 mortos.

Parecer final: aprovado no head f3c614ea. Sem achados bloqueantes; a junção não muda o comportamento da trava.

## Revalidação (E23.114, depois do índice de fixtures)
Delta lido: `forge-check parecer delta docs/reviews/trava-agente-morto.md`, intervalo `f3c614ea..d0b8e6d2`. No domínio, só `docs/hooks-fixtures.md` (E23.113: contagem 2420 para 2424, `conformidade` 1778/1309 para 1782/1313, `home-*` 7/6 para 11/10, reordenado). Instância que não fez a entrega, worktree própria, sem PR (sem CI a citar).
- Índice conferido: `python3 -I scripts/indice-fixtures.py --conferir` sai 0 ("em dia"); `ls tests/hooks/*/` soma 2424 `.json`, com `agentes` 71 e `conformidade` 1782, como o índice diz. Código, hooks e testes da trava não mudaram.

Parecer final: aprovado no head d0b8e6d2. Sem achados bloqueantes.
