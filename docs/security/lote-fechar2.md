---
tipo: revisao-seguranca
contrato: 1
pedido: lote-fechar2
branch: melhoria/lote-fechar2
commit: 5c6684ddd222f18cd82c055f0602e23340720d98
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: lote-fechar2 (revalidação, volta 3)

Escopo: revalidação por delta do parecer anterior (commit revisado `7c926e4`, parecer `435d059`) até `5c6684d`, pela decisão B do dono de 2026-10-27 (sort falso dos dois lados de `bin/forge-fechar:530`, mutantes Y1, Y2 e Y4, varredura de `:520-540` e o teste da contagem de commits de `:538`). O `forge-check delta` sobre este parecer lista só `tests/mutantes/lote-fechar2-2.json:54-86`, `tests/mutantes/lote-fechar2-3.json:1-27` e `tests/test_fechar_base_andou.py:17-21,30-32,59-60,243-265`; o intervalo `7c926e4..5c6684d` não toca `bin/`, `.github/` nem `hooks/` (`git diff --quiet` rc 0). O código de produção é o mesmo do parecer `435d059`, então não houve sonda nova.

## Gatilhos
Controle do Forge (`R-SEGURANCA`): o `forge-fechar` decide abrir e mesclar o PR (passo 2 e passo 2b) e apagar a branch remota (limpeza).

## Achados

## Detalhe dos achados
Sem bloqueante e sem recomendação nova. Verificações, com evidência:

1. **`bin/forge-fechar` não mudou.** Por isso continuam valendo as verificações do parecer `435d059`: validação da coluna 1 do `ls-remote` (`:141`) em falha fechada nos quatro chamadores, o laço sobre todos os merge-base (`:526`) e as guardas finais.
2. **Nenhuma asserção afrouxou.** O delta de `tests/test_fechar_base_andou.py` só acrescenta coisas: o `sort` falso (`:17-21`), o ramo `rev-list --count` do `git` falso (`:30-32`), a instalação do `sort` falso no PATH temporário (`:59-60`) e três testes (`:243-265`). Nenhuma linha removida. As specs de mutantes só ganharam entradas: Y1, Y2 e Y4 em `tests/mutantes/lote-fechar2-2.json:54-86`, e a spec nova `tests/mutantes/lote-fechar2-3.json` (M1 `:538` `|| die` virado `|| :`; M2 `:523` lista só com o primeiro merge-base).
3. **A falha da cadeia `sort && sort && comm` (`:530`) para em falha fechada, e o teste prova isso.** `_sort_que_falha_so_em` monta uma base com arquivo em comum, faz falhar só o `sort` da lista `a` ou só o da lista `b` e exige rc 1, a mensagem "não consegui cruzar as listas de arquivos", nenhum "sem arquivo em comum" e nenhum PR criado nem mesclado. Assim a falha de `sort` não passa como "sem arquivo em comum", que era o caminho do PR aberto sobre uma base em conflito. O teste da contagem (`:538`) exige parada sem PR quando o `rev-list --count` falha. Rodei o módulo `tests.test_fechar_base_andou` neste commit: 20 testes OK.
4. **Superfície nova dos testes.** O `sort` falso fica só no PATH temporário da suíte e repassa ao `sort` real, tirando o primeiro item do PATH, quando o arquivo de estado não existe. Ele não chega ao script de produção.
5. **PA-7.** `docs/engineering/achados-recorrentes.md` está sem achados registrados, então não há item a conferir.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas, todas locais: `forge-check delta`, `git diff` e `unittest`. A mutação da varredura de `:520-540` é prova do autor e do QA, e não foi refeita aqui. Faltaram no ambiente, e ficam como lacuna: `gitleaks`, `zizmor` e `actionlint` (o delta não traz credencial nem mudança de workflow).
