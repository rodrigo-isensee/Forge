---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: e25f079b9834ba470ac8ccda65e5ad678a426aaa
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (lote B, destino opaco, revalidação da volta U4)

Revalidação por delta (`forge-check parecer delta`), intervalo `e8c459de..e25f079b`. No domínio: `hooks/conformidade.py` (+164/-3: U4, `valores_da_palavra`, `valores_do_corpo`, `valores_da_variavel`, `corpo_da_funcao`, `resto_colado`, `valor_calculado`, `na_lista_positiva`, `CORPO_POSITIVO` com `--short`, `--abbrev-ref`, `true`, `false` e `:`), `docs/hooks.md` e as fixtures `opaco-*`. Fora do domínio: mutantes O83 a O98, `tests/test_hook_destino_opaco.py` e o índice de fixtures. Etapa E1.280, instância que não fez a entrega. Parecer anterior: `e8c459de`, reprovado (A1 e A2 bloqueantes, A3 recomendado).

## Gatilhos
`R-SEGURANCA`: hook de guarda (`conformidade`) que analisa entrada livre (linha de Bash) para proteger o `.git` (`config`, `hooks/`, marca da sessão). Bloqueio por `R-CONFORMIDADE`.

## Achados
- A4 (bloqueante) hooks/conformidade.py:561 · U4 trata a variável sem nome= na linha como do ambiente, mas o bash a grava: read < arq e "$REPLY", mapfile -t e "$MAPFILE", [[ =~ ]] e "$BASH_REMATCH", getopts e "$OPTARG" gravam .git/config com rc 0. Resto da A1 (R-CONFORMIDADE)
- A5 (recomendado) hooks/conformidade.py:1345 · Resto com barra que sobe (/../config) depois de opaco dentro do .git libera: "$(mktemp -u -p .git)"/../config e TMPDIR=.git com "$(mktemp -u)"/../config gravam .git/config. Já na develop f4b0c2ae; fora do texto da A9 (sem resto): cartão novo

## Sondas
- S1 · read < l2; echo a > "$REPLY" (l2 contém .git/config; projeto, tech-lead) · espera: 2 · obtido: 0
- S2 · read < l2; cp x "$REPLY" · espera: 2 · obtido: 0
- S3 · read < l2; echo a | tee "$REPLY" · espera: 2 · obtido: 0
- S4 · read < l3; install -m 755 x "$REPLY" (l3 contém .git/hooks/pre-push) · espera: 2 · obtido: 0
- S5 · read < l2; echo a > "${REPLY}" · espera: 2 · obtido: 0
- S6 · mapfile -t < l2; echo a > "$MAPFILE" · espera: 2 · obtido: 0
- S7 · [[ $(cat l2) =~ .+ ]]; echo a > "$BASH_REMATCH" · espera: 2 · obtido: 0
- S8 · getopts a: o -a .g""it/config; echo a > "$OPTARG" · espera: 2 · obtido: 0
- S9 · read < l2; echo a > "$REPLY" (worktree do projeto) · espera: 2 · obtido: 0

## Detalhe dos achados
Como as sondas rodaram: `tests/test_oraculo_v047.py` como biblioteca (`C`, `executar`, `em_paralelo`), sem editá-lo, num script no meu rascunho, com dois arquivos a mais no repositório do caso (`l2` com `.git/config`, `l3` com `.git/hooks/pre-push`). O "espera" é o do bash (`printf %s <destino>` depois do prefixo da linha, no repositório temporário); o "obtido" é o rc do hook no head `e25f079b`, papel `forge:tech-lead`, projeto em `melhoria/x`. S1 a S9 dão 0 também em `e8c459de` e na develop `f4b0c2ae`: o furo é anterior, mas é o que a A9 e a correção da A1 prometem fechar. No clone do Forge com papel de lista (`aq`), S1 recusa pela gramática de leitura.

**A4 · variável que o próprio bash grava (dimensão D2d nova; resto da A1).**
- Evidência: `hooks/conformidade.py:550-561`. `valores_da_variavel` só recusa a variável que aparece solta na linha (`for d`, `read d`) ou que tem mais de uma atribuição; sem `nome=` na linha, ela vale `SEM_VALOR` (ambiente), e `valor_no_git` (`:613`) troca `SEM_VALOR` sozinho num componente por `_`, que nunca é o `.git`. O bash grava variáveis sem que o nome apareça: `read` sem nome grava `REPLY`; `mapfile` e `readarray` sem nome, `MAPFILE`; `[[ … =~ … ]]`, `BASH_REMATCH`; `getopts`, `OPTARG`; `select`, `REPLY`; `cd`, `pushd` e `popd`, `PWD`, `OLDPWD` e `DIRSTACK`; e todo comando, `_` (este já recusa por `construcao_nao_modelada`).
- Caminho de ataque: o da A1. Um agente de qualquer papel, levado por injeção num arquivo ou numa saída de ferramenta, grava `.git/config` (a `R-VERIFY` cai com `core.hooksPath`; `core.fsmonitor` roda código em todo `git status`) ou `.git/hooks/pre-push` com o caminho num arquivo comum (o Write grava `l2` sem restrição) e `read < l2; echo '…' > "$REPLY"`. É o `cat` de arquivo da A1 (S10 do parecer anterior), em forma de variável.
- Por que é bloqueante: requisito do plano provado como não cumprido (`R-REVIEW`). A correção da A1 pede que o destino opaco libere só quando o hook sabe o valor, e o próprio texto da U4 em `docs/hooks.md` diz que o destino só passa com o valor que o hook calcula. O valor de `REPLY` vem do arquivo, que o hook não lê. Não é critério novo: é a mesma porta da A1 por outro caminho.
- Correção mínima (lista positiva, sem tocar no resto da U4): a variável sem `nome=` na linha vale `SEM_VALOR` só se o nome **não** for dos que o bash grava. Lista inteira dos que o bash grava durante a execução (manual do bash, "Shell Variables"): `_`, `REPLY`, `MAPFILE`, `BASH_REMATCH`, `OPTARG`, `OPTIND`, `PWD`, `OLDPWD`, `DIRSTACK`, `COPROC`, `BASH_ARGV`, `BASH_ARGV0`, `BASH_ARGC`, `BASH_COMMAND`, `BASH_SOURCE`, `BASH_LINENO`, `FUNCNAME`, `PIPESTATUS`, `READLINE_LINE`, `READLINE_POINT`, `READLINE_MARK`, `COMP_WORDS`, `COMP_CWORD`, `COMP_LINE`, `COMP_POINT`, `COMPREPLY`, `BASH_EXECUTION_STRING`, `EPOCHREALTIME`, `EPOCHSECONDS`, `RANDOM`, `SRANDOM`, `LINENO`, `SECONDS`. Com esses nomes, `valores_da_variavel` devolve `None` (recusa com a mensagem da U4). O nome que aparece como argumento de `read`, `mapfile`, `readarray`, `getopts`, `select` ou `printf -v` já recusa pela busca solta. Fixtures que bloqueiam: S1 a S9. Mutante: `REPLY` fora da lista. Legítimos que seguem: `"$TMPDIR"/x`, `"$HOME"/x`, `d=docs; echo a > "$d"/n.md`. Esforço: P. Dono: tech-lead (autor do lote B).

**A5 · resto com barra que sobe (recomendado; dimensão D4 nova, fora do lote).**
- Evidência: `hooks/conformidade.py:1345` (`resto_no_git`). O resto `/../config` depois de uma parte opaca não é lido como saída do diretório do opaco. Sondas (todas rc 0, esperado 2 pelo bash): `echo a > "$(mktemp -u -p .git)"/../config`; `export TMPDIR=.git; echo a > "$(mktemp -u)"/../config`; o mesmo com `cp x`, com `install -m 755 x …/../hooks/pre-push`, com `TMPDIR=.g''it` e com `TMPDIR=.git/hooks`. Controles livres e corretos: `"$(pwd)"/../x`, `"$(mktemp -u)"/../x`.
- Por que não bloqueia este lote: dá 0 igual em `e8c459de` e na develop `f4b0c2ae` (sem regressão), e o texto da A9 é o destino opaco **sem resto**. O resto com barra é da regra antiga, que `docs/hooks.md` declara cobrir ("com resto depois de `/`, vale o `resto_no_git`"), e a sonda mostra que não cobre o `..`. O caminho de ataque é o da A4, com a citação do `.git` à vista na linha.
- Correção mínima (cartão novo, levado ao usuário pelo Jarvis para decidir se entra neste pedido, `R-DECISAO`): no `resto_no_git`, o resto com componente `..` depois de uma parte opaca recusa, salvo quando o opaco é da lista positiva que não depende do ambiente (`git rev-parse --show-toplevel`, `pwd` sem `cd` na linha). `mktemp` com `-p`, `--tmpdir` ou `TMPDIR` atribuído na linha não entra na exceção. Esforço: P. Dono: tech-lead.

### O que foi conferido e está correto
- **A1 (U4), fora o resto da A4:** a lista positiva fecha o que o parecer anterior provou. `printf` com formato, `tr`, `sed`, `rev`, `base64`, `cat` e o aninhado recusam; `printf "%s" .g it`, `printf %s .g'i't`, `echo "$d"t` com `d=.gi`, função `f(){ echo .g; }` com resto colado, `echo` redefinido como função e `"$(echo "$(echo .git)")"` recusam. `"$(date +.git)"`, `"$(git rev-parse --short --git-dir)"` e `--abbrev-ref --git-common-dir` recusam (a citação vence a lista positiva, `na_lista_positiva`). `: ${d:=.git}; … "$d"/config` recusa.
- **A2 (resto colado):** `"$(echo .g)""$(echo it/config)"`, `"$(echo .g)$(echo it)"/config` e `"$(f)it/config"` recusam. `resto_colado` passa o caminho inteiro pela U4.
- **A3:** `na_lista_positiva` exclui o `mktemp -p .git` e o `--tmpdir=.git…` da lista positiva, também no U3 (`origem_do_git_no_opaco`).
- **Orçamento:** `TETO_DE_VALORES` (64 combinações) e a profundidade 4 de `valores_da_palavra` e `valores_do_corpo` devolvem `None`, que recusa (falha fechada). As regex novas (`PALAVRA_DO_CORPO`, `LITERAL`, `VARIAVEL_DO_VALOR`) não dependem de falha com alternância ambígua; `corpo_da_funcao` usa `[^{}]*` e `[^()]*`.
- **Falsos positivos vistos (do lado seguro):** `"$(echo .g*)"/config` recusa pela regra antiga "lido como `.git`"; `"$(true)"/../.git/config` recusa (o bash daria `/.git/config`, fora do repositório).
- **Sem afrouxar:** o diff não remove recusa; `CORPO_POSITIVO` ganhou `--short`, `--abbrev-ref`, `true`, `false` e `:`, cuja saída não é o `.git` sem citação, e a citação no corpo recusa antes.
- **Oráculo (EXT-1):** `tests/test_oraculo_v047.py` sem commit no intervalo (`git log e8c459de..e25f079b -- tests/test_oraculo_v047.py` vazio). Local: `python3 -m unittest tests.test_oraculo_v047 tests.test_hook_destino_opaco tests.test_conformidade_opaco` deu 9 testes OK em 236 s.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Suíte inteira: **sem CI no head**. `gh api …/commits/e25f079b…/check-runs` devolve `total_count` 0 e a branch não tem PR (o brief diz "sem PR"). Rodei só o oráculo e os módulos da entrega, citados acima. Quando houver PR, o portão pede o CI verde no head da revalidação.

Faltaram no ambiente: gitleaks, Semgrep, osv-scanner, zizmor e actionlint (`R-CUSTO`, não instalo). A entrega não traz segredo, dependência nem workflow; a análise foi manual e por sonda.
