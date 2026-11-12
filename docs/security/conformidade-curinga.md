---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/conformidade-curinga
commit: 9bd8340486854e946ad2bd810074a6dfaaf8e778
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v046 (E20.37, conformidade-curinga, volta 4 do furo A11)

Diff revisado: `c340c322..9bd83404` (3 commits: `3f9ed613`, `c46a684a`, `9bd83404`), lido numa worktree destacada. No domínio: `hooks/conformidade.py` (`origens_do_rev_parse` e `origem_so_generica`, novo) e as 8 fixtures `gitcomum-v3-*` novas. A spec de mutantes `-5` (G27 a G33) fica com o QA.

Veredito: **reprovado**. A volta 4 fecha as grafias citadas no A11 da E20.31: `c?nfig`, `[c]onfig`, `[!x]`, intervalos, `conf{i,}g`, `hook[s]/...`, por variável, `cp -l` e `cp -s`. Todas recusam, e o legítimo `HEA?` segue livre. O furo **não fechou**, porém, porque o hook expande o curinga com o glob do Python, e esse glob não lê a grafia do bash. Classe negada com `^` (`[^x]onfig`), classe POSIX (`[[:alpha:]]onfig`), equivalência e símbolo de ordenação (`[[=c=]]onfig`, `[[.c.]]onfig`) e `shopt -s nocaseglob` (`CONFI?`) casam nada no hook e casam `config` no bash. Nesses casos a origem se libera e o link físico grava no `.git/config` (A11 segue aberto, bloqueante). A volta não abriu caminho novo: tudo o que passa no head também passa na base `c340c322`. Um resíduo mais largo, que já existia, fica em cartão (A14): curinga num componente de pasta (`.g?t/config`) ou no nome de outro caminho protegido não é expandido na escrita nem no link.

## Gatilhos
`R-SEGURANCA`: controle do Forge (hook `conformidade`, guarda de link e de escrita em `.git/`), analisador de comando.

## Achados
- A11 (bloqueante) hooks/conformidade.py:1095 · segue aberto: o glob do Python não lê `[^x]`, `[[:alpha:]]`, `[[=c=]]`, `[[.c.]]` nem nocaseglob; `ln "$(git rev-parse --git-dir)"/[^x]onfig h` dá rc 0 e o link físico é o .git/config; também `cp -l`, `ln -s`, `cp -s`, por variável, `--git-common-dir` e `[^x]ooks/`
- A14 (recomendado) hooks/conformidade.py:1053 · já existia (base c340c322): curinga num componente de pasta ou no nome de outro protegido não é expandido; `ln .g?t/config h`, `ln -f x .g?t/config`, `cp x .g?t/config` e `cp x .forge/c?nfig.json` dão rc 0; cartão com prioridade

## Sondas
- S10 · ln "$(git rev-parse --git-dir)"/[^x]onfig h · espera: rc 2 R-CONFORMIDADE (.git/config) · obtido: rc 0, stderr vazio (head 9bd83404 e base); executado no bash, h tem o inode do .git/config
- S11 · ln "$(git rev-parse --git-dir)"/[[:alpha:]]onfig h · espera: rc 2 R-CONFORMIDADE (.git/config) · obtido: rc 0 (head); o mesmo com [[:lower:]], [[=c=]], [[.c.]], co[^x]fig; h tem o inode do .git/config
- S12 · shopt -s nocaseglob; ln "$(git rev-parse --git-dir)"/CONFI? h · espera: rc 2 R-CONFORMIDADE (.git/config) · obtido: rc 0 (head); h tem o inode do .git/config
- S13 · d=$(git rev-parse --git-dir); ln $d/[^x]onfig h · espera: rc 2 R-CONFORMIDADE (.git/config) · obtido: rc 0 (head); o mesmo com cp -l, ln -s, cp -s, --git-common-dir e --absolute-git-dir
- S14 · ln "$(git rev-parse --git-dir)"/[^x]ooks/pre-commit.sample h · espera: rc 2 R-CONFORMIDADE (.git/hooks/) · obtido: rc 0 (head)

## Detalhe dos achados
Método: o montador de `tests/test_hooks.py` (`Fixture.montar` e `rodar`), papel `forge:tech-lead`, projeto em `melhoria/x`. Cada comando foi rodado no hook e, depois, no bash do mesmo repositório temporário, para comparar o inode de `h` com o do `.git/config`. Comparei duas árvores: o head `9bd83404` e a base `c340c322`. Foram 60 casos distintos.
- Fecham no head (rc 2, eram rc 0 na base): `c?nfig`, `[c]onfig`, `co[!x]fig`, `[a-c]onfig`, `[c-c]onfig`, `[]c]onfig`, `c*g`, `*nfig`, `//c?nfig`, `../.git/c?nfig`, `../.git/[^x]onfig`, `conf{i,}g`, `hook?/pre-commit.sample` e duas origens no mesmo `ln` (14 casos). As grafias extglob (`@(config)`, `?(c)onfig`, `+(c)onfig`) já recusavam na base e seguem recusando (rc 2, pela regra genérica).
- Legítimos livres: `HEA?`, `[^x]EAD` e `[^x]orge` (o legítimo de `test_conformidade_verde` passa: 11 OK). `test_hook_git_comum` dá 1 OK em 11 s.
- Nenhum caminho novo: os 30 casos que passam no head (3 deles legítimos) também passam na base, e nenhum caso que recusava na base passa no head.

**A11 (alta, bloqueante; segue da E20.31, dimensão nova "dialeto do curinga: bash × Python").** Evidência: `hooks/conformidade.py:1095` expande o resto com `glob.glob`. O `fnmatch` do Python só nega com `!`, lê `[^x]` como "`^` ou `x`" e lê `[[:alpha:]]` como uma classe de caracteres literais seguida de `]`. Ele também não conhece `[[=c=]]`, `[[.c.]]` nem a opção `nocaseglob`. Assim, `origem_so_generica` (`hooks/conformidade.py:1080`) não acha nada específico e devolve `True` (`:1099`). O índice entra em `livres` (`:1078`), e `link_em_protegido` descarta o achado genérico (`:1060`). O bash expande essas grafias para `config`, e o link físico se cria (S10 a S13; S14 pega um arquivo de `.git/hooks/`). O caminho de ataque é o do A11 original: o agente barrado ao editar `.git/config` cria o link `h` e grava em `h` num comando seguinte, por exemplo para trocar `core.hooksPath` ou pôr `core.fsmonitor`. Bloqueia porque é o requisito desta volta ("curinga só libera se o glob não cair em regra específica") e está provado no bash.

Correção mínima, falha fechada, em `origem_so_generica`:
- resto com `[` não se libera, como as chaves (nenhum legítimo do corpus precisa de colchete numa origem de rev-parse);
- com só `?` e `*`, a comparação ignora maiúsculas: glob sobre os nomes em minúsculas, ou `fnmatch` com o nome e o padrão em minúsculas. Isso cobre `nocaseglob`.

`HEA?` e `forge-suite-Xverd?` seguem livres. Fixtures: S10, S11, S12, S13 e S14, mais `[[=c=]]`. Esforço P. Dono: tech-lead.

**A14 (alta, recomendado; já existia na base `c340c322`, fora do delta).** Evidência: `hooks/conformidade.py:1053` resolve as origens e os destinos de link pelo literal. `pastas_do_curinga` e `curinga_na_prova` (`:1022` a `:1033`) só expandem o curinga do nome, e só para a prova da suíte. Por isso, curinga num componente de pasta (`.g?t`, `.gi[t]`) ou no nome de outro caminho protegido não cai em regra nenhuma. O link passa rc 0 com `ln .g?t/config h`, `ln .gi[t]/config h`, `ln "$(git rev-parse --git-dir)"/../.g?t/config h`, `ln -f x .g?t/config`, `ln -sf x .gi[t]/config` e `cp -lf x .g?t/config`; no bash, `ln -f x .g?t/config` troca o `.git/config` por um link físico de `x`. A escrita também passa rc 0 com `cp x .g?t/config`, `mv x .g?t/config`, `echo a > .g?t/config`, `cp x .g?t/hooks/pre-commit.sample`, `cp x .forg?/config.json` e `cp x .forge/c?nfig.json`. O caminho de ataque é o mesmo do A11, sem `rev-parse` e mais curto. Não bloqueia esta volta porque não foi aberto por ela, está fora do delta e a correção é mais larga (todo caminho protegido, escrita e link). Mesmo critério do A13 na E20.31.

Correção mínima: em toda escrita e em todo operando de link com `CURINGA` em qualquer componente, expandir o caminho inteiro a partir da pasta (e do diretório comum, quando opaco), com a mesma falha fechada do A11 para `[`, chaves e maiúsculas, e conferir cada nome expandido com `caminho_barrado`. O que não expande para nada recusa se o literal, com o curinga trocado por qualquer caractere, puder cair em regra específica. Cartão com prioridade. Esforço M. Dono: tech-lead.

**Achados antigos (A12, A13, A4 a A10).** Não pioraram no delta. As linhas mudaram só pelo deslocamento do código.

## Riscos aceitos e ferramentas
Nenhum risco aceito. O portão é o CI do PR (bateria completa). Na máquina rodaram `python3 -m unittest tests.test_hook_git_comum` (1 OK) e `tests.test_conformidade_verde` (OK). Ferramentas usadas: `git worktree` destacada (head e base), o montador de fixtures e o bash, só em repositórios temporários. `gitleaks`, `semgrep`, `zizmor` e `actionlint` não rodaram: o delta não toca workflow nem segredo, e nada foi instalado (`R-CUSTO`).
