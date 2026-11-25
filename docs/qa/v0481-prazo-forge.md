---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: 21a96c1ab06722ed0e7b9cc7c3276912ea841b49
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 prazo-forge (#888, classe C), delta a4d12870..21a96c1a (E7.29)

Escopo: `git diff a4d12870..21a96c1a` lido: `hooks/_comum.py` (`registrar_sob_vigia`, a sessão decidida antes do registro, erro interno pelo mesmo caminho), `hooks/conformidade.py:130` (`mkfifo|mknod` em `ESCRITA_NO_TEXTO`), fixture `fifo-python-mkfifo-git-projeto-bloqueia`, 2 testes novos, 3 contagens de armados ajustadas, `tests/mutantes/v0481-prazo-forge-2.json` (M9 a M12) e 4 specs antigas realinhadas. Parecer anterior (commit a4d12870, aprovado, A1 a A3) lido. Clone: `/root/.forge-contrib/wt/v0481-prazo-forge-qa`.

## Achados
- A1 (recomendado) hooks/conformidade.py:130 · Na sessão do Forge, `python3 -c` com `os.mkfifo`/`os.mknod` no `.git` libera (rc 0), como já liberava `os.remove` no `.git` (paridade com a base); só o projeto recusa. O FIFO no `.git` por interpretador segue só no corte de prazo. Cartão.
- A2 (recomendado) hooks/conformidade.py:1776 · `mkfifo $TMPDIR/p` (alvo opaco) recusa nas duas sessões: fricção legítima, pelo desenho. Vale nota na mensagem ou no doc. Cartão (vem do A3 anterior).

## Situação dos achados anteriores
- A1 anterior (registro lento recusava sem marcador): fechado. Sonda de carga em arquivo, 16 combinações (Forge e projeto, sessão vigiada ou não, marcado ou não, registro de 0 s e de 0,8 s): o rc é igual com e sem atraso; o registro lento custa 0,50 s (o vigia) e nunca muda a decisão. Sem marcador e sessão não vigiada, libera (rc 0); marcado no Forge, 2.
- A2 anterior: fechado só para o projeto (fixture nova); a sessão do Forge virou o A1 acima.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Registro lento ou que falha não muda a decisão (E7.27) | `test_registro_que_nao_termina_nao_muda_a_decisao` | lento (5 s) e `OSError`, marcado e não, sessão não vigiada, menos de 4 s | passou |
| Erro interno: registro sob vigia, sem esperar o corte de 10 s | `test_erro_interno_com_registro_lento_nao_espera_o_corte` | registro de 5 s, rc 0, menos de 4 s | passou |
| FIFO no commondir e no gitdir, nas duas sessões | `test_fifo_no_commondir_e_no_gitdir_recusa_nas_duas_sessoes` (16 casos) | `commondir`/`gitdir` como FIFO | passou |
| mkfifo/mknod no .git recusam (7 fixtures, mínimo 7 afirmado) | `test_fixtures_fifo` | .git, curinga, opaco, `cd .git`, python no projeto | passou |
| Prazo vencido na sessão do Forge (E7.23, regressão) | `test_sessao_do_forge_recusa_so_a_linha_marcada`, `test_sessao_que_nao_se_decide_recusa` | marcado True/None/False, PostToolUse | passou |

## Cenários e resultado real
- Rodado só o item: `python3 -m unittest tests.test_hooks.PrazoVencidoNaSessaoDoForge tests.test_hooks.SondaS1ComRelogioFalso tests.test_hooks_volta_propriedades.VigiaAgentesPesado`: `Ran 11 tests in 16.490s OK`. A suíte inteira roda no CI do PR; não cito o `.verde` local.
- Vermelho antes do verde (cópia em `$TMPDIR`, `hooks/_comum.py` e `hooks/conformidade.py` da base, testes do head): os 3 testes novos caem (lento: FAIL; falha do registro: ERROR; erro interno: FAIL; 6 fixtures fifo: FAIL, incluindo a nova). O `forge-testes --vermelho` não foi usado; vale a cópia manual.
- Mutantes: `bin/forge-mutante tests/mutantes/v0481-prazo-forge.json tests/mutantes/v0481-prazo-forge-2.json --processos 2`: M1 a M12 `morreu` (M4 e M9 por erro do teste declarado, que passa sem o mutante); nenhum sobrevivente. `forge-mutante --base a4d128703 tests/mutantes/v0481-prazo-forge.json`: `base=5fb8e328... mb=5fb8e328... rev=21a96c1a...`, M6 a M8 mortos. `--cobertura --base 5fb8e328...`: rc 0, as linhas de guarda mudadas (`_comum.py` 2860, 2887, 2890, 2894; `conformidade.py` 1776, 2511) têm mutante; `registrar_sob_vigia` (M9, M11) e o regex (M12) cobertos pela spec 2.
- Specs realinhadas (`heredoc-donos`, `lote-unico-032-l31`, `v0480-vigia-agentes-pesado`, `v0480-vigia-trava-critica`): `--conferir --todas` no head e na base 5fb8e328 dão a mesma saída (26 linhas, `diff` vazio: igual à base; as 26 são trechos duplicados de specs não tocadas, dívida anterior). Mutantes rodados: lote, agentes-pesado e trava-critica, todos mortos (rc 0). `heredoc-donos` D15: `controle vermelho` (rc 2) idêntico na base 5fb8e328 (`--ids D15`): preexistente, fora do delta (o `test_fixtures` do controle cai neste sandbox); não bloqueia e não é do #888.
- Hook real (sondas em arquivo, 18 linhas, forge:dev e forge:tech-lead, só o rc): `mkfifo`/`mknod` com .git, curinga, `cd .git`, `command`, `env`, `--mode`, `--` e opaco: 2 nas duas sessões; push na main, `--force`, `--no-verify`: 2; `mkfifo /tmp/x`, `mkfifo build/pipe`, `ls`: 0. Python com `os.mkfifo`/`os.mknod` no `.git`: projeto 2, Forge 0 (A1); `node` com `execSync('mkfifo .git/f')`: projeto 2, Forge 0.
- Sem acessibilidade nem E2E (hook de linha de comando).
