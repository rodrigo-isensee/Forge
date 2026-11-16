---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-pr-hook-rapido
commit: 8eebc2a51576f5d9957653f4ad55bbdf7682f12b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Code review: hook R-REVIEW rápido no gh pr ready e no gh pr merge (PR-HOOK-RAPIDO, E2.117)

Escopo: pedido v047, etapa E2.141 (`R-REVIEW`), classe C, head `8eebc2a5` (Base-sha `bf475209`), instância que não fez a entrega. Sem parecer anterior: review completo. Li o diff inteiro de `bf475209...8eebc2a5`: 3 commits, 8 arquivos (`bin/forge-check` +40 -7, `hooks/parecer.py` +18 -12, `bin/forge-testes`, `tests/test_pr_hook_rapido.py` +180, `tests/test_testes_tocados.py`, spec de mutantes, `docs/hooks.md`, fragmento do changelog). QA (E2.143) e segurança (E2.142) correm sobre o mesmo head; não os refaço.

## Achados
- A1 (recomendado) hooks/parecer.py:565 · o aprovado gravado é JSON em `.git/forge/pr/<head>/`, gravável no sandbox, e o `escritor` é o sha256 público do forge-check do plugin: forjado, libera ready e merge sem parecer (sonda abaixo). No Forge o CI `bateria (pareceres)` segura o merge; nos projetos, ver A1 da segurança E2.142
- A2 (recomendado) bin/forge-check:362 · corpo truncado depois de um cabeçalho inteiro passa: lote `<sha> blob 500\nparecer: aprovado` devolve o texto parcial, contra o "nunca um texto parcial" do teste (tests/test_pr_hook_rapido.py:166); sugestão: `len(corpo) != tamanho` devolve {} e o rc do cat-file é conferido
- A3 (recomendado) bin/forge-check:5 · o docstring diz que o hook só lê o resultado gravado no `gh pr create`, e o comentário em bin/forge-check:1561 idem; agora ready e merge também o leem (texto antigo, classe AR-9); sugestão: atualizar as duas passagens
- A4 (recomendado) bin/forge-check:338 · 264 linhas contadas (M14, acima de 150) e dois comportamentos (atalho no hook e leitura em lote no forge-check); o corpo do PR precisa de `teto: excedido, 264 linhas, <motivo>`

## Sondas

## Parecer
**Aprovado**, com quatro recomendados. Faz o que a E2.117 pede sem afrouxar o veredito do `forge-check pr` (`R-REVIEW`):
- `verificar` (hooks/parecer.py:554-588): com `gravado` (EXIGE no create, ATALHO no ready e no merge), o aprovado do mesmo head, branch e base libera; o reprovado recusa; sem resultado, a conferência de hoje decide como antes, e o prazo vencido nela recusa com `rode antes forge-check pr`. O `create` segue exigindo o gravado (linha 585). O registro é preso ao head, à branch, ao `base_sha` resolvido por `base_do_delta` e ao `escritor`; outro head ou outra base cai no `ausente` e refaz a conferência (falha fechada). Testes de comportamento provam os quatro ramos com `cmd_pr` trocado por saída 97.
- `textos_da_arvore` (bin/forge-check:339-364): um `ls-tree -z` e um `cat-file --batch` por pasta, só blobs `.md` da própria pasta (como o `ls-tree pasta/` + `git show` anteriores), texto normalizado como o `git` em modo texto (teste compara com `git show`). Cache pelo id da árvore: o conteúdo é endereçado pelo hash, não envelhece. Resposta fora do pedido devolve {} (falha fechada); o caso de corpo truncado fica em A2, sem gatilho real (exige o git morrer no meio da saída).
- Pergunta do brief, "dá para forjar um aprovado do mesmo head?": sim. Sonda executada (`/root/.forge-contrib/v047-E2141-sonda/sonda_forja.py`, sobre a fixture do teste novo, sem pareceres na branch): `gh pr ready` e `gh pr merge` sem forja rc=2 (`R-REVIEW: ... nenhum parecer em docs/reviews/`); com o JSON escrito à mão (escritor = sha256 do forge-check que o hook carrega) rc=0, stderr vazio. Quem grava hoje é só o `gravar_resultado_do_pr`, mas nada impede outro escritor: a pasta fica no diretório comum do git, que o sandbox deixa gravar, e o `CITA_A_MARCA` do `conformidade` só vale nos projetos e só para o comando que cita `.git/forge`. No Forge, o merge no GitHub ainda passa pelo job `bateria (pareceres)` (catraca no CI), então o efeito local é tirar do rascunho ou mesclar sem a conferência do hook, com o CI como portão. Nos projetos não há esse segundo portão: é o A1 bloqueante da segurança (E2.142), que é de quem decide `R-SEGURANCA`; não o promovo aqui, só registro a prova. A correção que a segurança propõe (fora do clone do Forge o atalho só recusa pelo reprovado) muda `verificar` e pede revalidação deste parecer pelo delta.
- Mapa de testes: `test_pr_hook_rapido` entra em `FORGE_CHECK` e em `hooks/.*` do `bin/forge-testes`; a contagem de `test_testes_tocados` sobe para 85, com o comentário.
- PA-7 (`docs/engineering/achados-recorrentes.md`) conferido: AR-1 e AR-2 (mutantes e ramo de falha) cobertos; AR-4 os testes rodam o hook por `rodar`/`montar_proc` do `test_hooks`, com o ambiente da fixture; AR-9 cabe no A3; AR-12 a spec bate com o head (todos os mutantes acharam o trecho). Nenhum invariante de `tests/config.json` tocado.

Verificação (regra 5 de `docs/economia-de-tokens.md`; sem PR nem CI ainda, a suíte inteira fica com o CI do PR):
- `python3 -m unittest tests.test_pr_hook_rapido` no head: `Ran 10 tests in 33.414s` `OK`.
- `bin/forge-mutante --cobertura --base bf475209…`: as guardas mudadas `coberta` (PHR1, PHR5 a PHR8), a da base `isenta` (forge-check:348), nenhuma `apagada`.
- `bin/forge-mutante --processos 1 tests/mutantes/v047-pr-hook-rapido.json`: PHR1 a PHR8 `morreu` (8/8; PHR5 morre por erro do teste declarado sob o mutante: a subpasta `sub.md` vira objeto `tree` no lote).
