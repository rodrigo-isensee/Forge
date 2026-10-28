---
tipo: revisao-seguranca
contrato: 1
pedido: conferente-c2c3
branch: melhoria/conferente-c2c3
commit: 5818e849140c76b535795feec6238af523d3f68b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: conferente-c2c3 (C2, C3 e C1 do CONFERENTE-VELOCIDADE), volta 2

Pedido de revisão: CONFERENTE-VELOCIDADE-REV (E2.1). Base `develop`, Base-sha `ce1a341b9874143cf3fb8c998a76eb473adc1df3`, head revisado `5818e84`. Revalidação por delta do parecer anterior (`4f7f81b`, head `cbb5227`): `forge-check delta --parecer` listou `bin/forge-check:950-951`, `tests/mutantes/conferente-c1-2.json` e `tests/test_volta_por_delta.py:201-236`; todos lidos, mais o caminho de `cmd_entrega` em volta (`bin/forge-check:927-960`) e `arquivos_da_entrega` (`:488-511`), por ser controle do Forge.

## Gatilhos
- Controles do Forge (`R-SEGURANCA`): `bin/forge-check` (conferente de entrega e `forge-check pr`).
- O C1 afrouxa em parte `R-PROVA` por decisão do dono (2026-10-27, "A"), no tamanho do E4.

## Achados

## Revalidação do A2 (resolvido)
- `bin/forge-check:950-951`: no ramo `dos_dois_pais`, o filtro passa de `n in dos_dois_pais[0]` para `n in dos_dois_pais[0] or n in desfeitos`, com `desfeitos = desfeitos_da_entrega(raiz, base_sha, valido)` (`set()` sem `--desde`). A mudança só acrescenta ao escopo: o `or` torna o filtro superconjunto do anterior, e a lista de entrada (`arquivos_da_entrega`, `:488-506`) já está limitada a `desde..head` mais os desfeitos que também mudaram nesse intervalo; nada sai por esse caminho.
- Os três caminhos no `--desde`: (1) commit linear: `:504-505` (já resolvido no A1); (2) merge da base como último commit: `:950-951`, e nas etapas de merge `:957-958` soma o mesmo ao filtro por conteúdo; (3) merge seguido de commit: `dos_dois_pais` deixa de se aplicar e `:504-505` mantém o desfeito. As quatro etapas (`codigo`, `pr`, `merge-integracao`, `pedido-de-merge-ao-dono`) estão nos testes (`tests/test_volta_por_delta.py:201-236`, `subTest` por etapa), com assert de `escopo: confira "teste.py" +0 -1` e de ausência de "sem commit".
- Mutação à mão (`bin/forge-check`, tirar `or n in desfeitos`, equivalente ao F2 de `tests/mutantes/conferente-c1-2.json`): `test_desfeito_pelo_merge_da_base_como_ultimo_commit_fica_no_escopo` falha (4 falhas, uma por etapa); os testes `merge_e_commit` e `linear` seguem verdes, como esperado, pois cobrem outros mecanismos (F1 e F3 do mesmo arquivo as guardam). Arquivo restaurado por `git checkout`.
- Testes do item: `tests.test_volta_por_delta`, 61 testes, OK, no head.
- PA-7 (`docs/engineering/achados-recorrentes.md`): sem linha em vigor ("nenhum ainda"); a classe "arquivo desfeito some do escopo" já teve 2 voltas no lote (A1, A2), por isso o autor testou os três caminhos; sugiro o `tech-lead`/eu registrarmos a linha AR no PR de fechamento, sem bloquear.

## Riscos aceitos e ferramentas
- Risco aceito pelo dono: afrouxamento parcial de `R-PROVA` do C1 (2026-10-27), no tamanho do E4.
- Ferramentas: leitura estática, testes do item e mutação local. Sem dependência, segredo nem workflow no diff; `gitleaks`, `osv-scanner`, `zizmor` e `actionlint` não se aplicam.
