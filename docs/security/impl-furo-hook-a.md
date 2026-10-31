---
tipo: revisao-seguranca
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a2
commit: 5ccf07e8116b4f8bd7c7340460f4aeb9acdf8f29
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-furo-hook-a, branch a2

Etapa E1.3 do pedido `impl-furo-hook-a` (brief `impl-furo-hook-a-security-engineer-2`). Diff lido: `234dbe0..5ccf07e`. Modelo de ameaças: `~/.forge-contrib/docs/security/ameacas/furo-hook.md`, §4.2. Não sou o autor.

## Item entregue e M14
- **Item:** E2, A2 PARECER-LANCADOR (`hooks/parecer.py`, `analise_do_comando`).
- **M14 (decisão M14, `agents/tech-lead.md:19` na develop):** contam `hooks/parecer.py` (32+3) e `tests/test_hooks.py` (5): 40 linhas, abaixo de 150. Fixtures de `tests/hooks/`, `tests/fixtures/`, `tests/mutantes/`, `docs/hooks.md`, `changelog.d/` e o parecer ficam fora. Uma classe de comportamento em `hooks/` (o `parecer` lê o comando atrás do lançador), com corpus próprio (9 fixtures `parecer/`). **Cumpre.**
- A troca do oráculo `tests/fixtures/heredoc-volta-unica.json` (CO5, `parecer` de 0 para 2, sem o `nao_promete`) endurece e não afrouxa.

## Gatilhos
R-SEGURANCA, controles do Forge: o portão R-REVIEW do hook `parecer`.

## Achados
- A1 (recomendado) hooks/parecer.py:264 · `su -c` (da lista do C-A2-4) falta em OUTROS_LANCADORES, e `chronic`, `systemd-run` e `caffeinate` antes de `gh pr merge` com parecer reprovado saem 0. Cartão: comando fora das tabelas, numa linha com o PREFILTRO, recusa, em vez de lista.
- A2 (recomendado) hooks/parecer.py:616 · anterior à branch: chaves do bash escondem o merge do parecer (`{gh,pr} merge feature/x --merge` reprovado e `git {merge,feature/x}` na develop saem 0), e o conformidade no clone do Forge não as recusa. Item novo do modelo, ao dono.

## Detalhe dos achados
Sondas: cada uma monta a fixture pelo `Fixture`/`rodar` da própria worktree e roda o hook real (2 = recusa, 0 = passa). Nada rodou contra repositório real, rede ou produção.

**O que a branch fecha (todos os casos de abuso do §4.2 saem 2):** `timeout 60`, `env`, `nice`, `flock`, `ionice`, `parallel`, `watch`, `busybox`, `stdbuf`, `setsid`, `sudo -u`, `command`, `exec`, `time -p`, `nohup … &`, `env -S`, `sudo -s` e cadeias deles (`timeout --foreground 5 nohup env A=1 gh pr merge …`). Fecha também o `xargs` em todas as formas (`-r`, `-I{}`, `-a lista`, `--`, atrás de `timeout`), o `find` com `-exec`, `-execdir` e `-ok` (inclusive `/usr/bin/find`), e os mesmos casos com `git merge` e `git pull` na develop. Também saem 2 o nome do lançador entre aspas ou escapado (`"timeout"`, `\timeout`, `t\imeout`), o lançador dentro de `( )`, `{ ;}`, `if`, `$( )` e pipeline, e o `cd` de lançador (fixture própria). A contraprova `timeout 60 gh pr merge` com parecer aprovado sai 0. As fixtures do lote e o oráculo passam: `test_fixtures_do_lote_furo_hook_a` deu `OK` no HEAD revisado.

**A1.** Evidência: `hooks/parecer.py:264-265` lista `ionice`, `chrt`, `taskset`, `flock`, `unshare`, `script`, `watch`, `parallel`, `doas`, `busybox`, `expect` e `socat`. A lista do C-A2-4 tem também `su -c`. Sondas que saem 0 com parecer reprovado: `su -c 'gh pr merge …'`, `chronic gh pr merge …`, `caffeinate gh pr merge …` e `systemd-run --user gh pr merge …`. Caminho: a sessão, por erro ou por injeção, mescla atrás de um programa que roda outro e que o hook não conhece. O `su` pede senha e o Bash da sessão não tem terminal, então não há caminho realista. Os outros três dependem de o programa estar instalado e de uma escolha deliberada, a mesma classe de limite do N6 e do [B] de `docs/hooks.md`. Severidade baixa. Correção mínima (cartão, não esta branch): com o PREFILTRO na linha, a 1.ª palavra do comando simples que não é `gh`, `git`, `cd`, lançador de `LANCADORES` nem programa conhecido que só lê recusa R-REVIEW, falhando fechado, em vez de crescer a lista. Esforço M. Dono: tech-lead.

**A2.** Evidência: com a expansão de chaves do bash, `{gh,pr} merge feature/x --merge` vira `gh pr merge feature/x --merge`, e `{timeout,5} gh pr merge …`, `gh {pr,merge} …` e `git {merge,feature/x}` também saem 0 no `parecer`, com parecer reprovado ou sem parecer. O `analisar` recebe uma 1.ª palavra que não é `gh` nem `git`. No clone do Forge, o `conformidade` também libera essas linhas (sonda com a fixture `contrib-cwd-clone-sessao-do-forge-libera`), porque a rede da ADR 0011 (chaves com ação crítica) não vale lá. Na base `234dbe0` é igual: a branch não abre nem fecha isso. Caminho: contorno deliberado por injeção, que mescla com parecer reprovado no Forge. Severidade média, pelo ativo (R-REVIEW na develop do Forge), limitada por exigir intenção. Correção mínima: o `parecer` aplica `construcao_nao_modelada` (chaves, `$`, crase) a toda linha que casa o PREFILTRO, também no clone do Forge. Esforço P. É item novo, fora do lote, e vai ao dono como os N1 a N8 do modelo. Dono: tech-lead.

Dimensão nova para a matriz do modelo (§8, Mecanismo): **expansão do shell sem marcador ou fora do projeto** (chaves e glob). Ela aparece também nas branches a3, a4 e a5.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sondas locais pelo harness de fixtures e execução das fixtures do lote. `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` não estão no PATH (lacuna registrada; o diff não traz segredo, dependência nem workflow).
