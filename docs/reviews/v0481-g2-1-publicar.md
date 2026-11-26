---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: f3258bb890921173e775a174642fdb048f758158
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E6.37, #878, G2.1: forge-check parecer publicar; classe C), volta por delta (conflito com a develop resolvido)

Revalidação por delta do aprovado em 939e4d22 (E6.32; texto no git). Delta lido: `forge-check parecer delta` deste arquivo (no domínio: `bin/forge-check`, `bin/forge-testes`, `docs/hooks-fixtures.md`, `docs/indice-forge.md`, `tests/pesos-d4.json`, `tests/test_hooks.py`) e `git diff 939e4d22..f3258bb8`: os pareceres da rodada anterior, o merge limpo da `develop` 8f0a7313 em 99b48fbe e o merge da `develop` 020e4af7 em f3258bb8, com conflito em dois arquivos. Ordem do dono de 26/11 07:54: só a resolução e as correções; o que veio da `develop` foi revisado no PR de origem.

## Achados
- A2 (recomendado) hooks/conformidade.py:113 · Forma opaca (`python3 $(command -v forge-check)`) do A2 do E6.18, sem mudança neste delta: segue como cartão depois do merge.

## Achados anteriores
- A1 (bloqueante): corrigido no dc6bc47e; o delta não o reabre.
- A2 (recomendado): segue como cartão (A2 acima).

## Leitura do delta
- **Resolução do conflito** (`git show --remerge-diff f3258bb8`): só os dois arquivos em conflito diferem da fusão automática. Em `bin/forge-testes`, a tupla `FORGE_CHECK` fica com `test_fechar_corte` (da `develop`) e `test_forge_pareceres` (do item); nada mais muda. Em `docs/hooks-fixtures.md`, só o total (3592 do item, 3587 da `develop`) vira 3596; `scripts/indice-fixtures.py --conferir`: em dia.
- **A develop entrou igual:** dos 105 arquivos do delta, 96 só a `develop` tocou e são idênticos a 020e4af7 (`git diff --quiet 020e4af7 f3258bb8 -- <arquivo>`). Nos 9 tocados pelos dois, o patch do item sobre a `develop` nova (`020e4af7..f3258bb8`) tem as mesmas linhas +/- que sobre a base anterior (`8f0a7313..99b48fbe`) em `bin/forge-check`, `docs/indice-forge.md`, `tests/pesos-d4.json` e `tests/test_hooks.py`; em `bin/forge-testes` difere só pelo `test_fechar_corte` que a `develop` trouxe; os 3 restantes são os pareceres.
- **Merge 99b48fbe:** sem conflito; o `--remerge-diff` mostra só os 3 pareceres da rodada anterior.
- O código do item (`bin/forge-check`, `bin/forge_pareceres.py`, `hooks/conformidade.py`) não muda neste delta; os mutantes das specs do item seguem os do 939e4d22.

## Verificações
- Rodados aqui no f3258bb8: `python3 -I -m unittest discover -s tests -p test_forge_pareceres.py` (35 testes, OK); `-p test_fechar_corte.py` (35 testes, OK); `-p 'test_indice_fixtures*.py'` (OK).
- CI do f3258bb8 (`gh pr checks 878`): suíte 3.12 e 3.14 (partes 1 a 5), teto de pulados 3.12 e 3.14, bateria (passos), bateria (verificações longas), bateria (python 3.14), instalação e árvore já provada na develop verdes. Falham só os que esperam parecer ou rótulo: `bateria (pareceres)` (pareceres de review e segurança com `commit:` desatualizado por `bin/forge-testes`), `bateria` (agrega o de pareceres) e `catraca` (mudança em `bin/forge-check` e `hooks/conformidade.py` pede o rótulo `afrouxa-regra` depois do último push).
- ci: f3258bb890921173e775a174642fdb048f758158 verde

## Parecer
Aprovado. A resolução do conflito mantém os dois módulos na tupla `FORGE_CHECK` e regera o índice com o total certo; a `develop` entrou igual e o patch do item é o mesmo aprovado no 939e4d22. O A2 segue recomendado, como cartão depois do merge. A catraca espera o rótulo do dono.
