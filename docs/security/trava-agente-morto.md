---
tipo: revisao-seguranca
contrato: 1
pedido: v0457
branch: melhoria/trava-agente-morto
commit: f77bb51df14bee2e20a1814f622e37e45427f793
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v0457 (TRAVA-AGENTE-MORTO, E23.71)

Diff revisado: a1318e88..f77bb51d (hooks/agentes.py, hooks/conformidade.json, hooks/hooks.json, tests/test_trava_agente_morto.py, specs de mutantes). Classe C.

## Gatilhos
Hook de controle (R-TETO) que decide liberar vaga a partir de entrada lida do disco; política de caminhos protegidos (R-CONFORMIDADE). `R-SEGURANCA`.

## Achados
- A1 (bloqueante) hooks/conformidade.json:50 · C10 contornável: as entradas protegem os arquivos, não as pastas; trocar a pasta do projeto em ~/.claude/projects/ por uma falsa (mv) passa no hook e o agentes.py libera um agente vivo com notificação e meta.json forjados
- A2 (recomendado) hooks/agentes.py:781 · C8 só olha o SendMessage; se o Agent/Task aceitar retomar por id, o lancar não consulta as lápides; recusar ali também o id citado que tenha lápide com relançamento

## Sondas
- S1 · Bash de forge:tech-lead `mv {tmp}/home/.claude/projects/x {tmp}/home/.claude/projects/x.old` (pasta com <sessão>.jsonl e subagents/ reais) · espera: código 2 (C10) · obtido: código 0
- S2 · Bash de forge:tech-lead `mv {tmp}/falsa {tmp}/home/.claude/projects/x` · espera: código 2 (C10) · obtido: código 0
- S3 · Bash de forge:tech-lead `mv {tmp}/home/.claude/projects/x/<sessão> {tmp}/home/.claude/projects/x/old` · espera: código 2 (C10) · obtido: código 0
- S4 · Bash de forge:tech-lead `rm -rf {tmp}/home/.claude/projects/x` · espera: código 2 (C10) · obtido: código 0
- S5 · Liberacao sobre registro vivo depois de S1+S2 (falsa com <sessão>.jsonl trazendo notificação killed e meta.json com o mesmo toolUseId forjado) · espera: 1 registro · obtido: 0 registros, soltos ['killed']

## Detalhe dos achados

### A1: C10 não fecha o caminho da pasta (bloqueante)
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
- C2: hooks/agentes.py:346-360 (task-id pela chave, toolUseId do meta.json, carimbo > desde; uma divergente mantém). Cumprida, com a ressalva do A1 (meta e transcript forjáveis juntos pela troca de pasta).
- C3: hooks/agentes.py:262-284, 316-322, 349-351 (sessão atual, transcript só do evento, UUID e a+16 hex, realpath e O_NOFOLLOW, meta sem link no caminho). Cumprida.
- C4: hooks/agentes.py:256-257, 262-273, 299-313 (2 MB do fim, 2 s monotônico; estouro mantém). Cumprida.
- C5: hooks/agentes.py:230-245, 869-879 (dentro de `vigentes`, sob `hook.trava()`, gravado antes de qualquer recusa; o relançamento passa por `lancar`). Cumprida.
- C6: nenhum argumento, variável de ambiente nem campo da entrada aciona a liberação (lido no diff; teste c6). Cumprida.
- C7: nada por mtime nem silêncio; só a notificação. Cumprida.
- C8: lápide (hooks/agentes.py:374-406, 875) e gatilho novo em hooks/hooks.json; falha fechada no erro. Cumprida pelo SendMessage; ver A2.
- C9: hooks/agentes.py:325-330, 357-358 (registro de escrita só sai com `pesado.json` livre; o critério usa TRAVA_S, mais estrito que o do pesado). Cumprida.
- C10: não cumprida (A1).
- C11: hooks/agentes.py:740-762 (ASCII, O_NOFOLLOW, rotação, sem descrição; id e status já validados por regex). Cumprida; a refatoração do `registrar_recusa` troca `hook._run or hook.run()` por `hook.run()`, equivalente (`run()` devolve `_run` quando fixado).
- C12: 49 testes, um ou mais por condição de C1 a C11; rodei o módulo (OK). Os mutantes ficam com o QA.

### Tentativas pedidas pelo brief
- Liberar registro de agente vivo: só pelo A1 (S5); pela entrada do hook, por tool_result, por mensagem do usuário, por sidechain, por status depois do cabeçalho e por sessão alheia, não liberou (testes do módulo e leitura).
- Forjar a notificação: no transcript em si, barrado (echo, cp, tee e python com escrita: código 2); pela troca de pasta, passou (A1).
- Retomar depois da lápide: o SendMessage é recusado com relançamento vigente; ver A2 para o lançamento.
- Escrever nos transcripts protegidos: escrita direta barrada; remoção e troca da pasta, não (A1).
- C10 mais estreita: aceitável quanto ao conteúdo (a `memory/` não é prova de nada e segue livre), mas não como está: precisa dos nós de pasta do A1.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, o harness de fixtures do tests/test_hooks.py e o próprio módulo, com sondas locais em pasta temporária. gitleaks, semgrep e zizmor não se aplicam a este diff (sem segredo, sem workflow).
