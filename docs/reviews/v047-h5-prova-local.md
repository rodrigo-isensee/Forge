---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-h5-prova-local
commit: c046a44b34066447d9f595b9d31e3679ba2b9fba
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v047 (E2.646, item E2.642, H5-PROVA-LOCAL-POR-TESTES-TOCADOS)

Parecer sobre o head c046a44b, base 73a0ab81 (um commit).

## Escopo lido
- Diff: `bin/forge-mutante` (41+/2-), `tests/test_forge_mutante.py` (71+), spec `tests/mutantes/v047-h5-prova-local.json` (M1 a M5) e fragmento `changelog.d/`. Código e teste: 114 linhas, dentro da orientação M14; um comportamento só.
- E2.642 pede que o `forge-mutante` limite a mutação aos módulos do `forge-testes --listar` do diff, sem editar o `forge-testes`. A entrega faz isso no `dirigir` (só com `--base`): `modulos_listados` lê a linha do plano dirigido; `limitar` tira de cada mutante os testes fora desses módulos e imprime `testes fora dos módulos do diff`. Suíte completa, erro, prazo ou saída fora do formato não limitam. `bin/forge-testes` intocado. Nem mais, nem menos.
- O Forge não tem `docs/engineering/praticas.md`; o review segue o checklist da skill `engineering-practices`.

## Verificação
- A regex `PLANO_DIRIGIDO` bate com o texto de `bin/forge-testes:962`, e o `--listar` sai logo depois (`:967`), sem outra linha no stdout no modo dirigido.
- Direção segura: tirar testes nunca faz um mutante "morrer" falso (o controle roda sem o mutante); o pior caso é um sobrevivente a mais, que pede mais teste e não afrouxa o portão.
- Guardas novas (`except`, `if achado`, `if modulos_candidatos(t) & modulos`, `if not dentro or len(...) ==`): um mutante por linha (M1 a M5), cada um com teste de comportamento do ramo de falha. Os subprocessos do teste usam ambiente limpo e `-I`.
- Rodado aqui: `python3 -m unittest tests.test_forge_mutante.LimiteDosModulos`, 4 testes OK; `bin/forge-mutante tests/mutantes/v047-h5-prova-local.json --base 73a0ab81...`, M1 a M5 morreram (linhas 1050, 1051, 1051, 1034, 1038); `bin/forge-mutante --cobertura --base 73a0ab81...`, as 3 linhas de guarda saem `coberta`. Suíte inteira: fica para o CI do PR (sem suíte local, pelo brief).

## Achados
- A1 (recomendado) bin/forge-mutante:1032 · o forge-testes --listar lê a árvore do cwd (mapa, quem_importa, arquivos), e a mutação roda na cópia do --rev; com --rev diferente da árvore, o plano pode não ser o do sha. Rodar o listar na cópia ou registrar a limitação no uso.
- A2 (recomendado) tests/test_forge_mutante.py:1676 · o ramo sem plano dirigido depende de um detalhe interno do forge-testes (módulo do mapa sem arquivo dá suíte completa); se o mapa mudar, o teste passa a provar outra coisa. Um falso do subprocess com a linha de suíte completa deixaria o ramo independente.

## Sondas

## Parecer
Aprovado. Faz o que a E2.642 pede, com guardas cobertas por mutantes que morrem e falha sempre para o lado de rodar os testes inteiros. A1 e A2 são recomendações e não devolvem a entrega (`R-REVIEW`).
