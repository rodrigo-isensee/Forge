---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-f1-parecer-fora
commit: edaf7bc08b371efafbd4eeb58dcab39bcb0143eb
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (E29.6, #925, F1 corte 1, volta 1 por delta)

## Gatilhos
Gatilhos: controle de portão (leitura do parecer que decide o merge), integração com a API do GitHub pelo token da sessão, código em `PROTEGIDOS` (`bin/forge_pareceres.py`).

## Delta lido
`forge-check parecer delta` de `e26310c2..edaf7bc0`: no domínio só `bin/forge_pareceres.py` (`ler`, linhas 131 a 149); fora dele, `docs/indice-forge.md`, os dois arquivos de mutantes e `tests/test_forge_pareceres.py` (lidos para conferir os testes de A2 e A3). A rodada anterior fica no git (`2d3e3f32`).

## Estado dos achados anteriores
- A1 (bloqueante): resolvido. CI do head `edaf7bc0` (run 45935176061): suíte 1/5 a 5/5 nas duas versões, instalação, verificações longas e teto de pulados verdes; vermelhos só `bateria (pareceres)`, `bateria` (agregado dela) e `catraca`, que esperam os pareceres e o rótulo `afrouxa-regra` da integração, como diz o brief.
- A2 (recomendado): resolvido. `ler` recusa, antes de qualquer chamada ao `gh`, `contas` que não seja `set`/`frozenset` de str não vazias (`bin/forge_pareceres.py:135-136`); o filtro volta a ser igualdade exata (M1.1). Testes: `test_contas_que_nao_sao_conjunto_recusadas` (str, lista, tupla, dict, None, conjunto com int; confere que o `gh` não foi chamado), `test_contas_com_login_vazio_recusadas`, `test_contas_frozenset_vale`.
- A3 (recomendado): resolvido. O laço e `conferir` ficam dentro de `except (KeyError, TypeError, AttributeError, ValueError)` que vira `Recusa` com motivo (`:143-149`), como o `publicar`. `Recusa` herda de `Exception`, não de `ValueError`: a recusa do `gh` passa intacta, sem ser rebatizada. Login não hashable no `creator` (TypeError no `in frozenset`) também cai no mesmo ramo. Teste: `test_resposta_fora_do_contrato_vira_recusa` (sondas S3 a S5: `creator` str, `user` str, PR sem `number`). Falha fechada: um status malformado derruba a leitura inteira em vez de virar `(None, motivo)` daquele contexto; mais estrito, coerente com M19.1.

## O que aperta, o neutro e o que afrouxa
- Aperta: a leitura recusa contas fora de conjunto e resposta fora do contrato com motivo; `ler` segue sem chamador fora dos testes.
- Neutro: `publicar`, `agregado`, `conferir` e `frontmatter` sem mudança; nenhum workflow, token, dependência ou segredo novo.
- Afrouxa: nada. Continua valendo a ordem da rodada anterior: o corte 9 só liga `ler` depois de M1.4, M4.1, M4.2 e M10.1.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes afetados no head, com a trava de teste: `python3 -m unittest tests.test_forge_pareceres`, 69 testes, OK. Ferramentas ausentes no ambiente (lacuna registrada, nada instalado): varredor de segredos, SAST, auditoria de dependências e linters de workflow; o delta não toca dependência nem workflow.
