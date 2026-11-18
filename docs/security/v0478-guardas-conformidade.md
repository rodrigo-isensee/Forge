---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-conformidade
commit: b3312958a3c27f9c13a94853647bc357a59ca27b
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (E1.7, revalidação das guardas da conformidade no clone)

Delta lido (`forge-check parecer delta`): `b0ffec81..b3312958`, no domínio `hooks/agentes.py`, `hooks/conformidade.py`, `docs/hooks.md`, `tests/test_conformidade_verde.py`; mutantes e changelog fora. Rodada anterior (A1 a A3, sondas S1 a S8) no git, em `b0ffec81`.

Gatilhos: hook de conformidade (controle de escrita), estado do hook agentes (teto, R-TETO), falha fechada.

Estado dos achados anteriores:
- A1: correção (a), o hook lê a configuração da raiz da sessão (`pasta_da_config`, `hooks/agentes.py:160-166`). S3 fecha (teto 2, não 99); S1 e S2 seguem rc 0 por desenho (a escrita na worktree não vale para o teto com a sessão no clone). Fica aberto um contorno pelo cache da configuração (A1 abaixo).
- A2: `find` (`-delete`, `-exec`, `-ok`, `-fprint*`, `-fls`), `tar` (extração com `-C`/`--directory` ou pasta corrente, `-f` nos modos que gravam, opção longa abreviada) e `chmod`/`chown`/`chgrp`/`setfacl`/`chattr` passaram a recusar: S4 a S8 com rc 2 para tech-lead e jarvis, mais 15 variantes (`./.git/forge/`, `-P`, `-type f`, `--directory=`, `-C` antes de `-x`, `xvf`, `-R a-w`, `-exec truncate`, `$PWD/`, `env find`, `-path`, `find .git -delete`, `rsync --delete`, `../clone/.forge/config.json`, `-fls x -delete`). Limite aceito: `find . -name agentes.json -delete` (raiz como ponto de partida, como no `rm`). Abertos: os extratores da correção mínima anterior (`unzip -d`, `cpio -i`) e o `tar` que executa comando por opção.
- A3: sem mudança, segue recomendado.

Testes novos (`EstadoDoAgentesNoClone`, `ConfigDoTetoNoClone`, `ConfigDaWorktreeNoClone`): 16 OK localmente. Suíte inteira: só no CI (brief sem suíte local); CI do head não citável (sem PR).

## Achados
- A1 (bloqueante) hooks/agentes.py:171 · ler_config troca hook.raiz mas não zera hook._config: com .forge/versao gravado na worktree (rc 0), Hook.projeto já cacheou o config dela (_comum.py:2628), e teto 99 e piso 0.1 voltam com a sessão no clone (S9).
- A2 (bloqueante) hooks/conformidade.py:2237 · Ainda passam com rc 0 no clone: unzip -d .git/forge/run, cd .git/forge/run && cpio -idm, tar --to-command='rm ...' e tar --checkpoint-action=exec='rm ...' (o find -exec já é lido; o tar que executa por opção, não).
- A3 (recomendado) hooks/conformidade.py:3528 · Interpretador com caminho montado e xargs com a lista num arquivo: limite do analisador estático. Proposta da rodada anterior: negar a escrita no sandbox do Bash, decisão do usuário.
- A4 (recomendado) hooks/conformidade.py:2237 · bsdtar, busybox tar e 7z x -o<pasta> extraem no estado com rc 0 (ausentes do PATH desta máquina); tratar bsdtar e busybox tar como tar, e 7z x com -o como extração.

## Sondas
- S9 · fixture do clone com worktree <wt>: Bash `echo 1 > .forge/versao` com a pasta corrente em <wt> (rc 0); depois `h.projeto(<wt>, clone_do_forge=True); agentes.ler_config(h); h.config()` com CLAUDE_PROJECT_DIR=<clone> (clone teto 2, wt teto 99 e piso 0.1) · espera: 2 e 2.0 · obtido: 99 e 0.1
- S10 · Bash `unzip -o docs/a.zip -d .git/forge/run` no clone, tech-lead e jarvis · espera: rc 2 · obtido: rc 0
- S11 · Bash `cd .git/forge/run && cpio -idm < ../../../docs/a.cpio` no clone · espera: rc 2 · obtido: rc 0
- S12 · Bash `tar --to-command='rm .git/forge/run/agentes.json' -xf docs/a.tar` no clone · espera: rc 2 · obtido: rc 0
- S13 · Bash `tar -xf docs/a.tar --checkpoint=1 --checkpoint-action=exec='rm .git/forge/run/agentes.json'` no clone · espera: rc 2 · obtido: rc 0

## Detalhe dos achados
**A1.** Evidência: `hooks/_comum.py:2622` (`projeto` zera `_config`), `:2628` (`self.config()` para o `hooks_desligados` quando `raiz_do_projeto` acha `.forge/versao` na worktree), `:2634-2635` (o cache vence); `hooks/agentes.py:171-173` chama `hook.config()` com a raiz trocada e recebe o cache; `:1097` (piso) e `:1111` (teto) leem esse mesmo cache. Caminho de ataque: o da rodada anterior com um passo a mais: o subagente grava `.forge/versao` e `.forge/config.json` na worktree em que trabalha (rc 0; a guarda do clone cobre só a raiz da sessão); com a pasta corrente da sessão principal nessa worktree, o R-TETO usa o teto e o piso forjados (S9). Severidade: média. Correção mínima: em `ler_config`, `hook._config = None` antes de trocar a raiz; o cache que fica é o da raiz da sessão, o que `:1097` e `:1111` devem ler. Teste: `ConfigDaWorktreeNoClone` com `.forge/versao` na worktree, esperando `2 2.0`. Esforço: P. Dono: tech-lead.

**A2.** Evidência: `hooks/conformidade.py:2235-2243` lê `find`, `tar` e os de atributo; `unzip` e `cpio` não têm regra, e `alvos_do_tar` (`:1046-1071`) ignora as opções do tar que rodam comando de texto literal: `--to-command`, `--checkpoint-action=exec=`, `--use-compress-program`, `-I`, `--info-script`, `--new-volume-script`, `-F` e `--rsh-command`. Caminho de ataque: subagente troca ou apaga o `agentes.json` (G1, G4) com um zip ou cpio preparado em `docs/` (S10, S11) ou roda `rm` pelo próprio tar (S12, S13). Severidade: média. Correção mínima: `unzip` como extração na pasta de `-d` (ou na corrente); `cpio` com `-i`/`--extract` ou `-p`/`--pass-through` como extração na pasta corrente, na de `-D`/`--directory` e no destino do `-p`; no `tar`, o valor das oito opções acima vai ao `aninhado`, como o `-exec` do `find`. Teste: S10 a S13 em `test_comando_que_escreve_ou_remove_por_opcao_recusa`. Esforço: P. Dono: tech-lead.

**A4.** Evidência: `prog == "tar"` (`:2237`) casa só o nome `tar`. Caminho: o do A2, com binário pouco comum. Dono: tech-lead.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum (a escrita no config da worktree, S1 e S2, é o desenho aceito pelo autor e só pesa pelo A1). Ferramentas: sondas locais no hook (clone e worktree temporários em `$TMPDIR`), testes novos do diff (16 OK). Suíte inteira não rodada localmente; CI do head não citável.
