---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-develop-verde
commit: 1bd10c54ed4cba5bb1c58f4c7e788276923b08b3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E16.2, develop verde depois do #680)

Escopo: commit 1bd10c54 sobre a base 82bb9e57; três arquivos, 5 linhas a mais e 2 a menos, sem código de produção: `tests/pesos-d4.json` (peso do `test_indice_forge`), `tests/mutantes/v047-mapa-testes.json` (M8 com `de`/`para` da linha nova de `bin/forge-testes`) e o fragmento `changelog.d/v0478-develop-verde.md`. Nenhuma guarda mudada, logo nenhum mutante novo a declarar.

## Conferência
- Causa: o CI da develop no push de 82bb9e57 (run 44379527348) falhou em dois testes, `test_forge.PesosDaSuite.test_no_maximo_20_por_cento_dos_modulos_sem_peso` (42 de 209 sem peso, `test_indice_forge` na lista) e `test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes` (`v047-mapa-testes.json: M8`). O diff ataca exatamente essas duas causas, nada além (checklist 1).
- M8: o `de` novo é idêntico, caractere a caractere, à linha 302 de `bin/forge-testes` no head (1 ocorrência); o `para` remove só o `quem_importa`, preservando o `teste_do_indice` que o #680 acrescentou, então o mutante continua medindo a mesma guarda.
- Testes rodados no head (suíte inteira fica no CI do PR, `R-REVIEW`): os dois testes acima passam; na base, o de pesos falha com a mesma mensagem do CI. `bin/forge-mutante --processos 1 tests/mutantes/v047-mapa-testes.json`: M1 a M8 morreram (M8 em `bin/forge-testes:302`). `test_pesos*.py`: 18 OK. Os dois JSON carregam.
- Commit em Conventional Commits em português, fragmento com o nome da branch sem prefixo, sem edição do `CHANGELOG.md` (checklist 9).

## Parecer
Aprovado. Correção mínima e certeira da develop vermelha; sem achados. Observação fora do diff: com 41 de 209 módulos sem peso, a folga do teto de 20% é de um módulo; o próximo teste novo sem peso volta a quebrar a develop.
