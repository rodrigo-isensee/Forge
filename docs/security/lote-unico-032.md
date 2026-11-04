---
tipo: revisao-seguranca
contrato: 1
pedido: lote-unico-032
branch: melhoria/lote-unico-032
commit: cd93720c89c21f935783c98501d3817a5b7ad3f7
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-03
---
# Review de segurança: lote-unico-032 (E2.1 do pedido lote-unico-032-REV, volta 3)

Revalidação por delta (`forge-check delta --parecer`, intervalo `9f32431..cd93720`) da volta 3: as 2 correções 9f5c191 (L35, A5 deste parecer) e cd93720 (L13), contra o modelo de ameaças `docs/security/ameacas/lote-unico-032.md`. O parecer anterior (`36edb78`, sobre `9f32431`) fica como base; o resto do delta são pareceres e o fragmento do changelog. Leitura do diff e testes dos módulos tocados (D-5); a suíte inteira é do QA. Veredito: **aprovado**; o A5 está resolvido e as quatro recomendações anteriores seguem (sem mudança no delta, mesmas linhas).

## Gatilhos
`R-SEGURANCA`: controles do Forge tocados no delta (`bin/forge-check`, em `PROTEGIDOS`; `tests/config.json`; `tests/test_forge.py`). Nenhum arquivo de `hooks/`, `.github/` ou `.githooks/` no delta.

## Achados
- A1 (recomendado) bin/forge-check:1941 · `fila` (L18) ainda executa o `.githooks/pre-push` da raiz quando o texto contém `[ "$1" = "--status" ]`; a marca é texto e um hook alheio a copia. Ler a trava com flock LOCK_NB (sem mudança no delta).
- A2 (recomendado) bin/forge-check:553 · `gatilhos` casa o `gatilhos_seguranca` do plano técnico só pelo pedido exato; casar pelo id e pelo slug (sem mudança no delta).
- A3 (recomendado) bin/forge-mutante:649 · `--processos K` (L33) não confere a trava da suíte (C-33b só no texto de `skills/qa-testing/SKILL.md`); sem mudança no delta.
- A4 (recomendado) bin/forge-check:2058 · o `custo total` (L16) soma `custo do trecho: N tokens` lido de toda a célula, motivo livre incluído; ler só o sufixo que o `movimento` grava (sem mudança no delta).

## Revalidação do delta
**A5 (L35, 9f5c191): resolvido.** `tests/config.json:666` passa a `"agents/jarvis.md": 51`; `tests/test_forge.py:542-543` reprova a contagem abaixo da real além da acima (`:540-541`), então a contagem fica igual à real; `:544-545` dá o teto da soma `LEGADO_TRECHOS_MAXIMO = 284` (`:519`), igual à soma real. Prova com a `problemas_de_motivo` da branch sobre o `tests/config.json` da branch: hoje `[]`; com 1 trecho novo sem motivo em `agents/jarvis.md`, `trecho novo em arquivo do legado sem regra e porque`; com a contagem em 52, as duas recusas (contagem acima da real e soma 285 acima de 284). Os 34 arquivos do legado batem com a real; 34 = `LEGADO_SEM_MOTIVO_MAXIMO`. C-35/T-35: nada sai nem afrouxa. Conferido contra `b2580c6`: os 22 trechos que deixaram `agents/jarvis.md` estão todos em `invariantes` de `docs/regras/R-BRIEF.md`, `skills/briefs-e-conferencia/SKILL.md`, `skills/falar-com-o-dono/SKILL.md` e `skills/trabalho-em-paralelo/SKILL.md` (L51, já no título com destaque); nenhum outro trecho sumiu; `termos_proibidos_hash` igual. O delta em `tests/config.json` é só a linha `:666`, para baixo. Teste novo do n que sobe em `tests/test_forge.py:500-502`.

**L13 (cd93720): cumprido.** `RE_LINHA_REPROVADA` (`bin/forge-check:4022`) passa a não contar `escopo: integração da base`, `escopo: sem commit` e `escopo: união de \d+ briefs`. Conferi contra todas as linhas `escopo:` que o `entrega` imprime (`bin/forge-check:933-1250`): as que reprovam (`--desde sem conferência anterior`, `--desde gravado na própria entrega`, `brief ... ilegível ou fora de docs/briefs/`, `união de briefs de entregas diferentes`, `base fora do fluxo`, `Base-sha fora da branch`, `E4 sem o diff da base`, `merge-integracao sem os pareceres aprovados no head`) seguem contadas, e a `união de briefs de entregas diferentes` (`:1066`) não casa a exceção, que exige o número (sonda da expressão: `True` para ela, com e sem maiúscula; `False` só para `união de 3 briefs (...)`, `:1070`). As três exceções são as linhas que o `entrega` imprime com `False` (não reprova, `:1070`, `:1198`, `:1202`, `:1231`). É medida (C-10 a C-13): nenhuma recusa vira aviso (T-10), rc e veredito de `brief`, `entrega` e `pr` intactos, e a saída segue só com números (`assertNotIn("pendente", saida)`, `tests/test_forge.py:3093`). O texto de uso (`:107`) e a docstring (`:4027`) dizem a regra nova (AR-9 conferido).

## Por correção (volta 2, base deste delta)
Sem mudança: o detalhe da volta 2 (merge `6ef56a0`, 0e7f04a L16, 7eae698 L18, d58718a L13, 7d0f599 L15, bcad27a L49, c0c180e L35, 9b1e375 L31, 9f32431 L17) fica no parecer `36edb78`; A1 a A4 com evidência, caminho e correção como lá e na volta 1 (`5b36740`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check delta --parecer` (vigente 0.31.0), leitura do diff `9f32431..cd93720`, comparação dos `invariantes` com `b2580c6`, sonda da `RE_LINHA_REPROVADA` e da `problemas_de_motivo` da branch, e os testes dos módulos tocados (D-5): `tests.test_forge.RegrasInviolaveis` e `tests.test_forge.MedirAlucinacao`, 20 testes, OK. Lista de `docs/engineering/achados-recorrentes.md` (AR-1 a AR-10) conferida: nenhuma ocorrência nova no delta (o AR-3 não se aplica: a exceção é de medida, não de trava). Lacunas: `gitleaks`, `actionlint`, `zizmor`, `semgrep` e `osv-scanner` fora do PATH; o CI cobre o passo de segredos.
