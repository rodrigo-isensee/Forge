---
tipo: qa
contrato: 1
pedido: v047-catraca-hook-por-script
branch: melhoria/v047-catraca-hook-por-script
commit: 66a3a9a4bbcafbd3588f564bd2fc2a81964fe3e6
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-15
---
# QA: catraca, hook por script (v047, E2.84)

Escopo: `tests/catraca.py` (`script_do_hook`, `chaves_de_hooks`, `regra_hooks`), `tests/test_catraca.py`, corpus `tests/fixtures/catraca-hooks/sondas.json`, specs de mutantes. Sem especificação de UX nem API; as obrigações são o PR 565 (mudar interpretador, opções ou argumentos não remove o hook) e `R-CONFORMIDADE` (hook neutralizado segue acusado, A1 a A3 e S1 a S4 da segurança).

## Achados
- A1 (bloqueante) tests/catraca.py:261 · `CONTROLE_DO_SHELL` não tem quebra de linha: `command: "python3 x.py<LF>exit 0"` dá a mesma chave do hook original (split() descarta a LF), então o hook neutralizado não acusa (R-CONFORMIDADE). Bug em docs/qa/bugs/v047-quebra-de-linha-neutraliza-hook.md

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
