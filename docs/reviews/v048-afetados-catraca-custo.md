---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v048-afetados-catraca-custo
commit: ecc3b7429450779edbda367bb40ddf834e4417d4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: v048 (#960, AFETADOS-CATRACA-E-CUSTO, volta 1, classe C)

Revalidação (E9.7) do head ecc3b742. Delta lido: `forge-check parecer delta` deu `f4ae675c..ecc3b742`, com 7 arquivos no domínio: `bin/forge-testes`, o fragmento do changelog, as listas de mutantes -2, -3 e -5, `tests/test_afetados_catraca_custo.py` e `tests/test_forge_mutante.py`. Fora do domínio: os três pareceres da 1ª rodada.

## Achados
- A1 (recomendado) tests/test_afetados_catraca_custo.py:62 · saiu "scripts/protegido.pyx", único caso do protegido exato contra prefixo: `caminho == item` → `caminho.startswith(item)` sobrevive (S1). Ponha um protegido de brinquedo fora de scripts/ e o caso `.pyx` dele.

## Sondas
- S1 · `bin/forge-testes`: `any(caminho == item or` vira `any(caminho.startswith(item) or`, roda `tests.test_afetados_catraca_custo` · espera: algum teste falha · obtido: ecc3b742 OK (sobrevive); com o teste e a ferramenta do f4ae675c, `test_o_resto_fica_como_esta` falha (o mutante morria)

## Conferido
- A1 da 1ª rodada (stdout do plano): resolvido. A linha "catraca no diff" e o aviso da catraca que não pode rodar vão ao stderr (`bin/forge-testes:1366-1369`). Os três leitores do stdout: `.githooks/pre-push:587` descarta o stderr (`2>/dev/null`) e casa só o começo ("forge-testes: dirigido (" ou "nada a rodar"); `scripts/conferir-reversao.py` (`ponta_dirigida`) lê só a 1ª linha; `bin/forge-mutante:1193` (`modulos_listados`) faz fullmatch no stdout, que agora tem uma linha só. O contrato `ContratoDoListar` roda o `modulos_listados` real num diff em bin/, com ambiente limpo, e o M38 (linha de volta ao stdout) morre nele.
- A2 da 1ª rodada (texto do PR): resolvido. O corpo do #960 tem "Projeto de origem", "Como medir" e a E9.2 (LIMITE_LOCAL), e `catraca (conferência)` passa no ecc3b742.
- Falha fechada (A1 da segurança): o link em `tests/catraca.py` sempre pede a catraca. Ela também é pedida quando o arquivo some e o diff o lista. O diff vem de `git diff --name-only --no-renames`, então uma remoção entra na lista. O `catraca_rodavel` é conferido de novo na hora de executar, e o plano sai com rc 1 sem executar o alvo (`test_catraca_em_link_reprova_sem_executar` confere que `catraca-rodou` não existe). Sem `tests/catraca.py` e fora do diff (projeto sem catraca), nada muda (M39).
- Testes mudados, sem perda fora de A1: `test_catraca_em_link_nao_conta` fixava a falha aberta e virou `..._pede_a_catraca_e_nao_e_rodavel`, mais forte (3 casos e `catraca_rodavel`). As asserções de `r.stdout` foram para `r.stderr`, e o `--listar` ganhou `len(stdout.splitlines()) == 1`. O teste sem catraca agora procura em `stdout + stderr`, uma busca mais ampla. `scripts/outro.py` passou para o lado que pede a catraca, que é o novo comportamento. Entraram `lib/scripts/x.py` e `tests/scripts/x`, que provam que a regra é um prefixo da raiz e não uma substring.
- scripts/ em `PASTAS_DA_CATRACA`: bate com `SENSIVEIS` e `PASTAS_CUSTO` de `tests/catraca.py:51-52` (M37).
- Mutantes: M33 a M39, M9, M12 e M21 morreram aqui, um processo por spec (`bin/forge-mutante --processos 1 ... --ids`). `bin/forge-mutante --cobertura --base f4ae675c` dá rc 0: as guardas 587, 589, 600, 1367 e 1381 têm mutante.
- Testes locais do delta: `tests.test_afetados_catraca_custo tests.test_forge_mutante.ContratoDoListar` passam, 23 OK.
- Tamanho: o delta em `bin/forge-testes` tem +26 −10 e fica dentro do teto H1 junto com a 1ª rodada.
- ci: ecc3b7429450779edbda367bb40ddf834e4417d4 verde
- CI lido em `gh pr checks 960`, runs 46159710035 e 46159816483 com headSha ecc3b742. Verdes: suíte 1/5 a 5/5, bateria (passos, python 3.14, verificações longas), instalação, árvore já provada, catraca e catraca (conferência). Só `bateria (pareceres)` fica de fora, porque espera os pareceres.

## Parecer
Aprovado. O delta resolve os dois bloqueantes da 1ª rodada: o stdout do plano tem uma linha só, com teste de contrato no leitor que o lê inteiro, e o texto do PR está corrigido. Também fecha a falha aberta que a segurança apontou e põe scripts/ entre as pastas da catraca. A1 vira cartão depois do merge. O A3 da 1ª rodada, a mensagem "nada a rodar" depois do corte, segue como cartão.
