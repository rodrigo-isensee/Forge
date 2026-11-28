---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-ae3-1-controle
commit: 40244cc20339c7438a9a20ec66e8b92ccfc405d1
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E108.17, 3ª volta da AE3.1 `bin/forge_controle.py`)

Revalidação por delta sobre o parecer aprovado no head 59ad2edc (E108.6, no git). Head 40244cc2.

Gatilhos: controle do Forge que roda git na pasta de controle e decide o que entra no commit, chamado pelo relógio da AE3.2 fora do sandbox (D7).

## Delta lido
`forge-check parecer delta` de 59ad2edc..40244cc2, sem o que veio da develop: no domínio só `bin/forge_controle.py`, uma linha da docstring (`:3`, troca o caminho da proposta por "proposta v0479 de melhorias anti-erro"); nenhuma linha de código mudou. Fora do domínio: `docs/indice-forge.md`, `tests/pesos-d4.json` e `tests/test_forge_controle.py` (o embrulho de `git` no PATH que liga `GIT_CONFIG_NOSYSTEM` e o teste novo com `filter.lfs` numa config de sistema falsa; rodado, não relido além do diff).

## Achados anteriores
- A1 (bloqueante, E108.3): segue corrigido. `_comando_na_config` (`bin/forge_controle.py:60-72`) e `COMANDO_NA_CONFIG`/`LIGADA_SE_VERDADE` (`:25-27`) inalterados. Sondas refeitas no head, em repositório descartável em `$TMPDIR`: `core.fsmonitor` com comando deu `('nao-verificavel', 'comando na config core.fsmonitor')`, 0 execuções; `filter.Z.clean` com `*.md filter=Z` deu `('nao-verificavel', 'comando na config filter.z.clean')`, 0 execuções. O teste novo prova o mesmo para a config de sistema: sem o isolamento, `filter.lfs` do sistema deixa o `salvar` `nao-verificavel`; o embrulho é só do teste e não afrouxa o módulo, que continua lendo todas as origens.
- A2 e A3 (recomendados, E108.3): seguem corrigidos; código inalterado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados: `tests.test_forge_controle` (42 testes, OK) e as duas sondas acima. A suíte inteira fica para o CI do PR. SAST e varredura de segredos não estão no PATH: lacuna registrada.
