---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: 6aa5b7bec87035d37234363585f610a674fa0655
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E51.35, revalidação de CONFORMIDADE-DESLIGADA-NA-SESSAO-DO-FORGE)

Delta lido (H3, `R-REVIEW`): `forge-check parecer delta docs/reviews/v0479-conformidade-sessao-forge.md`, intervalo `96c0215f..6aa5b7be`; no domínio, só `tests/hooks/conformidade/e51-wt-ponto-argumento-pipe-aninhado-libera.json`. O aviso sobre o merge 9bc658b fora da `origin/develop` é a junção de pareceres da própria branch; nada dele cai no domínio além da fixture.

## Parecer
Aprovado. A fixture troca o caminho de exemplo de `*docs/reviews*` para `*docs/regras*` e explica o motivo na `descricao` (E51.34: com `docs/reviews` a barreira de papel do E50 recusaria por outro motivo, e a fixture deixaria de provar o que diz). `hooks/conformidade.py` não mudou. `docs/regras` segue no padrão de ação crítica (`hooks/conformidade.py:63`), então o texto reavaliado continua passando pela recusa opaca da guarda base, e a fixture prova o que diz: o ponto como argumento (`find .`) depois de um pipe passa.

Execução no head 6aa5b7be: `HookSessaoDoForge` (`tests/test_hooks.py`, fixtures `e51-*`, piso 55, os dois lados 0 e 2): 2 testes, OK. `tests/test_hooks_volta_corpus.py`: 33 testes, OK (138,0 s); o teto da soma (5897219) não mudou com a troca do texto. Nenhuma guarda mudada, nenhum mutante novo. Suíte completa: CI do PR #742 em andamento no head; `bateria (pareceres)` e `catraca` reprovadas antes deste parecer e do rótulo (ADR 0008).
