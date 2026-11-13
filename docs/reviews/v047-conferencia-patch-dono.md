---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-conferencia-patch-dono
commit: c793d6eae3908b56c6df2756c3e8dcdaf308d9c9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Code review: a conferência aceita o arquivo aplicado pelo dono (CONFERENCIA-PATCH-DO-DONO, E1.2)

Escopo: pedido v047, etapa E1.15 (`R-REVIEW`), classe C, sobre o head `69bd4863` (Base-sha `a986c292`). Li o diff inteiro de `a986c292...69bd4863`: um commit, 6 arquivos (`bin/forge-check` +88 -3, `tests/test_conf_escopo.py` +144, três specs de mutante e o fragmento do changelog). QA (E1.17) e segurança (E1.16) correm em paralelo sobre o mesmo head; não os refaço. As ameaças P1 a P12 são as de `docs/security/v047-e1-ameacas.md` (E1.5, fora da branch).

## Achados
- A1 (recomendado) bin/forge-check:1709 · as cláusulas de curinga e de `.`/`..`/barra dupla de `caminho_isentavel` não têm teste que as mate: trocadas por `False`, os casos C10 seguem verdes (o nome vem do `git diff`, que nunca traz `./` nem `//`); sugestão: tirar o que é inalcançável ou testar com arquivo real de nome com `[` (classe AR-2)
- A2 (recomendado) tests/test_conf_escopo.py:210 · os casos C10 passam pelo motivo errado (o nome declarado não casa com nenhum arquivo da entrega, então a isenção nem é tentada) e não afirmam o `motivo`; sugestão: afirmar `caminho que nunca isenta` ou tirar os casos
- A3 (recomendado) bin/forge-check:1739 · o `rev-list` e o `diff {commit}^1` rodam antes das recusas baratas (caminho, sha, ancestral); sugestão: movê-los para depois de `commit fora da branch`, sem mudar o resultado
- A4 (recomendado) bin/forge-check:1691 · o diff tem 235 linhas contadas (M14, acima de 150); o corpo do PR precisa de `teto: excedido, 235 linhas, <motivo>` quando o PR for aberto

## Sondas

## Parecer
**Aprovado.** Faz o que a E1.2 pede: o arquivo do dono sai do escopo só com a linha na forma exata no `## Histórico`, uma `DECISÃO DO DONO` que cita o sha40 e o caminho como palavras inteiras, o commit de um pai, da branch e fora do Base-sha, que altera o arquivo, e o head com o mesmo blob e modo; symlink, submódulo, caminhos de parecer, aceite, pedido, oráculo e autoria nunca isentam; o git que falha reprova (P11); a entrega que mexe em `docs/pedidos/` não isenta (P2). A isenção entra só no último ramo do laço, antes do `escopo_resolvido`, então não altera parecer, merge da base nem anexo implícito. Linha fora da forma vira aviso, sem efeito (P3). Nenhum defeito provado; os achados são recomendações.

Verificação (regra 5 de `docs/economia-de-tokens.md`, sem rerrodar a suíte; não há PR nem CI ainda):
- `python3 -m unittest test_conf_escopo` (de `tests/`, no head): `Ran 19 tests … OK`; a classe nova `PatchDoDono`: `Ran 8 tests … OK`.
- `bin/forge-mutante --cobertura --base a986c292…`: 20 linhas `coberta`, nenhuma descoberta.
- `bin/forge-mutante --processos 1` nas três specs (uma por vez; juntas a ferramenta recusa, "as specs são de pedidos diferentes"): 8/8, 8/8 e 7/7 `morreu`.
- Sonda do A1: com as duas cláusulas trocadas por `or False`, `test_declaracao_que_nao_isenta` deu `OK`; arquivo restaurado, `git status` limpo.
- Commit `69bd4863` em Conventional Commits, em português, um comportamento; fragmento `changelog.d/v047-conferencia-patch-dono.md` presente. O merge espera o escopo-ponto no mesmo `bin/forge-check` (diretriz 11 do pedido), o que é da integração, não deste review.

## Revalidação por delta (E1.30, instância que não fez a entrega)
Delta lido: `forge-check parecer delta docs/reviews/v047-conferencia-patch-dono.md`, intervalo `69bd4863..c793d6ea` (junção com #517 e #522; no domínio só `bin/forge-check` e `tests/test_conf_escopo.py`). Os achados A1 a A4 seguem recomendados, sem mudança.
- Ordem dos ramos em `linhas_de_entrega` (`bin/forge-check:2740-2746`): parecer, merge-integração, anexo implícito, anexo do portão (`etapa == "codigo"`, #517) e, no último `else`, `isencao_do_dono` (patch do dono) antes de `escopo_resolvido`; o anexo do portão vem antes da isenção, como o brief pede, e os dois comportamentos ficam.
- P1 a P12 (`docs/security/v047-e1-ameacas.md`): a junção não tocou `patches_do_dono` nem `isencao_do_dono`; a classe `PatchDoDono` (8 casos, que cobrem as recusas e a linha de P12) roda verde no head.
- `python3 -m unittest test_conf_escopo` (de `tests/`, head `c793d6ea`): `Ran 24 tests … OK` (19 anteriores mais `PareceresPeloPedido` e os de #517). Sem PR nem CI; carga ~11 em 12 CPUs, só o módulo afetado.
- Veredito mantido: **aprovado** no head `c793d6ea`.

