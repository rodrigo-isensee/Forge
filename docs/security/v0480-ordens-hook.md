---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-hook
commit: c63e96158e67cb61056a5552a12ed7a3f7354925
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E123.3, hook ordens, emenda "ordens em vigor" da ADR 0003)

Revisão completa única do diff 48d6f4b8..c63e9615: `hooks/ordens.py`, `hooks/hooks.json`, `hooks/conformidade.json`, o modelo `templates/projeto/.forge/ordens-em-vigor.md`, as fixtures `tests/hooks/ordens/` e `tests/hooks/vigia/time-parado-*`, `tests/test_hooks.py`, `tests/test_doutor.py`, `tests/test_vigia_parado.py`. Contra o texto da emenda (ADR 0003, "Emenda: ordens em vigor", itens 1 a 7).

Gatilhos: hook de controle (texto injetado no contexto da sessão principal a cada mensagem), política de conformidade (mapa de donos), afrouxa-regra (ADR 0003 item 1).

## Achados
- A1 (bloqueante) hooks/conformidade.py:3806 · na sessão do Forge, a de onde o ordens lê ~/.forge-contrib/docs/kanban/ordens-em-vigor.md, qualquer subagente grava o arquivo (Write e Bash): a entrada nova do conformidade.json só vale em projeto; CAMINHOS_DO_CONTROLE e CONTROLE_NO_TEXTO não a incluem
- A2 (bloqueante) hooks/ordens.py:77 · em projeto, o ordens lê o arquivo da cópia de trabalho do cwd; na worktree, o conformidade não protege o caminho (só o da raiz) e o dev o grava; com o cwd da sessão na worktree, o texto do dev sai como ordem do dono
- A3 (recomendado) bin/forge-init:221 · .forge/ordens-em-vigor.md fica versionado no projeto: texto de qualquer branch chega à cópia do Jarvis pelo merge, sem passar pelo Jarvis; as ordens são do dia e não da versão (emenda, "Por que o existente não basta")

## Sondas
- S1 · sessão do Forge, agent_type dev, Write em {tmp}/home/.forge-contrib/docs/kanban/ordens-em-vigor.md (montagem igual a cpb-dev-write-briefs-bloqueia) · espera: código 2, R-CONFORMIDADE · obtido: código 0, stderr vazio (o mesmo Write em docs/briefs/: código 2)
- S2 · sessão do Forge, agent_type dev, Bash: echo x >> ~/.forge-contrib/docs/kanban/ordens-em-vigor.md · espera: código 2 · obtido: código 0, stderr vazio
- S3 · projeto com worktree wt (branch b1), agent_type dev, Write em {tmp}/wt/.forge/ordens-em-vigor.md · espera: código 2, como {tmp}/wt/.forge/config.json (código 2) · obtido: código 0, stderr vazio
- S4 · ordens.py, UserPromptSubmit com cwd {tmp}/wt e {tmp}/wt/.forge/ordens-em-vigor.md gravado pelo dev · espera: só o arquivo do Jarvis ou silêncio · obtido: linha fixa e "ordem escrita pelo dev na worktree"

## Detalhe dos achados
**A1** (alta). Evidência: `hooks/conformidade.py:3806-3810` (`CAMINHOS_DO_CONTROLE` e `CONTROLE_NO_TEXTO` só com `pedidos` e `briefs`); `hooks/conformidade.json:67` (a entrada nova); `tests/test_hooks.py:3906` confere só o mapa no JSON, sem fixture de conformidade que tente a escrita. Na sessão de projeto o bloqueio funciona (sonda de controle: Write de dev em `~/.forge-contrib/docs/kanban/ordens-em-vigor.md` com a raiz num projeto, código 2), mas o arquivo do Forge só é injetado na sessão do Forge, justamente onde a guarda não age. Também passaram, na sessão do Forge, com código 0: `rm -rf ~/.forge-contrib/docs/kanban`, `mv ~/.forge-contrib/docs/kanban ~/.forge-contrib/docs/k2`, `ln -sfn ~/.forge-contrib/wt/x ~/.forge-contrib/docs/kanban`, `cp src/app.js ~/.forge-contrib/docs/kanban/` e `git -C ~/.forge-contrib checkout HEAD -- docs/kanban/ordens-em-vigor.md`. O `ln -sfn` importa: a guarda do link em `hooks/ordens.py:41` só exige o alvo dentro de `~/.forge-contrib`, e `~/.forge-contrib/wt/<cópia do dev>/` está dentro. Caminho de ataque: um subagente da sessão do Forge (por erro ou por texto injetado no que ele lê) grava uma linha no arquivo; a cada mensagem do dono ela entra no contexto do Jarvis sob o cabeçalho "ordens do dono" (elevação de privilégio entre papéis; é o risco que o item 6 da emenda mitiga). Correção mínima: acrescentar a `CAMINHOS_DO_CONTROLE` o caminho `~/.forge-contrib/docs/kanban/ordens-em-vigor.md` e fazer o texto casar (`CONTROLE_NO_TEXTO` e `PEDIDO_OU_BRIEF` com `ordens-em-vigor`), cobrindo também a remoção, a troca e o link das pastas mãe `~/.forge-contrib/docs/kanban/` e `~/.forge-contrib/docs/`, como o `.forge/` do projeto já tem (apagar `.forge/` recusa por `.forge/versao`). Fixtures de conformidade, papel dev e papel seguranca, sessão do Forge e de projeto, com as formas: Write, Edit, `>`, `>>`, `cp`, `mv`, `ln -sf` no arquivo, `ln -sfn`, `mv` e `rm -rf` na pasta `docs/kanban`, `git checkout -- docs/kanban/ordens-em-vigor.md`; e uma que passa (sessão principal, sem agent_type). Esforço M. Dono: tech-lead (conformidade).

**A2** (média). Evidência: `hooks/ordens.py:77` e `:34` (a base é a cópia de trabalho que contém o `cwd`, via `copia_de_trabalho` em `hooks/_comum.py:45`); o conformidade aplica as entradas de dono jarvis só à raiz (a mesma sonda com `.forge/pausa.json` na worktree também passa, enquanto `.forge/config.json` na worktree recusa). Caminho de ataque: o dev grava o arquivo na própria worktree (S3); quando a sessão principal está com o `cwd` nela (o `cd` persiste na sessão principal), o próximo `UserPromptSubmit` injeta o texto do dev (S4). Correção mínima, uma das duas: (a) o ordens lê sempre da cópia principal, pela pasta comum do git (`diretorio_comum`, como o `.forge/run/` do item 5 da ADR 0003), nunca da worktree; ou (b) o conformidade aplica a entrada `.forge/ordens-em-vigor.md` em toda cópia de trabalho do projeto, como faz com `.forge/config.json`. A (a) é a menor e fecha também a leitura de worktree de branch alheia. Fixtures: worktree com o arquivo alterado e `cwd` nela (espera: o arquivo da raiz ou silêncio). Esforço P. Dono: tech-lead.

**A3** (baixa). Evidência: `bin/forge-init:221` (lista `ignorados` sem `.forge/ordens-em-vigor.md`) e `templates/projeto/.forge/ordens-em-vigor.md:1`. Caminho: o dev altera o arquivo num commit da branch dele; o merge da integração o leva à cópia do Jarvis, e ele vira contexto sem o Jarvis o ter gravado. Passa pelo review, por isso é recomendação. Correção mínima: acrescentar `.forge/ordens-em-vigor.md` a `ignorados` (fora do git, como `.forge/run/`) ou um aviso do `forge-check pr` quando o diff toca o arquivo. Esforço P. Dono: tech-lead.

## Conferido e sem achado
- **Texto injetado (itens 2 e 3).** O cabeçalho (`hooks/ordens.py:24`) só leva `origem`, que é uma das duas constantes do script (`:33`, `:35`), sem texto do arquivo. O aviso do teto (`:26`, `:71`) só leva dois inteiros. Escape: `Cc`, `Cf`, `Zl` e `Zp` viram espaço (`:23`, `:58`), e só `\n` separa linha; sonda com U+2028, U+0085, U+200B, U+202E, `\v` e `\f` saiu numa linha só, sem controle. Teto: 15 linhas e 2000 caracteres contados depois do escape, com a quebra contada (`:65-71`); o corte sempre fecha com a linha fixa, sem omitir em silêncio. Bytes: lê no máximo 64 KiB + 1 (`:50`) e cala acima. Uma linha do arquivo pode imitar o cabeçalho (sonda: sai como linha comum, depois do verdadeiro); com só o Jarvis escrevendo (A1 e A2 corrigidos), isso é texto do dono, sem achado.
- **Link para fora (item 4).** `realpath` antes de abrir e base exigida entre os pais (`:40-42`); `O_NOFOLLOW`, `O_NONBLOCK` e `fstat` exigindo arquivo regular (`:44-49`): FIFO e dispositivo levantam e vão ao `erros.log`, sem travar. A falha está na largura da base no Forge (A1), não na checagem.
- **Eventos e sessão.** Só `SessionStart` (startup, resume, compact) e `UserPromptSubmit` (`hooks/hooks.json`, `hooks/ordens.py:75`); texto puro no stdout, sem `additionalContext` nem JSON; sai sempre com 0; sem git, rede nem execução. O `UserPromptSubmit` não dispara em subagente.
- **Mapa de donos em projeto.** Na raiz do projeto, Write, `>`, `cp`, `ln -sf` e `git checkout --` de dev, e Write de seguranca, recusam com código 2; o Jarvis (sem agent_type) passa; `mv .forge` recusa.
- **Item 7 (vigia).** O laço das fixtures só aceita `decision` e `reason` no `Stop` sem `stop_hook_active`, com `decision == "block"` e o `reason` em `fullmatch` do formato fixo (`tests/test_hooks.py:858-875`); o teste do laço prova que ele reprova `SubagentStop`, `stop_hook_active`, `approve` e texto livre. O commit c63e9615 não muda `hooks/vigia.py`.

## O que afrouxa (por escrito, como a emenda lista)
1. ADR 0003, item 1: 3.ª exceção a "um hook nunca injeta contexto", e a 1.ª num evento a cada mensagem (`UserPromptSubmit`).
2. `tests/test_hooks.py`, `test_hooks_json`: de `assertNotIn("UserPromptSubmit", ...)` para "o único comando no `UserPromptSubmit` é o `ordens.py`"; a lista de permitidos no `SessionStart` ganha `ordens.py`.
3. `tests/test_hooks.py`, `test_cada_hook_tem_caso_que_passa_e_que_bloqueia`: `ordens` entra no grupo que só avisa (códigos `{0}`), exigindo `sem-forge-versao`, `erro-interno` e os casos do teto e do arquivo ausente.
4. `tests/test_doutor.py`, `test_hooks_json_registra_o_doutor_so_em_sessionstart_e_stop`: de `assertNotIn("UserPromptSubmit", ...)` para `== ["ordens.py"]`.
5. Item 7: o laço das fixtures aceita `decision` e `reason` só no `Stop` do vigia, com o texto fixo.
Nada sai de `invariantes` em `tests/config.json` (o diff não toca o arquivo). As mudanças no código casam com o texto da emenda, sem afrouxar além dele.

## Fora do meu domínio (ao tech-lead)
Tempo do hook: 7 execuções num projeto mínimo deram de 115 a 180 ms, e o `import _comum` sozinho, de 102 a 204 ms, contra "menos de 100 ms no caso comum" (emenda, item 5, e critério de reversão). Não é achado de segurança.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura do diff e sondas locais pela máquina de fixtures (`Fixture.montar` e `rodar` de `tests/test_hooks.py`), fora do repositório. Rodados: `tests.test_hooks.OrdensEmVigor` e `tests.test_hooks.VigiaTimeParadoNasFixtures` (16 testes, OK). A suíte inteira não foi rodada (brief: sem suíte local) e não há CI desta branch ainda (sem PR).
