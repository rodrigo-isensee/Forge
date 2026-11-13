---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/v046-mapa-testes
commit: 78c8ad3fa3bfa18acd8f9e194b7416e4e947f454
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v046 (E22.7, MAPA do forge-testes, revalidação por delta)

Revalidação por delta `e6565be2..78c8ad3f` (volta E22.5) do parecer da E22.3, que reprovou o head `e6565be2` pelo A1. Li o delta com `forge-check parecer delta` e o diff inteiro de `bin/forge-testes`, `tests/test_testes_tocados.py` e `changelog.d/v046-mapa-testes.md`, em worktrees destacadas da base `a1318e88` e do head.

## Gatilhos
`R-SEGURANCA`: controle do Forge, o plano de testes do envio (o MAPA do `bin/forge-testes`, lido pelo `planejar` e pelo `--afetados` que o pre-push usa).

## Achados

## Sondas

## Detalhe dos achados
A1 da E22.3 (bloqueante, `bin/forge-testes:158`): **resolvido** pela correção 1 que o parecer anterior propôs. O commit `78c8ad3f` tira a regra `tests/test_ritmo\.py` do MAPA (antigas linhas 157-159) e a entrada `"tests/test_ritmo.py"` de `tests/test_testes_tocados.py` (antigas 57-58), e o fragmento do changelog deixa de anunciar a regra. Isso segue a DECISÃO DO DONO de 2026-10-24 (M8, opção C). O comentário de `bin/forge-testes:163` ("Módulo de teste no diff não tem regra: cai na suíte completa") volta a valer sem exceção.

Sonda S1 refeita no head, importando o script nas duas cópias:
- `planejar(["tests/test_ritmo.py"])`: base `a1318e88` e head `78c8ad3f` dão `('completo', ['tests/test_ritmo.py sem mapa'])`.
- `planejar(["tests/test_ritmo.py", "bin/forge-doutor"])`: `completo` na base e no head. Na E22.3 o head dava `dirigido` com 15 módulos.
- `planejar(["bin/forge-doutor"])`: base com 5 módulos, head com 9, e os 5 da base continuam no plano.

Nenhuma outra regra mudou. `git diff a1318e88..78c8ad3f -- bin/forge-testes` toca só a regra do `bin/forge-doutor` (`bin/forge-testes:118-120`), que ganha `test_doutor_custo, test_doutor_protecao_gh, test_doutor_relogio, test_qa_doutor_f8`. Essa regra só acrescenta módulos, como conferido na E22.3. No delta `e6565be2..78c8ad3f`, o domínio de segurança tem só as 3 linhas removidas do MAPA. `tests/test_testes_tocados.py` e o changelog estão fora do domínio e foram lidos: só tiram a entrada e o texto correspondentes. Nenhuma linha de guarda mudou, e por isso não há spec de mutante. `tests.test_testes_tocados` no head: 150 testes, OK (1 pulado, pré-existente).

PA-7: AR-3, AR-5, AR-7 e AR-11 (os de segurança) não se aplicam, porque o delta não toca hook, trava de ambiente, invocação de interpretador nem leitura do gh. A sonda rodou com `python3 -I`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check parecer delta`, leitura do diff, sonda S1 no `planejar` da base e do head (worktrees destacadas) e `tests.test_testes_tocados` no head. Lacuna: o gitleaks não está no PATH local. O delta não traz configuração nem credencial.
