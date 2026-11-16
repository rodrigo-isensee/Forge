---
tipo: qa
contrato: 1
pedido: v047-catraca-hook-por-script
branch: melhoria/v047-catraca-hook-por-script
commit: 230dfb01ddde3b7e84d47fdad161c8dbfc93ffc5
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-15
---
# QA: catraca, hook por script (v047, E2.84)

Escopo: `tests/catraca.py` (`script_do_hook`, `chaves_de_hooks`, `regra_hooks`), `tests/test_catraca.py`, corpus `tests/fixtures/catraca-hooks/sondas.json`, specs de mutantes. Sem especificação de UX nem API; as obrigações são o PR 565 (mudar interpretador, opções ou argumentos não remove o hook) e `R-CONFORMIDADE` (hook neutralizado segue acusado, A1 a A3 e S1 a S4 da segurança).

## Achados


## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| PR 565: `env`, `-s -E -X utf8` e argumentos extras não acusam | `Hooks.test_mudar_interpretador_opcoes_ou_argumentos_passa`, sonda PR565 | opção com valor (`-X`), `env` na frente | passou |
| Hook trocado acusa | `Hooks.test_script_trocado_barra` | arquivo diferente, mesmo evento | passou |
| Matcher mudado acusa | `Hooks.test_matcher_mudado_barra` | matcher | passou |
| Hook sem arquivo de código compara a linha inteira | `Hooks.test_hook_sem_script_compara_a_linha_inteira` | vazio (sem `command`, type prompt) | passou |
| Neutralização acusa (`-c`, `-m`, `-`, `-sc`, `/dev/null`, `true`, `echo`, prompt, `perl -E`) | `Hooks.test_hook_neutralizado_sem_tirar_o_script_barra`, `CorpusDasSondasDeHook` (S1 a S4, A3) | opção fora da lista inócua, outro interpretador | passou |
| Corpus não roda vazio | `CorpusDasSondasDeHook` (`>= 6` sondas, 1 alvo no hooks.json real) | suíte vazia | passou |

## Cenários e resultado real
- Head 40faab23; remoto (`git ls-remote`) igual ao head, nada a trazer por merge.
- `python3 -m unittest tests.test_catraca`: OK no head.
- Vermelho antes do verde: `bin/forge-testes --vermelho` ficou na fila da suíte e estourou o prazo de 400 s (rc 124, sem veredito, não vale como vermelho). Feito à mão numa cópia em `$TMPDIR` com `tests/catraca.py` da base `cb45a962` e os testes do head: `Ran 8 tests`, `FAILED (failures=11)`; caem os 5 testes novos de `Hooks` (cada subteste do neutralizado: `-c`, `-m`, `-`, `-sc`, `prompt`) e as sondas A3 e PR565 do corpus. Nenhum cai no head.
- Mutação (10 mutantes, 2 specs, `--processos 4`):
```
forge-mutante: pedido=v047 rev=40faab231edc spec=8b5a39c0... spec=4e61faa0...
CH-M1 a CH-M10 · morreu (CH-M2 por erro do teste declarado sob o mutante, que passa sem ele)
```
  Nenhum sobrevivente, nenhum equivalente.
- Cobertura (`--cobertura --base cb45a962`, rc=1): todas as condições mudadas de `script_do_hook` e `_opcao_inocua` saem `coberta`; a isenta de `not a.startswith("-")` sai `isenta`. Sobra `apagada · tests/catraca.py:277(base) · ar or cm`.
- Sobre a dúvida do brief: concordo, é limite da ferramenta. `ar or cm` era só texto da mensagem de acusação (`{ar or cm}` dentro do f-string), não decide nada; a nova mensagem é conferida por `test_script_trocado_barra` e `test_matcher_mudado_barra`. A ferramenta trata como condição qualquer `or` apagado e a isenta não aceitou o trecho de 6 caracteres.
- Bateria completa: não rodada aqui (a API do GitHub e a fila local impedem); a prova é o check-run `bateria` do mesmo sha no CI do PR (I5).
- Sondas extras lidas no código, sem bug: `-Xutf8` e `-Wignore` coladas passam; `-x` falha fechada; `-OO` passa.

## Revalidação por delta 40faab23..66a3a9a4 (E2.115)
- `forge-check parecer delta`: domínio com `tests/catraca.py`, `tests/test_catraca.py`, sondas, 2 specs de mutantes e changelog. O remoto avançou (1aad0483, só parecer do devops), trazido sem mudar o domínio.
- `python3 -m unittest tests.test_catraca`: OK no head.
- Vermelho antes do verde (manual, cópia em `$TMPDIR`, `tests/catraca.py` de 40faab23 e testes do head, classes `Hooks` e `CorpusDasSondasDeHook`): `Ran 10 tests`, `FAILED (failures=28)`. Caem os testes novos (`-I`, `-P`, `-W`, `-X` fora de utf8, `./python3`, `./env`, `timeout`, `||`, `;`, `$(`, aspas, dois hooks iguais) e as sondas S5 a S7, A7, shell-ou. Nenhum cai no head.
- Mutação, delta (`--base 40faab23 --processos 4`, 2 specs): `base=40faab231edc... rev=66a3a9a4bbca`, CH-M1 a CH-M15 todos `morreu` (CH-M2 por erro do teste declarado sob o mutante, que passa sem ele); nenhum sobrevivente. `--cobertura --base cb45a962` não rodou: fila R-TETO ocupada por outras sessões (posição 1 de 7); a conferência das condições mudadas fica ao review.
- Sondas manuais em `script_do_hook`, sem bug: `-Xutf8`, `-OO`, aspas em volta, `> /dev/null`, `&&`, barra colada, `utf8=2`, `command` vazio. Com bug: LF depois do script no `command` (A1).
- Bateria completa: a prova é o check-run `bateria` do mesmo sha no CI (I5); não rodada aqui.

## Revalidação por delta 66a3a9a4..ee91a8f0 (E2.148)
- Sem achados abertos. O A1 da volta 2 (bloqueante) está fechado em ee91a8f0 (tests/catraca.py:293), e o bug docs/qa/bugs/v047-quebra-de-linha-neutraliza-hook.md, resolvido.
- `forge-check parecer delta`: domínio com `tests/catraca.py`, `tests/test_catraca.py`, sondas, spec de mutantes `-3` e changelog. Remoto igual ao head, nada a trazer.
- A1 (reprodução no head, `script_do_hook`): `command` com `\n`, `\r`, `\t` ou `U+00A0` depois do script dá chave sem interpretador e com a linha inteira, diferente da do hook original. Corrigido.
- Delta lido: forma exec (`args`, mesmo vazio: o `command` é o executável inteiro, sem shell; `args` que não é lista falha fechada), lista positiva sem `args` (`[ -~]*`), campos fora de `statusMessage` e `once` entram na chave (`if`, `async`: acusam; `statusMessage`, `once`: não), `-b` fora das inócuas (`-b` fecha, `-bb` acusa). Sondas manuais: `python3 -- x.py` fecha; `PYTHONPATH=x python3 x.py` muda o interpretador e acusa; `command: "python3 x.py"` com `args: []` acusa (falso positivo aceitável, falha fechada).
- `python3 -m unittest tests.test_catraca.Hooks tests.test_catraca.CorpusDasSondasDeHook`: `Ran 12 tests`, OK; o corpus tem 28 sondas. O módulo inteiro `tests.test_catraca` também terminou com rc 0 no head.
- Vermelho antes do verde (manual, cópia em `$TMPDIR`, `tests/catraca.py` de 66a3a9a4 e testes do head, mesmas duas classes): `Ran 12 tests`, `FAILED`; caem `test_command_lido_como_o_claude_code_o_roda` (9), `test_campo_fora_da_lista_inocua_entra_na_chave` (6), `test_cada_sonda_acusa_o_esperado` (11), `test_hook_neutralizado_sem_tirar_o_script_barra` (2) e `test_hook_sem_script_compara_a_linha_inteira` (1). Nenhum cai no head.
- Mutação, delta (`--base 66a3a9a4 --processos 4`, spec `-3`): `base=66a3a9a4bbca... rev=ee91a8f00ceb`, CH-M16 a CH-M22 todos `morreu` (CH-M19 por erro do teste declarado sob o mutante, que passa sem ele); rc=0, nenhum sobrevivente, nenhum equivalente.
- Cobertura (`--cobertura --base 66a3a9a4`, rc=0): linhas 291, 292, 293, 298, 299 e 309 saem `coberta` (CH-M16 a CH-M21); a mudança de `OPCOES_INOCUAS_DO_PYTHON` (tirou `b`) não é condição e o CH-M22 a mata.
- Bateria completa: a prova é o check-run `bateria` do mesmo sha no CI do PR (I5); não rodada aqui.

## Critério → teste → resultado (volta 3)
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `R-CONFORMIDADE`: LF, CR, tab, NBSP no `command` acusam (A1) | `Hooks.test_command_lido_como_o_claude_code_o_roda`, corpus | separador de shell fora do ASCII imprimível | passou |
| Forma exec lida como o Claude Code a roda | idem, CH-M16, CH-M17 | `args` vazio, `args` fora de lista | passou |
| Campo extra do hook entra na chave | `Hooks.test_campo_fora_da_lista_inocua_entra_na_chave`, CH-M20, CH-M21 | `if`, `async`, campo novo; `statusMessage`/`once` não acusam | passou |
| `-b` não é inócua, `-bb` acusa | corpus, CH-M22 | opção nova na lista | passou |

## Revalidação por delta 79899789..230dfb01 (E2.168, volta 4: A10)
- Sem achados abertos. A10 (hooks.json fora do esquema da carga descarta todos os hooks) está fechado em `tests/catraca.py:336-405`: `EVENTOS_DO_HOOK` (lista fechada), tipos por campo, `NaN` e `Infinity` recusados, falha fechada.
- `python3 -m unittest tests.test_catraca.Hooks tests.test_catraca.CorpusDasSondasDeHook`: `Ran 14 tests`, OK; o corpus tem 36 sondas (S12 a S16 novas, mais `real` sem acusação).
- Vermelho antes do verde (manual, cópia em `$TMPDIR`, `tests/catraca.py` de 79899789 e testes do head): caem `test_cada_campo_fora_do_esquema_acusa` e as sondas do corpus por `AttributeError` (`erros_de_forma` não existe na base); nenhum cai no head.
- Mutação (`--base 79899789 --processos 4`, spec `-4`): `base=79899789af26 rev=230dfb01ddde`, CH-M23 a CH-M38 todos `morreu` (CH-M23, M32 e M35 por erro do teste declarado sob o mutante, que passa sem ele); nenhum sobrevivente. `--cobertura --base 79899789`, rc=0: 13 linhas mudadas todas `coberta`.
- Sondas manuais em `erros_de_forma`, sem bug: `timeout` booleano, `shell` ou `onFailure` fora da lista, `async` em texto, `args` texto, `NaN`, raiz `hooks` em lista acusam; hooks.json real, `timeout` 1.5, grupo sem `matcher`, grupo com `hooks` vazio passam; chave `hooks` duplicada vale a última (como o Claude Code).
- Observação, sem achado: `timeout` negativo ou zero passa; sem evidência de que a carga o recusa (baixa).
- Bateria completa: a prova é o check-run `bateria` do mesmo sha no CI do PR (I5); não rodada aqui.

## Critério → teste → resultado (volta 4)
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `R-CONFORMIDADE`: hooks.json fora do esquema acusa (A10) | `Hooks.test_hooks_json_fora_do_esquema_barra`, `test_cada_campo_fora_do_esquema_acusa`, CH-M23 a CH-M38 | evento fora da lista, tipo errado, NaN, JSON ilegível | passou |
| Corpus S12 a S16 acusa e `real` não | `CorpusDasSondasDeHook.test_cada_sonda_acusa_o_esperado` | `type` ausente, `timeout` texto, `args` não texto, evento e `matcher` inválidos | passou |
