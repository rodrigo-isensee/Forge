---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/v046-mutacao-bench
commit: e452582f9186c8b70a2a935d9c0e12e84ec6e48b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E7.6, melhoria/v046-mutacao-bench)

Revalidação por delta da E7.2 (reprovada no `60bba369` pelo A1). Instância que não fez a entrega.

Delta lido: `forge-check parecer delta docs/reviews/v046-mutacao-bench.md`, intervalo `60bba369..e452582f`, no domínio `bin/forge-changelog`, `bin/forge-mutante`, `changelog.d/v046-mutacao-bench.md`, `tests/mutantes/v046-mutacao-bench.json`, `tests/mutantes/v046-mutacao-bench-2.json`, `tests/test_changelog.py`, `tests/test_forge_mutante.py`.

## Achados
- A1 (recomendado) skills/qa-testing/SKILL.md:95 · segue aberto o A3 da E7.2: a skill do QA, agents/qa-engineer.md:20 e agents/tech-lead.md:25 não citam `SPEC --base`, e agents/tech-lead.md:41 não cita o bench da versão. Uma frase em cada, num PR seguinte.

## Parecer
Aprovado. O A1 da E7.2 está corrigido: `no_diff` (bin/forge-mutante:797) põe o mutante na rodada dirigida quando muda o `arquivo`, a spec versionada que o declara (caminho já resolvido e o processo na raiz do repositório, linha 821) ou o módulo de um dos seus `testes` (`modulos_do_teste`, linha 791). As sondas S1 e S2 viraram `test_teste_enfraquecido_entre_base_e_rev_roda_o_mutante_e_sobrevive` (rc 1, `M1 · sobreviveu`, sem `fora do diff: M1`) e a spec mudada tem `test_spec_mudada_entre_base_e_rev_roda_os_mutantes_dela`. O A2 da E7.2 (docstring) foi atendido: a ajuda diz o que conta, que helper importado não conta e que a 1.ª rodada do QA é a spec inteira.

Conferido e sem achado:
- Guardas do delta: `--cobertura --base 60bba369 --rev e452582f` sai rc 0, com `coberta` nas linhas 800 (M11, M12), 821 (M14, M15), 822 (M5) e 824 (M4); o `return any(...)` da linha 802 tem o M13 e os parênteses da linha 846 seguem com o M1 (o `de` foi atualizado). O autor relata 15/15 mortos; não refaço a mutação.
- `shlex.quote` na tag (A3 da segurança, dela) com teste `v9$(id)`; o ramo sem tag segue com o M10.
- Só o executor `unittest` existe, então o mapa `tests.x.Classe.teste` → `tests/x.py` cobre todos os casos de hoje.
- Testes do arquivo tocado, como o brief pede: `bin/forge-testes tests/test_forge_mutante.py`, 108 testes, OK (420 s). A suíte inteira fica no CI.
- Tamanho: o delta tem 76 linhas de código e teste; o PR inteiro passa de 150 (183, segundo o autor), e o corpo do PR precisa da linha `teto: excedido, 183 linhas, <motivo>`.
- Commits do delta: dois, Conventional Commits em português, um comportamento cada.
