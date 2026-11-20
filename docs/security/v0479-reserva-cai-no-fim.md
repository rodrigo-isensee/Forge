---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-reserva-cai-no-fim
commit: 50e06ac60ee54707c6a089a2b6e9a261fd649150
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-reserva-cai-no-fim

Etapa E60.3 do pedido v0478 (cartão RESERVA-NAO-CAI-NO-FIM). Diff lido: `ed5bfa02..50e06ac6`, ou seja `hooks/agentes.py`, `tests/test_agentes_interrompidos.py`, `tests/mutantes/v0479-reserva-cai-no-fim.json`, `tests/mutantes/v047-h2-autor-fica-2.json` e `changelog.d/v0479-reserva-cai-no-fim.md`.

## Gatilhos
Gatilhos: hook de controle (reserva de escrita por branch do R-TETO), estado de controle do Forge.

## Achados
- A1 (recomendado) hooks/agentes.py:1295 · Reserva antiga sem tool_use_id continua casando por tipo e pela ordem antes da reserva do próprio disparo: o agente que prova o tool_use_id pode levá-la, e o fim dele solta a branch do outro, ainda vivo. Correção: preferir a reserva de tool_use_id igual e só depois a que não tem.

## Sondas

## Detalhe dos achados
**Perguntas do brief.**
1. *Um agente consegue forjar o tool_use_id?* Não. No disparo, o valor vem do campo de topo do evento PreToolUse (`hooks/agentes.py:1207`, `hook.campo("tool_use_id")`), que o Claude Code preenche, e não de `tool_input`, que é o que o agente escreve. No início e no fim, o valor sai do meta do subagente (`hooks/agentes.py:1261` → `tool_use_do_meta`, `hooks/agentes.py:493`). O caminho vem do `transcript_path` do evento e só vale dentro de `~/.claude/projects/<projeto>/<sessão>.jsonl`. Um link no caminho do meta é recusado, o id passa por `ID_DE_AGENTE` e o valor por `USO_DE_AGENTE` (`hooks/agentes.py:388`). A escrita na pasta do projeto, no transcript e em `subagents/` é negada a todo papel (`hooks/conformidade.json:53-56`, `quem: []`) e pelo sandbox. Qualquer dúvida (sem meta, valor fora da forma, exceção) devolve `None` e volta ao casamento por id de antes, nunca a um casamento mais largo.
2. *Um agente consegue soltar a reserva de outro que ainda está vivo?* Quando os dois lados têm o tool_use_id, não. `e_do_agente` (`hooks/agentes.py:1272`) compara só o tool_use_id, e o início filtra as reservas de outro disparo (`hooks/agentes.py:1295`). O teste `FimDoAgente.test_o_fim_de_um_solta_a_branch_dele_e_nao_a_do_outro_vivo` prova isso, e os mutantes M1, M3, M4 e M5 o guardam. Se o id ficar preso a um registro de outro tool_use_id, a reserva fica até expirar. Isso fecha o lado da integridade (dois autores na mesma branch) e só custa disponibilidade. A brecha que sobra é o A1.

**A1.** Evidência: `hooks/agentes.py:1295` mantém na lista as reservas sem `tool_use_id`, e `hooks/agentes.py:1297-1299` escolhe pelo tipo a mais antiga. Sonda executada (cenário de `FimDoAgente`, só num arquivo temporário, fora do clone): B foi disparado com a versão anterior (reserva sem `tool_use_id`, `melhoria/B`), e A foi disparado depois, já com `toolu_AAAA` (`melhoria/A`). Ordem dos eventos: início de A, início de B, fim de A. Esperado: fica `melhoria/B`. Obtido antes do fim de A: A com `melhoria/B`, a reserva de A solta, B num registro sem branch. Obtido depois do fim de A: nenhuma branch presa, com B vivo. Caminho: não há atacante. Basta o plugin ser atualizado com reservas vivas (a janela vai até a expiração da reserva) ou um PreToolUse chegar sem `tool_use_id` na forma. Aí outro agente pode escrever na branch de B enquanto B ainda trabalha. Antes desta entrega o dano era o mesmo (a troca por ordem), então não é regressão. Por isso é recomendado e não bloqueante. Severidade: baixa. Correção mínima: no `iniciar`, procurar primeiro a reserva com `tool_use_id == uso` e só então cair nas que não têm `tool_use_id`. Um teste com uma reserva antiga sem `tool_use_id` e outra nova, do mesmo tipo, fecha o caso. Esforço: P. Dono: o autor da E60.1.

**Outros pontos conferidos, sem achado.** A leitura do meta tem limite de tamanho (`LIMITE_DO_META`) e vale só para um id na forma, então não abre caminho para fora da pasta. O custo extra do início e do fim é uma leitura pequena e não toca o transcript inteiro. O changelog não traz segredo nem dado pessoal.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Testes rodados no head: `tests.test_agentes_interrompidos.FimDoAgente` (4) e `tests.test_hooks_agentes_autor.PeloHook.test_fixtures_do_pedido` (M13), 5 OK. A suíte inteira fica com o CI. A branch não tem PR nem execução de CI até este parecer, então o portão do merge continua sendo o CI verde. Faltaram no ambiente: `gitleaks` e `semgrep`, fora do PATH. O diff não toca credencial nem dependência.
