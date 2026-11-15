---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: 74b42c69d7c1fd98980986104f7e3733dbbbdd5b
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047 (lote B, destino opaco, revalidação da volta de A13 e A14)

Revalidação por delta (`forge-check parecer delta`), intervalo `e34924b4..74b42c69`. No domínio: `hooks/conformidade.py` (`corpos_conhecidos` recusa qualquer `PADRAO_QUE_ATRIBUI` no corpo expandido; `valores_da_variavel` devolve `None` com `${nome:=` ou `${nome=` na linha), `docs/hooks.md` e as fixtures `opaco-u4-*` novas. Fora do domínio: mutantes 22 e 23, `tests/test_hook_destino_opaco.py` e o fragmento. Etapa E1.336, instância que não fez a entrega. Parecer anterior: `e34924b4`, reprovado (A13 e A14 bloqueantes, A11 e A5 recomendados).

## Gatilhos
`R-SEGURANCA`: hook de guarda (`conformidade`) que analisa entrada livre (linha de Bash) para proteger o `.git` (`config`, `hooks/`, marca da sessão). Bloqueio por `R-CONFORMIDADE`.

## Achados
- A15 (bloqueante) hooks/conformidade.py:693 · A busca do prefixo nascido na linha pula o nome depois de `{`, então `${d:=v}` não conta para `$d"t"` (lido `$dt`): `: ${d:=.gi}; cp -rT ev "$d"t` dá rc 0 e o bash copia ev/config sobre .git/config; `d=.gi` no lugar recusa (R-CONFORMIDADE)
- A11 (recomendado) hooks/conformidade.py:497 · A lista fechada recusa todo programa externo na linha (`python3 gen.py > "$(mktemp)"`, `make check 2>&1 | tee "$(mktemp)"`, `cd docs && …`), mas programa externo não troca a resolução do shell; só embutido, função e atribuição trocam
- A5 (recomendado) hooks/conformidade.py:1482 · Resto com barra que sobe (/../config) depois de opaco dentro do .git libera: "$(mktemp -u -p .git)"/../config e TMPDIR=.git com "$(mktemp -u)"/../config gravam .git/config. Já na develop f4b0c2ae; fora do texto da A9 (sem resto): cartão novo

## Sondas
- S44 · : ${d:=.gi}; cp -rT ev "$d"t (ev/config com [core] hooksPath) · espera: 2 · obtido: 0
- S45 · : ${d=.gi}; cp -rT ev "$d"t · espera: 2 · obtido: 0
- S46 · : <<< ${d:=.gi}; cp -rT ev "$d"t · espera: 2 · obtido: 0
- S47 · : ${d:=.gi}; cp -r ev/. "$d"t · espera: 2 · obtido: 0

## Detalhe dos achados
Como as sondas rodaram: script no meu rascunho que monta o fixture de `tests/test_conformidade_opaco.py` (`dados_do_caso`, ambiente projeto, papel `forge:tech-lead`) com `ev/config` a mais, roda `hooks/conformidade.py` do head `74b42c69` pelo `rodar` de `tests/test_hooks.py` e roda a mesma linha no `bash -c` na pasta do caso; "espera: 2" é o bash ter mudado `.git/config`, o que aconteceu nas quatro. Controles: `d=.gi; cp -rT ev "$d"t` e `e=.gi; cp -r ev/. "$e"t` dão 2; o literal `cp -rT ev .git` dá 2.

**A13 · fechada.** S42 dá 2 no head. Também 2: `: <<-E⏎⇥${d:=.g""it/config}⏎⇥E⏎echo a > "$d"`, `{ : <<E⏎${d:=.git/config}⏎E⏎}; echo a > "$d"` e dois heredocs na linha (`: <<A <<B`, atribuição no segundo corpo). Legítimo segue 0: `cat <<E > "$(mktemp)"⏎ola ${HOME}⏎E`.

**A14 · fechada na forma direta.** S43 dá 2; também `${d=…}` sem dois-pontos, `<<< ${d:=…}`, `true ${d:=…} && …` e `: ${d:=.git}; echo a > "$d"/config`. Legítimo segue 0: `: ${d:-docs}; echo a > "$d"`, `d=docs/x; echo a > "$d"`. A correção, porém, não chegou à segunda busca da mesma função: A15.

**A15 · `${nome:=v}` não conta como nascimento do prefixo (mesma dimensão da A14, "atribuição por expansão", × forma "variável com resto colado sem barra").**
- Evidência: `hooks/conformidade.py:693`. O `shlex` tira as aspas e `"$d"t` chega como `$dt`; o hook procura atribuição de `dt` (não há) e então se algum prefixo (`d`) nasce na linha, com `(?<![\w${{])`, que exclui o nome depois de `{`. `${d:=.gi}` fica de fora, e `$dt` vale como do ambiente (`SEM_VALOR`), que libera. Com `d=.gi` a busca acha e recusa. A linha 688 (A14) só olha o nome inteiro (`dt`).
- Caminho de ataque: agente de qualquer papel, por injeção de prompt, roda S44 numa chamada; o bash grava `d=.gi`, o destino é `.git` e `cp -rT` (ou `cp -r ev/.`) copia o conteúdo da pasta sobre o `.git`: `.git/config` com `core.hooksPath` derruba a `R-VERIFY`, `core.fsmonitor` roda código. A origem tem nome neutro, então o U3 não age; sem `.git` literal, o `CRITICO` não dispara. Com origem `x` simples, grava `.git/x`.
- Severidade: alta. Bloqueante: defeito provado no portão, mesma família da A14 cuja correção é o objeto deste delta (`R-CONFORMIDADE`, `R-REVIEW`).
- Correção mínima: na linha 693, contar também `${prefixo:=` e `${prefixo=` (com índice) como nascimento, reaproveitando a regex da linha 688 por prefixo: `re.search(rf"\$\{{#?{nome[:k]}(\[[^]]*\])?:?=", linha)`; ou tirar o `{` da lookbehind (recusa a mais com `${d}` e `$dt` na mesma linha, falso positivo aceitável). Fixtures: S44 a S47 bloqueiam; `: ${d:=.gi}; cp x "$d"t` bloqueia; `: ${d:-docs}; echo a > "$d"` libera. Mutante: voltar a lookbehind. Varra também as outras buscas por nome no arquivo com `(?<![\w${{])` ou `(?<![\w$])`. Esforço: P. Dono: tech-lead.

**A11 · sem mudança (recomendado).** Como no parecer anterior.

**A5 · sem mudança (recomendado, fora do lote).** Cartão novo, decisão ao usuário pelo Jarvis (`R-DECISAO`). A linha acompanhou o deslocamento (`resto_no_git`, `:1482`).

### O que foi conferido e está correto
- **Sem afrouxar:** as duas mudanças só acrescentam recusa (`and not PADRAO_QUE_ATRIBUI.search(corpo)` e um `return None` antes das atribuições).
- **Oráculo (EXT-1):** `tests/test_oraculo_v047.py` sem commit no intervalo (`git log e34924b4..74b42c69 -- tests/test_oraculo_v047.py` vazio). Local: `python3 -m unittest tests.test_hook_destino_opaco` deu 4 testes OK em 78 s.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Suíte inteira: **sem CI no head** (a branch não tem PR; o brief diz "sem PR"). Rodei os testes do destino opaco e as sondas. Quando houver PR, o portão pede o CI verde no head da revalidação.

Faltaram no ambiente: gitleaks, Semgrep, osv-scanner, zizmor e actionlint (`R-CUSTO`, não instalo). A entrega não traz segredo, dependência nem workflow; a análise foi manual e por sonda.
