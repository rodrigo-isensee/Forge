---
tipo: revisao-seguranca
contrato: 1
pedido: v0457
branch: melhoria/trava-agente-morto
commit: f3c614eaabe8d2fa2e10d1743f20630c2adb2cff
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v0457 (TRAVA-AGENTE-MORTO, E23.71, E23.99, E23.103 e E23.107)

Revalidação E23.107 (por delta 6e005f9b..f3c614ea, segunda junção com a develop, #522): **aprovado**. `forge-check parecer delta` mostra no domínio só `bin/forge-testes` (o mapa soma `test_pr_hook_prazo`; conflito resolvido com as duas entradas, sem efeito na trava). `hooks/agentes.py`, `hooks/conformidade.json`, `hooks/conformidade.py`, `hooks/hooks.json` e `tests/test_trava_agente_morto.py` sem diferença no intervalo; `hooks/_comum.py` e `hooks/parecer.py` vieram da develop (prazo do hook de PR, campo `contorno_do_prazo`, sem toque na liberação de vaga). `python3 -m unittest tests.test_trava_agente_morto`: 51 testes, OK. A2 e A3 seguem recomendados, sem promoção.

Revalidação E23.103 (por delta 31f2e643..6e005f9b, a junção com a develop): **aprovado**. `forge-check parecer delta` mostra no domínio só `bin/forge-testes` (o mapa de testes soma `test_hook_git_comum`, `test_prepush_refs` e módulos do doutor; sem efeito na trava). `hooks/agentes.py`, `hooks/conformidade.json` e `hooks/hooks.json` não mudaram em relação ao parecer. Mudou da develop o `hooks/conformidade.py` (rev-parse do .git, curinga e colchete na origem de link, #512 e anteriores), que toca o casamento da C10: conferido que o resultado dela não mudou (sondas abaixo). Os achados A2 e A3 seguem recomendados, sem promoção.

Revalidação E23.99 (por delta f77bb51d..31f2e643, volta E23.74): **aprovado**. O A1 (C10 pela pasta) está fechado; ficam só recomendações (A2 mantido, A3 novo). Primeira rodada (E23.71, f77bb51d): reprovado só pelo A1.

Diff revisado: a1318e88..f77bb51d (hooks/agentes.py, hooks/conformidade.json, hooks/hooks.json, tests/test_trava_agente_morto.py, specs de mutantes). Classe C.

## Gatilhos
Hook de controle (R-TETO) que decide liberar vaga a partir de entrada lida do disco; política de caminhos protegidos (R-CONFORMIDADE). `R-SEGURANCA`.

## Achados
- A2 (recomendado) hooks/agentes.py:786 · C8 só olha o SendMessage; se o Agent/Task aceitar retomar por id, o lancar não consulta as lápides; recusar ali também o id citado que tenha lápide com relançamento
- A3 (recomendado) hooks/conformidade.json:51 · o curinga `projects/*/*` também barra o mv e o rm da pasta `memory/` do projeto, embora docs/hooks.md diga que a `memory/` segue livre; só escrever dentro dela passa; alinhar o texto ou a regra

## Sondas
- S1 · revalidada em 31f2e643: `mv {tmp}/home/.claude/projects/x {tmp}/home/.claude/projects/x.old` (fixture home-claude-projects-mv-pasta-do-projeto) · espera: código 2 (C10) · obtido: código 2
- S2 · revalidada: `mv {tmp}/falsa {tmp}/home/.claude/projects/x` · espera: código 2 (C10) · obtido: código 2
- S3 · revalidada: `mv {tmp}/home/.claude/projects/x/<sessão> {tmp}/home/.claude/projects/x/old` · espera: código 2 (C10) · obtido: código 2
- S4 · revalidada: `rm -rf {tmp}/home/.claude/projects/x` · espera: código 2 (C10) · obtido: código 2

- S5 · fixtures C10 (mv da pasta do projeto, da sessão e forjada, rm da pasta; memoria-libera) no harness de tests/test_hooks.py em 6e005f9b · espera: código 2 nas quatro, 0 na memória · obtido: OK (5 verificadas)
- S6 · `python3 -m unittest tests.test_trava_agente_morto` em 6e005f9b · espera: OK · obtido: 51 testes, OK em 3,0 s

## Detalhe dos achados

### A1: C10 não fecha o caminho da pasta (bloqueante na E23.71; FECHADO em 31f2e643)
- **Revalidação E23.99:** hooks/conformidade.json:50-51 trazem `~/.claude/projects/*` e `~/.claude/projects/*/*` com `quem: []`, como proposto. Sondas extras (harness de fixtures, home temporário): mv da pasta do projeto, mv da falsa no lugar, mv da pasta da sessão, rm -rf do projeto, rm -rf do subagents/, rm do .jsonl, mv e rm de `projects/`, `ln -sfn` sobre o projeto, `cp -r` sobre ele, touch do meta.json, sed -i do meta.json, tee de .jsonl novo: todas código 2. `mv ~/.claude` cai na regra do `.claude/` (código 2, outra mensagem). Passam, sem ganho de ataque: `mkdir` de projeto novo (o hook só lê o `transcript_path` da sessão atual) e escrever dentro de `memory/` (esperado).
- **Evidência:** hooks/conformidade.json:50-51 protegem `~/.claude/projects/*/*.jsonl` e `~/.claude/projects/*/*/subagents/`. O casamento com curinga (`casa`, hooks/conformidade.py:480-486) só vale para o caminho do arquivo; a remoção ou troca de uma pasta intermediária (`projects/<p>`, `projects/<p>/<sessão>`) não é vista como remoção do que está dentro (só a pasta `projects/` inteira é, sonda de controle `mv ~/.claude/projects ...` → código 2). Sondas S1 a S4 com o harness de fixtures do tests/test_hooks.py e arquivos reais no home temporário.
- **Caminho de ataque:** um subagente desviado (injeção de prompt num arquivo lido, ou agente que quer passar do teto) num projeto sem o sandbox do Bash: cria em `$TMPDIR/falsa/` um `<sessão>.jsonl` com a notificação `killed` do id de um agente vivo e o `subagents/agent-<id>.meta.json` com um `toolUseId` qualquer (a C2 só confere que os dois batem, e ambos são dele); `mv` da pasta real do projeto para outro nome e `mv` da falsa no lugar. O próximo evento do hook agentes lê o transcript pelo `transcript_path` (realpath sob `~/.claude/projects/<p>/`, hooks/agentes.py:276-284, que a troca preserva) e tira o registro do agente vivo (S5). Ganho: vaga do teto (R-TETO) e do piso de memória liberada com o agente rodando, e a lápide passa a valer contra o id vivo. Onde o sandbox do Bash nega escrita em `~/.claude/projects/` (ADR 0009), o SO já barra; a C10 existe para a camada do Forge.
- **Severidade:** média (local, pede agente fora da regra; quebra a condição C10 do parecer da E23.46, que é requisito com gatilho).
- **Correção mínima:** proteger também os nós de pasta, sem barra final (o `casa` ancora em `$`, então os arquivos dentro de `memory/` seguem livres), em hooks/conformidade.json, com `quem: []`:
  - `~/.claude/projects/*` (pasta do projeto: S1, S2, S4)
  - `~/.claude/projects/*/*` (pasta da sessão e o `<sessão>.jsonl`: S3)
  Não pude provar a correção aqui (a edição de prova no meu worktree foi barrada por um hook, e não contornei); o dono prova com as sondas S1 a S4 como fixtures de `tests/hooks/conformidade/` (código 2) mais a `home-claude-memoria-libera` (código 0). Alternativa equivalente: a checagem de remoção e de destino de `mv` da conformidade tratar a pasta que casa com o prefixo de um caminho com curinga como protegida (toca hooks/conformidade.py, em voo noutra frente).
- **Esforço:** P. **Dono:** tech-lead (autor da E23.60).

### A2: retomada pelo lançamento (recomendado)
- **Evidência:** `recusar_retomada` (hooks/agentes.py:395) só roda com `tool_name == SendMessage`; `lancar` (hooks/agentes.py:781) não lê as lápides.
- **Caminho de ataque:** se a versão do Claude Code aceitar retomar um agente pelo id no próprio Agent/Task, a C8 é desviada. Não verifiquei que o parâmetro existe na versão em uso; sem ele, não há caminho.
- **Severidade:** baixa. **Correção mínima:** no PreToolUse de Agent/Task, aplicar a mesma conferência de `recusar_retomada` ao id citado na entrada. **Esforço:** P. **Dono:** tech-lead.

### Conferência de C1 a C12
- C1: hooks/agentes.py:253-254 (regex ancorada por `.match`, só até o status, lista positiva), 287-296 (type user, promptSource system, isSidechain False, content texto; tool_result em lista cai em TypeError e é pulado). Cumprida.
- C2: hooks/agentes.py:346-360 (task-id pela chave, toolUseId do meta.json, carimbo > desde; uma divergente mantém). Cumprida; a ressalva do A1 caiu com o fechamento da C10.
- C3: hooks/agentes.py:262-284, 316-322, 349-351 (sessão atual, transcript só do evento, UUID e a+16 hex, realpath e O_NOFOLLOW, meta sem link no caminho). Cumprida.
- C4: hooks/agentes.py:256-257, 262-273, 299-313 (2 MB do fim, 2 s monotônico; estouro mantém). Cumprida; no delta, `notas` virou propriedade que guarda `{}` antes de ler (hooks/agentes.py:340-349): falha da leitura vira nenhuma nota, o transcript é lido uma vez e nada é liberado (falha fechada).
- C5: hooks/agentes.py:230-245, 869-879 (dentro de `vigentes`, sob `hook.trava()`, gravado antes de qualquer recusa; o relançamento passa por `lancar`). Cumprida.
- C6: nenhum argumento, variável de ambiente nem campo da entrada aciona a liberação (lido no diff; teste c6). Cumprida.
- C7: nada por mtime nem silêncio; só a notificação. Cumprida.
- C8: lápide (hooks/agentes.py:374-406, 875) e gatilho novo em hooks/hooks.json; falha fechada no erro. Cumprida pelo SendMessage; ver A2.
- C9: hooks/agentes.py:325-330, 357-358 (registro de escrita só sai com `pesado.json` livre; o critério usa TRAVA_S, mais estrito que o do pesado). Cumprida.
- C10: cumprida em 31f2e643 (conformidade.json:50-53, 4 fixtures novas e o teste C10 com pastas; sondas acima). Ressalva menor: A3.
- C11: hooks/agentes.py:740-762 (ASCII, O_NOFOLLOW, rotação, sem descrição; id e status já validados por regex). Cumprida; a refatoração do `registrar_recusa` troca `hook._run or hook.run()` por `hook.run()`, equivalente (`run()` devolve `_run` quando fixado).
- C12: (E23.71: 49 testes; E23.99: 51, módulo OK em 31f2e643 em 1,8 s; sem PR aberto, a suíte inteira fica para o CI do PR) 49 testes, um ou mais por condição de C1 a C11; rodei o módulo (OK). Os mutantes ficam com o QA.

### Tentativas pedidas pelo brief
- Liberar registro de agente vivo: só pelo A1 (S5); pela entrada do hook, por tool_result, por mensagem do usuário, por sidechain, por status depois do cabeçalho e por sessão alheia, não liberou (testes do módulo e leitura).
- Forjar a notificação: no transcript em si, barrado (echo, cp, tee e python com escrita: código 2); pela troca de pasta, passou (A1).
- Retomar depois da lápide: o SendMessage é recusado com relançamento vigente; ver A2 para o lançamento.
- Escrever nos transcripts protegidos: escrita direta barrada; remoção e troca da pasta, não (A1).
- C10 mais estreita: aceitável quanto ao conteúdo (a `memory/` não é prova de nada e segue livre), mas não como está: precisa dos nós de pasta do A1.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Delta lido: docs/hooks.md (SendMessage, lápide e liberacoes.log descritos de acordo com o código), bin/forge-testes (mapa só soma o teste novo ao hooks/), hooks/hooks.json sem mudança (matcher do SendMessage já coberto pelo C8Gatilho). Ferramentas: leitura do diff, o harness de fixtures do tests/test_hooks.py e o próprio módulo, com sondas locais em pasta temporária. gitleaks, semgrep e zizmor não se aplicam a este diff (sem segredo, sem workflow).
