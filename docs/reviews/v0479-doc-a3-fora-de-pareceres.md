---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-doc-a3-fora-de-pareceres
commit: 0d656a84a470ccb3ea48dd0dd3aa854290fe1a2e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E55.3, documento e patch da A3 fora de docs/devops, head 0d656a84)

Escopo (E55.1): `docs/devops/` só guarda pareceres (`PASTAS_DO_SO_PARECER` em `bin/forge-check`), e o documento de aplicação da A3 e o patch estavam lá. O diff `5ccac0bf..0d656a84` move os dois para `docs/engineering/`. O `.patch` não muda (`similarity 100%`), e o `.md` só troca os três caminhos. As referências foram atualizadas: o `MAPA` do `bin/forge-testes` (linha 202), a constante `PATCH` e a docstring de `tests/test_sandbox_controle.py`, `docs/hooks.md:143` e o fragmento `changelog.d/v0479-sandbox-controle.md`. O fragmento novo `changelog.d/v0479-doc-a3-fora-de-pareceres.md` registra a correção. A mesma forma já existe em `docs/engineering/v0479-bp3-s2-container.{md,patch}`.

Lido:
- `grep -rn "devops/v0479-sandbox-controle"` no head não acha nada: nenhuma referência ficou para trás.
- Nenhuma guarda mudou (a linha do `MAPA` é dado, não ramo), então não há mutante a declarar.
- A entrega faz o que o pedido pede, nem mais nem menos (R-REVIEW, item 1 do checklist). Não toca neutralidade nem regra com ID (R-NEUTRO).
- Rodei aqui o teste tocado: `cd tests && python3 -m unittest test_sandbox_controle` deu `Ran 14 tests ... OK (skipped=2)`. Os dois testes do bubblewrap pularam (o sandbox não tem namespace), e a prova do `git apply` sobre o patch no caminho novo passou.
- A suíte inteira fica no CI do PR. Não havia PR aberto quando li, e não a rerrodei.

## Achados
- A1 (recomendado) tests/test_sandbox_controle.py:32 · o commit f979baf9 move o patch e deixa `PATCH` em docs/devops, então o teste fica vermelho nesse commit até o 0d656a84. A prática pede a suíte verde em cada commit; o squash apaga o intermediário.

## Parecer
Aprovado. A mudança só move os arquivos, as referências estão completas e o teste do item passa no caminho novo. O A1 não bloqueia: a `develop` mescla por squash, e o commit intermediário não chega à base.
