---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: e34924b4e6d18a37f1454420d1bfc759c787576d
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047 (lote B, destino opaco, revalidação da volta do corpo de heredoc)

Revalidação por delta (`forge-check parecer delta`), intervalo `000cd0c8..e34924b4`. No domínio: `hooks/conformidade.py` (`expansao_conhecida`, `corpos_conhecidos`, `corpo_desconhecido` em `valor_calculado` e no `finally` da releitura, `juntar_continuacoes` em `textos_do_valor`), `docs/hooks.md` e as fixtures `opaco-u4-h-*`. Fora do domínio: mutante 22, `tests/test_hook_destino_opaco.py` e o fragmento. Etapa E1.332, instância que não fez a entrega. Parecer anterior: `000cd0c8`, reprovado (A12 bloqueante, A11 e A5 recomendados).

## Gatilhos
`R-SEGURANCA`: hook de guarda (`conformidade`) que analisa entrada livre (linha de Bash) para proteger o `.git` (`config`, `hooks/`, marca da sessão). Bloqueio por `R-CONFORMIDADE`.

## Achados
- A13 (bloqueante) hooks/conformidade.py:551 · Corpo de heredoc sem aspas de embutido com `${d:=v}` de nome minúsculo passa (`NOME_INOFENSIVO`), e `valores_da_variavel` não vê o corpo: lê `$d` como do ambiente e libera; `: <<E` com `${a:=.g}${d:=${a}it/config}` e `echo a > "$d"` grava .git/config (R-CONFORMIDADE)
- A14 (bloqueante) hooks/conformidade.py:687 · `${d:=v}` na própria linha não conta como atribuição (só `d=` conta, e o `{` antes do nome sai da busca): `: ${d:=.g""it/config}; echo a > "$d"` dá rc 0 e grava .git/config; já na develop f4b0c2ae, dentro do texto da A9 (R-CONFORMIDADE)
- A11 (recomendado) hooks/conformidade.py:497 · A lista fechada recusa todo programa externo na linha (`python3 gen.py > "$(mktemp)"`, `make check 2>&1 | tee "$(mktemp)"`, `cd docs && …`), mas programa externo não troca a resolução do shell; só embutido, função e atribuição trocam
- A5 (recomendado) hooks/conformidade.py:1479 · Resto com barra que sobe (/../config) depois de opaco dentro do .git libera: "$(mktemp -u -p .git)"/../config e TMPDIR=.git com "$(mktemp -u)"/../config gravam .git/config. Já na develop f4b0c2ae; fora do texto da A9 (sem resto): cartão novo

## Sondas
- S42 · : <<E⏎${a:=.g}${d:=${a}it/config}⏎E⏎echo a > "$d" (⏎ é quebra de linha) · espera: 2 · obtido: 0
- S43 · : ${d:=.g""it/config}; echo a > "$d" · espera: 2 · obtido: 0

## Detalhe dos achados
Como as sondas rodaram: script no meu rascunho que monta um repositório (`develop` + `melhoria/x`, `.forge/versao`), roda `hooks/conformidade.py` do head `e34924b4` com a linha (papel `forge:tech-lead`) e roda a mesma linha no `bash -c` numa cópia; "espera: 2" é o bash ter gravado em `.git/config`, o que aconteceu nas duas. Nas sondas, `⏎` é quebra de linha.

**A12 · fechada.** S39, S40 e S41 dão 2 no head. Também 2: `<<-E` com tab, `{ : <<E … }` (grupo), heredoc dentro do `$(…)` do destino, `$\`+quebra+`[PATH=5]`, `<<<` com `$[`. `<<E""` com `$[PATH=5]` dá 0 e o bash não grava (corpo literal). Legítimo segue 0: `cat <<E⏎$HOME e ${x:-y}⏎E⏎echo a > "$(mktemp)"`.

**A13 · `${nome:=v}` de nome minúsculo no corpo de heredoc (dimensão da matriz: mecanismo "atribuição por expansão" × posição "corpo de heredoc expandido").**
- Evidência: `hooks/conformidade.py:551-555` (`corpos_conhecidos` → `expansao_conhecida`) aprova `${d:=…}` porque `d` casa `NOME_INOFENSIVO` (`:504`). O critério do nome minúsculo vale para a resolução de comando (o bash não lê `d`), não para o valor que a linha calcula: `valores_da_variavel` (`:679-695`) lê `texto_da_linha`, que vem sem os corpos, não acha atribuição de `d` e devolve `SEM_VALOR` (do ambiente), que sozinho num componente libera.
- Caminho de ataque: o da A12. Agente de qualquer papel, por injeção, roda S42 numa chamada; `:` é embutido, o bash expande o corpo no próprio shell e grava `d=.git/config`; o `echo` sobrescreve `.git/config` (`core.hooksPath` derruba a `R-VERIFY`, `core.fsmonitor` roda código). Sem `.git` literal na linha, o `CRITICO` não dispara.
- Severidade: alta. Bloqueante: o requisito do delta (corpo de heredoc sem aspas passa pelas buscas, `docs/hooks.md` A9) provado incompleto e defeito provado no portão (`R-CONFORMIDADE`, `R-REVIEW`).
- Correção mínima: em `corpos_conhecidos`, recusar (marcar `corpo_desconhecido`) o corpo expandido com qualquer `PADRAO_QUE_ATRIBUI`, de qualquer nome, além das três buscas; ou somar os corpos expandidos ao texto que `valores_da_variavel` lê. Fixtures: S42 e `: <<E⏎${d=.g""it/config}⏎E⏎echo a > "$d"` bloqueiam; `cat <<E⏎${x:-y}⏎E⏎echo a > "$(mktemp)"` libera. Mutante: tirar a recusa por nome minúsculo no corpo. Esforço: P. Dono: tech-lead.

**A14 · `${nome:=v}` na própria linha não conta como atribuição.**
- Evidência: `hooks/conformidade.py:685` exclui da busca de "outra ocorrência" o nome depois de `{` e `:687` só acha `nome=`; `${d:=v}` não casa nenhum dos dois, e `$d` vale como do ambiente. `${d=v}` casa `d=` e recusa (conferi: 2). Já na develop `f4b0c2ae` e em `000cd0c8` (mesma sonda dá 0 nos três), mas dentro do texto da A9 ("as variáveis da linha que ele usa"), não fora dele como a A5.
- Caminho de ataque: igual, com S43 (sem heredoc).
- Severidade: alta. Bloqueante: requisito da A9 não cumprido (`R-CONFORMIDADE`).
- Correção mínima: em `valores_da_variavel`, devolver `None` quando a linha tem `${nome:=` ou `${nome=` (também com índice): `re.search(rf"\$\{{#?{nome}(\[[^]]*\])?:?=", linha)`. Fixtures: S43, `a=.g; : ${d:=${a}it/config}; echo a > "$d"` e `: ${a:=.g}${d:=${a}it/config}; cp x "$d"` bloqueiam; `: ${x:-a}; echo a > "$(date)"` libera. Esforço: P. Dono: tech-lead.

**A11 · sem mudança (recomendado).** Como no parecer anterior: sobra recusa, nunca falta, e o falso positivo está declarado em `docs/hooks.md`.

**A5 · sem mudança (recomendado, fora do lote).** Cartão novo, decisão ao usuário pelo Jarvis (`R-DECISAO`). A linha da evidência acompanhou o deslocamento do arquivo (`resto_no_git`, `:1479`).

### O que foi conferido e está correto
- **Sem afrouxar:** `expansao_conhecida` é extração das três buscas que já estavam em `linha_conhecida`, sem mudança de ordem nem de regex; `corpo_desconhecido` só acrescenta recusa em `valor_calculado`, e o `finally` o devolve ao valor de fora (o heredoc dentro de `$(…)` é subshell e não vaza para fora, o de fora vale dentro). A troca do `replace("\\\n", "")` por `juntar_continuacoes` em `textos_do_valor` (A4 do QA E1.329) não junta `\\` + quebra.
- **Falha fechada:** `linha` `None` em `valor_calculado` cai no `barrar`.
- **U3 e `$(pwd)`:** `corpo_positivo` e a troca de `$(pwd)` por `$PWD` (`:1723`) não leem `corpo_desconhecido`, mas não abrem: com `cp` o U4 recusa depois (sonda `: <<E⏎$[PATH=5]⏎E⏎cp config "$(date)"` dá 2), e `pwd` é embutido, que nem `PATH` nem `BASH_CMDS` trocam, e aritmética só grava número em `PWD` (não absoluto, o embutido o ignora).
- **Oráculo (EXT-1):** `tests/test_oraculo_v047.py` sem commit no intervalo (`git log 000cd0c8..e34924b4 -- tests/test_oraculo_v047.py` vazio). Local: `python3 -m unittest tests.test_hook_destino_opaco` deu 4 testes OK em 19 s.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Suíte inteira: **sem CI no head** (a branch não tem PR; o brief diz "sem PR"; `gh run list` sem saída no ambiente). Rodei os testes do destino opaco e as sondas, citados acima. Quando houver PR, o portão pede o CI verde no head da revalidação.

Faltaram no ambiente: gitleaks, Semgrep, osv-scanner, zizmor e actionlint (`R-CUSTO`, não instalo). A entrega não traz segredo, dependência nem workflow; a análise foi manual e por sonda.
