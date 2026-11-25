---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: 4ab16b74a90aa0d9214d1a6c32764dfac9e7fe89
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 prazo-forge (#888, classe C), delta 1d6692f5..4ab16b74 (E7.46)

- ci: 4ab16b74a90aa0d9214d1a6c32764dfac9e7fe89 verde

Escopo: `git diff 1d6692f5..4ab16b74` lido sem o merge da develop (`5f99d144`): `hooks/_comum.py` (`idade_do_processo`, `prazo_da_etapa`, `resta`, parâmetro `idade` de `executar`), `hooks/conformidade.py` (só docstring), `test_hooks.py`, `test_hooks_volta_corpus.py`, `test_hooks_volta_propriedades.py`, spec `v0481-prazo-forge-3.json` (M14 a M21), M22 em `-2.json`, fixtures renomeados, changelog. Parecer anterior (1d6692f5, aprovado) lido. Clone `/root/.forge-contrib/wt/v0481-prazo-forge-qa-engineer`, no head do remoto (`git ls-remote` = 4ab16b74).

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A5 (E7.32) e A6/A1 (E7.40): o prazo conta da partida do processo; a recusa do `gh pr merge` com FIFO no .git sai antes do corte de 10 s | `PrazoVencidoNaSessaoDoForge.test_partida_lenta_recusa_o_merge_antes_do_corte` (parede real, partida 3 s atrasada) | idade do processo + 7,5 + 0,5 + 0,5 abaixo de 10 s | passou |
| Sessão e registro cabem no que resta do teto; sem tempo, a sessão recusa e o registro não roda | `SondaS1ComRelogioFalso` (relógio falso) | resta <= 0 | passou; M14 a M21 morrem |
| Prazo vencido sem prazo do hook (forçado) conta o teto pelo prazo comum | `test_prazo_vencido_sem_prazo_do_hook_registra` | `prazo_s` vazio | passou; M22 morre |
| `idade_do_processo` só no processo do hook, 0 sem `/proc` | `test_idade_do_processo_so_no_processo_do_hook_e_zero_sem_proc` | argv[0] alheio, sem `/proc` | passou |
| `idade` fora dos hooks e do driver do lote | `test_hooks_volta_corpus` (assinatura keyword-only, default None) | chamada com `idade` | verde no CI |

## Resultado real
- **A5 fechado, sem enfraquecer teste.** Linhas removidas dos testes e specs lidas: só trocas de docstring, o `idade` somado às asserções de assinatura e ao conjunto proibido, e o `de/para` dos mutantes seguindo a assinatura nova. Nenhum `skip`, nenhuma asserção afrouxada. O teste de partida lenta passou a usar o FIFO no `HEAD` (o do `commondir` já recusa antes, desde o #886): o caminho que espera o git, o do A5, segue coberto.
- Local, só os módulos tocados: `python3 -m unittest tests.test_hooks.SondaS1ComRelogioFalso tests.test_hooks.PrazoVencidoNaSessaoDoForge tests.test_hooks_volta_propriedades.VigiaAgentesPesado`: `Ran 19 tests in 29.775s OK`. `test_hooks_volta_corpus` roda inteiro no CI (verde lá).
- Mutantes do delta: `bin/forge-mutante tests/mutantes/v0481-prazo-forge-3.json --base 1d6692f5 --processos 2` (cabeçalho `base=1d6692f507ac... rev=4ab16b74a90a`): M14 a M21 `morreu` (M15 por erro do teste declarado, que passa sem o mutante). `-2.json` com `--base 1d6692f5`: M9 a M13 e M22 `morreu` (M9 e M22 por erro do teste declarado). Nenhum sobrevivente. `bin/forge-mutante --cobertura --base 5f99d144` sem condição descoberta.
- Vermelho antes do verde: M22, M19 e M21 são os vermelhos dos testes novos (o mutante é a implementação quebrada, e o teste cai).
- Nada que barra hoje deixa de barrar: a idade só encurta o prazo restante; sem `/proc` ou fora do processo do hook, vale 0 (o comportamento de antes).

## CI do PR (PARECER-LE-O-CI)
`gh pr checks 888` (com `XDG_CACHE_HOME` gravável), runs do head `4ab16b74`: as 10 partes da suíte (3.12 e 3.14, 5 de 5), `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação`, `teto de pulados` e `árvore já provada na develop` estão `pass`. Falham só os três que esperam o parecer ou o rótulo:
- `bateria (pareceres)` e `bateria`: faltam pareceres no head (este grava o do QA; `bateria` repete o resultado de `PARECERES: failure`).
- `catraca` (log lido): R-CONFORMIDADE pede o rótulo `afrouxa-regra` do dono para `hooks/_comum.py` e `hooks/conformidade.py` (controles), depois do último push; R-QA lista a guarda `critico is None and evento != 'PreToolUse'` (`_comum.py:2875` da develop atual `6cc4cd5a`) como "apagada" sem mutante: a guarda foi refeita em `recusa = evento != "PostToolUse" and (critico is not None or evento == "PreToolUse")` (já coberta por M1, de rodadas anteriores). Aviso "valor esperado trocado" em `test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo_com_disputa_provada`, que não barra.

## Achados
Nenhum.
