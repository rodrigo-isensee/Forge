---
tipo: review
contrato: 1
pedido: primeiro-uso-f3
branch: melhoria/primeiro-uso-f3
commit: 262356e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: primeiro uso F3 (forge doutor)

- **Mudança:** `bin/forge-doutor` (Python, biblioteca padrão; também `forge doutor` pelo despachante); hook `hooks/doutor.py` (SessionStart e Stop); `forge_doutor()` em `hooks/_comum.py`; chamadas do atalho `jarvis`, do `forge-upgrade` e do `tech-lead` (antes de abrir PR).
- **Conferências:** plugin instalado e versão; `.forge/versao` x plugin; proteção do git (`core.hooksPath`, pasta e permissão de `.githooks`); `gh auth status` (só no modo completo; erro de rede não vira "sem login"); identidade do git; `.claude/settings.json` com `agent: forge:jarvis`; sandbox ligado; `develop` e `homolog`. Tudo bem = silêncio e saída 0; senão, cabeçalho e lista em linguagem simples, saída 1.
- **Conserto:** só o restaurável a partir do modelo do Forge (religar `core.hooksPath` e permissão, recriar `.githooks`, `agent` no settings com cópia em `~/.local/state/forge/backup/`, branch local que existe no GitHub). Exige terminal (teste com pty) e "s"; Enter, "n" e `--rapido` não mexem em nada. Settings ilegível, `gh` e identidade só viram instrução. Teste estático: sem `--force`, `--no-verify`, `reset --hard`, `clean -f` nem `push`.
- **Frequência:** atalho `jarvis` roda o doutor rápido antes do `claude` (custo zero de tokens, pausa com Enter se listou algo); SessionStart examina e grava `.forge/run/doutor` sem escrever no stdout; Stop reexamina só se a data mudou e avisa uma vez por problema com `systemMessage` de uma linha (até 200 caracteres). Cache da data decide; `FORGE_HOJE` só nos testes.
- **Desvio da arquitetura (decisão do review):** o desenho previa a chamada dentro do `vigia`. Foi para um hook separado (`doutor.py`) porque o `vigia` tem fixtures que exigem stdout vazio em SessionStart e a mensagem fixa de violações; mexer nelas alteraria resultados de fixture existente. Mesma política: só avisa, nunca `additionalContext`, e não usa `UserPromptSubmit` (o stdout viraria contexto, ADR 0003).
- **Vermelho antes:** `tests/test_doutor.py` escrito antes do código; sem a mudança falharam 35 testes e 6 deram erro (script e hook inexistentes). **Verde depois:** 398 testes (`python3 -m unittest discover -s tests`), `shellcheck scripts/jarvis bin/forge` e `scripts/validar-plugin.sh` passam; o shellcheck não se aplica a `forge-doutor` (Python). Fixtures com HOME, git e `gh` falsos, sem rede (`R-CUSTO`), sem termo de projeto (`R-NEUTRO`).
- **Atenção ao dono:** toca `hooks/` e `tests/hooks/`, protegidos: o PR precisa do rótulo `afrouxa-regra`. Duas asserções de `tests/test_hooks.py` passaram a aceitar o `doutor` ao lado do `vigia`; nenhuma fixture existente foi alterada. Sem mudança de versão (sobe na release, ADR 0006). Depende do #102 (F2).

Parecer de autor, feito pelo mesmo agente que escreveu a mudança; o review independente fica a cargo do `tech-lead` no PR.

## Review independente
Revisor: `forge:tech-lead`, sem participação na autoria. Diff do PR #103 lido por inteiro a partir de `f4de24d` (o que vem do #102 fica fora); head revisado `1d2a10b`. Testes no checkout do PR: `python3 -m unittest discover -s tests`, 398 OK. Comportamentos conferidos com testes extras descartáveis sobre o `HookDoutor` de `tests/test_doutor.py`.

**Parecer: reprovado** (um achado médio que bloqueia, de conserto pequeno; o resto aprovado).

- **[médio, bloqueia] `hooks/doutor.py:47-49`: o aviso não é "uma vez por dia".** Todo `SessionStart` (inclusive `source` `resume`, `compact` e `clear`) chama `examinar`, que regrava o cache com `avisado: false`. Reproduzido: com um problema, `SessionStart(startup)` + `Stop` avisa; `SessionStart(compact)` + `Stop` avisa de novo; `SessionStart(resume)` + `Stop` de novo. Em sessão longa, o aviso volta a cada compactação, o contrário do que dizem `docs/hooks.md` ("no máximo uma vez por dia e por problema") e o `CHANGELOG.md`. Não gasta token (é `systemMessage`), mas é ruído, que é o que a F3 quer evitar. Sugestão: no `SessionStart`, manter `avisado` quando a data do cache é a de hoje e a lista de problemas é a mesma (ou já está contida no que foi avisado), com teste para `compact` e `resume`.
- **[baixo, recomendado] `hooks/doutor.py:46`: o diagnóstico roda dentro de `hook.trava()`,** a mesma trava de `agentes`, `pesado`, `vigia` e da autoria da `conformidade`. Normalmente leva cerca de 32 ms (medido no `SessionStart`), mas com o `git` travado o `PreToolUse` dos outros hooks espera até o timeout de 10 s deste. Sugestão: chamar `diagnosticar` fora da trava e usá-la só para ler e gravar o cache. Também convém um limite menor que 10 s em `rodar` quando chamado pelo hook (hoje é 15 s).
- **[baixo, recomendado] `bin/forge-doutor:117-129`: o conserto da proteção do git** troca qualquer `core.hooksPath` diferente de `.githooks` (por exemplo, um gerenciador de hooks que a pessoa já usava) sem guardar o valor anterior, e responde "religuei" sem conferir o código de saída do `git config`. A nova conferência logo depois mostra o que sobrou, então não há mentira duradoura. Sugestão: citar o valor atual na frase e guardá-lo junto da cópia de segurança.
- **[baixo, recomendado] Arquitetura F3:** o critério "SessionStart < 100 ms" é testado no `Stop` com cache e com limite de 0,3 s (`test_abrir_em_menos_de_cem_ms_em_media`). Medi cerca de 32 ms no `SessionStart`; o teste deveria medir esse evento.
- **[informativo] Cache forjado:** o `.forge/run/doutor` só é lido pelo próprio doutor; nenhum outro hook o consulta, então forjá-lo não pula checagem de segurança. Forjado, ele cala o aviso do dia ou mostra ao usuário um texto qualquer com o prefixo "Forge doutor:" (conferido). Isso fica coberto porque `.forge/` é caminho protegido na `conformidade` e o `vigia` vê o que escapar. Aceito.
- **Conferido e aprovado:**
  - Custo de contexto (ADR 0003): o `SessionStart` não escreve no stdout (fixture e teste), e o `Stop` emite só `systemMessage` de uma linha, até 200 caracteres, nunca `additionalContext`.
  - Conserto seguro: só no modo completo, com TTY em stdin e stdout e "s". O `settings.json` é alterado com cópia em `~/.local/state/forge/backup/`, e o arquivo ilegível não é tocado. As `settings` do usuário, o `gh` e a identidade do git só são lidos ou viram instrução. Nada destrutivo: `git branch` sem `-f`, sem `push`, `reset` ou `--force`.
  - Robustez: o `executar` sai 0 em erro interno e registra no `erros.log` (fixture `erro-interno`); o hook não é `critico` e não afrouxa outro controle. Fora de projeto do Forge, o hook não age.
  - `R-CUSTO`: o `--rapido` não usa rede (teste com `gh` falso). O modo completo só chama `gh auth status`, que é gratuito. O `claude` dos testes é falso.
  - As duas asserções de `tests/test_hooks.py`: a primeira exige do `doutor` só código 0, o que é mais estrito; a segunda só acrescenta `doutor.py` ao conjunto permitido em `SessionStart`/`Stop`, e a regra de stdout vazio no `SessionStart` continua valendo para as fixtures e para `test_doutor`. Nada afrouxado.
  - Desvio do autor (hook separado do `vigia`): aceitável. Não altera fixture nem mensagem do `vigia`, segue a mesma política e pode ser desligado à parte por `hooks_desligados`.
  - Atalho `jarvis` e `forge-upgrade`: só `--rapido`, que não conserta nem pergunta e cuja falha não impede seguir. `R-NEUTRO`: nenhum termo de projeto.
- **Para o dono:** o PR toca `hooks/` e `tests/hooks/` e precisa do rótulo `afrouxa-regra`, como o autor já registrou.

## Re-review independente
Revisor: `forge:tech-lead`, sem participação na autoria. Diff `ad1ef91..262356e` (`bin/forge-doutor`, `hooks/doutor.py`, `tests/test_doutor.py`) lido por inteiro; head revisado `262356e`. Testes no checkout do PR: `python3 -m unittest discover -s tests`, 401 OK.

**Parecer: aprovado.** Os três pontos do review foram atendidos; restam três recomendações que não bloqueiam.

- **Aviso em `resume` e `compact`: resolvido.** `SessionStart` reexamina, mas `examinar` mantém `avisado` quando data e lista de problemas são iguais às do cache. Problema novo no mesmo dia avisa de novo (correto). Testes novos cobrem os dois casos.
- **Diagnóstico fora da trava: resolvido.** `diagnosticar` roda sem trava; ela cobre só ler e gravar o cache. O `rodar` do hook usa 3 s (`LIMITE_GIT`), contra 15 s do comando.
- **Backup do `core.hooksPath`: resolvido.** O valor anterior é guardado, citado na frase, e o código de saída do `git config` é conferido. Teste novo cobre.
- **[baixo, recomendado] Corrida residual no `Stop` (`hooks/doutor.py:66-74`).** O estado é lido sob trava, a trava é solta e depois regravado por inteiro com `avisado: true`. Duas sessões simultâneas podem avisar duas vezes, e um `SessionStart` concorrente pode ter o cache mais novo sobrescrito por um estado velho. Não há arquivo corrompido (a gravação é sob trava) e o efeito é no máximo um aviso repetido ou um cache de um dia que se refaz na próxima sessão. Sugestão: na segunda trava, reler o cache, voltar a checar `avisado` e só então imprimir.
- **[baixo, recomendado] Timeout do `git` não aparece como "não consegui checar" (`bin/forge-doutor:206-228`).** Não fica silencioso demais (nunca vira "ok"), mas vira afirmação falsa: `git config --list` estourando deixa `config_git` vazio e gera "proteção desligada" e "o git não sabe seu nome"; `for-each-ref` estourando gera "a branch develop/homolog/main não existe". Com 3 s isso é mais provável do que com 15 s, e o texto engana. Sugestão: se `rodar` falhar, devolver um único problema "não consegui checar o git (demorou demais)" e pular as conferências que dependem dele.
- **[baixo, recomendado] Backup pode ser sobrescrito (`bin/forge-doutor:132`).** `if ativo:` também vale quando `ativo` já é `.githooks` (só a permissão estava errada), e então a cópia guarda `.githooks` por cima do valor original. Sugestão: guardar só se `ativo` não estiver em `(".githooks", str(pasta))`.
