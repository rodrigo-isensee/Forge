---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-fechar-sem-homolog
commit: e3e38dc8f2716cce938fee31019f87ae37703de8
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047-fechar-sem-homolog

Etapa E2.123 do pedido v047, lote FE1. Diff revisado: `bf475209..e3e38dc8` (`bin/forge-fechar`, `tests/test_fechar.py`, `tests/mutantes/v047-fechar-sem-homolog.json`, fragmento do changelog).

## Gatilhos
Controle do fluxo de merge (`R-FLUXO`, `R-MAIN`): o passo 2 do fechamento passa a aceitar, sem a branch no origin, um head "já no alvo" e segue para a limpeza; o passo 1c passa a buscar a `origin/homolog` quando ela falta no clone.

## Achados
- A1 (recomendado) bin/forge-fechar:831 · a leitura do gh que falha no ja_no_alvo conta como não mesclado (fail-closed, pelo status do filtro final), mas nenhum teste do item a exercita; um teste com o gh falhando nas 3 tentativas trava esse ramo (AR-2).

## Sondas

## Detalhe dos achados
**Pergunta do brief: dá para forjar "já no alvo"?** Não, com caminho de ataque realista. `ja_no_alvo` (`bin/forge-fechar:831`) só é chamado com a remota ausente e lida com sucesso (`bin/forge-fechar:1174-1175`; leitura que falha já para no `|| die`). Vale por um de dois caminhos:
1. `merge-base --is-ancestor <sha> $base`: a base é a ref local (`origin/develop` por padrão, ou `--base` do próprio operador). Forjar exige escrever na ref local do operador, que já é o dono da máquina; e o passo 3 (`bin/forge-fechar:1184`) já tratava esse mesmo caso como mesclado antes desta mudança. Sem ganho novo.
2. PR na lista do gh com estado `MERGED`, base igual ao alvo, `headRefOid` igual ao sha conferido (40 caracteres exatos, comparação de campo inteiro) e `isCrossRepository` diferente de `true`. O PR de fork com o mesmo nome de branch fica fora (o teste `test_2_remota_apagada_sem_merge_do_head_no_alvo_continua_pedindo_push` cobre fork, PR aberto, outra base e outro head). Forjar um MERGED do próprio repositório no alvo exige permissão de merge na develop protegida, ou seja, já ter o que o atacante ganharia. Os campos vêm separados por espaço; estado, nome de ref e sha não aceitam espaço, então não há deslocamento de coluna.

**O que o "já no alvo" falso destravaria:** nada que apague trabalho. Com `remoto_sha` igual ao conferido, o passo 3 refaz o teste (mais frouxo no fork, mas só alcançado depois do teste estrito do `ja_no_alvo`) e marca `ja_mesclado=1`: não cria PR nem mescla. A limpeza (`limpar_entrega`, `bin/forge-fechar:548`) confere o sha da branch local contra o mesclado antes de remover worktree ou branch e nunca força; a remota já não existe. O efeito restante é mover o cartão para Pronto, que só ocorre com uma das duas provas acima.

**Busca da homolog no 1c** (`bin/forge-fechar:822`): refspec constante, sem entrada do usuário; só roda com a ref ausente e só escreve a ref de rastreamento. Falha avisa e o `--conferir-ref` sai com 1 sem a ref, então o 1c continua parando (fail-closed). O interpretador do promover continua com `-I` (AR-5 conferido).

**A1:** severidade informativa; correção mínima: um caso no teste do passo 2 com o gh falhando nas 3 leituras e a remota ausente, esperando a parada do passo 2 com o pedido de push; esforço P; dono: autor da branch.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes do item rodados localmente (7, verdes); a suíte inteira fica para o CI do PR. Varreduras de segredo e de workflow não se aplicam ao diff (sem segredo, sem workflow).
