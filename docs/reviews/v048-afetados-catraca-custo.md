---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v048-afetados-catraca-custo
commit: f4ae675c22dd8b656a5dc28a7db85f1e3e3d1e99
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: v048 (#960, AFETADOS-CATRACA-E-CUSTO, E9.1 e E9.2, classe C)

1ª rodada completa no head f4ae675c (E9.3), diff `ed6e6dbf..f4ae675c`: `bin/forge-testes` (+109 −12, dentro do teto H1), teste novo `tests/test_afetados_catraca_custo.py`, 5 listas de mutantes e o fragmento do changelog.

## Achados
- A1 (bloqueante) bin/forge-testes:1353 · a 2ª linha do stdout ("catraca no diff") quebra o `modulos_listados` do bin/forge-mutante:1193, que faz fullmatch no stdout inteiro: diff em bin/, hooks/ ou protegido perde o recorte H5 e roda os testes declarados inteiros (S1). Mande a linha ao stderr ou leia só a 1ª linha, com teste.
- A2 (bloqueante) bin/forge-testes:1 · corpo do PR #960: `catraca (conferência)` vermelha no f4ae675c (R-CONTRIB, sem "Projeto de origem" nem "Como medir"); o corpo só descreve a E9.1 (M1 a M23, "23 morreram") e omite a E9.2 (LIMITE_LOCAL, M24 a M32). Corrija o texto; sem esse check verde o review não aprova.
- A3 (recomendado) bin/forge-testes:1342 · acima do limite, sem catraca e sem teste do arquivo mudado, o plano cai em "nada a rodar (nenhum teste afetado)" logo após o aviso de corte, e o pre-push repete "nenhum teste afetado": a mensagem diz o contrário do aviso; diga que o plano ficou todo para o CI.

## Sondas
- S1 · bin/forge-mutante `modulos_listados(["bin/forge-mutante"])` com o forge-testes da base ed6e6dbf e do head f4ae675c · espera: o mesmo recorte nos dois (test_forge, test_forge_mutante, ...) · obtido: base 6 módulos; head conjunto vazio (stdout com a linha "catraca no diff")

## Conferido
- Lista de protegidos: `protegidos_da_catraca` lê a `PROTEGIDOS` de `tests/catraca.py` por `ast`, sem cópia; o teste `ListaDaCatracaReal` usa a catraca real.
- Falha fechada: PROTEGIDOS ilegível, vazia, lista, com não-texto, por chamada ou ausente conta como tocada e leva os dois (`test_protegidos_ilegiveis_contam_como_tocados`). Catraca ausente ou em link não entra (repositório sem catraca, como os projetos).
- Corte de 1.000 só no `--afetados` (`args.afetados and ...`, linha 1336), com teste dos dois lados (1000 e 1001) e do modo sem `--afetados`.
- Pre-push: lê só a 1ª linha do `--afetados --listar` (`.githooks/pre-push:587-590`), que segue "forge-testes: dirigido (" ou "forge-testes: nada a rodar"; o aviso do corte vai ao stderr. O `scripts/conferir-reversao.py:51` também lê só a 1ª linha. O consumidor que lê o stdout inteiro é o forge-mutante (A1).
- Guardas: `bin/forge-mutante --cobertura --base ed6e6dbf` dá todas as guardas mudadas cobertas (a 1235 da base isenta, com motivo); os 32 mutantes declarados (M1 a M32, 5 listas) morreram aqui, 1 processo.
- Testes locais do diff: `tests.test_afetados_catraca_custo` 19 OK; `tests.test_testes_tocados tests.test_changelog` 290 OK (1 pulado); `tests/catraca.py --base ed6e6dbf` rc=0.
- CI do f4ae675c (`gh pr checks 960`): suíte 1/5 a 5/5, bateria (passos, python 3.14, verificações longas), instalação e árvore já provada verdes; `catraca` espera o parecer; `catraca (conferência)` vermelha pelo texto do PR (A2). Sem CI verde fora das exceções, não há linha de CI verde neste parecer.

## Parecer
Reprovado. O código faz o que E9.1 e E9.2 pedem, com a lista sem cópia, a falha fechada e o corte só no `--afetados`. Bloqueia: A1, a linha nova no stdout desliga o recorte de módulos do forge-mutante justamente nos diffs de classe C (sugestão: a nota da catraca vai ao stderr, ou o forge-mutante passa a ler a 1ª linha, com teste de contrato que roda o `modulos_listados` com a catraca no plano); A2, o texto do PR, que deixa um check obrigatório vermelho e não descreve a E9.2. A3 vira cartão depois do merge. Na volta, o review lê só o delta.
