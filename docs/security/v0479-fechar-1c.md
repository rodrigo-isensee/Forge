---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-fechar-1c
commit: ef6b06e61476178a4d6dc4a5bd4c07bb8ccdc699
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0479-fechar-1c

Escopo: diff `73842444..ef6b06e6` (bin/forge-fechar, teste do 2b, mutante M1, fragmento do changelog), etapa E30.3 do pedido v0478. O `forge-fechar` é controle de merge; a pergunta é se o 1c novo no commit do merge do 2b falha fechado (nada sobe nem anda quando recusado) e se o argumento novo de mensagem abre injeção.

## Gatilhos
Gatilhos: controle de merge (forge-fechar, passo 2b com o 1c no merge), guarda de fluxo de branches (R-FLUXO)

## Achados

## Sondas

## Detalhe dos achados
Sem achado. Análise:

- Ordem e falha fechada: `bin/forge-fechar:844` chama `promovivel` depois do `commit-tree` e antes de qualquer escrita de ref (worktree `merge --ff-only`, `update-ref`) e do `git push origin` (`:854`). `promovivel` roda no shell principal (não em subshell) e a recusa cai em `die` (`:69`, `exit 1`), então o script termina sem avançar a branch nem enviar; o único resto é um commit solto no banco de objetos local, sem ref, inofensivo. Provado por `test_e30_1_base_com_release_nao_promovida_recusa_o_merge_sem_envio` (promover-homolog real, head local e remoto iguais ao antigo, sem PR nem merge) e `test_e30_1_merge_nao_promovivel_para_antes_do_envio_e_o_head_antigo_passou` (o 1c viu o commit do merge com os pais head antigo e base do servidor); o mutante M1 desliga a chamada e os dois testes o matam.
- Estado entre chamadas: `rc_1c=0` é `local` e zerado a cada chamada (`:910`); o 1c do head antigo (rc 0) não vaza para o 1c do merge.
- Entrada: `$novo` vem do `git commit-tree` sobre uma árvore já exigida hexadecimal (`:839`) e vai entre aspas como argumento único ao script de promoção, chamado com `python3 -I` e prazo de 300 s; o `$2` novo (`${2:+ ($2)}`) só entra no texto da mensagem de `die`, sem `eval` nem reinterpretação; `$base` e `$ref` são do operador local.
- Sem afrouxamento: o 1c do head (passo 1c) e o do recomeço com `--trazida` continuam; o envio segue `git push origin` sem forçar nem pular o pre-push (R-VERIFY). O `FORGE_PROMOVER` continua só com `FORGE_FECHAR_TESTE=1` (`:194-199`, inalterado).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados: os 3 testes `e30_1` e o módulo `tests.test_fechar_base_andou` inteiro (40 testes, OK, 58 s); a suíte inteira fica no CI do PR (ainda sem PR neste head). Lacunas do ambiente: shellcheck e gitleaks fora do PATH (não instalados, R-CUSTO); o shellcheck roda no CI.
