---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-conformidade
commit: bdbdc257dd492ee2ec6f79af7614b3a5d82e57e2
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (E1.15, revalidação das guardas da conformidade no clone, volta 3)

Delta lido (`forge-check parecer delta`): `848dd5ec..bdbdc257`, no domínio `hooks/conformidade.py` (catálogo `DESTINOS`, `com_valor`, `pastas_da_troca`, `alvos_do_tar`, `alvos_do_cpio`, `alvos_do_unzip`, `alvos_do_7z`, `EXTRATORES`, applet do `toybox` em `:2292`), `docs/hooks.md` (seção "Estado e expiração"), `tests/test_conformidade_verde.py` (`test_opcoes_do_catalogo_recusam`, `test_opcoes_do_catalogo_fora_do_estado_seguem_livres`, `CatalogoDosDestinos`); mutantes e changelog fora. Rodada anterior (A3, A5, S9 a S15) no git, em `848dd5ec`.

Gatilhos: hook de conformidade (controle de escrita), estado do hook agentes (teto, R-TETO), falha fechada.

Estado dos achados anteriores:
- A5: fechado. S15 refeita: as quatro formas com rc 2 para tech-lead e jarvis (S16). Vizinhas com rc 2: `7z X`, `-W<pasta>`, `-Sdel`, `7za`, `/usr/bin/toybox tar`, `toybox unzip -d`, `busybox 7z -O`, `bsdtar --cd=`, `--cd` antes do `-f`, `bsdtar -s '|^|...|'`, `--transform` com `./`, com duas expressões por `;`, com flag `x` e com `\/` escapado, `--one-top-level=` absoluto, antes do `-x`, abreviado (`--one-top=`) e relativo após `cd docs` (S17). Estado intacto ao fim.
- A3: segue recomendado (decisão do dono, sandbox), agora com a família "destino vindo do conteúdo do arquivo" (abaixo).

Sobre `7z x -spf` e `tar -P` (abertos sem remendo): entram no A3, não bloqueiam. O destino sai dos nomes gravados dentro do arquivo, que o analisador estático não lê; é o mesmo limite do caminho montado em tempo de execução por interpretador, já registrado em `docs/hooks.md`. A família é maior que as duas opções: `cpio -i` sem `--no-absolute-filenames` honra nome absoluto por padrão e `unzip -:` aceita `../`, ambos com rc 0 hoje (S18). Recusar `-P`/`--absolute-names`/`-spf` taparia só parte da família, e o ganho para o subagente é o mesmo do `sort -o`, que já passa. A saída que fecha a classe inteira é a do A3: o sandbox do Bash nega escrita em `<diretório comum do git>/forge/` e em `.forge/config.json` da raiz da sessão.

`7Z` (nome do programa em caixa alta) passa com rc 0, mas não há binário com esse nome no Linux: sem caminho de ataque, sem achado.

Testes do diff: `CatalogoDosDestinos` e `EstadoDoAgentesNoClone`, 14 OK localmente (GNU tar 1.35 no PATH, sem pulo). Suíte inteira: só no CI (brief sem suíte local); CI do head não citável (sem PR).

## Achados
- A3 (recomendado) hooks/conformidade.py:2374 · Lista negativa não fecha a família: sort -o, curl -o, wget -O, gzip, zip -m, patch -o, split, sqlite3, git -C init, dpkg-deb -x, ar x, pax -r, interpretador e destino vindo do arquivo (tar -P, 7z -spf, cpio -i absoluto, unzip -:) gravam no estado com rc 0. Saída: sandbox (dono).

## Detalhe dos achados
**A3.** Critério sem mudança; a evidência ganha a família do destino vindo do conteúdo do arquivo: `tar -xPf`, `tar --absolute-names`, `bsdtar -xPf`, `7z x -spf`/`-spf2`, `cpio -idm` com nome absoluto e `unzip -:` com `../`. Caminho: o subagente cria um arquivo cujo membro é `<clone>/.git/forge/run/agentes.json` (ou `../`) e o extrai de uma pasta livre; troca ou apaga o `agentes.json` e burla o R-TETO. Severidade: média (ator interno, sem ganho fora da máquina). Correção mínima: negação de escrita no sandbox do Bash para `<diretório comum do git>/forge/` e `.forge/config.json` da raiz da sessão; decisão do usuário, levada pelo Jarvis (`R-DECISAO`). Paliativo opcional, se o dono não quiser o sandbox: recusar no clone `-P`/`--absolute-names` (tar, bsdtar), `-spf`/`-spf2` (7z, sem caixa), `-:` (unzip) e `cpio -i`/`-p` sem `--no-absolute-filenames`. Dono: usuário (decisão), devops-engineer (configuração) ou tech-lead (paliativo).

## Sondas
- S16 · Bash `7z x docs/a.7z -O.git/forge/run`, `7z a docs/a.7z .git/forge/run/agentes.json -SDEL`, `bsdtar -xf docs/a.tar --cd .git/forge/run`, `toybox tar -xf docs/a.tar -C .git/forge/run` (S15 refeita), tech-lead e jarvis · espera: rc 2 · obtido: rc 2
- S17 · Bash `7z x docs/a.7z -W.git/forge/run`, `bsdtar -x --cd .git/forge -f docs/a.tar`, `tar -xf docs/a.tar --transform='s,a,b,;s,^,.git/forge/,'`, `tar -x --file=docs/a.tar --one-top=.git/forge`, `cd docs && tar -xf a.tar --one-top-level=../.git/forge` · espera: rc 2 · obtido: rc 2
- S18 · Bash `7z x docs/a.7z -spf`, `tar -xPf docs/a.tar`, `tar -xf docs/a.tar --absolute-names`, `bsdtar -xPf docs/a.tar`, `cpio -idm < docs/a.cpio`, `unzip -: docs/a.zip` (A3) · espera: rc 2 se paliativo; A3 pede sandbox · obtido: rc 0

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum (A3 é recomendado e aguarda decisão do dono). Ferramentas: sondas locais no hook pela fixture `CloneDoForge` (clone temporário), testes do diff (14 OK). Lacunas: 7z, bsdtar, toybox e cpio fora do PATH (sondas só no analisador; o comportamento de `-spf`, `-P`, `cpio` e `unzip -:` vem da ajuda de cada programa). Suíte inteira não rodada localmente; CI do head não citável.
