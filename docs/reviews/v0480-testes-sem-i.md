---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-testes-sem-i
commit: 870f0b9157ad1953d2aa343be767e85b48ab0c34
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E161.2, forma única de rodar o módulo de teste na raiz; PR #845)

Escopo: diff `789fc141..870f0b91`, com 6 arquivos: `skills/qa-testing/comandos.md`, três skills que apontam para ele, `tests/test_forge.py` (classe `RodarUmModuloComIsolamento`) e o fragmento `changelog.d/v0480-testes-sem-i.md`. Não há código de controle no diff, só texto e teste, então fica dentro do H1 e sem guarda a declarar.

Verificado:
- O pedido é cumprido. A forma `python3 -m unittest tests.test_x` aparece uma vez só, em `comandos.md`, e `qa-testing`, `briefs-e-conferencia` e `contribuir-com-o-forge` apontam para lá. O `-I` continua onde protege (o subprocesso do teste e o script que lê dado de fora), e `agents/tech-lead.md` não mudou. `git grep -- '-I -m unittest'` só encontra a forma antiga no `CHANGELOG.md` e em pareceres antigos de `docs/`, que são histórico.
- A forma nova funciona nos módulos reais. Listei os `tests/test_*.py` sem `sys.path.insert` e nenhum importa um módulo vizinho de `tests/`. Assim, o fixture novo (que põe a própria pasta no `sys.path`) reproduz o caso do Forge e não deixa passar um módulo que quebraria.
- Comparação com o teste antigo:
  - O teste antigo exigia a forma uma vez em cada skill e a rodava em cada uma. O novo exige a forma exata uma vez em `comandos.md` e a roda. Também barra a forma antiga em todo `.md` de `skills/` e `agents/` (com um piso de 40 arquivos lidos) e mantém a seção 5 em `nice` e um arquivo por vez. O teste de que `-I` com `tests.test_x` não importa continua igual.
  - Nesses pontos, o teste novo não ficou mais frouxo, e a busca da forma antiga cobre mais arquivos que antes.
  - A exceção é a verificação do ponteiro, descrita no A1.
- Rodei `python3 -m unittest tests.test_forge.RodarUmModuloComIsolamento` no head: 3 testes, OK.
- Mutantes rodados numa cópia do head em `$TMPDIR`:
  - Com a forma antiga de volta em `contribuir-com-o-forge`: 1 FAIL.
  - Com a forma de `comandos.md` trocada para `-I`: 1 FAIL e 1 ERROR.
  - Os dois mutantes morrem.
- CI do PR no head 870f0b91 (run 45331713345): a instalação, a bateria e a catraca passaram, e a suíte em partes ainda roda. Citei o CI sem rerrodar a suíte; o merge depende dela verde.

## Achados
- A1 (recomendado) tests/test_forge.py:8086 · O ponteiro só confere "comandos.md" em qualquer parte do arquivo. Para qa-testing/SKILL.md isso já era verdade na base (2 menções), então tirar o ponteiro novo da linha 75 não derruba o teste. Sugestão: conferir o texto do ponteiro ('Um módulo de teste' ou "onde o `-I` vale").

## Sondas

## Parecer
Aprovado. A forma de rodar um módulo ficou num lugar só, o `-I` segue onde protege e o teste reescrito não afrouxou o que já cobria: a forma é rodada e a forma antiga é barrada em mais arquivos. O A1 é recomendado e vira cartão depois do merge.
