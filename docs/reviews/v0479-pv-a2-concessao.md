---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-a2-concessao
commit: 9b6dca25db319a73277a5bc2bfaf151af8cd53a6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E57.66, PR-VERDE A2 parcial, concessão presa ao commit), volta sobre 1f07bb3d

## Sondas
- S1 · corpo da S1 anterior ("... depois do CI verde", idem "antes da release", "sem a segurança", "só com o QA"), Estado-inicial ativa · espera: adulterada com ressalva · obtido: adulterada (caso `ressalva-0..3` do teste, verde)
- S2 · `fora_do_vocabulario("... item PV-A2 a menos que o QA reprove")` · espera: palavras fora · obtido: ['menos', 'qa', 'que', 'reprove']
- S3 · `fora_do_vocabulario("... item PV-A2 so amanha")` · espera: ['so'] · obtido: ['so']

## Parecer
Aprovado. Delta lido: `forge-check parecer delta` de 4c325c55 a 9b6dca25, domínio código e testes (`bin/forge_autorizacao.py`, `tests/test_autorizacao.py`, quatro specs de mutante e o fragmento do changelog). Os pareceres do QA e da segurança no intervalo ficam com eles.

- **A1 (fechado).** `RESSALVA` saiu. Entrou `VOCABULARIO` (`:30`), um conjunto fechado de termos de ato, validade do item 6, permissão, artigos, preposições e cortesia, e entrou `fora_do_vocabulario` (`:150`), função única que o `gravar` da G1.2 pode importar. Concessão `ativa` com palavra fora dele fica `adulterada`. O teste confere que nenhuma marca do item 5 da ADR 0018 está no vocabulário, e as quatro ressalvas da S1 antiga viraram casos. O termo do ato agora é palavra inteira, fora do nome do cartão, e isso fecha o caso `item ROTULO-1`.
- **A2 (fechado).** O diff depois do `Commit` usa `--no-renames`, e cada arquivo precisa estar numa pasta de parecer e ter `branch:` igual ao `Ramo` no frontmatter. Arquivo apagado lê vazio e recusa, então a renomeação de código para `docs/qa/` fica `inativa` (teste novo). Os EXIGIDOS (`review`, `qa`, `revisao-seguranca`) fecham também o A4 da segurança.
- **A3 (fechado).** O fragmento do changelog diz "PR-VERDE A2, parcial" e deixa a recusa no `gravar` para o cartão preso à G1.2.

Tamanho: 89 linhas em `bin/` contra a base `d4f0b10a`, dentro do H1.

**Ferramentas citadas, sem refazer.** `tests.test_autorizacao.ItemPresoAoCommit`: 8 testes, OK (2,8 s, ambiente limpo). `bin/forge-mutante --cobertura --base 4c325c55`: rc 0, e toda guarda do delta tem mutante declarado (`:153`, `:162`, `:171`, `:196`, `:201`, M30 a M32 na spec `-4`). A execução dos mutantes fica com o QA. A suíte inteira fica no CI do PR.
