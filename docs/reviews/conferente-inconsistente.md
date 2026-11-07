---
tipo: review
contrato: 1
pedido: versao-035
branch: melhoria/conferente-inconsistente
commit: 4c13fe443a6459d7de79d2aa0e4eeae211eed2e3
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-06
---
# Review: versao-035 (E4 CONFERENTE-INCONSISTENTE)

Branch `melhoria/conferente-inconsistente` em 4c13fe4, base d9b26bb (`origin/develop`). Diff lido inteiro: `agents/conferente.md` (+2 -1), `bin/forge-testes` (+1 -1), `changelog.d/conferente-inconsistente.md` (+2), `tests/test_conferente_estavel.py` (+95). Contra o desenho (E4 em `docs/arquitetura/versao-035-desenho.md`), o modelo de ameaças (E4, C-1 a C-9 e T-1 a T-6) e a decisão do dono de 2026-11-05 15:20.

## Achados
- A1 (bloqueante) agents/conferente.md:49 · `ls -l agents/<nome>.md` é relativo ao diretório em que o conferente roda; num projeto (sem `agents/`, ver templates/projeto) e nesta sessão (cwd /workspaces) o arquivo não existe, e o texto manda `forma: destino não encontrado`, que reprova todo brief com PQ cmd.
- A2 (recomendado) agents/conferente.md:49 · agente de stack (node-backend, react-frontend) cai em `destino não encontrado` e reprova, enquanto o C-5 do modelo de ameaças aceitava o caminho de `stacks/`; trate junto com o A1, decidindo com o arquiteto o caminho do destino fora do clone do Forge.
- A3 (recomendado) tests/test_conferente_estavel.py:1 · o teste tem 95 linhas e o desenho fixou 40; os testes de C-2 a C-8 justificam parte do aumento, mas registre a mudança de teto no pedido ou enxugue as asserções repetidas sobre a mesma frase.

## Parecer
Reprovado por A1, defeito provado. Na raiz de um projeto não existe `agents/` (`ls templates/projeto` mostra só `CLAUDE.md`, `KANBAN.md` e `docs`), porque os agentes vêm do plugin. Nesta sessão, `ls -l agents/tech-lead.md` rodado em `/workspaces` dá "No such file or directory". O texto novo do item 4 manda tratar arquivo ausente como `forma: destino não encontrado`, que reprova. Na prática, fora do clone do Forge, todo brief com PQ `cmd` (quase todos) seria reprovado pelo conferente, e o efeito vai na direção contrária do cartão, que é reduzir reprovação espúria. Sugestão para o autor, com o arquiteto: com o arquivo do destino ausente porque a raiz não é o clone do Forge, o caso sai `não verificável` em vez de reprovar, ou o `--destino` passa a resolver o caminho por uma raiz conhecida, sem `$` (a `conformidade` recusa) e sem caminho tirado do brief (T-2). O A2 entra na mesma correção. A lista de comandos permitidos não pode mudar (C-7).

Lido sem achado:
- Regra "Decidido pelo comando não se reabre" (`agents/conferente.md:20`). Cobre só `forma: ok`, `corte:` que não reprova, `citação: ok` e `decisões: ok` da saída desta passada (C-2, T-4). Deixa fora fidelidade, contradição literal e etapa (C-1, T-3). Exige a linha do comando no achado (C-3). Limita o hash aprovado a forma e corte, e o fato novo do disco reprova (C-4).
- Ponto levado pelo Jarvis (Histórico 16:06): `corte: etapa (ok)` como corte decidido não abre brecha no C-1. O item 3 já mandava copiar o `corte:` do comando sem cobrar o que ele não cobra. A etapa que fica por leitura é a do item 5 (a `Etapa:` e a tabela de PR e merge), e a regra a exclui de forma explícita ("Os três itens ... ficam fora desta regra").
- Seção "Comandos permitidos" idêntica: o hash está no teste (C-7, T-1). `ls` e `grep` já estão na lista.
- `bin/forge-testes:81`: `test_conferente_estavel` entra em `LEITORES_DE_TEXTO`. É uma tupla, não uma linha de guarda, e não pede mutante.
- Fragmento do changelog presente. Commits em Conventional Commits.
- Teto M14: 97 linhas de código e teste (`bin/` 2, `tests/*.py` 95), dentro de 150. O PR não toca `hooks/` nem `tests/catraca.py`. As duas partes (não reabrir e ferramentas do destino) são o E4 único do pedido, no mesmo arquivo, sob a mesma decisão do dono, e não contam como dois comportamentos para a M14.
- Rótulo `afrouxa-regra` (C-9): fica com o dono na E2.8. Segurança (E2.5): a cargo do `security-engineer`, não refeita aqui.

Testes: a suíte inteira do push de 4c13fe4 passou (`/tmp/push-e4-4.log`: "Ran 2623 tests ... OK (skipped=32)", `push_rc=0 16:09:22`, com `test_conferente_estavel` no processo 2). Não rodei os testes dos arquivos tocados porque o load1 ficou acima de 8 (15,0 e 15,5 em `/proc/loadavg`), conforme a regra de carga do dono. O `bin/forge-testes --listar` pede a suíte completa (o diff mexe no mapa), e ela já está coberta pelo log acima.
