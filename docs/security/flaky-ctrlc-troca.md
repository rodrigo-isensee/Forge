---
tipo: revisao-seguranca
contrato: 1
pedido: flaky-ctrlc-troca
branch: melhoria/flaky-ctrlc-troca
commit: a6adac96786de046c4eb5db80b7eff038de159a3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: flaky-ctrlc-troca

Diff revisado: `41ba611...a6adac9` (3 arquivos: `tests/test_atualizar.py`, `tests/mutantes/flaky-ctrlc-troca.json`, `changelog.d/flaky-ctrlc-troca.md`).

## Gatilhos
Controles do Forge (`R-SEGURANCA`): os testes que guardam a recuperação da marketplace na troca do plugin (`forge atualizar`, `bin/forge_versoes.py:fixar_plugin`). O código de produção não muda; só o arnês de teste.

## Achados

## Detalhe dos achados
Sem achado bloqueante nem recomendado. O que conferi:

1. **Restaurar o SIGINT no filho não esconde defeito real do `forge atualizar`.** O `preexec_fn` de `tests/test_atualizar.py:165` só põe o SIGINT em `SIG_DFL` no processo do `forge atualizar` sob teste, que é o estado em que ele roda de verdade quando a pessoa aperta Ctrl-C: só o job em primeiro plano recebe o Ctrl-C do terminal, e o shell interativo o lança com SIGINT no padrão. O SIGINT ignorado só existia porque o pre-push lança a suíte com `&` (`.githooks/pre-push:297`), um artefato do arnês. Com o SIGINT ignorado em produção (lista assíncrona de script não interativo), o Ctrl-C não chega ao processo por definição POSIX, e o caminho que resta é o da falha comum, que também devolve a marketplace original (`bin/forge_versoes.py:471-476`, `devolver_original`). O SIGTERM segue tratado à parte (`bin/forge_versoes.py:410-422`). Não há caminho em que o defeito apareça para quem usa e o teste deixe de mostrar.
2. **O teste ainda prova a volta à marketplace original.** `test_sigint_entre_o_remove_e_o_add_devolve_a_marketplace_original` (`tests/test_atualizar.py:1043`) não mudou e continua exigindo que o último `marketplace add` seja a fonte original e que haja `install`/`update` depois dele; com o SIGINT no padrão ele passa a exercer o ramo do `KeyboardInterrupt` (`bin/forge_versoes.py:462-468`, sob `_sem_interrupcao`), que é o ramo que o nome promete, em vez do ramo da falha comum. O teste do ponto e da marca (`tests/test_atualizar.py:1054`) não perdeu asserção.
3. **A regressão fica guardada.** O teste novo (`tests/test_atualizar.py:1067`) roda o alvo num filho com SIGINT ignorado. Prova local: numa cópia sem o `preexec_fn`, ele falha (rc=1, `FAILED (failures=1)`); com a correção, a classe `CtrlCNaTroca` inteira passa com SIGINT ignorado (8 testes, rc=0). O mutante F1 (`tests/mutantes/flaky-ctrlc-troca.json`, `bin/forge_versoes.py:270`) morreu no `bin/forge-mutante` (rc=0), aplicado e desfeito pelo próprio script, sem resíduo na árvore (`git status` limpo).
4. **Nada fora de `tests/` mudou além do fragmento `changelog.d/flaky-ctrlc-troca.md`**, exigido pelo processo de versão e sem código. `bin/`, `.githooks/`, workflows e `tests/config.json` intactos.

Observação informativa (sem caminho de ataque, não é achado): `preexec_fn` não é seguro com threads no processo pai; a suíte é de uma thread e o lambda só chama `signal.signal`, então o risco é nulo hoje.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão manual do diff e dos caminhos de sinal em `bin/forge_versoes.py`; testes da classe `CtrlCNaTroca` com SIGINT ignorado, contraprova sem a correção e `bin/forge-mutante`. Lacunas: `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH (o diff não toca workflow, dependência nem configuração com segredo).
