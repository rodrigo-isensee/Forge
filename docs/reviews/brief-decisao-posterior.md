---
tipo: review
contrato: 1
pedido: versao-035
branch: melhoria/brief-decisao-posterior
commit: 90a57d43ad227effc0c2f5938743f0ca4f4cedeb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-05
---
# Review: BRIEF-DECISAO-POSTERIOR (E5 da versao-035)

Escopo: `d9b26bb...90a57d4` (3 commits): `bin/forge-check` (+17 -9), `bin/forge-testes` (+1 -1), `tests/test_decisao_aprovacao_raiz.py` (novo, +83), `tests/test_testes_tocados.py` (+1 -1), fragmento `changelog.d/brief-decisao-posterior.md`. Teto M14: 113 linhas de código e teste, dentro; nenhum arquivo de `hooks/` nem de `PROTEGIDOS`. Um comportamento só (ampliar a P-N4 ao quadro fora do clone, com o aperto do item 2 junto, que o C-8 exige no mesmo PR). Revisor: outra instância, não a que implementou. Julgado contra a seção `## E5.` do `docs/arquitetura/versao-035-desenho.md` e o E5 de `docs/security/ameacas/versao-035.md`.

## Verificado na prática
- Módulos tocados (`python3 -m unittest tests.test_decisao_aprovacao_raiz tests.test_decisao_aprovacao tests.test_testes_tocados`): 98 testes, OK. A forma `-I -m unittest` dá `ModuleNotFoundError: tests` (o modo isolado tira a pasta atual do caminho); sem `-I`, roda.
- Mutantes à mão numa cópia (`git archive` do HEAD, fora da worktree), contra `tests.test_decisao_aprovacao_raiz`: `bin/forge-check` da base inteira (7 falhas); sem a comparação da coluna 2 (3); ordem `raiz` antes da raiz do brief (3); sem `dentro_da_raiz` (1); sem a raiz do brief (3); link pulado com queda para o seguinte (2). Todos mortos: o teste prova o item 1, o item 2, a ordem (C-4) e o "não cai" (C-5).

## Afrouxamento no tamanho autorizado (decisão do dono de 15:20)
- T-7: o diff no `bin/forge-check` fica nas três regiões: `hora_da_aprovacao` (assinatura com `pedido_id` obrigatório, sem omissão), `decisoes_cobradas` (parâmetro final `pedido_id=None`, a frase da docstring e o `return`, com `aprovacao` None sem `brief` ou sem `pedido_id`, falha fechada) e a chamada em `avaliar_brief`, que repassa o id já calculado ali. Os outros chamadores de `decisoes_cobradas` não mudam.
- C-1, C-6, C-7: `decisao_posterior` intacta; a hora vem sempre de uma linha do quadro; modo `brief` e resultado aprovado seguem exigidos. Brief sem aprovação, decisão sem hora e modo `entrega` não ganham exceção.
- C-2, T-1: igualdade por `casefold` na coluna 2 inteira, com `pedido_id` vindo de `avaliar_brief`; o teste cobre caixa diferente (vale), `outro`, `exemplo-x` e `exemplo.md` (não valem).
- C-3, T-4: o `mtime` do brief segue exigido (`c[0] >= escrita`); o teste cobre a aprovação retrodatada.
- C-4, T-3, T-5: tupla fixa de três bases e `next(...)`: o primeiro candidato decide, sem somar nem mesclar tabelas e sem glob. Brief fora de `docs/briefs` fica só com `raiz` e `RAIZES_DE_BRIEF`.
- C-5, T-2: candidato achado por `lexists` e conferido por `dentro_da_raiz(..., ("docs/kanban",))`; reprovado, devolve None sem cair no seguinte; o próprio arquivo como link para em `O_NOFOLLOW` (`_tabela_segura`). Mesmo critério de `ler_registro`.
- C-9: a saída segue `decisões: decisão posterior à aprovação` (o teste a confere).
- C-10: o rótulo `afrouxa-regra` e a medida de reversão vão no corpo do PR (E2.7 e E2.8), fora desta branch.

## Achados
- A1 (recomendado) bin/forge-check:5174 · docs/kanban como link para pasta sem conferencias.md: lexists dá falso e a busca cai na base seguinte (igual ao ler_registro). Sem ganho ao atacante, mas a letra do C-5 diz não cair. Sugestão: lexists também no docs/kanban do candidato.
- A2 (recomendado) bin/forge-check:5180 · Sem spec de mutação do E5 em tests/mutantes (a pn4-decisao-aprovacao.json não cobre coluna 2, ordem nem link). Os mutantes à mão deste review morreram; sugestão: gravar a spec para o QA e o CI repetirem.

## Parecer
Aprovado. O código faz o que a seção E5 do desenho pede: a aprovação passa a ser lida do quadro da raiz do brief, com o aperto do A3 da P-N4 no mesmo PR, e o afrouxamento ficou no tamanho que o dono autorizou às 15:20: só brief já aprovado, pela linha do pedido certo, posterior ao `mtime`, no primeiro quadro válido da ordem fixa. Os controles C-1 a C-9 conferem no diff e nos testes; o C-10 é do PR. A1 e A2 não devolvem a entrega: A1 é uma leitura estrita do C-5, sem nenhum caminho de abuso (cair na base seguinte dá o mesmo que não ter o link); A2 é coisa de ferramenta. Segurança: a E2.2 deixou a E2.5 para o E5 só se houver dúvida no review; este review não abre dúvida de segurança.
