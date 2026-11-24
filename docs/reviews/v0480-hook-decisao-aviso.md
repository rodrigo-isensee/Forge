---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-hook-decisao-aviso
commit: 2ecd153cf6433fab911a286b4fb5bf19ede4cde6
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E172.10 (PR #857, hook decisao só avisa no Stop do Jarvis; código de E172.6)

Diff revisado: `5f1c6e97..2ecd153c` (7 arquivos, +231/-1; código de produção `hooks/decisao.py` 44 linhas e `hooks/hooks.json` +10, dentro do teto H1).

## O que está certo
- `hooks/decisao.py` reusa as fontes únicas (`medir_decisoes` de `bin/forge_transcricao.py`, `mensagem_ao_dono` do `meta`, `sessao_do_jarvis` do `vigia`); sai só por `systemMessage`, nunca `decision` nem `additionalContext` (ADR 0003, item 1); sem escrita; erro interno pelo `executar`.
- `tests/test_hook_decisao.py`: 11 casos, um por ramo de silêncio e de aviso, em subprocesso com ambiente limpo e `-I`; rodado aqui: `Ran 11 tests ... OK`.
- Mutantes M1 a M6, um por guarda; a catraca do PR está verde.

## CI do head 2ecd153c
Run 45424053750 vermelho. Fora o `bateria (pareceres)` (esperado com os pareceres pendentes), quatro testes falham pelo diff e reproduzem aqui no head (`python3 -m unittest test_hooks.Hooks.test_hooks_json test_hooks.Hooks.test_cada_hook_tem_caso_que_passa_e_que_bloqueia test_forge.PesosDaSuite.test_pr_nao_aumenta_os_modulos_sem_peso`: `FAILED (failures=3)`); o quarto, `test_testes_tocados`, está no log da parte 1/5. O PQ do autor ("644 OK") não cobriu `test_hooks`, `test_testes_tocados` nem `test_forge`.

## Achados
- A1 (bloqueante) hooks/hooks.json:313 · o decisao entra no Stop sem atualizar a lista do test_hooks_json (tests/test_hooks.py:1546), que só admite meta, _maquina, vigia e doutor no Stop: CI vermelho na parte 1/5. Inclua o decisao na lista e no texto do assert, citando a regra que o permite.
- A2 (bloqueante) hooks/decisao.py:1 · hook novo sem fixtures em tests/hooks/decisao/ (ADR 0003, item 8): test_cada_hook_tem_caso_que_passa_e_que_bloqueia falha. Traga sem-forge-versao, erro-interno e um caso de aviso, e ponha o decisao na tupla dos que só avisam (tests/test_hooks.py:1530).
- A3 (bloqueante) tests/test_hook_decisao.py:1 · módulo de teste novo sem peso em tests/pesos-d4.json: test_forge.PesosDaSuite.test_pr_nao_aumenta_os_modulos_sem_peso falha (['test_hook_decisao'] != []) na parte 3/5.
- A4 (bloqueante) tests/test_hook_decisao.py:1 · o mapa de testes tocados não liga hooks/decisao.py nem hooks/hooks.json ao test_hook_decisao: MapaCobreOQueOsTestesLeem.test_todo_arquivo_lido_por_um_modulo_roda_esse_modulo falha nos dois caminhos (parte 1/5).
- A5 (recomendado) hooks/decisao.py:28 · o corte em 20.000 caracteres vem antes de medir_decisoes, que procura o Recomendo até o fim do texto: grupo perto do teto com a recomendação depois do corte dá aviso falso. Medir o texto inteiro só para o Recomendo, ou um caso de teste que fixe o comportamento.

## Sondas
- S1 · python3 -m unittest test_hooks.Hooks.test_hooks_json (em tests/, head 2ecd153c) · espera: OK · obtido: FAIL, {'decisao.py', ...} not less than or equal to {'meta.py', '_maquina.py', 'vigia.py', 'doutor.py'}
- S2 · python3 -m unittest test_hooks.Hooks.test_cada_hook_tem_caso_que_passa_e_que_bloqueia · espera: OK · obtido: FAIL, decisao sem fixtures em tests/hooks/
- S3 · python3 -m unittest test_forge.PesosDaSuite.test_pr_nao_aumenta_os_modulos_sem_peso · espera: OK · obtido: FAIL, Lists differ: ['test_hook_decisao'] != []
- S4 · log do CI, job 138552436157 (parte 1/5), test_testes_tocados · espera: OK · obtido: FAIL para modulo='test_hook_decisao' em hooks/decisao.py e hooks/hooks.json

## Na volta
Revalide pelo delta (`forge-check parecer delta docs/reviews/v0480-hook-decisao-aviso.md`): A1 a A4 se fecham com o CI verde nas cinco partes e no `bateria`.
