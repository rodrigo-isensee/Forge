---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-conformidade
commit: 848dd5ecd7bc18a87f957a26aec0e4bd1e88f51c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (E1.11, revalidação das guardas da conformidade no clone)

Delta lido (`forge-check parecer delta`): `b3312958..848dd5ec`, no domínio `hooks/agentes.py` (`pasta_da_config`, `ler_config`), `hooks/conformidade.py` (`ler_opcoes`, `alvos_do_tar`, `alvos_do_cpio`, `alvos_do_unzip`, `alvos_do_7z`, `EXTRATORES`, applet do `busybox`), `docs/hooks.md` (seção "Estado e expiração"), `tests/test_conformidade_verde.py`; mutantes e changelog fora. Rodada anterior (A1 a A4, S9 a S13) no git, em `b3312958`.

Gatilhos: hook de conformidade (controle de escrita), estado do hook agentes (teto, R-TETO), falha fechada.

Estado dos achados anteriores:
- A1: fechado. `ler_config` zera `hook._config` antes de trocar a raiz e `pasta_da_config` basta a sessão no clone (`hooks/agentes.py:160-177`). S9 refeita pelo teste `test_versao_na_worktree_nao_deixa_o_config_dela_no_cache`: `2 2.0` no teto e no piso, também pelo `h.config()` depois da leitura.
- A2: fechado. S10 a S13 com rc 2 para tech-lead e jarvis; variantes extras com rc 2: `unzip -qod`, `tar -x -f ... --directory <pasta>`, `nice tar`, `env tar`, `timeout 5 unzip`, `busybox cpio -D`, `/bin/busybox tar`.
- A3: sem mudança, segue recomendado (decisão do dono). A lista do autor entra aqui (ver abaixo).
- A4: fechado. `bsdtar -C`, `busybox tar -C` e `7z x -o<pasta>` com rc 2. Resíduos nas formas novas desse catálogo viram A5 (recomendado).

Sobre a lista do autor (`sort -o`, `curl -o`, `wget -O`, `gzip`, `zip -m`, `patch -o`, `split`, `sqlite3`, `git -C .git/forge/run init`): confirmei rc 0 em todos, já na base. É a classe do A3: um analisador de lista negativa não fecha a família "programa que grava por opção", e qualquer um desses dá ao subagente o mesmo ganho que o `unzip -d` dava. Não bloqueiam este item: o escopo (E1, AGENTES-JSON-SEM-GUARDA) era fechar as formas apontadas, e elas fecharam; bloquear por mais um nome da lista não muda a postura enquanto o resto da família passa. A saída estrutural segue a do A3: negar a escrita em `.git/forge/` e `.forge/config.json` no sandbox do Bash, decisão do dono (`R-DECISAO`). O mesmo vale para `dpkg-deb -x`, `ar x`, `pax -r -s` e `tar --transform` (este último também cai no limite da raiz como ponto de partida, já registrado em `docs/hooks.md`).

Testes do diff (`EstadoDoAgentesNoClone`, `ConfigDaWorktreeNoClone`, `ConfigDoTetoNoClone`): 18 OK localmente. Suíte inteira: só no CI (brief sem suíte local); CI do head não citável (sem PR).

## Achados
- A3 (recomendado) hooks/conformidade.py:2312 · Lista negativa não fecha a família: sort -o, curl -o, wget -O, gzip, zip -m, patch -o, split, sqlite3, git -C init, dpkg-deb -x, ar x, pax -r e interpretador com caminho montado gravam no estado com rc 0. Saída estrutural: sandbox nega escrita em .git/forge/ (dono).
- A5 (recomendado) hooks/conformidade.py:1136 · alvos_do_7z casa só -o e -sdel em minúscula, mas o 7-Zip lê as chaves sem caixa: 7z x -O<pasta> e -SDEL passam com rc 0; bsdtar --cd <pasta> e toybox tar também. Correção: casefold nas chaves do 7z, --cd no bsdtar, toybox como o busybox.

## Detalhe dos achados
**A3.** Sem mudança de critério desde a rodada anterior; a lista do autor e as quatro formas novas (`dpkg-deb -x`, `ar x` na pasta do estado, `pax -r -s`, `tar --transform`) são a evidência atual. Caminho: subagente troca ou apaga `agentes.json` e burla o R-TETO. Severidade: média (ator interno, sem ganho fora da máquina). Correção mínima: negação de escrita no sandbox do Bash para `<diretório comum do git>/forge/` e `.forge/config.json` da raiz da sessão; decisão do usuário, levada pelo Jarvis. Dono: usuário (decisão), devops-engineer (configuração).

**A5.** Evidência: `hooks/conformidade.py:1136-1137` (`a.startswith("-o")`, `"-sdel" in args`), `:1143` (`EXTRATORES` sem `toybox`), `:2230` (só `busybox` repassa ao applet); `alvos_do_tar` não conhece o `--cd` do `bsdtar` (sinônimo de `-C`). Caminho: o do A2, com a caixa da chave trocada. 7z, bsdtar e toybox ausentes do PATH desta máquina: o rc 0 é do hook; a leitura sem caixa das chaves é do 7-Zip (parser de linha de comando sem caixa). Severidade: baixa (mesmo ganho que o `sort -o` do A3, que já passa). Correção mínima: comparar as chaves do 7z com `lower()`; `"cd"` nas longas de pasta do `bsdtar`; `toybox` como o `busybox` em `:2230`. Teste: as quatro formas em `test_extrator_e_tar_por_opcao_recusam`. Esforço: P. Dono: tech-lead.

## Sondas
- S9 · teste `ConfigDaWorktreeNoClone.test_versao_na_worktree_nao_deixa_o_config_dela_no_cache` (`.forge/versao` na worktree, sessão no clone) · espera: 2 2.0 · obtido: 2 2.0
- S10 · Bash `unzip -o docs/a.zip -d .git/forge/run` no clone, tech-lead e jarvis · espera: rc 2 · obtido: rc 2
- S11 · Bash `cd .git/forge/run && cpio -idm < ../../../docs/a.cpio` · espera: rc 2 · obtido: rc 2
- S12 · Bash `tar --to-command='rm .git/forge/run/agentes.json' -xf docs/a.tar` · espera: rc 2 · obtido: rc 2
- S13 · Bash `tar -xf docs/a.tar --checkpoint=1 --checkpoint-action=exec='rm .git/forge/run/agentes.json'` · espera: rc 2 · obtido: rc 2
- S14 · Bash `bsdtar -xf docs/a.tar -C .git/forge/run`, `busybox tar -xf docs/a.tar -C .git/forge/run`, `7z x docs/a.7z -o.git/forge/run` (A4) · espera: rc 2 · obtido: rc 2
- S15 · Bash `7z x docs/a.7z -O.git/forge/run`, `7z a docs/a.7z .git/forge/run/agentes.json -SDEL`, `bsdtar -xf docs/a.tar --cd .git/forge/run`, `toybox tar -xf docs/a.tar -C .git/forge/run` (A5) · espera: rc 2 · obtido: rc 0

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum (A3 e A5 são recomendados; o A3 aguarda decisão do dono). Ferramentas: sondas locais no hook pela fixture `CloneDoForge` (clone temporário), testes do diff (18 OK). Lacunas: 7z, bsdtar, toybox, pax e sqlite3 fora do PATH (sondas só no analisador). Suíte inteira não rodada localmente; CI do head não citável.
