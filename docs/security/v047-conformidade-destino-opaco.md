---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: 041c671bbcca2cb1fdee5b9d65304151bbf649a5
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047 (lote B, destino opaco, revalidação da volta da A6)

Revalidação por delta (`forge-check parecer delta`), intervalo `85043cc4..041c671b`. No domínio: `hooks/conformidade.py` (`RESOLUCAO_TROCADA` em `na_lista_positiva` e na troca de `$(pwd)` por `$PWD`), `docs/hooks.md` e as fixtures `opaco-u4-seg3-*`. Fora do domínio: mutantes 16 e 17, `tests/test_hook_destino_opaco.py` e o índice de fixtures. Etapa E1.320, instância que não fez a entrega. Parecer anterior: `85043cc4`, reprovado (A6 bloqueante, A5 recomendado).

## Gatilhos
`R-SEGURANCA`: hook de guarda (`conformidade`) que analisa entrada livre (linha de Bash) para proteger o `.git` (`config`, `hooks/`, marca da sessão). Bloqueio por `R-CONFORMIDADE`.

## Achados
- A7 (bloqueante) hooks/conformidade.py:555 · O ramo `echo`/`printf %s` do U4 não consulta RESOLUCAO_TROCADA: `source e.sh`, `alias echo=…` com `shopt` e `enable -n echo; PATH=./bin:$PATH` antes de `echo a > "$(echo saida.txt)"` gravam .git/config com rc 0. Mesma classe da A6 (R-CONFORMIDADE)
- A8 (bloqueante) hooks/conformidade.py:496 · RESOLUCAO_TROCADA casa o texto cru: `'source'`, `\.`, `"."`, `sour''ce`, `$s` com s=source, `eval '. ./f.sh'`, `BASH_CMDS[date]=./d`, `declare "${P}TH=./bin"` e `read -r P''ATH` trocam a resolução e gravam .git/config com rc 0 (R-CONFORMIDADE)
- A9 (recomendado) hooks/conformidade.py:496 · `.` vale como palavra em qualquer posição, não só como comando: `find . -name x > "$(mktemp)"` e `ls -la . > "$(date +%F).log"` recusam (falso positivo comum)
- A5 (recomendado) hooks/conformidade.py:1355 · Resto com barra que sobe (/../config) depois de opaco dentro do .git libera: "$(mktemp -u -p .git)"/../config e TMPDIR=.git com "$(mktemp -u)"/../config gravam .git/config. Já na develop f4b0c2ae; fora do texto da A9 (sem resto): cartão novo

## Sondas
- S17 · . ./e.sh; echo a > "$(echo saida.txt)" (e.sh: `echo(){ printf %s .git/config; }`) · espera: 2 · obtido: 0
- S18 · source e.sh; echo a > "$(echo saida.txt)" · espera: 2 · obtido: 0
- S19 · enable -n echo; PATH=./bin:$PATH; echo a > "$(echo saida.txt)" (bin/echo imprime .git/config) · espera: 2 · obtido: 0
- S20 · três linhas: `shopt -s expand_aliases` / `alias echo='printf %s .gi''t/config'` / `echo a > "$(echo saida.txt)"` · espera: 2 · obtido: 0
- S21 · 'source' f.sh; echo a > "$(date)" (f.sh: `date(){ echo .git/config; }`) · espera: 2 · obtido: 0
- S22 · \. ./f.sh; echo a > "$(date)" · espera: 2 · obtido: 0
- S23 · "." ./f.sh; echo a > "$(date)" · espera: 2 · obtido: 0
- S24 · sour''ce f.sh; echo a > "$(date)" · espera: 2 · obtido: 0
- S25 · \source f.sh; cp config "$(date)" (U3) · espera: 2 · obtido: 0
- S26 · s=source; $s f.sh; echo a > "$(date)" · espera: 2 · obtido: 0
- S27 · eval '. ./f.sh'; echo a > "$(date)" · espera: 2 · obtido: 0
- S28 · BASH_CMDS[date]=./d; echo a > "$(date)" (d: script executável que imprime .git/config) · espera: 2 · obtido: 0
- S29 · chmod +x bin/date; P=PA; declare "${P}TH=./bin"; echo a > "$(date)" · espera: 2 · obtido: 0
- S30 · chmod +x bin/date; read -r P''ATH <<< ./bin; echo a > "$(date)" · espera: 2 · obtido: 0

## Detalhe dos achados
Como as sondas rodaram: `tests/test_oraculo_v047.py` como biblioteca (`montar`, `rodar_hook`, `ambiente`), sem editá-lo, num script no meu rascunho, com arquivos a mais no repositório do caso (`f.sh`, `e.sh`, `d`, `bin/date`, `bin/echo`). Para cada linha: o rc do hook no head `041c671b` (papel `forge:tech-lead`, projeto em `melhoria/x`) e a própria linha rodada pelo bash (`--norc --noprofile`) numa cópia do repositório, com hash do `.git` (menos `objects/` e `index`) antes e depois. Em S17 a S30 o bash gravou no `.git` e o hook deu 0; o "espera: 2" é esse resultado do bash.

**A6 · fechada na forma literal.** S10 a S16 do parecer anterior dão 2 no head (as sete), e `cp config "$(mktemp -d)"`, `echo a > "$(date +%F).log"` sem `.` na linha e `echo a > "$(date)"` seguem 0. A classe, porém, não fecha: A7 e A8 são o mesmo mecanismo (a linha troca o que o nome resolve) por portas que a correção não cobriu.

**A7 · o ramo `echo`/`printf %s` não passa pela troca de resolução.**
- Evidência: `hooks/conformidade.py:547-558` (`valores_do_corpo`): `RESOLUCAO_TROCADA` só é lida em `na_lista_positiva` (`:505`) e na troca do `pwd` (`:1606`); o ramo seguinte calcula `echo` e `printf %s` pelo nome, olhando só `corpo_da_funcao` na linha. A função carregada por `.`/`source`, o alias e `enable -n echo` com `PATH` trocam o `echo` sem nenhum `echo(){` na linha. Nem os itens que já estão na lista (`source`, `alias`, `enable`, `PATH`) desligam esse ramo.
- Caminho de ataque: o da A6. Um agente de qualquer papel, levado por injeção num arquivo ou saída de ferramenta, grava com o Write um `e.sh` comum e roda `. ./e.sh; echo '[core] hooksPath=…' > "$(echo saida.txt)"`: o destino é `.git/config` (`core.hooksPath` derruba a `R-VERIFY`; `core.fsmonitor` roda código em todo `git status`).
- Severidade: alta (contorno do portão que guarda o `.git`, sem privilégio). Bloqueante: requisito do próprio delta (`docs/hooks.md`: o comando cuja resolução a linha troca não vale) provado como não cumprido (`R-REVIEW`).
- Correção mínima: em `valores_do_corpo`, antes do ramo de `echo`/`printf`, devolver `None` quando a linha casa `RESOLUCAO_TROCADA` (a mesma checagem normalizada da A8). Fixtures que bloqueiam: S17 a S20. Esforço: P. Dono: tech-lead (autor do lote B).

**A8 · a lista fechada casa o texto cru, e o bash tira aspas e barra antes de resolver (dimensão nova: forma da palavra que troca a resolução).**
- Evidência: `hooks/conformidade.py:496-498`. O lookbehind `(?<![^\s;&|(){}])` exige espaço ou operador antes do nome, então `'source'`, `"."`, `\.`, `\source` e `sour''ce` não casam; o nome vindo de expansão (`$s`), o `eval` com o comando entre aspas, as matrizes `BASH_CMDS` (o mesmo que `hash -p`) e `BASH_ALIASES` e o nome de variável montado (`declare "${P}TH=…"`) ou partido por aspas (`read -r P''ATH`) ficam fora da lista.
- Caminho de ataque: o da A7, com `date`, `pwd`, `mktemp`, `true` ou `git rev-parse --show-toplevel` no destino (U4) ou no U3 (`\source f.sh; cp config "$(date)"`, S25).
- Severidade: alta. Bloqueante pelo mesmo motivo da A7; pela skill, achado fora das dimensões vira dimensão nova da matriz, não correção pontual.
- Correção mínima (lista inteira; vale para `na_lista_positiva`, a troca do `pwd` e o ramo da A7): (1) casar `RESOLUCAO_TROCADA` sobre a linha com `'`, `"` e `\` removidos; (2) acrescentar à lista de palavras `eval` e `trap`, e aos nomes `BASH_CMDS` e `BASH_ALIASES`; (3) tratar como troca a palavra em posição de comando (início de linha ou depois de `;`, `&&`, `||`, `|`, `(`, `{`, quebra de linha) que começa com `$` ou crase; (4) tratar como troca `declare`, `typeset`, `export`, `local`, `readonly`, `read`, `mapfile`, `readarray` e `printf -v` com nome de variável que traz `$` ou crase. Fixtures que bloqueiam: S21 a S30. Mutantes: tirar a remoção de aspas, tirar `eval`, tirar `BASH_CMDS`. Legítimos que seguem: `echo a > "$(date)"`, `echo a > "$(date +%F).log"`, `cp config "$(mktemp -d)"`, `source f.sh; echo a > docs/saida.txt`. Esforço: P. Dono: tech-lead.
- Fora: o `PATH` herdado da sessão com programa falso já instalado (residual R1, o sandbox), e variáveis que mudam a saída sem trocar o programa (`TZ`, `LC_*`, `LOCPATH`, `LD_PRELOAD` sobre `date`), que exigem artefato compilado ou locale montado; ficam como residual R1, sem achado.

**A9 · falso positivo do `.` (recomendado).** O `.` é comando só na posição de comando; como argumento (`find .`, `ls .`, `git -C .`) não troca nada, mas hoje tira a lista positiva da linha inteira (rc 2 nas duas linhas do achado, o bash não grava no `.git`). Correção: casar `.` só na posição de comando, depois da normalização da A8. Esforço: P. Dono: tech-lead. Não bloqueia: sobra recusa, nunca falta.

**A5 · sem mudança (recomendado, fora do lote).** Como no parecer anterior; cartão novo, decisão ao usuário pelo Jarvis (`R-DECISAO`).

### O que foi conferido e está correto
- **Sem afrouxar:** o diff só acrescenta recusas (`RESOLUCAO_TROCADA` antes da lista positiva e na troca do `pwd`); nenhuma recusa saiu.
- **Orçamento:** `RESOLUCAO_TROCADA` é uma alternância de literais sem quantificador aninhado; roda uma vez por corpo e uma por linha.
- **Oráculo (EXT-1):** `tests/test_oraculo_v047.py` sem commit no intervalo (`git log 85043cc4..041c671b -- tests/test_oraculo_v047.py` vazio). Local: `python3 -m unittest tests.test_oraculo_v047` deu 3 testes OK em 74 s.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Suíte inteira: **sem CI no head**. A consulta de check-runs do commit `041c671b` devolve `total_count` 0 e a branch não tem PR (o brief diz "sem PR"). Rodei o oráculo e as sondas, citados acima. Quando houver PR, o portão pede o CI verde no head da revalidação.

Faltaram no ambiente: gitleaks, Semgrep, osv-scanner, zizmor e actionlint (`R-CUSTO`, não instalo). A entrega não traz segredo, dependência nem workflow; a análise foi manual e por sonda.
