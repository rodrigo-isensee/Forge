---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v047-conformidade-cf1
commit: 7412a90f2e2389af96e3e8aa0ead8f22de90baee
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047 (CF1, A17 a A19 do hook conformidade)

Revalidação por delta, head `7412a90f` (v0474 E1.30). Rodada anterior: commit `0121b3b2`, aprovado (no git). Delta lido: `forge-check parecer delta`, intervalo `0121b3b2..7412a90f`, sem o que veio da base. No domínio: `bin/forge-testes`, `docs/hooks.md`, `tests/test_conformidade_verde.py`, `tests/test_oraculo_v047.py`; fora: `docs/hooks-fixtures.md`, os dois specs de mutante e `tests/test_testes_tocados.py` (li os specs mesmo assim).

## Gatilhos
Gatilhos: hook de guarda (`conformidade`) que analisa entrada livre (uma linha de Bash) para proteger o `.git`, bloqueio por `R-CONFORMIDADE` (`R-SEGURANCA`).

## O que mudou e como conferi
- **Junções `b7a82cf4` e `7412a90f`** (`git show --remerge-diff`): em `hooks/conformidade.py` o conflito ficou com o lado da branch (`DECLARADORES`, `OPCAO_SEM_REFERENCIA`, `atribui_como_argumento` e o `or ... atribui_como_argumento` da A19 em `valores_da_variavel`, linha 730); o resto do arquivo é o da develop. Prova: `git diff e2880b42 7412a90f -- hooks/` só traz A17 (`hooks/_comum.py:39` e `:615`), A18 (`hooks/conformidade.py:327`) e A19 (`:698` a `:730`); e o blob de `hooks/conformidade.py` é o mesmo no `0121b3b2` e no `7412a90f` (`895de584`), assim como `hooks/_comum.py`. O hook que aprovei não mudou; nada da develop se perdeu.
- **`bin/forge-testes`**: a junção manteve `test_conformidade_verde` em `FORGE_CHECK` e acrescentou, pela develop, `test_estado_ilegivel` e `test_pre_push_patch`/`test_ambiente_hook`; nada sai do mapa de quem roda com o hook.
- **Specs G6 e O60**: o `de` casa uma vez no head e o `para` não existe nele (conferido por script); o O60 desliga só o `len(atribuicoes) > 1` e preserva a A19, que é como o mutante deve ficar.
- **Testes**: `test_conformidade_verde` ganhou a linha ilegível (com e sem a prova) e `test_oraculo_v047` trocou `README.md` por `LEIAME.md` e passa o ambiente por `sem_manutencao`, as duas vindas da develop; o oráculo não perdeu caso.

## Sondas e testes no head
Rodei `tests.test_conformidade_verde`, `test_hook_destino_opaco`, `test_conformidade_opaco`, `test_hook_git_comum` e `test_oraculo_v047`: 26 testes, OK. Sondei o hook real (harness `Fixture` de `tests/test_hooks.py`) com 18 linhas de A17, A18, A19 e legítimos: 18 de 18 como esperado (`cp ev/config .git/config 2>/dev/null`, `cp ev/config {fd}>x .git/config`, `set -- .git; cp -rT ev "$@"`, `declare -rn d=_`, `o=-n; declare $o d=_` dão 2; `grep foo docs 2>/dev/null`, `echo 2 > docs/a.md`, `declare -r d=docs`, `local d=docs` dão 0). Nenhum bloqueante: a sonda não entra em `## Sondas`. Suíte inteira: não rodei; o CI do PR é o portão dela.

## Achados
- A17 (recomendado) hooks/_comum.py:615 · Fechado, sem mudança no delta: o descritor colado (`2>x`, `{fd}>x`) não é palavra; sondas da rodada dão 2.
- A18 (recomendado) hooks/conformidade.py:327 · Fechado, sem mudança no delta: `$@` e `$*` em `SO_VARIAVEL`; `set -- .git; cp -rT ev "$@"` dá 2.
- A19 (recomendado) hooks/conformidade.py:730 · Fechado: a junção manteve o `or atribui_como_argumento`; `declare -n d=_` e `$o` com `-n` dão 2, `declare -r d=docs` libera.
- A20 (recomendado) hooks/conformidade.py:1464 · Segue aberto, sem mudança: resto com barra depois de valor que cita o `.git` (`d=.git; cp -rT ev "$d/."`) libera; igual na develop, não é regressão; cartão de prioridade alta.
- A11 (recomendado) hooks/conformidade.py:500 · Segue aberto, sem mudança: a lista fechada recusa programa externo na linha, que não troca a resolução do shell.
- A5 (recomendado) hooks/conformidade.py:1522 · Segue aberto, sem mudança: resto com barra que sobe (`/../config`) depois de opaco dentro do `.git` libera; mesma família do A20.

## Sondas

## Detalhe dos achados
**A20.** Evidência: `hooks/conformidade.py:1464` (`resto_colado`, que só decide o resto sem barra; o resto com barra é do `resto_no_git`, que olha só os nomes protegidos). Caminho de ataque: um agente com a linha livre grava `d=.git; cp -rT ev "$d/."` (ou `"$(echo .git)/."`, `"$@/."`, `"$_/."` depois de `: .git`); `ev/` traz `config` com `hooksPath` ou `hooks/pre-push`; o bash copia tudo sobre o `.git` e o hook libera com 0, enquanto o literal `cp -rT ev .git/.` dá 2 (`/.` é o próprio diretório). Mesmo com o `.git/c` (nome fora da lista) o literal dá 2 e `"$(echo .git)"/c` libera. Idêntico em `develop` `86ac0fcb`, em `081473ac` e na cf1: não é regressão. Severidade: alta (grava `config` e `hooks/` do repositório). Correção mínima: com valor que cita o `.git` (U1) e resto com barra, recusar o resto vazio, `.`, `./` e todo componente fora de uma lista positiva, no `resto_colado`, em vez de pedir o nome da lista do git; fixture por forma de `$d/.`, `$@/.`, `$(…)/.` e `"$@"/c`. Esforço: P. Dono: `software-engineer`. Cartão de prioridade alta junto do A5.

Os achados A17 a A19 seguem fechados no head `7412a90f` (fecharam no `fbc41e6c`); os 32 fixtures `opaco-cf1-*` cobrem as mesmas formas que sondei, com os falsos negativos de descritor, `$@`/`$*` e `-n` nos nomes dos arquivos.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Faltaram no ambiente: gitleaks, Semgrep, osv-scanner, zizmor e actionlint (`R-CUSTO`, não instalo). A entrega não traz segredo, dependência nem workflow; a análise foi manual e por sonda.
