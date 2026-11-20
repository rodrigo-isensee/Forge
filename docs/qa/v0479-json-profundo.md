---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-json-profundo
commit: fbab4dede7912d7650c8787b4edbbaed2e73e1fb
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-json-profundo (v0478 E44.1, JSON-PROFUNDO-PY314)

Teto de 64 níveis de `[` e `{` antes do `json.loads` no estado dos hooks (`hooks/agentes.py`), na catraca (`tests/catraca.py`) e no `--ci` do `bin/forge-placar`, com a fonte em `hooks/_json_raso.py`. Só os módulos tocados rodaram (sem suíte local; a suíte inteira é o check-run `bateria` do CI do PR). Sem especificação de UX: as obrigações são as do comportamento descrito no código e nos testes do autor (acima do teto recusa com mensagem fixa; no teto passa; dentro de string não conta; as três cópias iguais).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Estado dos hooks acima de 64 níveis é ilegível, no teto lê | `test_estado_ilegivel.LerEstado.test_json_aninhado_fundo_e_ilegivel` (aberto 200000, fechado 65 e 5000, fechado 64 passa) | 64/65 níveis | passou (M2 morreu) |
| Catraca recusa acima do teto com mensagem fixa e sem traceback | `test_catraca.Hooks.test_json_aninhado_acima_do_teto_e_ilegivel` | 64/65, `[` em string | passou (M3, M13 a M20 morreram) |
| `--ci` do placar acima do teto sai com 2, sem traceback, e no teto não recusa | `evals.test_placar.Medir.test_ci_aninhado_acima_do_teto_sai_com_2_sem_traceback` | 64/65, aberto, fundo | passou (M1 morreu) |
| As três cópias respondem igual; bytes UTF-8/16/32 contam como o `json` | `test_json_raso.TetoComum` (2 testes) | 64/65, escape `\"`, string, UTF-16/32, bytes inválidos | passou (M4 a M12 morreram) |
| Mapa do `forge-testes` leva o placar ao `test_json_raso` | `test_testes_tocados` (164 testes, 1 pulado: `/proc` de outro namespace, já na base) | n/a | passou |

## Provas
Módulos tocados com `python3 -I`: `test_json_raso` 2 ok; `test_estado_ilegivel` 9 ok; `test_testes_tocados` OK (skipped=1); o teste novo do `test_catraca` e o do `evals.test_placar` ok por `-k`.

Vermelho (`forge-testes --vermelho 004ce869d641ca62394d705c4453d8a014002f15 --modulos test_json_raso,test_estado_ilegivel,test_catraca`; `--modulos` não aceita `evals.*`):
```
vermelho: base=004ce869d641 head=fbf2c6f7936d módulos=test_json_raso,test_estado_ilegivel,test_catraca (restrito por --modulos)
tests.test_catraca.Hooks.test_json_aninhado_acima_do_teto_e_ilegivel · H=ok · B=erro · prova (API ausente)
tests.test_catraca.TetoDaQuarentena.test_o_forge_nao_passa_do_teto_da_quarentena · H=ok · B=erro · sem veredito
tests.test_estado_ilegivel.LerEstado.test_json_aninhado_fundo_e_ilegivel · H=ok · B=falha · prova (asserção)
tests.test_json_raso.TetoComum.test_as_copias_respondem_igual · H=ok · B=erro · prova (API ausente)
tests.test_json_raso.TetoComum.test_bytes_contam_como_o_json_os_decodifica · H=ok · B=erro · prova (API ausente)
sem veredito: volta ao autor; não vale como vermelho nem como já falhava.   (rc=2)
```
O "sem veredito" é teste antigo e inalterado do `test_catraca` (varre `tests/` atrás de pulados): na cópia mista (testes no HEAD, código na base) ele erra por importar o `test_json_raso` novo sem o `_json_raso`; no HEAD passa. É efeito da cópia mista, não defeito. Os quatro testes novos têm vermelho provado.

Vermelho do placar à mão (cópia em `$TMPDIR`, HEAD com o `bin/forge-placar` da base): `Ran 1 test ... FAILED (failures=3)` (os três subtestes aberto, fechado e fundo caem).

Mutação (`forge-mutante` nas três specs do autor, `--processos 3`; 20 mutantes, saída 0):
```
M1 · morreu · bin/forge-placar:198
M2 · morreu · hooks/agentes.py:415
M3 · morreu · tests/catraca.py:128
M4 · morreu · hooks/_json_raso.py:22 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
M5 a M12 · morreu · hooks/_json_raso.py:27,28,30,32,34,36,38,40
M13 a M20 · morreu · tests/catraca.py:106,107,109,111,113,115,117,119
rc=0
```
`forge-mutante --cobertura --base 004ce869d641ca62394d705c4453d8a014002f15`: todas as condições mudadas saem `coberta`, nenhuma `não coberta` nem `isenta`.

Sonda minha em `ler_estado` (não é teste do autor): bytes inválidos `\xff\xfe\xfd[` saem ilegíveis (JSONDecodeError); `{"agentes":[]}` e o mesmo com BOM UTF-8 leem; 80000 bytes de `[\x00` saem "aninhado acima de 64 níveis". Sem achado.

Fora do diff, anotado: `hooks/` ainda tem `json.loads` de `plugin.json`, `config.json`, `_maquina.py` e `vigia.py` sem o teto; são arquivos do próprio projeto ou linhas curtas, fora do pedido (E44.1 cita estado, catraca e placar).

## Revalidação (head fbab4ded, E44.5)
`forge-check parecer delta`: intervalo fbf2c6f7..fbab4ded, só `docs/indice-forge.md` no domínio (uma linha nova de `hooks/_json_raso.py`, sem código nem teste). Merge da develop fora do escopo. `python3 -I -m unittest discover -s tests -p test_indice_forge.py`: 19 testes OK. O resto do parecer anterior segue valendo; a suíte inteira é o check-run `bateria` do CI.
