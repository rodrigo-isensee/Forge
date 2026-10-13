---
tipo: review
contrato: 1
pedido: hook-vigia
branch: melhoria/hook-vigia-v2
commit: 8b1c77d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Code review: hook `vigia` (ADR 0009, seção 8)

Escopo: `origin/develop..11eb9f0` (2 commits): `hooks/vigia.py`, `hooks/hooks.json`, `tests/hooks/vigia/` (12 fixtures), `tests/test_hooks.py`, `docs/hooks.md`, `CHANGELOG.md`. Referências: ADR 0003 (itens 1 e 4) e ADR 0009 (seções 7 e 8).

Como revisei: leitura do diff; `python3 -m unittest discover -s tests` (164 testes, verde); execução do hook, fora dos fixtures, num projeto temporário com `.forge/versao`. Simulei alterações repetidas, transcrições com bloqueio seguido de nova tentativa, `SessionStart` com `source: compact` e 60 mil arquivos em `.claude/worktrees/`, medindo o tempo.

Parecer: **reprovado**, com 4 ajustes que bloqueiam. O desenho está certo e o canal também. O que falha: a deduplicação esconde a reincidência; o `contorno` acusa a correção esperada depois de um bloqueio; a varredura entra nas worktrees; e o harness deixou de proteger o `SessionStart` dos outros hooks.

## O que está correto
- **Nunca injeta contexto no modelo.** A única saída é `{"systemMessage": ...}` em uma linha, com código 0, e só em `Stop`/`SubagentStop` (`hooks/vigia.py:236-240`). O `SessionStart` não escreve nada (`iniciar`, `hooks/vigia.py:164-172`). O teste confere que a saída tem só a chave `systemMessage` e nenhuma quebra de linha.
- **Erro interno libera.** Usa `executar` sem `critico`: sai 0 e grava no `erros.log`, sem saída. Reproduzido com `.forge/config.json` corrompido e com entrada inválida (`test_entrada_invalida_libera` passou a incluir o `vigia`).
- **Leitura incremental de verdade.** A transcrição é lida a partir do deslocamento salvo, só até a última linha completa (`hooks/vigia.py:64-75`). Transcrição truncada ou rotacionada (menor que o deslocamento) recomeça do zero. Linha parcial ou JSON inválido é ignorado. Transcrição principal desconhecida começa do fim, sem ler o histórico.
- **Tempo no caso comum:** cerca de 34 ms por `Stop` (meta: 300 ms).
- **Neutralidade e custo zero:** só biblioteca padrão e git local, sem rede e sem chamada a modelo. `IGNORADOS` cita só caminhos do Claude Code. O teste `Neutralidade` passa.
- **Documentação honesta.** `docs/hooks.md` lista o que o hook não detecta, o falso positivo conhecido e as suposições sobre a plataforma, com fonte e data.

## Achados: bloqueiam

**B1. A deduplicação por texto silencia a reincidência.**
- Onde: `hooks/vigia.py:217-218` (`vistos` guarda `tipo:detalhe`) e `hooks/vigia.py:146` e `203` (detalhe sem nada que identifique a ocorrência).
- Problema: a mesma violação repetida depois produz o mesmo texto e é filtrada. Reproduzido:
  - `.githooks/pre-push` alterado gera aviso; alterado de novo no turno seguinte, nada é avisado nem gravado em `violacoes.jsonl`;
  - um contorno em `main` gera aviso; um segundo contorno real em `main`, dias depois e em outra sessão, fica mudo até saírem 300 entradas de `vistos`.
- Por que importa: o arquivo mais visado é exatamente o que fica invisível depois do primeiro aviso.
- Sugestão: deduplicar só o que é estado persistente (`git status`, já coberto pelo hash). `em-vigor` já é diferencial, porque a base avança a cada turno, então não precisa de `vistos`. Para `contorno`, deduplicar pelo `tool_use_id` da tentativa, não pelo texto. Fixture: alterar o mesmo arquivo em vigor em dois turnos e esperar dois avisos.

**B2. O `contorno` acusa a correção esperada depois de um bloqueio e diverge da ADR.**
- Onde: `hooks/vigia.py:99-104` (alvo de `git`/`gh` = última palavra) e `hooks/vigia.py:143-147` (qualquer chamada não barrada com alvo em comum e entrada diferente).
- Problema: a ADR 0009, seção 8, define contorno como nova tentativa "por outra ferramenta, script ou agente". O código conta qualquer chamada com entrada diferente, inclusive da mesma ferramenta. Além disso, os bloqueios não expiram e valem entre sessões. Falsos avisos reproduzidos:
  - `git push --no-verify origin feature/x` barrado (`R-VERIFY`), seguido de `git push origin feature/x`. É a correção que a própria mensagem pede, e foi acusada como contorno;
  - `git push origin main` barrado (`R-MAIN`), seguido de `git log --oneline main`. Também valeria para `git checkout main` ou `git diff main`, em qualquer sessão futura.
  - O mesmo vale para `R-REVIEW`/`R-QA` (gravar o parecer e repetir o `git merge`/`gh pr create` com outro título) e `R-WIP` (corrigir o `KANBAN.md` é editar o mesmo alvo).
- Por que importa: o fluxo "bloqueou, corrigiu, repetiu" é o caminho feliz em todos os projetos. Falso aviso frequente ensina o usuário a ignorar o vigia.
- Sugestão:
  1. Contar só bloqueios de `R-CONFORMIDADE` e `R-MAIN` (em que o próprio alvo é proibido ao papel).
  2. Exigir outra ferramenta (Write barrado e Bash no mesmo caminho) ou um Bash que executa script, `sh -c`, `eval` ou `bash <arquivo>`, como diz a ADR. Em `git`/`gh`, exigir o mesmo subcomando de escrita (`push`, `merge`, `pr merge`), não qualquer leitura.
  3. Limitar o bloqueio à mesma sessão (`session_id`) e a `expiracao_horas`.
  4. Fixtures negativos para os três casos acima.

**B3. A varredura de `.claude/` percorre as worktrees inteiras antes de ignorá-las.**
- Onde: `hooks/vigia.py:54-58`.
- Problema: `sorted(alvo.rglob("*"))` lista tudo antes de `ignorado(rel)` filtrar. Com `.claude/worktrees/` (onde o Claude Code cria worktrees, com `node_modules`), cada `Stop`, `SubagentStop` e `SessionStart` percorre cópias inteiras do projeto. Ao chegar em `LIMITE_ARQUIVOS`, o laço faz `continue`, não `break`. Medido: 60 mil arquivos levam 2,7 s por turno, contra 34 ms sem eles. Projeto real com duas ou três worktrees passa do `timeout` de 10 s, com a trava de estado presa nesse tempo.
- Sugestão: usar `os.walk` podando `dirs[:]` pelos `IGNORADOS` antes de descer, e parar ao chegar no limite. Recomendado no mesmo ajuste: guardar `(tamanho, mtime_ns)` e só recalcular o SHA-256 quando mudarem. Hoje cada turno pode ler até 3000 arquivos de 2 MB. Fixture ou teste de tempo com uma árvore grande em `.claude/worktrees/`.

**B4. O harness afrouxou a proteção do `SessionStart` para todos os hooks.**
- Onde: `tests/test_hooks.py:246` e `tests/test_hooks.py:134-140` e `195`.
- Problema: antes, nenhum hook podia ficar em `SessionStart`, onde o stdout com código 0 vira contexto do modelo (ADR 0003, item 1: "inclusive em `SessionStart`"). Agora:
  - qualquer hook pode ser registrado ali sem o teste falhar;
  - a saída dos `passos` não é conferida, e nenhum fixture tem `SessionStart` como entrada principal num projeto do Forge. O `sem-forge-versao` não cria `.forge/run`, então não exercita `iniciar`;
  - por isso, um `print` acidental no `iniciar` do vigia também passaria;
  - a exigência de `saida` não está restrita ao `vigia` (`tests/test_hooks.py:198`).
- Sugestão:
  - em `test_hooks_json`, exigir que os grupos de `SessionStart` (e de `Stop`) referenciem só `vigia.py`;
  - em `executar_passos`, conferir stdout vazio e código 0 em toda `entrada` de `SessionStart`;
  - incluir o fixture `inicio-silencioso`, com `SessionStart` como entrada principal num projeto do Forge;
  - em `tests/test_hooks.py:198`, `assertEqual(f.hook, "vigia")`.

## Achados: recomendados

- **R1. `SessionStart` de `compact`/`resume`/`clear` zera a base no meio do trabalho.** Onde: `hooks/vigia.py:164-172`. A compactação automática dispara `SessionStart` durante uma tarefa. A base de hashes é regravada e o deslocamento da transcrição salta para o fim. O que mudou antes da compactação deixa de aparecer como `em-vigor`; fica só o `git status`, que não vê arquivo ignorado. Também se perde o trecho da transcrição entre o último `Stop` e a compactação. Uma segunda sessão aberta na mesma raiz também zera a base da primeira. Sugestão: com `source` diferente de `startup`, ou com a raiz já no estado, rodar `verificar` antes (ou não sobrescrever) e manter o deslocamento existente.
- **R2. Estado sem poda.** Onde: `hooks/vigia.py:167` e `170`. `transcricoes` ganha uma entrada por sessão e por subagente, e `raizes` uma por worktree, com até 3000 hashes cada. Nada sai, e todo turno lê e regrava o `vigia.json` inteiro, que cresce sem limite. O `violacoes.jsonl` também cresce sem limite, ao contrário do `erros.log`, que roda em 256 KB. Sugestão: descartar transcrições cujo arquivo não existe mais ou mais velhas que `expiracao_horas`, descartar raízes inexistentes e rodar o `violacoes.jsonl` como o `erros.log`.
- **R3. Mudança legítima chamada de "violação".** Onde: `hooks/vigia.py:239`, `bin/forge-upgrade:45` e `81`. O `forge-upgrade` grava `.forge/versao`, e uma edição do usuário em `.claude/settings.json` no meio da sessão também aparece como "violação". A documentação aceita o aviso, mas a palavra acusa quem fez o certo. Sugestão: para `em-vigor` e `git`, dizer "mudança em arquivo em vigor" e reservar "violação" para `contorno`. Outra opção: não avisar `em-vigor` quando a transcrição do turno mostra a chamada a `forge-upgrade`.
- **R4. Atribuição em sessões simultâneas.** Onde: `hooks/vigia.py:198-204` e `223-225`. A base é por raiz, não por sessão: a sessão que roda o `Stop` primeiro leva no `violacoes.jsonl` o `agente` e a `sessao` da mudança feita por outra sessão ou pelo usuário. Basta documentar em `docs/hooks.md` ("o registro diz quem viu, não quem fez").
- **R5. Linha de renomeação no `git status`.** Onde: `hooks/vigia.py:181-183`. `R  a -> b` vira o caminho `a -> b` e escapa de `ignorado`. Sugestão: `--porcelain -z` ou pegar o lado depois de ` -> `.
- **R6. Suposição não conferida.** O formato do `tool_result` de uma chamada barrada por hook (`is_error` e `R-XXX:` no texto) ainda não foi conferido contra uma transcrição real (`docs/hooks.md` diz isso). Antes da `homolog`, gravar um fixture a partir de uma transcrição real com um bloqueio do `conformidade`.
- **R7. Pendência da ADR.** A ADR 0009 (riscos, item 6) conta com "o vigia registrando hook ausente" como mitigação. Não está neste PR nem em "o que não detecta". Sugestão: registrar como pendência em `docs/hooks.md` ou no quadro.

## Para aprovar
Corrigir B1 a B4, com os fixtures negativos de B2 e o teste de B4. Os recomendados podem ir para o quadro, com cartão, exceto R1, que é barato e convém entrar junto.

## Revalidação (1146e65)

Escopo: `f98b082..0d74071` (correções do autor) mais o ajuste da guarda da suíte. Suíte: 168 testes verdes. Parecer: **aprovado**. Os 4 bloqueios estão corrigidos, com fixtures negativos e testes de estrutura; sobram 1 recomendado novo e pendências já registradas no CHANGELOG e em `docs/hooks.md`.

| Achado | Situação | Evidência |
|---|---|---|
| B1 deduplicação por texto | corrigido | `vistos` removido; contorno deduplicado pelo id da chamada (`estado["contornos"]`); `em-vigor` é diferencial; fixtures `em-vigor-reincide`, `contorno-repetido` |
| B2 contorno acusa a correção | corrigido | só `R-CONFORMIDADE` e `R-MAIN`; `eh_contorno` exige outra ferramenta, outro mecanismo de escrita ou o mesmo push/merge que passou em `R-MAIN`; mesma sessão e `expiracao_horas`; 6 fixtures negativos e 2 positivos |
| B3 varredura entra nas worktrees | corrigido | `os.walk` com poda de `subpastas` e parada no limite; teste com espião de `os.walk` e teste de tempo com 6000 arquivos. O hash por `(tamanho, mtime)` fica pendente (recomendação) |
| B4 harness afrouxado | corrigido | `SessionStart` e `Stop` só com `vigia.py`; stdout vazio e código 0 em `SessionStart` dos `passos`; fixture `inicio-silencioso`; `saida` restrita ao `vigia` |
| R1 compactação zera a base | corrigido | `iniciar` preserva base, deslocamento e `erros` em `resume`/`compact`/`clear`; fixture `compactacao-preserva-base` |
| R2 estado sem poda | corrigido | `podar` e `rotacionar` (256 KB), com teste |
| R3 "violação" para mudança legítima | corrigido | `GRAVIDADE`: só o contorno é "violação"; `em-vigor` e `git` são "mudança(s)" |
| R4 atribuição com sessões simultâneas | corrigido (documentado) | `docs/hooks.md`: "o registro diz quem viu, não quem fez" |
| R5 renomeação no `git status` | corrigido | `caminho_da_linha` usa o lado novo; teste. Nome de arquivo com ` -> ` literal não é tratado (aceitável) |
| R6 formato real do bloqueio | pendência | declarada em `docs/hooks.md` e CHANGELOG; fixture de transcrição real antes da `homolog` |
| R7 hook ausente (ADR 0009, riscos, item 6) | pendência | declarada em `docs/hooks.md` e CHANGELOG; abrir cartão no quadro |

### Achados novos
- **N1 (recomendado). Falso positivo em `R-MAIN` com leitura do alvo por `merge`.** `hooks/vigia.py:149-150`: o alvo de `git`/`gh` é a última palavra, então um `git merge main` na branch de trabalho (trazer a `main`, que a prática manda fazer) tem o mesmo subcomando e o alvo `main` de um `git merge x` barrado na `main`, e conta como contorno. Sugestão: no `R-MAIN`, exigir também a mesma sequência de argumentos ou a mesma branch atual; ou aceitar o falso positivo e dizê-lo em "Falso positivo possível" de `docs/hooks.md`. Não bloqueia: o aviso é só para o usuário, só na mesma sessão e dentro do prazo.
- **N2 (informativo). Chamada e resultado em lotes diferentes.** `usos` vive só dentro de uma chamada a `contornos`; se o `tool_use` cair num trecho lido em um turno e o `tool_result` no seguinte, o bloqueio não é visto. Raro (o resultado vem logo depois); tratar junto do fixture real (R6).

### Ajuste da guarda da suíte (`tests/guarda_git.py`)
`diferenca` passa a ignorar as seções `branch.*` (o git grava o rastreamento ao criar ou enviar branches em paralelo) e continua acusando `user.*`, `core.*`, `commit.*`, `include*`, `alias.*`, `remote.*.url` e qualquer chave nova. Testes: mudar `branch.x.remote` não falha; mudar cada uma das chaves vigiadas falha; a seção depois de um `[branch]` continua vigiada.

## Revalidação (8b1c77d)

Escopo: `fd27ded..e74b287` (correção do N1: `hooks/vigia.py` e o fixture `merge-main-na-branch-de-trabalho`). `e74b287..8b1c77d` não toca `hooks/vigia.py`, `hooks/hooks.json` nem `tests/hooks/vigia/` (diff de nomes vazio), então o código avaliado é o mesmo revisado e testado. Suíte: 187 testes verdes. Parecer: **aprovado**.

| Achado | Situação | Evidência |
|---|---|---|
| N1 falso positivo em `R-MAIN` com `merge` | corrigido | `eh_contorno` exige, para `merge`, `rebase` e `gh pr merge`, os mesmos argumentos do bloqueio (`perfil_da_chamada` agora grava `args`); `git merge main` depois de `git merge x main` barrado não conta. `push` mantém a regra anterior, mas só conta com a `main` no alvo, então um `git push origin feature/x` após o barrado não é acusado |

### Verificações
- Fixture `merge-main-na-branch-de-trabalho` falha com o `hooks/vigia.py` de `fd27ded` (o aviso `contorno` é emitido) e passa com o atual: o teste de regressão cobre o bug.
- Caso repetido com os mesmos argumentos (`git merge x main` barrado e de novo) continua acusado como contorno (fixture `contorno-repetido` e o caminho `args` iguais).
- Bloqueios gravados por versões anteriores no `vigia.json` não têm `args`: `bloqueio.get("args")` vira `None` e nunca bate, então o pior caso é deixar de avisar um contorno de merge/rebase antigo, não acusar uma correção. Aceitável.

### Pendências (não bloqueiam)
- Continuam as pendências já registradas em `docs/hooks.md` e no CHANGELOG (R6, formato real do bloqueio; R7, hook ausente; hash por `(tamanho, mtime)`).
