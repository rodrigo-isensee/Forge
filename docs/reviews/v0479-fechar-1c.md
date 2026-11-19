---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-fechar-1c
commit: ef6b06e61476178a4d6dc4a5bd4c07bb8ccdc699
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E30.2, 1c no merge do 2b do forge-fechar)

Diff 7384244..ef6b06e6: `bin/forge-fechar` (+6 -3 de código), um teste de dry-run ajustado, três testes novos em `tests/test_fechar_base_andou.py`, mutante M1 e fragmento de changelog. Dentro do teto H1 e um comportamento só.

## O que foi lido
- `trazer_a_base` (bin/forge-fechar:837): o `promovivel "$novo"` entra depois do `commit-tree` e antes de qualquer escrita (update-ref, ff da worktree, push). Recusado, o `die` para sem andar a branch local nem a remota; o teste com o `promover-homolog` de verdade e a base com release 0.0.2 não promovida prova o caso real, e o falso que só aceita o head antigo prova a ordem (head antigo conferido primeiro, depois o merge com os pais certos).
- `promovivel` ganhou o 2º argumento opcional `<onde>`, só na mensagem (`${2:+ ($2)}`); as chamadas antigas (linhas 1066 e 1273) ficam iguais.
- Guardas do diff: uma linha nova de controle (a chamada que pode morrer, linha 844), com M1 declarado. `bin/forge-mutante tests/mutantes/v0478-fechar-1c.json` no ef6b06e6: `M1 · morreu · bin/forge-fechar:844`. Os 3 testes `e30_1` e de dry-run rodados: OK.
- Suíte inteira: fica no CI do PR (sem PR nesta etapa); não rerrodada aqui.

## --dry-run sem executar o 1c
Aceitável. O dry-run só descreve: não cria o commit de merge, logo não há árvore a conferir, e o 1c do head também não roda no dry-run (contrato de `test_1c_no_dry_run_e_fora_da_base_develop_nao_roda`, tests/test_fechar.py:307). Executar o 1c só no merge do 2b quebraria essa simetria e o "sem efeito" do dry-run (o `git fetch` da homolog). A descrição do passo 2b passou a citar o 1c, e o teste novo a prende.

## Achados
- A1 (recomendado) bin/forge-fechar:844 · o recomeço com --trazida roda o 1c de novo no mesmo sha do merge (linha 1273): até 300 s e um fetch a mais por fechamento com base andada; vale um cartão para pular o 2º 1c quando o sha já foi conferido na cadeia.

## Parecer
Aprovado. Faz o que a E30.1 pede (a base com release não promovida para antes do envio, sem gastar run de CI: R-CUSTO), sem afrouxar guarda (R-VERIFY: o push segue o de sempre). A1 não devolve; vira cartão.
