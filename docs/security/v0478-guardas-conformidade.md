---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-conformidade
commit: b0ffec816f8306b84660a00ae226317464ceed17
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (E1.3, guardas da conformidade no clone)

Diff lido: `4182a6b9..b0ffec81` (`hooks/conformidade.py`, `hooks/agentes.py`, fixtures `estadoclone-*`, `tests/test_conformidade_verde.py`, mutantes). Requisitos: C9 e C10 de `docs/security/v047-v2-ameacas.md` (seção 2) e a parte de hook do CONFIG-TETO-SEM-GUARDA.

O que fechou: a `GuardaDaProva` deixa valer, no clone, a recusa de `.git/forge/` e do `.forge/config.json` da raiz da sessão, para todo papel, o jarvis incluído (C9: `hooks/conformidade.py:3528`, `:3533-3541`); a falha fechada da linha que o hook não lê cobre o estado (C10: `hooks/conformidade.py:3562-3565`). Conferido por sonda nas formas: `>`, `>|`, `exec 3>`, heredoc, `tee`, `cp`, `mv`, `install`, `dd of=`, `rsync`, `touch`, `sed -i`, edição no lugar por interpretador, `ln` e `ln -s` (origem e destino), link simbólico já existente para o arquivo e para a pasta, `cd` encadeado, ancestral (`rm -rf .git`, `mv .git`, `rm -rf "$(git rev-parse --git-common-dir)"`), caminho absoluto a partir de worktree e de fora do clone, Write e Edit; todas com rc 2 para tech-lead e jarvis. Testes novos (`EstadoDoAgentesNoClone`, `ConfigDoTetoNoClone`): 9 OK localmente. CI do head: não citável (sem PR, sem execução visível).

O que não fechou: o teto lido pelo hook `agentes` vem da cópia de trabalho da pasta corrente, e a guarda protege só o da raiz da sessão (A1); remoção e sobrescrita por comandos que o analisador não modela (A2).

## Gatilhos
Gatilhos: hook de conformidade (controle de escrita), estado do hook agentes (teto, R-BRIEF), falha fechada.

## Achados
- A1 (bloqueante) hooks/conformidade.py:3519 · O teto vem do .forge/config.json da cópia que contém a pasta corrente (agentes.py:1141, raiz_de_estado), mas a guarda só barra o da CLAUDE_PROJECT_DIR. Em worktree do clone o subagente grava teto_agentes 99 com rc 0, e o hook o lê quando o jarvis está nela.
- A2 (bloqueante) hooks/conformidade.py:898 · No clone, find .git/forge -delete, find .git -name agentes.json -delete e tar -xf a.tar -C .git/forge/run passam (rc 0): apagam ou trocam o registro (G1, G4). O mesmo com .forge/config.json. chmod 000 no estado também passa (J10 da C9, fora do teste).
- A3 (recomendado) hooks/conformidade.py:3528 · Interpretador com caminho montado (-c com '.git/'+'forge/run/agentes.json', ou script gravado antes) apaga ou reescreve o estado e o config com rc 0: limite do analisador estático. Proposta: negar a escrita no sandbox do sistema, decisão do usuário.

## Sondas
- S1 · Write em <wt>/.forge/config.json com {"teto_agentes": 99}, papel forge:tech-lead e forge:jarvis, CLAUDE_PROJECT_DIR=<clone> · espera: rc 2 · obtido: rc 0
- S2 · Bash `echo '{"teto_agentes":99}' > .forge/config.json` com a pasta corrente na worktree <wt> · espera: rc 2 · obtido: rc 0
- S3 · Hook('agentes').projeto(<wt>, clone_do_forge=True) e config()['teto_agentes'] com CLAUDE_PROJECT_DIR=<clone> (clone 2, wt 99) · espera: 2 · obtido: 99
- S4 · Bash `find .git/forge -delete` no clone, tech-lead e jarvis · espera: rc 2 · obtido: rc 0
- S5 · Bash `find .git -name agentes.json -delete` no clone · espera: rc 2 · obtido: rc 0
- S6 · Bash `tar -xf docs/a.tar -C .git/forge/run` no clone · espera: rc 2 · obtido: rc 0
- S7 · Bash `find .forge -delete` e `tar -xf docs/a.tar -C .forge` no clone (config da raiz) · espera: rc 2 · obtido: rc 0
- S8 · Bash `chmod 000 .git/forge/run/agentes.json` no clone (J10) · espera: rc 2 · obtido: rc 0

## Detalhe dos achados
**A1.** Evidência: `hooks/agentes.py:1141` (`hook.projeto(hook.cwd(), clone_do_forge=True)` → `raiz_de_estado(cwd)` → `copia_de_trabalho`, `hooks/_comum.py:45-49` e `:83-92`) e `hooks/_comum.py:2640` (`self.raiz / ".forge" / "config.json"`); a guarda compara com `Path(realpath(self.h.raiz)) / CONFIG_DA_RAIZ`, onde `h.raiz` é a `CLAUDE_PROJECT_DIR` (`hooks/conformidade.py:3518-3519`, `:3553`). As worktrees do clone em `~/.forge-contrib/wt/` já têm pasta `.forge/`. Caminho de ataque: um subagente (qualquer papel sem lista) grava `teto_agentes` alto no `.forge/config.json` da worktree em que trabalha (rc 0, S1, S2); quando a sessão principal dispara um agente com a pasta corrente nessa worktree (o `cd` persiste na sessão principal), o hook lê o teto forjado (S3) e o R-TETO deixa de limitar. O mesmo vale para `piso_memoria_gb`, `peso` e `ritmo`. Severidade: média (pré-condição: a pasta corrente da sessão principal numa worktree). Correção mínima, uma das duas: (a) no clone, o hook `agentes` lê a configuração da raiz da sessão (`raiz_declarada()`), não da cópia da pasta corrente; ou (b) `GuardaDaProva.caminho_barrado` barra o `.forge/config.json` do topo de toda cópia de trabalho cujo diretório comum (`diretorio_comum`) seja o do clone, não só o da raiz. (a) é menor e tira a divergência entre quem lê e quem guarda. Teste: S1 a S3 como caso de abuso (worktree do clone, pasta corrente nela). Esforço: P. Dono: tech-lead.

**A2.** Evidência: o conjunto de remoção `REMOCAO` (`hooks/conformidade.py:898`) é `rm`, `mv`, `rmdir`, `unlink`, `shred`; `find` com `-delete` e `tar` com extração e `-C` não são lidos como escrita no alvo, e `chmod` não chega à recusa do caminho. A C9 manda recusar escrita, remoção, renomeação, link, `chmod`, `chown`, `touch` e `truncate`. Caminho de ataque: um subagente apaga o `agentes.json` (S4, S5) ou o troca por um arquivo de um tar preparado em `docs/` (S6): teto, duplicado e Z10 liberados (G1, G4); no config da raiz, o mesmo apaga ou troca o teto (S7). A lacuna é do analisador comum e vale também na sessão de projeto (sonda com `.forge/run/` de projeto: `find .forge/run -delete` e `tar -C .forge/run` sem recusa), então a correção fecha as duas. Severidade: média. Correção mínima (dimensão nova da matriz, "comando que escreve ou remove por opção"): tratar como escrita ou remoção nos caminhos iniciais e no destino: `find` com `-delete`, `-exec`, `-execdir`, `-ok`, `-okdir`, `-fprint`, `-fprintf`, `-fls` (alvo: os pontos de partida e o arquivo das opções `-f*`); `tar` com `-x`/`--extract`/`--get` (alvo: `-C`/`--directory`, ou a pasta corrente), e também `cpio -i`/`-p`, `unzip -d` e `rsync --delete`; `chmod`, `chown`, `chgrp`, `setfacl`, `chattr` (alvo: os operandos). Teste: J10 (`chmod 000`) e S4 a S8 nas fixtures do clone, para tech-lead e jarvis. Se o dono quiser a lacuna do analisador num PR próprio, o recorte é decisão do usuário (`R-DECISAO`), não deste parecer. Esforço: M. Dono: tech-lead.

**A3.** Evidência: a recusa vem do texto e dos caminhos que o analisador resolve (`hooks/conformidade.py:3528`, `:3538-3541`); `-c` com o caminho concatenado (`open('.git/'+'forge/run/agentes.json','w')`, `os.remove(os.path.join('.git','forge','run','agentes.json'))`, `open('.forge/'+'config.json','w')`) dá rc 0 no clone e na sessão de projeto. Caminho de ataque: subagente que procura contornar de propósito; nenhum analisador estático fecha essa família. Severidade: baixa, como limite conhecido. Proposta (decisão do usuário, configuração dele, `R-DECISAO`): negar a escrita no sandbox do Bash para `<diretório comum do clone>/forge`, `<raiz do clone>/.forge/config.json` e `~/.forge-contrib/wt/*/.forge/config.json`, que vale para qualquer forma de escrita. Esforço: P. Dono: usuário (configuração), levado pelo jarvis.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: sondas locais no hook (clone e worktree temporários em `$TMPDIR`), testes novos do diff (9 OK). Suíte inteira não rodada localmente (brief: sem suíte local); CI do head não citável.
