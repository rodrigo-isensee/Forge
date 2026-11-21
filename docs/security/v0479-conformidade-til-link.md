---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-til-link
commit: 2acfe2102f93ac66e2c86d572df67347e0963dca
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-conformidade-til-link (v0478 E80.10, terceira revalidação)

Delta lido (`forge-check parecer delta`): `9451e78c..2acfe210`. No domínio estão `hooks/conformidade.py` (`EM_VIGOR_NO_TEXTO` :3909, `FECHADO_NA_LINHA` :3899 e o ramo `INTERPRETES` :2432), as fixtures novas `tilsubst-*` e `linkcopia-python-m-*` e o texto de `docs/hooks.md`. A rodada anterior está no git (e9d0b2b4).

## Gatilhos
Gatilhos: controle do Forge (hook `conformidade`), escrita em arquivo em vigor e na pasta de controle

## Resultado
**A mudança só aperta.** Rodei 61 sondas com o mesmo fixture no hook da base (9451e78c) e no do head. Nenhuma passou de recusa (2) para liberação (0). Foram 32 de 0 para 2, 7 ficaram em 2 e 22 ficaram em 0. As três mudanças só acrescentam recusa: a regex casa mais nomes, o `FECHADO_NA_LINHA` ganhou uma alternativa e a isenção do `-m` ficou menor. O corpus legítimo continua liberando: `cat .forge/config.json`, `git -C x log`, `for f in .github/workflows/*.yml; …`, `perl -Mstrict -e … .githooks/pre-push`, `python3 -m tarfile -l|-c`, `python3 -m zipfile -l`, `python3 -m json.tool .forge/config.json`, `python3 -c "print(1)"`, `python3 x.py`, `git log … > $TMPDIR/h.txt` e `python3 -m tarfile -e … $TMPDIR/t`. Os testes `test_fixtures_do_til_em_substituicao`, `test_fixtures_do_link_por_copia` e `test_fixtures_do_controle_so_jarvis` passam no head (3 OK).

Estado dos achados anteriores:
- **A4: corrigido.** As sondas S1 a S3 da rodada anterior recusam no head. Também recusam `./.forge`, `".fo"rge`, `mapfile`, `perl -e` e `node -e` por `$d`. Aceito o desvio da minha sugestão: com `\.forge` inteiro no lugar de `.forge/(versao|config.json|run)`, a regra fecha mais, e as linhas S1 e S2 só trazem `.forge`. O `.forge-contrib`, o `.github`, o `.githooks` e o `.gitignore` seguem livres.
- **A5: corrigido em parte.** O `python -m tarfile|zipfile -e|--extract` recusa nas duas regras (S4, a parte python da S5, `-mtarfile`, `-I -m`, `-X utf8 -m`, `-ve`, `--ex`, `--e`, `env python3`, `x=1 python3`, `/usr/bin/python3.12`, `'tarfile'` e `tar\file`). Seguem abertos o restante da correção mínima e o `pypy` na linha que cita arquivo em vigor. Veja A5 e S1 a S3.
- **A6:** aguarda a DECISÃO DO DONO (`R-DECISAO`) e não foi tratado nesta volta. Não é achado novo.

A suíte inteira não rodou. Não há PR nem CI para este head, então a suíte fica com o CI.

## Achados
- A5 (bloqueante) hooks/conformidade.py:3899 · resto da correção mínima: `unrar x` e `unsquashfs` dão 0 na linha que cita `~/.claude` e na que cita o controle, e `pypy3 -m tarfile|zipfile -e` e `pypy3 -c` dão 0 na linha em vigor (`pypy` fora de `INTERPRETES`, :72). Ver S1 a S3.
- A6 (bloqueante) hooks/conformidade.py:3910 · o git que restaura link segue aberto e aguarda a DECISÃO DO DONO (`R-DECISAO`). Não foi tratado nesta volta e não é achado novo.

## Sondas
- S1 · fixture tilsubst-for-bloqueia: `d=~/.claude; unrar x ~/l.rar $d/` e `d=~/.claude; unsquashfs -f -d $d ~/l.sqfs` · espera: código 2 · obtido: código 0 (base e head)
- S2 · fixture linkcopia-7z-bloqueia: `unrar x ~/l.rar ~/.forge-contrib/wt/ && echo x >> ~/.forge-contrib/wt/q/docs/pedidos/v1.md` (também `unsquashfs -f -d ~/.forge-contrib/wt/ ~/l.sqfs && …`) · espera: código 2 · obtido: código 0 (base e head)
- S3 · fixture tilsubst-for-bloqueia: `pypy3 -m tarfile -e ~/l.tar ~/.claude/`, `pypy -m zipfile -e ~/l.zip .git/` e `d=~/.claude; pypy3 -c "open('$d/settings.json','a')"` · espera: código 2 · obtido: código 0 (base e head). Na linha do controle, `pypy3 -m tarfile -e …` já dá 2.

## Detalhe dos achados
**A5 (resto).** Evidência: `hooks/conformidade.py:3899`. O `FECHADO_NA_LINHA` não traz `unrar`, `rar`, `unsquashfs`, `bsdcpio`, `unar` nem `aunpack`. Em `:72`, o `INTERPRETES` (`python|perl|ruby`, `node`, `php`, `deno`, `bun`) não traz `pypy`. Por isso, na linha que cita arquivo em vigor, o `pypy` não cai no ramo de :2432. O `docs/hooks.md` diz "todo extrator de pacote no modo que extrai", e hoje isso não é verdade. Caminho de ataque: é o mesmo da A2 e da A5 anteriores. Um papel que não é o jarvis, ou um conteúdo injetado, extrai um pacote com o link para `~/.forge-contrib` ou para `~/.claude/` e grava pelo link na mesma linha. O `unsquashfs` vem com o `squashfs-tools`, dependência do `snapd` no Ubuntu, então existe em boa parte das estações. Severidade: alta onde o extrator existe, porque a pasta de controle (`DECISÃO DO DONO`) fica sem `denyWrite` do sandbox (A14). Nesta estação, `unrar`, `unsquashfs`, `unar` e `pypy` não estão instalados, por isso não houve laboratório de link.

Correção mínima, a lista inteira:
1. Em `FECHADO_NA_LINHA`, acrescentar `unrar` e `rar` com `x` ou `e`, `unsquashfs` (qualquer forma), `bsdcpio` com `-i` ou `-p`, `unar` e `aunpack`.
2. Pôr `pypy` em `INTERPRETES` (`(python|pypy|perl|ruby)…`).
3. Fixtures novas para S1 a S3 e, como legítimo, `unrar l` e `unsquashfs -l`.

A alternativa é pôr esse resto no mesmo pedido de aceite do dono que a A6. Esforço: P. Dono: o autor do hook (o tech-lead da E80.9).

**A6.** A evidência e a correção estão no parecer e9d0b2b4 e não mudaram. Aguarda o dono.

## Riscos aceitos e ferramentas
Não há risco aceito. As sondas rodaram pelo `Fixture` e pelo `rodar` de `tests/test_hooks.py`, sobre a base (`git archive 9451e78c`) e sobre o head. Lacunas: não há CI para o head (sem PR), a suíte inteira não rodou, e `unrar`, `unsquashfs` e `pypy` estão ausentes, por isso não houve laboratório de link.
