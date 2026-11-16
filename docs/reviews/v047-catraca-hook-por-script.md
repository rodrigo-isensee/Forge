---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-catraca-hook-por-script
commit: 66a3a9a4bbcafbd3588f564bd2fc2a81964fe3e6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 (CATRACA-HOOK-POR-SCRIPT, E2.53; review E2.61; revalidações E2.82 e E2.113)

Revalidação por delta da volta 2 (E2.97), instância que não fez a entrega. Delta lido: `forge-check parecer delta` deste parecer, intervalo `40faab23..66a3a9a4`, domínio: `changelog.d/v047-catraca-hook-por-script.md`, `tests/catraca.py`, `tests/fixtures/catraca-hooks/sondas.json`, `tests/mutantes/v047-catraca-hook-por-script.json`, `tests/mutantes/v047-catraca-hook-por-script-2.json` e `tests/test_catraca.py`. Código e teste contra a base cb45a962: 163 linhas (`tests/catraca.py` 60+13, `tests/test_catraca.py` 90+0), acima da orientação M14 de 150; um comportamento só (a chave do hook), e o excesso são casos de teste das sondas: o corpo do PR precisa de `teto: excedido, 163 linhas, <motivo>`.

## Achados
- A1 (recomendado) tests/catraca.py:310 · Corrigido em 66a3a9a4: `hooks_contados` conta as chaves (Counter); `test_dois_hooks_com_a_mesma_chave_contam_dois` barra a retirada de um de dois hooks iguais.
- A2 (recomendado) tests/catraca.py:270 · Corrigido em 66a3a9a4: `_sem_aspas` tira só o par de aspas iguais; `test_script_entre_aspas_no_command_e_o_mesmo_script` cobre o par, aspas sem par e outro caractere nas pontas (CH-M14, CH-M15).
- A3 (recomendado) tests/mutantes/v047-catraca-hook-por-script-2.json:79 · Segue aberto: falta a isenta da apagada `ar or cm` (linha_base 277); o `motivo` da isenta existente cita `_opcao_inocua`, que não existe mais. Acrescentar a isenta e atualizar o motivo.
- A4 (recomendado) tests/catraca.py:258 · `b` na lista inócua deixa passar `-bb`, que faz do BytesWarning exceção (rc=1, não bloqueia): a mesma classe do `-W error` que o A5 da segurança tirou. Sem gatilho provado no hook atual; tirar `b` ou aceitar só `-b`.

## Sondas
- S1 · hooks.json real, hook conformidade do PreToolUse sem `args`, `"command": "python3 -s -E ${CLAUDE_PLUGIN_ROOT}/hooks/conformidade.py\nexit 0"` · espera: 1 removido · obtido: removidos 0 (mesma forma da S8 do A8 da segurança; prova independente, o achado é do domínio dela)

## Parecer
**Aprovado** no domínio do code review. A volta responde ao A1 e ao A2 deste parecer e ao A4 a A7 da segurança: `-I` e `-P` saíram da lista inócua, `-X` só com `utf8` (junto ou separado), `-W` volta à linha inteira, o interpretador é o 1º termo como escrito (só `env` do sistema sai da frente), o `timeout` entrou na chave e o controle do shell depois do script (`||`, `;`, `$(`) volta à linha inteira. Falha fechada em todo ramo novo.

Leitura: funções pequenas (`_sem_aspas`, `_termos_da_opcao_inocua`) com docstring do motivo; constantes nomeadas com o porquê no comentário; `chaves_de_hooks` mantida como fachada de `hooks_contados`; a mensagem de `regra_hooks` passa a mostrar o timeout. Testes: o ramo de falha de cada guarda nova tem caso de comportamento (subTest por troca em `test_hook_neutralizado_sem_tirar_o_script_barra`), e o corpus do hooks.json real afirma mínimo de 15 sondas e alvo único (checklist 11).

Guardas: um mutante por linha mudada (CH-M1 a CH-M8 e CH-M9 a CH-M15, duas specs); o CH-M4 troca `if not passo` por um `pop` para o laço terminar sob o mutante, aceitável. AR-12 conferido: as specs acompanham as linhas do commit.

Segurança fora do meu domínio, citada sem refazer: o parecer `docs/security/v047-catraca-hook-por-script.md` no head 66a3a9a4 (ed6aca1f, E2.114) está **reprovado** com A8 (a chave lê o `command` como o shell em toda forma: quebra de linha e espaço não ASCII escapam sem `args`, e com `args` o `command` não é dividido) e A9 (`if`, `async` e outros campos fora da chave). A classe não fecha até a volta, que muda `tests/catraca.py` e pede nova revalidação por delta. A classe "catraca lê o command diferente do shell" volta neste pedido (aspas no A2, quebra de linha no A8).

Verificadores citados (rodados aqui no head 66a3a9a4; a suíte inteira fica no CI do PR, que o item ainda não tem):
- `bin/forge-mutante tests/mutantes/v047-catraca-hook-por-script.json tests/mutantes/v047-catraca-hook-por-script-2.json`: CH-M1 a CH-M15 `morreu` (CH-M2 por erro do teste sob o mutante).
- `bin/forge-mutante --cobertura --base cb45a962`: não rodado; a trava R-TETO estava com outra sessão (fila 1 de 7). Fica com o autor (A3).
- `python3 -m unittest tests.test_catraca.Hooks tests.test_catraca.CorpusDasSondasDeHook`: `Ran 10 tests ... OK`.

Commits: 66a3a9a4 (fix), Conventional Commits em português com a etapa.
