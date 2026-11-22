---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-prazo-unico-estavel
commit: 08e2525e442b1754e2df6e066afb1948d175f422
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E124.4, PrazoUnico determinístico)

Diff lido inteiro (48d6f4b8..08e2525e): `tests/test_fechar_checks_do_head.py` (classe `PrazoUnico`) e o fragmento `changelog.d/v0480-prazo-unico-estavel.md`. O `bin/forge-fechar` não muda: a guarda de merge (nada se mescla sem o check obrigatório verde no head, E114) fica como estava.

Gatilhos: nenhum no código de controle; o parecer vem por a ferramenta vigente exigir a classe (teste de uma guarda do forge-fechar).

## Achados

## Sondas

## Detalhe dos achados
- O teste continua provando a guarda: `returncode == 1`, a mensagem de check obrigatório não verde com o sha do head e `merges() == []` (`tests/test_fechar_checks_do_head.py:158-164`). A troca só tira o prazo de 1 s sensível à carga; não afrouxa a asserção de "nada foi mesclado" e acrescenta a conta de uma leitura só de `gh pr checks`.
- A fixture altera apenas o `gh` falso no diretório temporário do teste (`:148-152`), com `assertEqual(count, 1)` antes da troca, e o `sleep` lê um arquivo do próprio estado do teste; sem rede, sem segredo, sem escrita fora do temporário.
- Execução local só deste teste: `python3 -m unittest tests.test_fechar_checks_do_head.PrazoUnico`, 1 teste, OK (8,5 s). A suíte inteira fica com o CI do PR.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Varredura de segredos por padrão no diff (sem ocorrência); o varredor de segredos dedicado não está no PATH deste ambiente (lacuna registrada).
