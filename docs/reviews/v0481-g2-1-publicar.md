---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: 939e4d22a8040dcf65b47201c97c6d7a17ed795e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E6.32, #878, G2.1: forge-check parecer publicar; classe C), volta por delta (develop trazida)

Revalidação por delta do aprovado em dc6bc47e (E6.26; texto no git). Delta lido: `forge-check parecer delta` deste arquivo (revalida: `docs/hooks-fixtures.md` mudou) e `git diff dc6bc47e..939e4d22`, que é só o merge da `develop` em 34ab6714 (#885, G4 F1) mais o índice gerado. O conteúdo do #885 foi revisado no PR de origem e fica fora do domínio.

## Achados
- A2 (recomendado) hooks/conformidade.py:113 · Forma opaca (`python3 $(command -v forge-check)`) do A2 do E6.18, sem mudança neste delta: segue como cartão depois do merge.

## Achados anteriores
- A1 (bloqueante): corrigido no dc6bc47e; o delta não o reabre (patch do item idêntico, M37 morre no head).
- A2 (recomendado): segue como cartão (A2 acima).

## Leitura do delta
- **Lógica sem mudança:** o patch do item contra a base (`git diff 34ab6714 939e4d22`) é igual, linha a linha, ao patch aprovado (`git diff 6cc4cd5a dc6bc47e`, merge-base antigo), fora `docs/hooks-fixtures.md` e os pareceres; só cabeçalhos `index`/`@@` diferem (deslocamento de linhas). Os dois têm 31 arquivos.
- **Índice gerado:** `docs/hooks-fixtures.md` muda 3 linhas (total 3583 → 3592; `conformidade` 2709 → 2718; `contrib-*` 144 → 153), as 9 fixtures `contrib-publicar` do item sobre o corpus da `develop`. `scripts/indice-fixtures.py --conferir`: em dia; o corpus no head tem 3592 arquivos (3583 na base + 9).
- **Nenhum teste perdido:** os `def test_` de `tests/` no head (7011) contêm a união dos da base 34ab6714 (6975) e do dc6bc47e (7000): 0 ausentes.
- **Merge em `hooks/conformidade.py`:** o item e o #885 tocam o arquivo; o merge não teve conflito nele, e os 7 mutantes da spec `-6` (guardas do item no hook) morrem sobre o código combinado.

## Verificações
- Rodados aqui no 939e4d22: `python3 -m unittest tests.test_indice_fixtures` (7 testes, OK); `bin/forge-mutante --processos 1 tests/mutantes/v0481-g2-1-publicar-6.json` (M31 a M37 morreram, hooks/conformidade.py:2646, 2649, 1389 a 1393); as demais specs do item cobrem `bin/forge-check` e `bin/forge_pareceres.py`, que o delta não toca.
- CI do 939e4d22 (`gh pr checks 878`): suíte 3.12 e 3.14 (partes 1 a 5), teto de pulados 3.12 e 3.14, bateria (passos), bateria (verificações longas), bateria (python 3.14), instalação e árvore já provada na develop verdes. Falham só os que esperam parecer ou rótulo: `bateria (pareceres)`, `bateria` e `catraca`.
- ci: 939e4d22a8040dcf65b47201c97c6d7a17ed795e verde

## Parecer
Aprovado. O delta é só a `develop` trazida e o índice regenerado; o patch do item é o mesmo aprovado no dc6bc47e, nenhum teste se perdeu e os mutantes do hook morrem no head. O A2 segue recomendado, como cartão depois do merge. A catraca espera o rótulo do dono.
