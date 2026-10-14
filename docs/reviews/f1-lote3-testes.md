---
tipo: review
contrato: 1
pedido: f1-lote3-testes
branch: melhoria/f1-lote3-testes
commit: 5704eea
parecer: aprovado
revisor: forge:qa-engineer
data: 2026-10-13
---
# Parecer de autor: disciplina de testes e guardas contra suíte vazia (fonte F1, lote 3)

Escopo: `origin/develop..5704eea` (1 commit): `skills/qa-testing/SKILL.md`, `skills/engineering-practices/SKILL.md`, `templates/projeto/docs/qa/_modelo.md`, `tests/test_forge.py`, `tests/test_hooks.py`, `tests/config.json`, `CHANGELOG.md`. O autor é o `qa-engineer`: este parecer é de autoria; o review independente é do `tech-lead`.

## Item 4 (obrigação → teste, regra de parada)
Seção nova na `qa-testing` (88 linhas, limite 133, sem arquivo de referência) e coluna "fronteira protegida" na tabela critério → teste, também no modelo de QA do projeto.

## Item 7 (guardas)
Helper `minimo(itens, n, rotulo)` em `tests/test_forge.py`: levanta `AssertionError` se o percorrido tem menos de N itens (N de hoje menos margem pequena). Aplicado nos helpers `agentes_do_plugin`, `skills_do_plugin` e `arquivos_texto` (cobre todos os testes que os usam) e direto em: manifesto, stacks, `invariantes`, `Neutralidade`, `NeutralidadeDoNucleo`, `AntiDuplicacao`, `RegrasComId`, `ForgeInit`, migração 0.7.0, workflows e, em `tests/test_hooks.py`, fixtures, scripts de hook e `hooks.json`. Mais de 25 testes ganharam guarda. Listas literais curtas escritas no próprio teste (`for x in ("a", "b")`) não entraram: não podem ficar vazias sem editar o teste.

## Prova da mutação
- Renomear, uma por vez, `hooks`, `docs/regras`, `tests/hooks`, `tests/migracoes`, `templates/projeto`, `.github/workflows`, `agents`, `skills` e `stacks` derruba a suíte (FAILED em todas); desfeito em seguida (`git status` limpo).
- Antes × depois, nos mesmos dois testes (`CI.test_acoes_fixadas_por_sha` e `Neutralidade.test_sem_termos_de_projeto`) com `.github/workflows` e `tests/transcricoes` renomeadas: na `develop`, `OK` (passavam sem ler nada); com a mudança, `FAILED (failures=2)`.
- Nenhum teste afrouxado: só se acrescentou afirmação (o `assertGreaterEqual` e `assertTrue(pacotes)` antigos viraram `minimo`, com o mesmo piso ou mais alto).

## Verificação
`python3 -m unittest discover -s tests`: 310 testes, OK. `scripts/validar-plugin.sh`: passou. Invariantes só acrescentados (3 arquivos novos em `tests/config.json`).

## Risco
Os pisos acompanham o tamanho de hoje; remover arquivos legitimamente a ponto de cruzá-los exige baixar o N no mesmo PR, o que fica visível no diff.
