---
tipo: review
contrato: 1
pedido: f1-lote3-testes
branch: melhoria/f1-lote3-testes
commit: 7164cd1
parecer: reprovado
revisor: forge:tech-lead
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

## Review independente
Revisor: `forge:tech-lead`, sobre `7164cd1` (validação local; cota do Actions esgotada).

Resultados no checkout do PR:
- `python3 -m unittest discover -s tests`: 310 testes, OK. `scripts/validar-plugin.sh`: passou.
- `catraca.py --modo pareceres` e `--modo pr-texto` (com o corpo do PR em `PR_BODY`): sem acusação. Versão e changelog: `plugin.json` segue 0.12.0 e há linha nova em `[Não publicado]`: ok.
- **`catraca.py` (modo regras, `--base` = merge-base com `develop`): FALHA.** `R-CONFORMIDADE: asserções em tests/ caíram de 715 para 712`.

### Bloqueia
- `tests/test_forge.py` (3 pontos): `self.assertTrue(pacotes, ...)`, `self.assertTrue(fontes, ...)` e `self.assertGreaterEqual(len(casos), 5)` foram trocados por `minimo(...)`, que levanta `AssertionError` por dentro de um helper e não conta como asserção para a catraca (o AST só conta `assert` e `assert*`). O parecer de autor diz que nada foi afrouxado e, de fato, o piso é igual ou maior, mas o CI da catraca reprovaria o PR e só o rótulo `afrouxa-regra` (do dono) o liberaria. Correção sugerida, sem perder força: manter as três asserções originais ao lado do `minimo` (ou fazer o `minimo` terminar em um `assert`/`self.assert*` que a catraca enxergue); depois a catraca deve dar 715 ou mais.

### Conferido, sem ressalvas
- Nenhuma asserção antiga foi removida além dessas três; as demais mudanças só acrescentam.
- Pisos realistas, com margem pequena e sem travar a adição de itens (hoje x piso): agentes 8x7, skills 12x11, regras 14x13, fixtures de hook 468x460, hooks 7x5, workflows 3x3, invariantes 27 arquivos x23 e 104 trechos x95, termos por hash 11x10. Só a remoção legítima de itens cruza o piso, e isso aparece no diff.
- Mutação por amostragem: renomear `docs/regras` derrubou 8+ testes (ERROR/FAIL); desfeito, árvore limpa.
- Seção "Teste nasce de obrigação, e para quando ela está coberta" na `qa-testing`: clara, curta e com regra de parada objetiva.
- Item 10 do checklist está em `skills/engineering-practices/SKILL.md`; o `tech-lead` carrega a skill pelo frontmatter (`skills: engineering-practices`).

Parecer: **reprovado** até a catraca passar. Os demais pontos estão aprovados; o reenvio é só o ajuste das três asserções.
