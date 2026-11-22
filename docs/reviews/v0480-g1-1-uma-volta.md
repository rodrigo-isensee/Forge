---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-1-uma-volta
commit: 8522e8fe58bcfd9240228b875f1314237bee1f27
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 · G1.1 (no máximo 1 volta por item), etapas E100.2 e E100.6

Revisão única (ORDEM DO DONO 21/11 22:13): a revalidação (E100.6) leu só o delta `forge-check parecer delta` de 57c0cbff..8522e8fe (no domínio: `agents/jarvis.md`, `bin/forge-check`, `changelog.d/v0480-g1-1-uma-volta.md`, `skills/briefs-e-conferencia/autor-ate-o-merge.md`, `tests/mutantes/v0480-g1-1-uma-volta{,-2,-3}.json`, `tests/test_volta_por_delta.py`). Desenho: `docs/propostas/g1-g3-fluxo-rapido.md`, seções 2 e 5.

## Achados
- A4 (recomendado) bin/forge-check:4247 · A forma canônica aceita texto depois da branch: "DECISÃO DO DONO: mais uma volta para melhoria/x foi negada" vale 2 voltas (sonda na revalidação). Ancore o fim (`\.?\s*$`) ou exija nada além da branch e de um ponto final.

## Revalidação (E100.6, head 8522e8fe)
- A1 (bloqueante, 57c0cbff) resolvido: `voltas_da_branch` conta as voltas pelo item (briefs com `Volta-de:` da mesma `Branch:` do anterior) e recusa o anterior que já tem sucessor, em `gerar_volta` (bin/forge-check:4307) e em `conferir_volta` (bin/forge-check:4441); o brief com `(volta N)` sem `Volta-de:` também é recusado (bin/forge-check:8731). A sonda S1 da rodada anterior virou `test_volta_conta_o_item_e_nao_a_cadeia`: o 2.º `--volta` do original sai rc 1 com "já tem volta", e a conferência da mesma volta escrita de novo é recusada.
- A2 (recomendado) resolvido: só a forma canônica logo depois do prefixo da decisão autoriza, e as linhas contam como conjunto. Sondas refeitas: "nenhuma volta a mais para melhoria/x" dá 1 (antes 2); linha repetida em duas fontes vale uma (`test_so_a_forma_canonica_autoriza_e_uma_linha_vale_uma_volta`). Resta a cauda livre depois da branch (A4).
- A3 (recomendado) resolvido: `agents/jarvis.md:31` diz "máx. 1 volta por item", coerente com o R-QA novo e com `autor-ate-o-merge.md`.

## Verificação
- Testes afetados: `tests.test_volta_por_delta.BriefDeVolta`, 29 testes, verdes no head 8522e8fe, com ambiente limpo (`env -i`) e `python3 -I`. Suíte inteira: com o CI do PR (sem PR aberto agora; nada a citar).
- Mutantes: `bin/forge-mutante` nas três specs, M1 a M22 morreram (M1 por erro sob `None`, como antes). `bin/forge-mutante --cobertura --base 57c0cbff`: toda guarda do delta coberta (4261, 4269, 4272 a 4274, 4307, 4311, 4441, 4443, 8731); a guarda apagada em 4421(base) foi substituída pela 4443.
- Tamanho (H1): o delta soma cerca de 20 linhas líquidas de código em `bin/forge-check`; o item segue dentro do teto de 150.
- Regras de leitura alcançadas pelo delta: R-QA coerente entre `agents/jarvis.md`, `autor-ate-o-merge.md` e a mensagem de recusa; fragmento do `changelog.d/` atualizado com a branch.

## Parecer
Aprovado no head 8522e8fe. O bloqueante A1 está corrigido nos dois caminhos (gerar e conferir), com teste do ramo de falha e mutante por linha de guarda, todos mortos. A2 e A3 foram resolvidos na volta. A4 é novo, recomendado, e vira cartão depois do merge (R-REVIEW).
