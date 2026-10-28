---
tipo: review
contrato: 1
pedido: flaky-ctrlc-troca
branch: melhoria/flaky-ctrlc-troca
commit: a6adac96786de046c4eb5db80b7eff038de159a3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: flaky-ctrlc-troca

Escopo lido: `41ba611...a6adac9` (1 commit, 3 arquivos: `tests/test_atualizar.py` +14/-1, `tests/mutantes/flaky-ctrlc-troca.json`, `changelog.d/flaky-ctrlc-troca.md`). Teto M14: 15 linhas contadas (`tests/*.py`); o JSON do mutante e o fragmento ficam fora. Nenhum arquivo de `hooks/` nem de `PROTEGIDOS`. Pedidos lidos: `FLAKY-CTRLC-TROCA` e `FLAKY-CTRLC-TROCA-REV`. PA-7 (`docs/engineering/achados-recorrentes.md`): lista vazia, nada a conferir.

## Achados
- A1 (recomendado) tests/test_atualizar.py:165 · o preexec_fn não é seguro com threads vivas no processo da suíte (aviso da documentação do subprocess); hoje nenhum teste deixa thread viva no momento do Popen, mas se surgir, trocar por um script de arranque que volta o SIGINT ao padrão e faz exec

## Diagnóstico conferido
- Causa: `.githooks/pre-push:297` lança a suíte com `&` (desde `74f712d`); o bash sem controle de jobs deixa SIGINT ignorado no filho assíncrono e o Python que nasce com SIGINT em `SIG_IGN` não instala o `KeyboardInterrupt`. O `kill -INT $PPID` do `claude` falso some, o falso sai com 1 e o `forge atualizar` trata como falha comum ("Não deu para trocar o plugin"). Não é a corrida do `sleep 0.6`: a suposição do pedido cai.
- Reprodução (cópia em `$TMPDIR`, sem o `preexec_fn`): `CtrlCNaTroca` com SIGINT ignorado no processo da suíte reprova o teste original de forma determinística (`'Nada foi atualizado' not found`, saída com "Não deu para trocar o plugin"); com SIGINT padrão passa. Com a correção: `CtrlCNaTroca` sob SIGINT ignorado `Ran 8 tests ... OK`; `tests.test_atualizar` inteiro sob SIGINT ignorado `Ran 79 tests ... OK`; o teste original 30 vezes seguidas sob SIGINT ignorado, 30/30.

## Alcance do preexec_fn
- Vale só para o caminho com `respostas` (pty) do `rodar`; o caminho sem terminal não muda. O pty não é terminal de controle do filho (sem `setsid`), então nenhum Ctrl-C de fora chega por ele: a mudança só faz o filho tratar o SIGINT como trataria rodando a suíte num terminal interativo. Os demais testes de pty do arquivo passam sob SIGINT ignorado (79/79 acima), e o `test_sigint_entre_o_remove_e_o_add_devolve_a_marketplace_original` passa nos dois modos.

## Teste novo e mutante
- `test_o_ctrl_c_na_troca_vale_mesmo_com_a_suite_rodando_com_o_sigint_ignorado` roda o teste original num processo com SIGINT em `SIG_IGN` e afirma `rc=0` e `Ran 1 test` (o nome não pode deixar de resolver em silêncio). Sem o `preexec_fn` ele reprova mesmo com a suíte rodando de um terminal (conferido: `FAILED (failures=1)` só nele): é o teste que falha antes e passa depois. O `sys.exit(...)` em volta do `unittest.main` é redundante (ele já sai), sem efeito.
- `tests/mutantes/flaky-ctrlc-troca.json` F1: `interrompido = True` aparece uma vez em `bin/forge_versoes.py:270`; `bin/forge-mutante tests/mutantes/flaky-ctrlc-troca.json` deu `F1 · morreu · bin/forge_versoes.py:270` e a árvore ficou limpa.
- Nenhuma asserção saiu: o diff do teste só acrescenta linhas, e a única linha alterada é o argumento do `Popen`.

## Parecer
Aprovado. A correção ataca a causa provada (SIGINT herdado ignorado), não afrouxa o que o teste prova e traz teste de regressão e mutante morto. Changelog em fragmento, sem tocar o `CHANGELOG.md` nem código de produção (`R-NEUTRO`, `R-CUSTO` sem impacto). A1 é recomendação, não devolve.
