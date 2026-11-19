---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-selecao-testes
commit: 124f2f6acd1f473ea547e7e106824506996814a0
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (E18.7, melhoria/v0478-selecao-testes), revalidação

Volta por delta. A rodada anterior (E18.4, commit 53f89698) está no git.

Gatilhos: controle do Forge (seleção de testes em `bin/forge-testes`; pesos e carimbo K6 em `scripts/suite-paralela.py`, R-TETO).

## Delta lido
`forge-check parecer delta` no intervalo 53f89698..124f2f6a dá "nenhum arquivo do domínio mudou". Fora do domínio mudaram os pareceres de review, QA e segurança e `tests/test_suite_paralela.py` (+11). Li o teste novo inteiro. O merge aa855ba só trouxe o parecer anterior desta etapa.

## Achados anteriores
- A1 (recomendado), `scripts/suite-paralela.py:922`: **resolvido**. O teste `test_medir_verde_nao_grava_o_carimbo_da_suite_verde` (`tests/test_suite_paralela.py:400-409`) roda `--medir test_a` verde e confere que não há `*verde*` em `.git`. Depois roda a suíte sem marcas e exige que ela não reuse e que rode a, b e c.
  - Sonda de mutante, numa cópia do head: gravar o carimbo em `medir` com o hash da árvore tirado antes de rodar faz o teste reprovar (`FAILED (failures=1)`).
  - O mutante que tira o hash depois de rodar sobrevive no brinquedo. Lá, o `pesos-d4.json` recém-gravado suja a árvore, então `hash_da_arvore` dá None e nada é gravado. Essa é a mesma guarda de `fechar_verde` (`:896`), então o mutante não tem efeito.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas: `forge-check parecer delta` e a leitura do teste novo. `discover -s tests -p test_suite_paralela.py -k medir` deu 8 OK no head. Também rodei os dois mutantes acima. A suíte inteira roda só no CI do PR e não foi rodada aqui. Não há segredo, dependência nem workflow no delta.
