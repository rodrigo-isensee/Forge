---
tipo: revisao-seguranca
contrato: 1
pedido: lote-atualizar
branch: melhoria/lote-atualizar
commit: 8353dae8ded7363d55a975547807149c147199dc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: lote-atualizar (rodada 2)

Revalidação só do delta da volta 1, `571312a...8353dae` (3 commits: `c783bc1`, `de9e974`, `8353dae`; `bin/forge-atualizar`, `tests/test_atualizar.py`, `changelog.d/lote-atualizar.md`). A rodada 1 (aprovado, `9bb7ff9`, sobre `f1cf78c`) não foi reaberta. Veredito: aprovado. A recomendação do código de saída entrou, e a mudança não abre nenhum caminho novo para mover a branch do projeto a um commit errado.

## Gatilhos
`controles do Forge`: `desfazer_mesclagem` (`bin/forge-atualizar:135-143`) move a branch `forge/upgrade-<nova>` do projeto.

## Achados

## Detalhe dos achados
Conferido por leitura e por `tests.test_atualizar` (75 OK, `HOME` em `$TMPDIR/security-engineer-loteatualizar2/`) sobre `8353dae`:

- **Recomendação do código de saída (rodada 1): atendida.** `desfazer_mesclagem` devolve True só quando não há `MERGE_HEAD` e o `HEAD` está em `antes` (`bin/forge-atualizar:143`). Ela confere o estado final em vez do código de saída de cada comando, o que é mais forte: cobre o `merge --abort` que falhou e o `checkout -B` recusado. "Desfiz a mesclagem" só sai com True (`:123-124`). Com False, `avisar_nao_desfez` (`:130-132`) diz que a mesclagem ficou e dá os dois comandos, `git merge --abort` ou `git checkout -B forge/upgrade-<nova> <antes>`. O caminho do `EOFError`/`KeyboardInterrupt` também avisa (`:118-119`). O teste novo com `.git/index.lock` (`tests/test_atualizar.py`, `test_desfazer_recusado_nao_diz_que_desfez_e_ensina_o_comando`) cobre o checkout recusado. O teste do F4-A9 agora roda com o ambiente isolado e afirma que a resolução foi commitada antes do erro (A1 do review).
- **Commit de destino.** O alvo do `checkout -B` continua sendo só `antes`, o `HEAD` lido em `:110` logo antes do `merge`. O `if` passou de `elif` a `if` depois do `merge --abort` (`:140`). Com isso, o checkout roda depois de um abort que deu certo só se o `HEAD` não estiver em `antes`, e o abort sempre volta para o `HEAD` de antes do merge, que é `antes`. Se o abort falha, o `MERGE_HEAD` fica, o checkout não roda e a função devolve False. Nenhum alvo novo entrou.
- **Comando sugerido.** `nova` vem da tag já validada pelo fluxo aprovado na rodada 1, e `antes` é um sha40 do `rev-parse`. A linha impressa não carrega texto do projeto que possa injetar algo em quem a copiar.
- **Trabalho não commitado.** O `checkout` continua sem `-f` (`:142`). Se ele recusar, a função devolve False e a mensagem diz isso.
- **Informativo, fora das dimensões de risco.** Com o `HEAD` destacado em `antes` por ação paralela do dono, a função devolve True com a branch ainda no merge. Isso exige mexer no projeto em outro terminal no meio da execução, e não há atacante nem ganho. Não é achado. Fora do delta e sem reabrir: `:167-168` (o "n" do dono) mantém a mensagem fixa depois do `merge --abort`. É a mesma classe, de impacto informativo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura e `python3 -m unittest tests.test_atualizar`. Faltaram no PATH: `gitleaks` e `semgrep` (lacuna registrada). O delta não tem credenciais, rede nem dependência nova.
