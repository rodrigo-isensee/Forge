---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/ci-lote-e1
commit: 00e6d4304a6612dc657b084cef669944b7dd9371
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-11
---
# QA: v046 (E1.2, lote E1 do CI), revalidação da volta 1

Escopo incremental: delta b38fe7e6..00e6d430 (ci.yml, 3 testes, `tests/mutantes/v046-ci-lote-e1.json`, fragmento do changelog). Sem custo novo (`R-CUSTO`).

## Achados
- A1 (bloqueante) .github/workflows/ci.yml:1 · resolvido (anterior): passos baratos no job `bateria`; Provas, shellcheck e e2e no job `verificacoes` (`needs: [bateria]`); partes esperam só `[arvore, bateria]`; o agregador exige `bateria`, `verificacoes`, partes e pulados; vermelho barato reprova sem esperar a suíte.
- A2 (recomendado) .github/workflows/ci.yml:1 · aceito (anterior): Neutralidade sai dos passos e roda só nas partes (`tests.test_forge`); perde o vermelho cedo dela, custo de minutos só nesse caso, e a regra segue guardada na suíte.
- A3 (recomendado) scripts/suite-paralela.py:568 · `forge-check --cobertura` lista sem mutante a condição `c.isprintable() and c != '`'` (e a linha 564). `scripts/` está fora da regra de mutante declarado; vale um mutante que tire o filtro de crase.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A18: vermelho barato pula partes e verificações longas, agregadores reprovam | `MatrizNeedsEAgregadorTest` (pula as 6 partes e `bateria (verificações longas)`; `status` failure) | passo vermelho | passou |
| A18: fiação (agregador exige as 4 necessidades; `verificacoes` precisa só de `bateria`) | `FiacaoDoCI`, `MatrizNeedsEAgregadorTest` (needs literais) | needs exatos | passou |
| Passos que eram jobs continuam existindo | `LeituraDosWorkflowsTest.test_bateria_consolidada_mantem_os_passos_que_eram_jobs` (lê os dois jobs) | n/a | passou |
| QA-1: teto de 30 caídos | `Logica.test_testes_que_cairam_no_resumo_tem_teto_e_id_limpo` (30 literal, 37 entradas, "e mais 7") | limite 30 e 31 | passou |

## Cenários e resultado real
- Testes afetados no head 00e6d430: `MatrizNeedsEAgregadorTest`, `LeituraDosWorkflowsTest`, `FiacaoDoCI`, `Logica`, `Brinquedo`: 79 testes, OK (125 s).
- Mutantes declarados (6, `bin/forge-mutante tests/mutantes/v046-ci-lote-e1.json`): M1 a M6 morreram; nenhum sobrevivente. Cobrem needs das partes (M4), `needs` de `verificacoes` (M5), agregador (M6), filtro de crase, teto e chamada do resumo.
- Vermelho antes do verde: os testes de fiação do delta (`verificacoes` nos needs) citam job que a base não tem, então falham nela; M4 a M6 provam que quebram ao tirar a implementação. `forge-testes --vermelho` não rodado de novo (máquina carregada, o anterior estourou o prazo).
- Promessa de tempo: o comentário do ci.yml agora diz "sem medida do vermelho ainda"; não há promessa de 30 s a conferir. Medida real só no CI do PR.
- Limite: no CI o `if` de `verificacoes` usa `needs.bateria.outputs.pesada != 'false'`; só confirmável com run real (a branch não tem PR/run). Suíte inteira fica com o check-run `bateria` do PR.
