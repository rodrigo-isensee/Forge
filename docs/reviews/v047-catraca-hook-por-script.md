---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-catraca-hook-por-script
commit: 40faab231edc2a7a4a74e3e60841b10770de18a1
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 (CATRACA-HOOK-POR-SCRIPT, E2.53; review E2.61; revalidação E2.82)

Revalidação por delta da volta E2.67, instância que não fez a entrega. Delta lido: `forge-check parecer delta` deste parecer, intervalo `9811ca97..40faab23` (bd62b9e5, 40faab23 e o merge e8499ceb), domínio: `changelog.d/v047-catraca-hook-por-script.md`, `tests/catraca.py`, `tests/fixtures/catraca-hooks/sondas.json`, `tests/mutantes/v047-catraca-hook-por-script.json`, `tests/mutantes/v047-catraca-hook-por-script-2.json` e `tests/test_catraca.py`. Código e teste contra a base cb45a962: 112 linhas (`tests/catraca.py` 39+10, `tests/test_catraca.py` 63+0), dentro do teto M14; um comportamento (a chave do hook).

## Achados
- A1 (recomendado) tests/catraca.py:297 · A chave segue um conjunto: dois hooks iguais em evento, matcher, tipo, interpretador e script, com argumentos diferentes, viram uma chave, e remover um passa calado. Sem gatilho no hooks.json do Forge; contar as chaves (Counter).
- A2 (recomendado) tests/catraca.py:286 · Script entre aspas no command (`python3 "x.py"`) não casa o sufixo e cai na linha inteira: acrescentar `-s -E` volta a acusar (falso positivo, falha fechada). Sem gatilho no Forge; tirar as aspas do termo antes do sufixo.
- A3 (recomendado) tests/mutantes/v047-catraca-hook-por-script-2.json:27 · `forge-mutante --cobertura --base cb45a962` sai rc=1: `apagada · tests/catraca.py:277(base) · ar or cm` sem isenta (o `or` da mensagem antiga). A catraca não barra (tests/ fora da classe C); acrescentar a isenta com `linha_base` 277.

## Sondas

## Parecer
**Aprovado** no domínio do code review. O delta responde aos bloqueantes A1 e A2 e ao A3 da segurança (E2.62): `script_do_hook` devolve (tipo, interpretador, script), só pula opções da lista inócua do Python e volta à linha inteira, sem interpretador, em qualquer outro caso (`-c`, `-m`, `-`, termo antes do script, interpretador que não é Python): falha fechada. A ordem do dono do PR 565 segue atendida (`test_mudar_interpretador_opcoes_ou_argumentos_passa`, sonda `PR565` da fixture).

Leitura: funções pequenas (`_ultimo_trecho`, `_opcao_inocua`) com docstring do motivo; constantes nomeadas; a mensagem de `regra_hooks` mostra tipo, interpretador e script com o ID `R-CONFORMIDADE`. Testes: `test_hook_neutralizado_sem_tirar_o_script_barra` cobre o ramo de falha de cada guarda nova por comportamento (subTest por troca), e `CorpusDasSondasDeHook` roda S1 a S4 e A3 sobre o `hooks/hooks.json` real, com mínimo de 6 sondas e alvo único afirmados (checklist 11). Sem subprocesso no teste novo.

Guardas: 10 linhas de guarda mudadas, um mutante por linha (CH-M1 a CH-M10, duas specs, a 2ª passado o 8º); a condição apagada da base na linha 267 tem isenta. Resta o A3.

Segurança fora do meu domínio, citada sem refazer: o parecer `docs/security/v047-catraca-hook-por-script.md` no mesmo head (29192417, E2.83) está **reprovado** com A4 (`-I`/`-P` na lista inócua), A5 (valor livre de `-X`/`-W`) e A6 (interpretador só pelo último trecho); a classe não fecha até a volta. A correção desses itens muda `tests/catraca.py` e pede nova revalidação por delta.

Verificadores citados (rodados aqui no head 40faab23; a suíte inteira fica no CI do PR, que o item ainda não tem):
- `bin/forge-mutante tests/mutantes/v047-catraca-hook-por-script.json`: CH-M1 a CH-M8 `morreu` (CH-M2 por erro do teste sob o mutante).
- `bin/forge-mutante tests/mutantes/v047-catraca-hook-por-script-2.json`: CH-M9 e CH-M10 `morreu`.
- `bin/forge-mutante --cobertura --base cb45a962`: rc=1, só a apagada do A3 fora; as demais `coberta` ou `isenta`.
- `catraca.regra_guardas_dos_hooks` (MUTANTES-SPEC-HOOKS) sobre cb45a962..40faab23: `[]`.
- `python3 -m unittest tests.test_catraca.Hooks tests.test_catraca.CorpusDasSondasDeHook`: `Ran 8 tests ... OK`.

Commits: bd62b9e5 (fix) e 40faab23 (test), Conventional Commits em português com a etapa; o fragmento em `changelog.d/` descreve a chave nova (seção Corrigido).
