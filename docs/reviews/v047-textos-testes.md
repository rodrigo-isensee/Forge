---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-textos-testes
commit: 219c3c50ae76ef60bded7b6337ad6803673485d9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 (E1.268, item E1.255)

Intervalo revisado: `c5c3a449..219c3c50` (base `origin/develop` = merge-base), 2 commits, 5 arquivos, 54+/9-. Código e teste contados (M14): `tests/test_forge.py` 43 linhas, dentro do teto; skills e fragmento são `.md`.

## Achados
- A1 (recomendado) skills/contribuir-com-o-forge/SKILL.md:21 · 4c7b51c4 corta texto fora do item (motivo de não usar worktree de outro clone; aviso de que forge-check docs e pre-push barram, briefs-e-conferencia:27; exemplo de clone sem refs, qa-testing:89) sem dizer no commit nem no PR que foi para caber no tamanho.

## Sondas

## Parecer
Aprovado. O diff faz o que E1.255 pede (CONTRIB-TESTE-NICE da Q6 do dono, UNITTEST-I-NAO-IMPORTA, BRIEF-UNITTEST-DISCOVER): a seção 5 da contribuição traz `nice -n 19` e um arquivo por vez; qa-testing e briefs-e-conferencia trazem `python3 -I -m unittest discover -s tests -p test_x.py`. O fragmento `changelog.d/v047-textos-testes.md` existe e o `CHANGELOG.md` não foi tocado.

Teste `RodarUmModuloComIsolamento`: não fica só na leitura do texto. Ele extrai a forma de cada skill e a roda num projeto mínimo que imita o Forge (sem `__init__.py`, com import de vizinho), com ambiente limpo (só `PATH`) e `sys.executable` com `-I`, e prova o contrário: `-m unittest tests.test_x` sob `-I` falha com `No module named 'tests'`. Contagem exata por skill (1 forma cada), então o teste não passa vazio. Rodei o teste novo no head: `nice -n 19 python3 -I -m unittest discover -s tests -p test_forge.py -k RodarUmModuloComIsolamento` → `Ran 3 tests ... OK`.

Sem guarda de código no diff (só skills, fragmento e teste): não há mutante a declarar. A suíte inteira fica para o CI do PR (ainda não aberto); cito o PQ do autor no log do pedido: `test_forge 613 OK` no 219c3c50.

A1 é recomendado: os cortes ficam do mesmo tamanho que o texto novo (as três skills mudam menos de 30 bytes) e não tiram regra com ID nem trecho de `invariantes`; o CI confere estes últimos.
