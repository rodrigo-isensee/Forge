---
tipo: review
contrato: 1
pedido: lote-prepush-parecer
branch: melhoria/lote-prepush-parecer
commit: 5ca9a43d31b1b273ae47c906800bb4cd56105962
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Review: lote-prepush-parecer

Pedido LOTE-PREPUSH-PARECER-REV (E1.1), revalidação do zero sobre o head `5ca9a43` (decisão técnica de 2026-10-28 14:53). Diff lido: `git diff 9c4c615...5ca9a43` (8 arquivos, +382 -59).

## Achados
- A1 (recomendado) .githooks/pre-push:260 · comentário desatualizado: diz que só a suíte inteira anota a prova; agora o dirigido anota `.dirigida` e o curto sobre prova dirigida acrescenta a árvore ao `.verde` (linha 334), o que também contradiz a linha 174 ("segue só no `.verde`"); alinhar os dois comentários
- A2 (recomendado) .githooks/pre-push:191 · a prova `.dirigida` é aceita para qualquer `refs/heads/*`, mas o dirigido só existe para `melhoria/*`; restringir a aceitação da `.dirigida` a `refs/heads/melhoria/*` deixa a regra igual à do push de código (hoje sem gatilho prático: exige a mesma árvore)
- A3 (recomendado) tests/test_pre_push_parecer_curto.py:207 · `assertNotEqual(codigo_sha, "1" * 40)` é sempre verdadeiro e não prova nada; remover
- A4 (recomendado) tests/test_pre_push_parecer_curto.py:166 · o E2 é provado em partes (o curto anota a árvore sem a trava); falta o teste composto: segundo parecer sobre o primeiro parecer já anotado, depois do rebase, roda só as classes curtas
- A5 (recomendado) .githooks/pre-push:326 · o acréscimo do caminho curto não apara o `.verde` (o teto de 200 linhas só volta na próxima suíte inteira); crescimento pequeno, e a perda de linha na corrida com o `mv` já é falha fechada

## Parecer
Aprovado. Os três itens fazem o que o pedido pede, sem afrouxar o caminho curto.

- **E1 (primeiro envio só de parecer sem suíte):** o dirigido verde de `melhoria/*` anota a árvore em `.dirigida` (`.githooks/pre-push:336`), e o `so_parecer` aceita `.verde` ou `.dirigida` com as mesmas guardas (`tem_prova`: arquivo regular, não link, do próprio usuário). O `so_parecer` passou para antes da fila (linha 205); não há corrida com a anotação da suíte do código, porque o commit remoto que ele confere só existe depois que o pre-push do código terminou. O `arvore_inicio` e o `inicio_limpo` são recapturados depois da espera (linhas 243-244); mesmo sem a recaptura, a comparação com `arvore_fim` falharia fechada. O dirigido vermelho não anota (teste `test_dirigido_vermelho_nao_anota...`).
- **E2 (nova tentativa do push que perde a corrida):** o envio curto não abre a trava nem entra na fila (linha 209), e a anotação curta é por acréscimo; a perda de uma linha numa corrida com o `mv` do aparar só faz o próximo envio rodar a suíte inteira (falha fechada). As mensagens de não fast-forward e de remoto ausente passam a mandar `git pull --rebase` (linhas 115 e 121), antes da trava. O caminho de nova tentativa está documentado nos três agentes que enviam parecer (`agents/tech-lead.md`, `agents/security-engineer.md`, `agents/qa-engineer.md`). O código pesado continua esperando a vez e é barrado sem ela (`test_envio_de_codigo_continua_esperando...`).
- **E3 (comentários):** `.githooks/pre-push` e `bin/forge-fechar:375` alinhados ao pre-push atual (PREPUSH-DELETE); a linha do `forge-fechar` é só comentário, conforme a decisão técnica de 2026-10-28 15:08.
- **Merge com a develop 9c4c615:** `9c4c615` é ancestral do head, e o diff de dois pontos é igual ao de três pontos, então o merge não traz mudança própria (sem resolução de conflito). O commit `a34081d` usa a mensagem padrão do git em vez de Conventional Commits; é histórico já enviado e fica como está (`R-VERIFY`).

Ferramentas, saída citada: `bash -n` e `shellcheck .githooks/pre-push` sem saída (ok); `python3 -m unittest tests.test_pre_push_parecer_curto`: `Ran 9 tests ... OK`. Os mutantes (`tests/mutantes/lote-prepush-parecer.json`, M2 a M9) cobrem as guardas novas (prova dirigida, link, destino da anotação, curto antes da fila, anotação curta, mensagens). Rodá-los e conferir a cobertura é do QA (E3.1); a segurança do controle do Forge é da E2.1, e este parecer não a refaz.

Teto M14: 347 linhas (`.githooks/pre-push` 134, `bin/forge-fechar` 2, `tests/test_pre_push_parecer_curto.py` 211), abaixo de 400. Não toca `hooks/` nem `tests/catraca.py`. Fragmento em `changelog.d/lote-prepush-parecer.md` presente. `R-NEUTRO` e `R-CUSTO` preservados. Achados recorrentes (PA-7): a lista está vazia e nenhuma classe se repetiu neste pedido, então não há linha AR.
