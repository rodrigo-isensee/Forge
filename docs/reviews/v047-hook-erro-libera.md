---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-hook-erro-libera
commit: 804c96124a10056bd58c621c6e7e2aa5274a0cd5
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 · HOOK-ERRO-LIBERA (E3.16)

Head revisado 9e3f57c6 (merge da develop c5aa70e1 sobre a série de commits da E3.7 e E3.11). Classe C, instância que não fez a entrega.

## Achados
- A1 (recomendado) hooks/conformidade.py:730 · `os.path.expanduser` segue solto em conformidade.py:730 e :2452 e em parecer.py:473 e :829; não lança, mas a C1 pede função única e o teste só barra `.expanduser()` literal. Unificar em `expandir_home` na próxima passada.
- A2 (recomendado) hooks/_comum.py:2744 · `barrar_sem_versao` também usa `marcado`, agora ampliado: sem `.forge/versao`, a escrita que cita caminho da política ou tem alvo opaco passa a recusar (R-CONFORMIDADE). Coerente com a intenção, mas fora do texto das ADRs 0003 e 0009; dizer no corpo do PR.
- A3 (recomendado) hooks/_comum.py:2785 · a C5 exige no corpo do PR a medida das linhas de prazo vencido do `erros.log` da cópia principal que passariam a recusar; não há no branch. Levar ao PR, número medido.

## Sondas

## Parecer
Aprovado. Condições conferidas no código e nos testes:
- C1: `expandir_home` em `_comum.py:94` e uso nos 4 pontos de `Path(...).expanduser()` de `conformidade.py` (:881, :976, :2121, :2376); zero `.expanduser()` literal em `hooks/*.py`, com teste estrutural (A1 é o resíduo de `os.path`).
- C2 e C3: `termos_da_politica` monta os termos do JSON real (sem barra final, `~/` em quatro formas mais o home real, `*` como `[^/\s]*`); `ESCREVE_NA_LINHA` é a união pedida; política ilegível ou sem `caminhos` marca tudo; `ALVO_OPACO` cobre `$`, crase e `<(`. O teste gera `cp x <entrada>` de cada uma das 48 entradas.
- C4: `arquivo_marcado` resolve o caminho (link, `..`, `~`) contra a raiz da sessão ou a política; caminho vazio marca; coberto por teste e fixtures de Write/Edit.
- C5: `prazo_vencido` passa pelo mesmo `marcado`; `marcado` captura `Exception` e marca (falha fecha). Fixtures `errointerno-prazo-*`. Medida em A3.
- C6: `-s -E` nas 18 entradas do `hooks.json`, com teste estrutural e sonda E7 (`usercustomize` e `sitecustomize` com `os._exit(0)`; com a linha do hooks.json rc 2, sem as opções rc 0). A catraca ajustada ignora opções antes do script, e trocar o script ainda conta como remoção.
- C7: `conferir_brief` roda antes do estado, com `try` que recusa em qualquer exceção; a liberação de agente morto grava antes da recusa; `SystemExit` do `bloquear` não é engolido. Fixtures do `agentes` (estado corrompido, clone sem estado, selo, forma, hash).
- C8: ADR 0003 (item 4), ADR 0009 (seção 7), `docs/hooks.md` e docstring de `registrar_erro` atualizados no mesmo branch (E3.11: cada mudança em `_comum.py`, `agentes.py` e ADRs vem de C5, C7 ou C8).

Teto M14: 432 linhas de código e teste (`git diff --numstat --no-renames origin/develop...HEAD` nos caminhos que contam), acima das 150; uma classe só (falha fechada do hook por erro e prazo), com corpus próprio. O corpo do PR precisa de `teto: excedido, 432 linhas, <motivo>`.

Provas rodadas por mim: `tests/test_hook_erro_libera.py` com 11 testes, OK (35 s); `bin/forge-mutante` nas 5 specs (`v047-hook-erro-libera.json` e `-2` a `-5`): todos os mutantes morreram, nenhum sobrevivente (M3, M4, M15, M20 e M23 morrem por erro do teste declarado, não por asserção). Sem PR aberto, não há CI a citar; a suíte inteira fica para o CI do PR.

## Revalidação (E3.35) · delta 9e3f57c6..4c350b2f

Lido `forge-check parecer delta`: intervalo 9e3f57c6..4c350b2f, domínio de código e testes (hooks/conformidade.py, hooks/_comum.py, bin/forge-testes, 14 fixtures `errointerno-*` novos, specs `-2` e `-5`, `test_hook_erro_libera.py`, `test_testes_tocados.py`). Instância que não fez a entrega.

- `ESCRITORES` agora inclui `CAMINHOS_NO_GIT` (rm, mv, checkout, restore) e `GIT_GRAVA_ARQUIVO` (apply, am), reaproveitando as listas da guarda normal, sem lista paralela.
- `BASE_TROCADA` (cd, pushd, popd, -C, --chdir, --git-dir, --work-tree, GIT_DIR, GIT_WORK_TREE) marca a linha que escreve; a aspa antes do `cd` pega `sh -c '...'` e `bash -c "..."`. Sondei à mão: `cd docs && cp`, `sh -c 'cd ..'`, `git -Cdocs checkout`, `env -C`, `command cd` marcam; `cdrom=1 cp` não casa `cd`; `cd build && ls` libera (fixture legítimo).
- Os 14 fixtures cobrem o ramo de falha de cada verbo e o legítimo (`git-checkout-de-branch-libera`, `cd-e-ls-libera`); os mínimos do teste subiram (39 e 7).
- Achados A1 a A3 da passada anterior seguem recomendados e não bloqueiam.

## Achados da revalidação
- A4 (recomendado) hooks/conformidade.py:2831 · `git -c core.worktree=<fora> checkout -- a` (relativo, sem termo da política) não marca no erro interno: `BASE_TROCADA` não vê `-c core.worktree`. Gatilho remoto (exige erro interno do hook no mesmo comando) e a guarda normal já trata; somar `core\.worktree` na próxima passada.

## Parecer da revalidação
Aprovado no 4c350b2f. Sem bloqueante: nenhum defeito provado nem requisito ou segurança com gatilho.

Teto M14: 445 linhas de código e teste, acima das 150; uma classe só (falha fechada do hook por erro e prazo), com corpus próprio. O corpo do PR precisa de `teto: excedido, 445 linhas, <motivo>`.

Provas rodadas por mim: `python3 -m unittest -q tests.test_hook_erro_libera tests.test_testes_tocados` 161 testes, OK (1 pulado por /proc do sandbox, alheio ao diff). `bin/forge-mutante` nas specs `v047-hook-erro-libera.json`, `-2` e `-5`: todos os mutantes morreram, nenhum sobrevivente (inclui M12, M13 e M34 a M40). Sem PR aberto, não há CI a citar; a suíte inteira fica para o CI do PR.

## Revalidação (E3.39) · delta 4c350b2f..9666b6bf (junção da develop)

Lido `forge-check parecer delta`: domínio de código e testes, escopo sem o que veio da base. Instância que não fez a entrega. Entram `bin/forge-testes` (linha do mapa para `templates/projeto/.forge/config.json`, da develop), `tests/apoio_volta_unica.py` e `tests/test_hooks.py`.

- Conflito em `tests/test_hooks.py` (`test_rotulo_so_dono_gh_pendurado_decide_antes_do_timeout_do_hook`): a resolução manteve os dois lados, `h["args"][-1]` (desta branch, igual aos demais usos do arquivo e de `test_doutor.py`) e `teto = (limite - 1) * fator_de_carga()` (da develop). O `sleep 30` do falso `gh` segue acima do teto máximo (`limite - 1` vezes 2 no pior caso), então o teste ainda pega o `gh` pendurado.
- `nucleos_do_processo` e `fator_de_carga` migraram para o apoio, antes do import de `test_hooks`, e `test_hooks` as importa de volta no fim do módulo. Importei nas duas ordens (apoio primeiro e `test_hooks` primeiro) sem erro; `fator_de_carga(4, 2)` dá 2.0 (teto) e `fator_de_carga(1, 4)` dá 1.0.
- Nenhuma guarda do hook mudou neste delta; os mutantes anteriores seguem valendo.

Achados da revalidação: nenhum novo. A4 (recomendado, passada anterior) segue aberto e não bloqueia.

## Parecer da revalidação (E3.39)
Aprovado no 9666b6bf. Sem bloqueante.

Provas rodadas por mim: o teste do `gh` pendurado, OK (6 s); `tests.test_hook_erro_libera` 11 testes, OK; `tests.test_testes_tocados` 150 testes, OK (1 pulado, /proc do sandbox, alheio ao diff). Sem PR aberto, não há CI a citar; a suíte inteira fica para o CI do PR.

## Revalidação (E3.44) · delta 9666b6bf..804c9612 (E3.42: dois testes corrigidos)

Lido `forge-check parecer delta`: intervalo 9666b6bf..804c9612, domínio de código e testes; entram `docs/hooks-fixtures.md`, `tests/apoio_volta_unica.py` e `tests/test_hooks_volta_corpus.py`. Instância que não fez a entrega.

- `tests/apoio_volta_unica.py:403`: o driver do lote passa a `executar` o `MARCADOR` do conformidade, o mesmo do `__main__` do hook (`hooks/conformidade.py:2959`, `MarcadorDaPolitica` em :2893); antes passava `CRITICO`, e o lote decidia com marcador diferente do subprocesso.
- `tests/test_hooks_volta_corpus.py:108` e a docstring acompanham. Mutante à mão (driver de volta a `CRITICO`, numa cópia por `git archive`): o teste do driver falha com `{'conformidade': 'CRITICO', ...} != {'conformidade': 'MARCADOR', ...}`; morre.
- `docs/hooks-fixtures.md`: índice regerado (2463 fixtures, `errointerno-*` 31); `scripts/indice-fixtures.py --conferir` dá "em dia".
- Nenhuma guarda do hook mudou neste delta; os mutantes declarados seguem valendo.

Achados da revalidação: nenhum novo. A1 a A4 (recomendados, passadas anteriores) seguem abertos e não bloqueiam.

## Parecer da revalidação (E3.44)
Aprovado no 804c9612. Sem bloqueante.

Provas rodadas por mim: `test_driver_do_lote_chama_o_executar_como_o_main_de_cada_hook` OK; `test_decisao_em_lote_igual_ao_subprocesso_do_hook` e `test_corpus_nos_dois_hooks` OK (2 testes, 206 s). CI do PR 550 no head 93fe731e ainda com a suíte pendente; `catraca` vermelha pede o rótulo `afrouxa-regra` do dono (mudança em `hooks/`, R-CONFORMIDADE), fora deste delta, e a `bateria (pareceres)` depende dos pareceres no head. A suíte inteira fica para o CI.
