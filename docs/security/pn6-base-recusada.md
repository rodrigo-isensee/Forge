---
tipo: revisao-seguranca
contrato: 1
pedido: pn6-base-recusada
branch: melhoria/pn6-base-recusada
commit: fab197c47dabb6714cd86b45a93a62b0962f87ce
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-29
---
# Review de segurança: pn6-base-recusada

Escopo: `git diff 31257c14c8d245d66e7806edb7cd65e22b3aeb04...fab197c47dabb6714cd86b45a93a62b0962f87ce` (bin/forge-check, tests/test_conferencia_base_dono.py, tests/mutantes/pn6-base-recusada.json, changelog.d/pn6-base-recusada.md). Pedido PN6-BASE-RECUSADA-REV, E2.1.

## Gatilhos
`R-SEGURANCA`, gatilho controles do Forge: o `forge-check` (entrega e brief gerar --volta) decide o intervalo conferido de uma entrega.

## Achados
- A1 (recomendado) bin/forge-check:1422 · o gerar --volta julga a base com head = ref; a base do dono igual à ref é recusada, mas o entrega a aceitaria no head da correção (posterior). Falha fechada, sem perda de controle: só uma recusa a mais.

## Detalhe dos achados
Conferências feitas, todas sobre o commit fab197c:

1. **cmd_entrega igual ao da 31257c1 para toda entrada.** `veredito_do_desde` (bin/forge-check:854-867) reproduz ramo a ramo o bloco removido do `cmd_entrega`: (a) `desde_e_a_base` verdadeiro dá a linha `base:` não reprovadora, valido e origem None; (b) sem `--desde`, nada; (c) `desde_valido` vazio ou diferente do `--desde` reprova com `escopo: --desde sem conferência anterior`, valido None e a origem devolvida pelo `desde_valido` (como antes, quando `origem_da_base` ficava com ela); (d) `pedido_na_entrega` reprova com `escopo: --desde gravado na própria entrega`, valido None; (e) senão, valido e origem. A ordem dos testes é a mesma, e `ref_da_base` (bin/forge-check:849-851) é a mesma expressão do `base_ref` antigo. Depois do veredito, `de`, `arquivos_da_entrega` e a linha informativa do dono usam `valido` e `origem_da_base` como antes. Não achei entrada que o entrega aceite agora e recusasse na 31257c1.
2. **A guarda pedido_na_entrega.** Está na função única (bin/forge-check:865), chamada pelos dois caminhos; o mutante M8/M9 a cobre no gerar e o M10 no entrega; o teste `test_base_gravada_na_propria_entrega_recusa_como_no_entrega` confere os dois lados.
3. **O gerar não aceita base que o entrega recusa.** `recusa_do_desde` (bin/forge-check:1415-1429) julga exatamente o `bases[-1][0]` que o gerar põe no `--desde` da PQ (bin/forge-check:1550-1552), com o mesmo Base-sha (`sha_base`) e a mesma base (`a.base`) da PQ. A recusa só acrescenta um rc 1; não há caminho em que ela torne aceito o que antes não era, e o `forge-check entrega` continua o portão. Sem base no Histórico, o comportamento antigo (`--desde` em PREENCHER) fica (M5).
4. **Nenhum caminho que pule a conferência.** A recusa vem antes de qualquer saída do brief (bin/forge-check:1480); a única saída sem ela é a de rc 1/2 anteriores. Entradas para o git: o `desde` vem do regex sha40 do Histórico, a `ref` é validada por `sha_do_commit`, o `a.base` passa por `sha_do_commit` com `--end-of-options`; o `sha_base` é commit validado ou a constante PREENCHER (vira não-ancestral, sem injeção de opção). O texto da recusa leva só prefixos de sha validados e uma linha constante.
5. **PA-7.** Nenhum item de docs/engineering/achados-recorrentes.md se aplica (não há shell, trava de ambiente, python em caminho de hook nem pasta do git nova).

A1, detalhe: evidência bin/forge-check:1422 e bin/forge-check:830 (`desde_valido` exclui a base do dono igual ao head). No gerar, o head é a ref da volta; no entrega da volta, o head já traz a correção. Uma base do dono fixada exatamente na ref da volta é recusada no gerar, embora o entrega da correção a aceitasse. Caminho de ataque: nenhum (falha fechada; o efeito é uma pergunta ao dono que a P-N6 queria evitar, no caso raro). Severidade: informativa. Correção mínima: nenhuma obrigatória; se o caso aparecer, documentar na mensagem que a base do dono igual à ref é recusada de propósito, ou não aplicar no gerar a exclusão do head. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, `python3 -m unittest tests.test_conferencia_base_dono tests.test_volta_por_delta` (93 testes, OK) na worktree em fab197c. Sem gitleaks/semgrep nesta revisão (o diff não traz segredo nem dependência; não instalei nada).
