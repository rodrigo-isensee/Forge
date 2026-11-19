---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-conformidade
commit: f36dad1a5c05fe303545264048ed0673f2841598
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0478 (E1.17, portão no head f36dad1a e pergunta do dono "só aperta?")

Delta lido (`forge-check parecer delta`): `bdbdc257..f36dad1a`, nenhum arquivo do domínio (só os três pareceres). A pergunta do dono pede mais que o delta: li o diff inteiro contra a `origin/develop` (`c720891e`; merge-base `4182a6b9`, sem mudança em `hooks/` entre os dois) em `hooks/conformidade.py`, `hooks/agentes.py`, `tests/` e mutantes. Rodada anterior (A3, A5, S16 a S18) no git, em `6a3e3983`.

Gatilhos: hook de conformidade (controle de escrita), estado do hook agentes (teto, R-TETO), falha fechada.

Estado dos achados anteriores: A5 fechado (sem mudança); A3 segue recomendado (decisão do dono, sandbox).

## Só aperta?
**Não.** Um ponto aceita o que a `origin/develop` recusava e é defeito (A6); outro aceita mais por desenho (P2) e fica com o dono. O resto só aperta.

Método: o mesmo executor de fixtures da suíte (`tests/test_hooks.py`, `Fixture.montar` e `rodar`), com os hooks da `origin/develop` e os do head, sobre as mesmas entradas; conta a transição do código de saída (2 recusa, `ask` pergunta, 0 libera).
- D1, corpus inteiro do head (2271 fixtures do `conformidade`): 2→2 1683, 0→0 565, ask→ask 19, 0→2 4 (as `estadoclone-*` novas); **2→0 e 2→ask: zero.** Nenhuma fixture existente mudou (`--diff-filter=MDR` só nos hooks, docs, dois mutantes e no teste novo; o teste não perde linha).
- D2, cada Bash do corpus com `busybox ` e `toybox ` na frente (4166) e 83 comandos gerados × 8 papéis × projeto e clone (1328): 0→2 1889, 0→ask 34, **2→0 5**, todos sem perda de controle (P3).
- D3, 54 applets do busybox e do toybox que rodam outro programa × 10 cargas recusadas × 3 prefixos × 2 papéis (3240): 0→2 172, **2→0 196**, todos o A6.
- Agentes (S20): config da worktree mais estrito ou ilegível recusava e agora vale o da raiz (P2).

Pontos que aceitam mais:
- **P1 = A6 (defeito).** `hooks/conformidade.py:2292` troca `busybox` pelo applet antes de `:2311`; a base tinha `busybox` em `ENVOLVEDORES` e varria a linha com `atualizacao`. Applet fora de `ENVOLVEDORES`, `SHELLS` e `INTERPRETES` que roda programa perde a varredura: `forge-atualizar` e `forge atualizar` passam (S19). O rótulo espera o dono.
- **P2 (por desenho).** `hooks/agentes.py:160`, `:266`, `:1113`, `:1164`: com a sessão no clone, teto, piso, ritmo e peso vêm do `.forge/config.json` da raiz da sessão. Um config na worktree mais estrito (`teto_agentes: 1`, `piso_memoria_gb: 999`) ou ilegível (`{`) recusava o disparo; agora vale o da raiz (S20). Esse arquivo é escrito por qualquer subagente (é o canal do A1), não um controle do dono; o arquivo que o dono controla e a conformidade guarda passa a decidir. Com `.forge/versao` na worktree, o config ilegível segue recusando (`hook.projeto` o lê antes). Aceita mais só contra valor que o dono não pôs; decisão dele.
- **P3 (falso positivo antigo, sem execução).** Os 5 de D2: `busybox echo 'rode no terminal: forge atualizar'`, `busybox git commit -m '... forge atualizar' --allow-empty`, `busybox forge salvar -m '... forge atualizar'` (a base recusava a citação) e `busybox|toybox git switch -c feature/x && git branch tmp && git commit -m 'feat: x'` (a base não via a troca de branch). Não há applet `git` nem `forge` no busybox: a cadeia para no primeiro comando. Sem controle perdido.

O que só aperta:
- Recusas novas: `find` (`-delete`, `-exec`, `-fprint*`), extratores do catálogo `DESTINOS`, `chmod`/`chown`/`chgrp`/`setfacl`/`chattr`, applet do busybox/toybox (D3: `busybox taskset|flock|unshare` vira lançador recusado; `busybox rm -rf .githooks` passava e recusa), recusas do estado na `GuardaDaProva` (`:3709` a `:3762`) e o recuo por texto (`ESTADO_NO_TEXTO`, `:3783`). `ESCRITORES` só ganha nomes. Os ramos novos entram antes de `pacotes`, sem nome em comum (`hooks/conformidade.json`: npm, pnpm, yarn, pip, pip3, uv, poetry, cargo, bundle, composer, gem, go, apt, apt-get, brew).
- `GuardaDaProva.caminho_barrado` devolve None para `.forge/config.json` fora da raiz, mas na base nenhuma recusa desse caminho valia na prova: nada sai.
- Catraca 36→37: um `skipTest` novo, condicional (sem GNU tar no PATH), num teste novo (`tests/test_conformidade_verde.py:463`); não toca decisão do hook nem tira asserção; o `teto_pulados` do CI segue 1 (`tests/config.json:923`). Com GNU tar 1.35 aqui, `CatalogoDosDestinos` roda (3 OK). Afrouxa só a prova numa máquina sem GNU tar (recomendado A1 do review).
- 33 usos legítimos: seguem rc 0 no head (S9 do review). No clone, meus 40 legítimos × 7 papéis: 280 de 280 rc 0 nos dois lados. Em projeto, 42 casos (extrair, `find -delete`, `chmod -R`, `chown -R` em `docs/`) passam a recusar por alcançar `docs/security/aceites/`: aperto com custo de uso, não afrouxa.
- Mutantes: as duas mudanças (`v047-hook-estado-ilegivel-2`, `z075-uma-delegacao-por-branch`) só seguem o texto novo, com a mesma mutação.

Testes do diff: `EstadoDoAgentesNoClone`, `ConfigDoTetoNoClone`, `ConfigDaWorktreeNoClone` 20 OK; `CatalogoDosDestinos` 3 OK. Suíte inteira: só no CI (brief sem suíte local); CI do head não citável (sem PR).

## Achados
- A6 (bloqueante) hooks/conformidade.py:2292 · Troca do busybox pelo applet perde a varredura de ENVOLVEDORES: `busybox linux64|setarch|chroot|watch|run-parts|su -c|ash -c ... forge-atualizar` (ou `forge atualizar`) recusava na base e passa (196 de 3240). Corrigir: `self.atualizacao(palavras)` antes da troca.
- A7 (recomendado) hooks/conformidade.py:2292 · Lacuna anterior, não regressão: applet do busybox que roda programa e não está em LANCADORES (`chroot`, `setarch`, `nsenter`, `su -c`, `ash -c`...) esconde `git push --no-verify`, `rm -rf .githooks`, `gh pr merge --admin`: rc 0 na base e no head.
- A3 (recomendado) hooks/conformidade.py:2374 · Lista negativa não fecha a família: sort -o, curl -o, wget -O, gzip, zip -m, patch -o, split, sqlite3, git -C init, dpkg-deb -x, ar x, pax -r, interpretador e destino vindo do arquivo (tar -P, 7z -spf, cpio -i absoluto, unzip -:) gravam no estado com rc 0. Saída: sandbox (dono).

## Detalhe dos achados
**A6.** Caminho: um subagente (tech-lead, dev) numa máquina com busybox roda `busybox linux64 forge-atualizar`; a base recusava (R-CONFORMIDADE, "troca o plugin e mexe no projeto"), o head libera e o plugin é trocado sem a pessoa. Severidade média (ator interno, exige busybox instalado, efeito no plugin e no projeto). Applets que perdem a recusa em D3, todos com `forge-atualizar`, `forge atualizar` e `'forge atualizar'`, com `busybox` e `/bin/busybox`: chroot, nsenter, setarch, linux32, linux64, chpst, su -c, watch, start-stop-daemon, ssd, run-parts, setuidgid, envdir, envuidgid, softlimit, cttyhack, runuser, ash -c, hush -c, toybox, tclsh, awk, inotifyd, tcpsvd, udpsvd, nc -e, ftpd, httpd, crond, sv, runsv, runsvdir (e `sh -c`/`bash -c` sem aspas). Correção mínima, em `leitura_do_segmento`: na troca, varrer antes as palavras originais, `if prog in ("busybox", "toybox") and ...: self.atualizacao(palavras)` e só então trocar (o `toybox` ganha a varredura que o `busybox` já tinha). Teste: as entradas de S19 com rc 2. Dono: tech-lead.

**A7.** Mesma família do A6, mas já aberta na base: a guarda não modela os applets lançadores, então a carga atrás deles não é lida. Correção mínima: na troca, se o applet não está em `LANCADORES` de `hooks/_comum.py` nem em `SHELLS`/`INTERPRETES`/`ENVOLVEDORES` e não é programa conhecido da guarda, recusar como `LANCADORES_RECUSADOS` (os 32 applets do A6). Dono: tech-lead; não bloqueia esta entrega (não é regressão).

**A3.** Sem mudança desde `6a3e3983`.

## Sondas
- S19 · Bash `busybox linux64 forge-atualizar`, `busybox setarch x86_64 forge atualizar`, `busybox ash -c 'forge atualizar'`, `/bin/busybox watch forge-atualizar`, forge:tech-lead, projeto · espera: rc 2 (como na origin/develop) · obtido: rc 0 no head, rc 2 na base
- S20 · agentes, sessão no clone (`.forge/config.json` da raiz `{"teto_agentes": 5}`), pasta na worktree com `{"teto_agentes": 1, "piso_memoria_gb": 999}` e depois `{` · espera: o mais estrito ou a recusa (só aperta) · obtido: base `1 999` e `JSONDecodeError` (recusa); head `5 2.0` nos dois

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: executor de fixtures da suíte sobre os hooks da `origin/develop` (cópia por `git archive`) e do head, 10 977 entradas por lado; `tests/catraca.py --modo regras` (duas linhas: 36→37 e mudança em `hooks/conformidade.py`); testes do diff (23 OK). Lacunas: busybox e toybox fora do PATH (sondas só no analisador); suíte inteira não rodada localmente; CI do head não citável.
