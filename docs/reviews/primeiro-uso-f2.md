---
tipo: review
contrato: 1
pedido: primeiro-uso-f2
branch: melhoria/primeiro-uso-f2
commit: 229ec44
parecer: aprovado
revisor: forge:tech-lead (independente)
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

## Review independente

Revisor: `tech-lead`, sobre o HEAD 6a8795a. Resultado: **aprovado**, com recomendações (nenhuma bloqueia).

- **Verificação:** 337 testes OK; `shellcheck` limpo em `bin/forge`, `forge-salvar`, `forge-desfazer` e `forge-novo-projeto` (os dois scripts em Python, `forge-check` e `forge-upgrade`, não são shell e o shellcheck os recusa por natureza). Testes com HOME, gitconfig, remoto bare e `gh` falsos; nada fixo da conta do dono, nenhuma rede.
- **desfazer:** não perde trabalho. Mudança não salva vai para `stash -u` com lista dos arquivos, confirmação e caminho de volta (`--recuperar`); último registro vira `revert`, nunca `reset`; recusa mesclagem, primeiro registro e `main`/`develop`/`homolog`/sem branch; Enter e fim da entrada contam como não; sem `--force`, `reset --hard` nem `clean` (teste estático). Linguagem simples, sem jargão na tela.
- **salvar:** nas branches protegidas ou sem branch cria `trabalho/<data>` antes de commitar, então nunca grava nem envia nelas; recusa segredos; `push` sem força; sem rede, avisa que o trabalho ficou salvo na pasta.
- **BUG-03 (pasta sempre `~/<nome>`):** aceitável. A pasta já é avisada na tela, pasta existente e não vazia continua recusada, e o objetivo é o limite de 10 interações para o público que não programa. Recomendo registrar em `docs/propostas/primeiro-uso/decisoes.md` a suposição atualizada ("pasta fixa `~/<nome>`, avisada; quem quiser outra pasta move depois"), pois a linha atual ("perguntada a cada vez") ficou desatualizada.
- **Repositório vazio com `--sim`:** confirmado, `ler` sempre lê a entrada, então a pergunta continua. Correto.
- **Recomendações (não bloqueiam):**
  1. `bin/forge-salvar` (push): se o envio é recusado porque o GitHub tem registros novos (não é rede), a mensagem diz "rede ou permissão". Diferenciar e orientar ("peça ajuda ao Jarvis"); hoje o conflito não tem tratamento próprio.
  2. `bin/forge-salvar`: com mesclagem ou conflito em andamento, `git add -A` registraria marcas de conflito. Recusar com aviso quando houver caminhos não resolvidos (`git ls-files -u`).
  3. `bin/forge-salvar`: a checagem de segredos usa `ls-files -o -m`, então arquivo de segredo já posto na área de preparo (`git add`) passa. Incluir `git diff --cached --name-only`.
  4. `bin/forge-desfazer`: com mesclagem em andamento o `stash` falha com mensagem crua do git; avisar antes. Também, se `stash pop` gera conflito, o texto "nada foi perdido" é verdadeiro, mas a pasta pode ficar com marcas; dizer isso.
  5. CI: incluir os quatro scripts bash de `bin/` no job `shellcheck` (pendência já registrada).
- **Itens 1 a 4:** sugiro cartão de acompanhamento, com teste para cada um; não impedem a F2, pois falham sem apagar nada.

## Re-review independente

Revisor: `tech-lead`, sobre o HEAD 229ec44 (correção das recomendações 1 a 4 e da suposição da pasta). Resultado: **aprovado**, sem item que bloqueie.

- **Verificação:** 342 testes OK; `shellcheck` limpo em `bin/forge`, `forge-salvar`, `forge-desfazer` e `forge-novo-projeto`. Só mudaram os dois scripts, os testes e `decisoes.md`; nenhum hook, catraca ou invariante.
- **Rec. 1 (push recusado):** atendida; a mensagem de conflito diz que nada se perdeu, que não se enviou para não apagar o que há lá e manda chamar o Jarvis. Teste com segundo clone cobre o caso e exige a ausência de "rede ou permissão".
- **Rec. 2 (mesclagem e marcas):** atendida; `ls-files -u` ou `MERGE_HEAD` recusam antes de qualquer `add` e o HEAD não se move (testado); marcas `<<<<<<< `/`>>>>>>> ` em arquivo tocado também recusam. O laço com `&&` não derruba o `set -e`.
- **Rec. 3 (segredo no índice):** atendida; `diff --cached --name-only` entra na lista, com teste de `.env` posto por `git add -f`.
- **Rec. 4 (desfazer):** atendida; mesclagem recusada antes do `stash`, sem texto cru do git. O aviso de `--recuperar` está claro: "nada foi perdido, mas a pasta pode ter ficado com marcas de conflito (<<<<<<<). Peça ajuda ao Jarvis". Se o `pop` deixar conflito, `salvar` e `desfazer` passam a recusar com o aviso de mesclagem, o que protege.
- **Suposição da pasta:** `decisoes.md` atualizado ("pasta fixa `~/<nome>`, avisada; quem quiser outra pasta move depois").
- **Observações (não bloqueiam, para o cartão de acompanhamento):**
  1. `bin/forge-salvar`: o padrão `rejected` também casa com "remote rejected" (hook ou proteção do GitHub), que mostraria o texto de "alguém mudou". Preferir `non-fast-forward|fetch first|stale info` e deixar o resto cair em "rede ou permissão".
  2. Nos demais erros de push o texto do git deixou de aparecer (a saída é capturada). Imprimir `$erro` em stderr no caminho genérico ajuda o diagnóstico.
  3. Nomes com acento ou espaço saem entre aspas em `ls-files` (`core.quotepath`); a checagem de segredo e de marcas os ignora. Usar `-z` ou `-c core.quotepath=off`.
  4. CI: os scripts bash de `bin/` ainda fora do job `shellcheck` (pendência já registrada).
