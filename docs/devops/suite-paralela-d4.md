---
tipo: revisao-devops
contrato: 1
pedido: suite-paralela-d4
branch: melhoria/suite-paralela-d4
commit: 84de155340ab1991d6aa494d1de96e221ae8628c
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-22
---
# Review de devops: suite-paralela-d4

## Parecer
Aprovado, sem bloqueantes. Revisão estática da entrega inteira (`c092f1b..84de155`) contra o desenho da D4 e o modelo de ameaças (AB-1 a AB-14), com o delta da volta 3 reconferido.

## Achados

## Evidência por ponto
- **Delta da volta 3 (`830bf9f..84de155`):** só `tests/test_pre_push_trava.py`, 15 linhas trocadas por 15: renome de nomes, comentários, docstring e mensagens de asserção (a palavra que casava o padrão de segredo virou "vez"; o auxiliar passou a se chamar `vezes`). Nenhuma chamada `assert*` ganhou nem perdeu linha, nenhum literal esperado do hook mudou, nenhum teste foi removido ou pulado, e o arquivo compila. Pipeline, hook e `ci.yml` intactos neste delta; o resto segue como revisado na volta 2.
- **Divisão e completude (AB-1, AB-2, AB-5, AB-13):** `scripts/suite-paralela.py` lista os módulos por glob, confere a partição (repetido, faltando, desconhecido) e compara o multiconjunto dos IDs rodados com o da descoberta completa; zero testes, relatório ausente, rc diferente de 0 ou morte por sinal reprovam, e a árvore de trabalho e o `.git/config` são conferidos ao fim. O peso só equilibra e nunca decide o que roda. Falha fechada em `FORGE_SUITE_PROCS` inválido.
- **Isolamento e encerramento (AB-3, AB-4, AB-6, AB-12):** cada filho tem grupo próprio (`start_new_session`), TMPDIR próprio com modo 700 apagado no `finally`, e vigia o pai (SIGKILL no orquestrador não deixa órfão). `encerrar` mira só `killpg` dos pids dos próprios filhos; o hook mata só o filho da suíte e espera por ele antes de soltar a trava, sem `pkill -f`. O código de saída de cada filho é lido pelo pid.
- **Fila e trava (AB-7):** a senha só ordena a espera; a exclusão continua sendo o flock. Senha de processo morto é descartada por flock obtido, a pasta é conferida (dono, não é link, modo 700), o prazo é único para fila e trava e esgotado barra sem rodar a suíte. Sem a fila, cai para a trava com aviso. O script recusa rodar sem a trava presa e anotada pelo hook (`FORGE_SUITE_TRAVA`) e, à mão, reentra por `--suite`, na mesma fila.
- **PREPUSH-JA-NO-REMOTO (AB-9, AB-10):** o hook só pula com zero refs no stdin, ou seja, a decisão de "já é igual ao remoto" é do git, não do hook; qualquer linha (inclusive deleção ou ref nova) segue para a suíte. O modo `--suite` não pula. O push de deleção segue rodando a suíte (PREPUSH-DELETE-SEM-SUITE fica fora, como decidido).
- **Launcher de 120 s em `tests/test_hooks.py`:** só o prazo do git dentro do teste é largado (o de produção em `bin/forge-check` não muda). O teste novo prova as duas pontas: com 120 s o git lento de 6 s passa e com o prazo de produção (5 s) o fixture falha. Hook que travar de verdade ainda estoura em 120 s no `subprocess.run`; falha real não é escondida.
- **`.github/workflows/ci.yml`:** `rapida` e `bateria` chamam o mesmo script (guarda de completude nos dois); o passo dos pareceres e a release (`release.yml`) seguem em série, com teste de contraprova. `permissions`, SHAs das ações, `concurrency` e `timeout-minutes` (10 e 15) não mudaram; nenhum `continue-on-error`, nenhum segredo novo, nenhum artefato ou cache novo. Resumo de passos via `GITHUB_STEP_SUMMARY` apenas.
- **`hooks/pesado.py`:** o script e `.githooks/pre-push --suite` entram na lista de tarefas pesadas (R-TETO); teste cobre os positivos e a contraprova (`cat`).

## Ferramentas
- Usadas: `bash -n` em `.githooks/pre-push` (ok), leitura do diff e dos testes novos.
- Faltaram no PATH: `actionlint` e `shellcheck`. Lacuna registrada: a bateria do CI roda os dois sobre `.githooks/pre-push` e `ci.yml` e é quem fecha essa conferência. A suíte completa não foi rodada por mim (R-TETO); ela roda no pre-push do envio e no CI.

## Recomendações (não bloqueiam)
- Uma senha `.nova-<pid>` de processo morto por SIGKILL no meio de `fila_entrar` fica na pasta da fila (o glob da fila não a vê, então não atrapalha a ordem); vale uma limpeza de `.nova-*` com flock obtido na próxima versão.
- Conferir o tempo da bateria e da `rapida` no checkpoint da release (`gh run list`): os tetos de 10 e 15 minutos ficam folgados com a divisão, e o teto de 4 processos serve ao runner gratuito de 4 núcleos.
- Se `pesos-d4.json` envelhecer, regravar com `FORGE_SUITE_MEDIR=1` após as 3 execuções reais decididas pelo dono.

## Custo e rollback
Sem custo novo: mesmos runners gratuitos, menos minutos de CI por execução (mesmo trabalho em até 4 processos), nenhum serviço, cache ou artefato (R-CUSTO). Rollback: reverter o commit da entrega devolve o passo do CI e o hook à suíte em série; o `.githooks/pre-push` já tem o recuo em série quando o script falta.
