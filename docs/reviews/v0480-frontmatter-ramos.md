---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-frontmatter-ramos
commit: 1d6bd64f2f93b80e9609cfa48ec64fb1f3cd8e76
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 · casos por ramo de erro do conferidor de frontmatter (E137.3), etapa E137.14

Diff `0e59c446..1d6bd64f`: `tests/test_frontmatter_agentes.py` (+66, classe `RamosDeErro` e o auxiliar `_fm`) e o fragmento `changelog.d/v0480-frontmatter-ramos.md`. Só teste: nenhuma linha de `erros_do_frontmatter` nem código de produção muda, então não há guarda nova a declarar em `tests/mutantes/` e o teto H1 não se aplica (0 linhas de código).

## Ferramentas
- Suíte: só no CI do PR #823 (rascunho), pendente na hora deste parecer; não rerrodada aqui (`R-REVIEW`).
- Teste do arquivo tocado: `python3 -I tests/test_frontmatter_agentes.py -v` → `Ran 17 tests`, `OK`.

## Leitura
- Cada ramo de `erros_do_frontmatter` tem caso que o derruba: sem abertura, sem fechamento, linha fora de `chave: valor` (número de linha conferido: `- item` é a linha 4 com `_fm`), aspas duplas e simples sem fechar, valor de uma aspa só (pega a remoção de `len(valor) < 2`), aspa simples solta (`'it's'`, com o contraponto `'it''s'` válido), escalar terminado em `:`, escalar com ` #`, indicadores YAML que pulam a checagem, comentário e linhas em branco ignorados, falta de `name`, de `description` e obrigatório vazio. O ramo `': ' in valor` já tinha caso (`test_detecta_dois_pontos_sem_aspas`).
- Os casos de erro conferem a lista inteira (igualdade ou `len == 1` mais o texto), não só "há erro": um ramo que passe a acusar a mais também cai.
- Testes determinísticos, sem subprocesso nem disco; nomes dizem o ramo.
- Fragmento do changelog no formato da pasta (`### Alterado`), sem editar o `CHANGELOG.md`.
- A mutação dos indicadores (S1) mostra que só 6 dos 10 prefixos têm caso; o ramo como um todo cai, então é recomendado, não bloqueante.

## Achados
- A1 (recomendado) tests/test_frontmatter_agentes.py:111 · os prefixos `!`, `%`, `@` e crase da lista de indicadores não têm caso: tirá-los da tupla deixa a classe verde (S1); somar `"!a b: c"`, `"%a b: c"`, `"@a b: c"` e um com crase ao `subTest`.

## Sondas
- S1 · cópia do teste com a tupla de indicadores reduzida a `("[", "{", "|", ">", "&", "*")`, agents e stacks reais · espera: algum caso cai · obtido: Ran 17 tests, OK

## Parecer
Aprovado. O item faz o que a E137.3 pede, um caso por ramo de erro, sem tocar no conferidor; o único achado é cobertura parcial dentro do ramo dos indicadores, recomendado (vira cartão depois do merge).
