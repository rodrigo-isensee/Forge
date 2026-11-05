---
tipo: qa
contrato: 1
pedido: release-0.33.0
branch: melhoria/release-0.33.0
commit: c004a70a01459b483322b006a012bac382bb36e6
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-05
---
# QA: release-0.33.0

## Achados
- A1 (recomendado) tests/test_hooks.py:1157 · test_registro_de_agente e as 4 fixtures agentes/* dependem do pid do sandbox e caem também na main 0.32.0; vale cartão de isolamento do teste.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Suíte inteira no commit de release | `.githooks/pre-push --suite` em cópia detached no c004a70 (2612 testes, 92 módulos) | n/a | 8 falhas, todas de ambiente e provadas iguais na main (abaixo) |
| Plugin válido | `scripts/validar-plugin.sh` | n/a | rc 0, Validation passed |
| E3 versão bate com a leva | `plugin.json` 0.33.0 e `CHANGELOG.md` `[0.33.0]` | n/a | passou: Adicionado (ato-github), Alterado e Corrigido, sem quebra; minor correto |

## Cenários e resultado real
Suíte inteira (cópia em c004a70, 29m46s, 4 processos): `FAILED (failures=7, errors=1, skipped=31, guarda=2)`. O `guarda=2` são só as duas saídas de processo com rc 1; `git status` e `.git/config` não mudaram. Log: `/root/.forge-contrib/qa-logs/release-0.33.0-suite.log`.

Falhas e prova na main 1b62cfd (cópia `qa-main-0.32.0`, mesmo sandbox):
- `test_atualizar.test_ancestral_chamado_claude_recusa...` (1 erro + 1 falha, forge-atualizar e forge-voltar-versao): caem iguais na main (`release-0.33.0-pidns-comparacao.log`).
- `test_hooks.test_registro_de_agente_solta_so_com_prova_de_sessao_morta`: cai na main em repetição (`release-0.33.0-registro-agente.log`); em uma rodada passou na main, então depende do pid.
- 4 fixtures `agentes/*` (`inicio-sem-par-grava-pid-da-sessao`, `reserva-grava-pid-e-sessao`, `inicio-casa-reserva-da-sessao-e-mantem-pid`, `inicio-so-casa-reserva-da-mesma-sessao`): caem iguais na main na segunda rodada (`release-0.33.0-fixtures-agentes-main2.log`; a primeira passou, `...-fixtures-agentes.log`). O diff da leva em `hooks/agentes.py` só troca texto de mensagem, sem tocar `da_sessao` nem `pid_valido`.
- `test_muitos_heredocs_recusam_dentro_do_orcamento` (1 forma na leva): na main caem 8 formas do mesmo teste, dependente de carga (load 16 a 20 na máquina); orçamento de tempo, não de lógica.

Nenhuma falha é da leva; nenhum teste novo da leva caiu. Vermelho antes do verde e mutantes da leva ficaram nos pareceres de cada PR (a leva não muda código além deles).
