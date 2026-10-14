---
tipo: review
contrato: 1
pedido: primeiro-uso-f2
branch: melhoria/primeiro-uso-f2
commit: bf9b821
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: primeiro uso F2 (salvar, desfazer, primeiro pedido guiado, bugs baixos da F1)

- **Mudança:** `bin/forge-salvar` e `bin/forge-desfazer` (novos, listados pelo despachante); skill `novo-projeto` com o primeiro pedido guiado (pedido, protótipo, aprovação, entrega) e a dica de salvar/desfazer; correções em `bin/forge-novo-projeto`.
- **salvar:** em `main`, `develop`, `homolog` ou sem branch cria `trabalho/<AAAAMMDD-HHMM>` antes; respeita `.gitignore`; recusa `.env`, chaves e certificados; `push -u` simples, sem força; se o envio falha, diz que o trabalho está salvo na pasta, e rodar de novo reenvia.
- **desfazer:** não salvo vai para `git stash push -u -m "desfeito ..."` (volta por `--recuperar`); último registro vira `git revert --no-edit` e push normal; recusa mesclagem, primeiro registro e branches principais; sempre mostra o que volta e só age com "sim" (Enter ou fim da entrada contam como não). Teste estático garante que os scripts não contêm `--force`, `--no-verify`, `reset --hard` nem `clean -f`.
- **Bugs:** BUG-03 a pasta deixa de ser perguntada (`~/<nome>`, avisada na tela), o roteiro fica em 10 interações (terminal 2 mais skill 8; teste estrutural conta); BUG-07 pasta apagada avisa e oferece baixar de novo (desmarca só `clonado`, não refaz commit nem branches); BUG-08 `gh auth status` com erro de rede diz "sem conexão", não "sem login"; BUG-09 repositório existente, vazio e privado é oferecido no passo do nome (com `--sim` a pergunta continua, pois reusar não é criar); BUG-10 colchete duplicado removido.
- **Vermelho antes:** testes escritos antes do código; sem a mudança falharam 22 testes de `test_novo_projeto` e 17 de `test_salvar_desfazer` (scripts inexistentes). Os testes antigos tiveram a linha da pasta removida da entrada.
- **Verde depois:** 337 testes (`python3 -m unittest discover -s tests`), `shellcheck` dos quatro scripts de `bin/` e `scripts/validar-plugin.sh` passam. Fixtures com `gh` e `claude` falsos, HOME e git temporários; nada de rede (`R-CUSTO`); sem termo de projeto (`R-NEUTRO`).
- **Atenção:** o job `shellcheck` do CI ainda não lista `bin/forge`, `bin/forge-novo-projeto`, `bin/forge-salvar` nem `bin/forge-desfazer` (`.github/` é protegido; pendência já registrada na 0.12.0). Não toca em hooks, catraca nem invariantes. Sem mudança de versão (sobe na release, ADR 0006).

Parecer de autor, feito pelo mesmo agente que escreveu a mudança; o review independente fica a cargo do `tech-lead` no PR.
