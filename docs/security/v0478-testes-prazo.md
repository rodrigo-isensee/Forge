---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-testes-prazo
commit: bf3ce6af7420bc86931931866ef462163b5cec3c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478-testes-prazo

Escopo: diff `4182a6b9..bf3ce6af` (DEFEITO-TESTES-DE-PRAZO-SOB-CARGA, v0478 E12.1): `bin/forge_sempre_atual.py`, `tests/sem_claude_ancestral.py`, `tests/test_hooks.py`, `tests/test_sempre_atual.py`, `tests/mutantes/v0478-testes-prazo.json`, `tests/mutantes/v047-sempre-atual-12.json`, `changelog.d/v0478-testes-prazo.md`. Classe C (`forge-check classe`: sensível da catraca `bin/forge_sempre_atual.py`; teste de controle `tests/test_hooks.py`).

## Gatilhos
Gatilhos: nenhum item da lista da R-SEGURANCA; parecer pela classe C (`bin/` sensível da catraca e teste de controle do hook `parecer`).

## Resumo
- Produção: `bin/forge_sempre_atual.py:155-159` só extrai a leitura do /proc para `pids_do_proc()`; `processos_de_interesse` (`:170`) chama a função com o mesmo filtro `isdigit` e o mesmo `except OSError` → `duvida`. Comportamento em produção idêntico; nenhum script de `bin/` importa `tests/sem_claude_ancestral.py` (só a docstring o cita).
- Lançador dos testes (`tests/sem_claude_ancestral.py:29-56`): troca `pids_do_proc` só quando o script é `forge-sempre-atual`, mostrando os descendentes do `--ate`. Os `claude` e `forge-fechar` falsos do próprio teste descendem dele e seguem visíveis, então a guarda continua exercitada; `descende_de` termina em ciclo, pid 0 e leitura falha (`_pai_e_nome` devolve `(0, "")`). Mutantes M1-M4 cobrem as quatro decisões.
- Afrouxamento do teste do prazo (`tests/test_hooks.py:100-121`, `:1199-1222`): a recusa do merge legítimo só passa como carga com código 2, mensagem do vigia de 8 s, relógio ≥ prazo e CPU dos filhos + sono do git ≤ prazo − 1 s. Só aceita recusa (direção fechada): nenhuma liberação indevida passa a ser aceita; a recusa por regra e a do vigia de 3 s continuam reprovando (`test_liberar_ou_provar_a_carga_aceita_so_a_recusa_explicada_pela_carga`).

## Achados
- A1 (recomendado) tests/test_hooks.py:1216 · A saída por carga aceita qualquer recusa do vigia de 8 s com pouca CPU; uma regressão do hook que bloqueie em espera (E/S, subprocesso parado) num merge legítimo passa como carga. Só disponibilidade (recusa), não abre liberação; sugerir contar PRAZO-CARGA no CI.

## Sondas

## Detalhe dos achados
A1. Evidência: `tests/test_hooks.py:1216` (o `except AssertionError` que consulta `carga_explica_a_recusa`) e `:1204-1209` (a medida é CPU dos filhos, que não conta tempo bloqueado). Caminho: não há atacante; o risco é um defeito de desempenho do hook `parecer` (espera bloqueante nova no caminho do `gh pr merge`) ficar escondido no CI, com o merge legítimo recusado em produção (falha fechada, só disponibilidade). Severidade: baixa. Correção mínima: o job do CI conta as linhas `PRAZO-CARGA` e avisa (ou reprova) quando aparecem em execução sem carga alta, ou o teste registra o `sono` real medido. Esforço: P. Dono: `qa-engineer` (teste) e `devops-engineer` (aviso no CI).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Testes novos rodados localmente no head bf3ce6af: `tests.test_sempre_atual.ProcessoDeOutraParteDaSuite` (3) e `tests.test_hooks.Hooks.test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo_com_cpu_folgada` e `test_liberar_ou_provar_a_carga_aceita_so_a_recusa_explicada_pela_carga`: 5 OK. Suíte inteira: não rodada (brief); nenhuma execução de CI no head até este parecer (sem PR), o CI fica como portão próprio da classe C. Ferramentas: o varredor de segredos não está no PATH (lacuna); o diff não toca configuração, credenciais nem workflow.
