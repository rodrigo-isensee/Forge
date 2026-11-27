---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-versao-com-20
commit: 2e6da2d5b9a7cf5d9a7a35bb7319b4b23a28b894
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481

Code review por delta (E36.10) da volta 2 do #928. Delta lido: `forge-check parecer delta docs/reviews/v0481-versao-com-20.md`, intervalo `b19c7f53..2e6da2d5`, 1 arquivo no domínio (`tests/config.json`, uma linha).

- ci: 2e6da2d5b9a7cf5d9a7a35bb7319b4b23a28b894 verde

## Parecer
Aprovado no meu domínio.

- **A1 da volta 1 (resolvido).** `tests/config.json:849`: a chave de `invariantes_motivo_trecho` passa a "a versão fecha quando a branch de integração soma 20 itens integrados, sem versão por dia", igual ao invariante de `tests/config.json:656` e ao texto de `templates/projeto/CLAUDE.md:15`; o `porque` novo diz o dano da ausência (volta a fechar versão por dia) e cita a diretriz 34 e a ordem do dono. `grep "2 por dia" tests/config.json`: nada.
- **Testes.** `python3 -m unittest tests.test_forge -k invariante` (fila `trava-teste-a`): 2 testes OK.
- **Tamanho (H1).** Zero linha de código fora testes e documentação.
- **CI.** `gh pr checks 928` no head 2e6da2d5: suíte (3.12 e 3.14, 5 partes cada), bateria (python 3.14), bateria (passos), bateria (verificações longas), instalação (python 3.14), teto de pulados e "árvore já provada na develop" em `pass`; `bateria`, `bateria (pareceres)` e `catraca` esperam os pareceres (G3).
- **Commit.** `test(config): ...` em Conventional Commits em português, com pedido e etapa.
