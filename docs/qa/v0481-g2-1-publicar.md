---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: f3258bb890921173e775a174642fdb048f758158
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481-g2-1-publicar (E6.38, PR #878, G2.1: forge-check parecer publicar; classe C), volta por delta

Parecer anterior: aprovado em 939e4d22 (E6.33). Head revisado f3258bb8 (`HEAD` = remoto). Delta lido: `git diff 939e4d22..f3258bb8`: merge da develop 020e4af7 (0.47.19: #875, #877, #901, #903, #904, #905) com conflito em `bin/forge-testes` (tupla `FORGE_CHECK`) e `docs/hooks-fixtures.md` (índice gerado). O que veio da develop foi revisado no PR de origem; conferido só que entrou igual.

## Critério → teste → resultado (delta)
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A lógica do item não mudou: o patch contra a develop é igual ao aprovado | linhas `+/-` ordenadas, fora do índice e de `docs/qa`, `docs/reviews`, `docs/security`: `git diff 34ab6714 939e4d22` contra `git diff 020e4af7 f3258bb8`; a única diferença são as 2 linhas da tupla `FORGE_CHECK` | patch por base | igual, salvo a tupla |
| Conflito da tupla: os dois módulos ficam | `FORGE_CHECK` do head tem `test_fechar_corte` (develop) e `test_forge_pareceres` (item); `test_fechar_corte.py` 35 testes e `test_forge_pareceres.py` 35 testes | módulo sumido da tupla | passou |
| Índice regenerado em dia: 3596 = 3592 do item + 4 `salvar` da develop | `python3 scripts/indice-fixtures.py --conferir`: "em dia"; o diff do delta só soma o grupo `salvar` e a contagem | n/a | conferido |
| Nenhum teste do item se perdeu | `test_hooks.py -k test_fixtures_do_publicar` e `-k RecusaComFifoNoPerfil`: 8 testes | `--raiz` e FIFO no perfil | passou |

## Cenários e resultado real
- Só os módulos tocados: `test_forge_pareceres` 35 OK; `test_fechar_corte` 35 OK; `test_hooks` `test_fixtures_do_publicar` + `RecusaComFifoNoPerfil` 8 OK. A suíte inteira ficou com o CI.
- Mutantes: as specs do item (`tests/mutantes/v0481-g2-1-publicar*.json`) e o código que elas mutam não mudaram no delta (patch igual); o parecer 939e4d22 vale (M31 a M37 mortos, sem sobrevivente). Não rerrodados.
- Vermelho antes do verde: sem teste novo no delta.

## CI do head exato
`gh pr checks 878`, run 45806174857 com `headSha` f3258bb890921173e775a174642fdb048f758158: `suíte (python 3.12 e 3.14, partes 1 a 5)`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `teto de pulados` (2), `instalação (python 3.14)` e `árvore já provada na develop` verdes. Vermelhos: `bateria (pareceres)` (passo "Parecer de review (e de QA para a homolog)…"), `bateria` (passo "Passos e partes verdes") e `catraca` (passo "Regras que somem ou afrouxam…"): os três esperam os pareceres e o rótulo deste head, fora das partes que contam.

- ci: f3258bb890921173e775a174642fdb048f758158 verde

## Parecer
Aprovado no head f3258bb8: a resolução do conflito manteve os dois módulos na tupla, o índice está em dia, o patch do item é igual ao aprovado e o CI está verde nas partes que contam.
