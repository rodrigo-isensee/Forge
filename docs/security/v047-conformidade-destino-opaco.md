---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: 85043cc4008c8d1395412674e3aef71d77c2153e
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (lote B, destino opaco, revalidação da volta do lote B)

Revalidação por delta (`forge-check parecer delta`), intervalo `e25f079b..85043cc4`. No domínio: `hooks/conformidade.py` (`VARIAVEIS_DO_BASH` em `valores_da_variavel`; `na_lista_positiva(corpo, linha)` sem redefinição do comando como função, no U4 e no U3; a troca de `$(pwd)` por `$PWD` só sem `pwd(){…}`), `docs/hooks.md` e as fixtures `opaco-u4-rev2-*`, `opaco-u4-seg2-*` e `opaco-semresto-u3-mv-target-duas-vezes`. Fora do domínio: mutantes O99 a O104, O45, O55, `tests/test_hook_destino_opaco.py` e o índice de fixtures. Etapa E1.304, instância que não fez a entrega. Parecer anterior: `e25f079b`, reprovado (A4 bloqueante, A5 recomendado).

## Gatilhos
`R-SEGURANCA`: hook de guarda (`conformidade`) que analisa entrada livre (linha de Bash) para proteger o `.git` (`config`, `hooks/`, marca da sessão). Bloqueio por `R-CONFORMIDADE`.

## Achados
- A6 (bloqueante) hooks/conformidade.py:496 · Lista positiva confia no nome do comando, que a linha troca sem definir função: `. ./f.sh`, `source`, `hash -p`, `PATH=./bin`, alias e `GIT_WORK_TREE=.git` gravam .git/config com rc 0. Mesma porta da A1 do review E1.279 (R-CONFORMIDADE)
- A5 (recomendado) hooks/conformidade.py:1355 · Resto com barra que sobe (/../config) depois de opaco dentro do .git libera: "$(mktemp -u -p .git)"/../config e TMPDIR=.git com "$(mktemp -u)"/../config gravam .git/config. Já na develop f4b0c2ae; fora do texto da A9 (sem resto): cartão novo

## Sondas
- S10 · . ./f.sh; echo a > "$(date)" (f.sh: `date(){ echo .git/config; }`; projeto, tech-lead) · espera: 2 · obtido: 0
- S11 · source f.sh; echo a | tee "$(date)" · espera: 2 · obtido: 0
- S12 · . ./g.sh; cp config "$(date)" (g.sh: `date(){ echo .git; }`; U3) · espera: 2 · obtido: 0
- S13 · chmod +x d; hash -p ./d date; echo a > "$(date)" (d: script que imprime .git/config) · espera: 2 · obtido: 0
- S14 · chmod +x bin/date; PATH=./bin:$PATH; echo a > "$(date)" (bin/date: o mesmo script) · espera: 2 · obtido: 0
- S15 · três linhas: `shopt -s expand_aliases` / `alias date='echo .gi''t/config'` / `echo a > "$(date)"` · espera: 2 · obtido: 0
- S16 · export GIT_WORK_TREE=.git; cp config "$(git rev-parse --show-toplevel)" · espera: 2 · obtido: 0

## Detalhe dos achados
Como as sondas rodaram: `tests/test_oraculo_v047.py` como biblioteca (`C`, `executar`, `em_paralelo`), sem editá-lo, num script no meu rascunho, com arquivos a mais no repositório do caso (`f.sh`, `g.sh`, `d`, `bin/date`, `l2`, `l3`). O "espera" é o do bash (`printf %s <destino>` depois do prefixo da linha, no repositório temporário); o "obtido" é o rc do hook no head `85043cc4`, papel `forge:tech-lead`, projeto em `melhoria/x`.

**A4 · fechada.** S1 a S9 do parecer anterior dão 2 no head (`REPLY`, `MAPFILE`, `BASH_REMATCH`, `OPTARG`, `${REPLY}`, com `echo >`, `install`, `tee`, `cp` e na worktree). `VARIAVEIS_DO_BASH` (`hooks/conformidade.py:488`) traz a lista inteira pedida, e `valores_da_variavel` (`:562`) devolve `None` com esses nomes. Legítimos seguem: `echo a > "$TMPDIR"/x`, `echo a > "$(date +%F).log"` e `cp config "$(mktemp -d)"` dão 0.

**A1 do review E1.279 (função) · fechada na forma pedida.** `date(){ echo .gi""t/config; }`, `function true { … }` e `pwd(){ echo .git; }` com `cp config "$(pwd)"` recusam; `eval "da""te(){ … }"` recusa por outra regra (`chaves` com ação crítica); `cd .git; cp config "$(pwd)"` recusa.

**A6 · o comando da lista positiva trocado sem definição de função na linha (dimensão D2e nova: mecanismo de resolução do comando).**
- Evidência: `hooks/conformidade.py:496-500` (`na_lista_positiva`) só olha `corpo_da_funcao` na própria linha; `CORPO_POSITIVO` (`:415-417`) casa pelo nome (`date`, `pwd`, `true`, `mktemp`, `git rev-parse --show-toplevel`). No bash, o nome resolve por alias, função (também a carregada por `.` ou `source`), tabela de `hash` e `PATH`, e a saída de `git rev-parse --show-toplevel` segue `GIT_WORK_TREE`. Nenhum desses aparece como `nome(){` na linha.
- Caminho de ataque: o da A1 e da A4. Um agente de qualquer papel, levado por injeção num arquivo ou numa saída de ferramenta, grava com o Write um arquivo comum (`f.sh` com a função, ou um script) e roda `. ./f.sh; echo '…' > "$(date)"`: o destino é `.git/config` (`core.hooksPath` derruba a `R-VERIFY`; `core.fsmonitor` roda código em todo `git status`) ou, pelo U3, `cp pre-push "$(date)"` com `date` imprimindo `.git/hooks`.
- Por que é bloqueante: requisito provado como não cumprido (`R-REVIEW`), sem critério novo. O texto da U4 em `docs/hooks.md` diz que o destino só passa com o valor que o hook calcula, e o delta declara que o comando redefinido não vale pela lista positiva; S10 a S16 são a mesma redefinição por outro mecanismo. Pela skill, achado fora das dimensões vira dimensão nova da matriz.
- Correção mínima (sem tocar no resto da U4): `na_lista_positiva` devolve `False`, e a troca de `$(pwd)` por `$PWD` não acontece, quando a linha tem, como comando (início de linha ou depois de `;`, `&&`, `||`, `|`, `(`, `{` ou quebra de linha), qualquer item desta lista inteira: `.`, `source`, `hash`, `alias`, `shopt`, `enable`, `builtin`, `command`; ou atribuição (solta, com `export`, `declare`, `typeset`, `local`, `readonly` ou `env`) a `PATH`, `BASH_ENV`, `ENV`, `TMPDIR` ou a qualquer nome `GIT_*`. Fixtures que bloqueiam: S10 a S16. Mutantes: tirar `source` e tirar `PATH` da lista. Legítimos que seguem: os três da A4 acima e as linhas livres de `docs/hooks.md`. Esforço: P. Dono: tech-lead (autor do lote B).
- Fora: o `PATH` herdado do ambiente da sessão com um `date` falso já instalado antes da linha (residual R1, o sandbox).

**A5 · sem mudança (recomendado, fora do lote).** O `resto_no_git` com `..` depois de opaco segue como no parecer anterior; dá 0 igual na develop `f4b0c2ae`. Correção mínima (cartão novo, decisão ao usuário pelo Jarvis, `R-DECISAO`): no `resto_no_git`, o resto com componente `..` depois de uma parte opaca recusa, salvo quando o opaco é `git rev-parse --show-toplevel` ou `pwd` sem `cd` na linha; `mktemp` com `-p`, `--tmpdir` ou `TMPDIR` atribuído na linha não entra na exceção. Esforço: P. Dono: tech-lead.

### O que foi conferido e está correto
- **Sem afrouxar:** o diff só acrescenta recusas (`VARIAVEIS_DO_BASH`, a função antes da lista positiva, a troca de `pwd` condicionada); nenhuma recusa saiu.
- **Orçamento:** `corpo_da_funcao` roda uma vez por corpo; as regex são as da rodada anterior (`[^{}]*`, `[^()]*`), sem alternância ambígua.
- **Oráculo (EXT-1):** `tests/test_oraculo_v047.py` sem commit no intervalo (`git log e25f079b..85043cc4 -- tests/test_oraculo_v047.py` vazio; último commit `730843a9`). Local: `python3 -m unittest tests.test_oraculo_v047` deu 3 testes OK em 60 s.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Suíte inteira: **sem CI no head**. A consulta de check-runs do commit `85043cc4` devolve `total_count` 0 e a branch não tem PR (o brief diz "sem PR"). Rodei só o oráculo e as sondas, citados acima. Quando houver PR, o portão pede o CI verde no head da revalidação.

Faltaram no ambiente: gitleaks, Semgrep, osv-scanner, zizmor e actionlint (`R-CUSTO`, não instalo). A entrega não traz segredo, dependência nem workflow; a análise foi manual e por sonda.
