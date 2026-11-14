---
tipo: review
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-fechar-cartao
commit: ccb7613465a8be32a8fecf2070b9ad630836f364
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: melhorias-de-projeto-1311 (fechamento: FECHAR-REF-POR-NOME)

## Achados
- A1 (recomendado) tests/test_fechar_ref_por_nome.py:20 · test_dry_run_descreve_o_nome duplica a asserção de tests/test_fechar.py; o M3 só é morto pelo teste de test_fechar.py. Inofensivo.
- A2 (recomendado) tests/mutantes/mp1311-fechar-cartao-2.json:7 · M6 e M8 declaram a mesma troca (`de` e `para` iguais) na linha 826 de bin/forge-fechar; um mutante com os dois testes bastaria. Inofensivo.

## Sondas

## Parecer
Aprovado. Classe C, head 0884fae2, instância que não fez a entrega.

- Faz o que o item pede: com a branch local, `forge-check pr` recebe o nome (`ref_check="$ref"`); sem ela, o sha lido do servidor via `remoto_exato` (`bin/forge-fechar` 820-832). O dry-run segue a mesma regra.
- Cadeia do sha conferido intacta: `sha_conferido` lido antes do passo 1, `head_atual` relido depois do passo 1 e no passo 2, `--match-head-commit` no merge; o caminho sem branch local mantém o commit exigido (`cat-file`) e a releitura no servidor. Teste `test_head_que_anda_durante_a_conferencia_ainda_para` cobre o head que anda.
- Guardas do diff: 3 linhas mudadas, 3 mutantes declarados (M1, M2, M3), todos mortos (`bin/forge-mutante tests/mutantes/mp1311-fechar-cartao.json`). Cada ramo tem teste de comportamento.
- Testes rodados aqui (sem PR, só os afetados): test_fechar 99 OK, test_fechar_ref_por_nome 4 OK, test_fechar_sha_conferido 9 OK, test_fechar_base_andou 30 OK. `shellcheck bin/forge-fechar` sem saída.
- Tamanho: bin/forge-fechar 19 linhas e testes dentro da orientação de 150; um comportamento só. Fragmento em `changelog.d/` presente.

## Revalidação (delta 0884fae2..a47ef67b)
Aprovado no head a47ef67b, instância que não fez a entrega. Delta lido por `forge-check parecer delta`: `bin/forge-fechar`, `tests/mutantes/mp1311-fechar-cartao.json`, `tests/test_fechar.py`, `tests/test_fechar_ref_por_nome.py`, `tests/test_fechar_sha_conferido.py`.
- `ref_check` e `ref_dry` passam a `refs/heads/$ref` (linhas 768 e 826): a tag de mesmo nome não desvia a conferência. O `sha_conferido` já era lido por `refs/heads/$ref`, então a cadeia do `--match-head-commit` não muda.
- Teste novo `test_tag_de_mesmo_nome_nao_desvia_a_conferencia` cria a tag em outro sha, prova que o nome curto a casa e confere a chamada e o `--match-head-commit` com o sha da branch.
- Mutantes: M1 a M5 mortos (`bin/forge-mutante tests/mutantes/mp1311-fechar-cartao.json`); M4 e M5 cobrem as duas linhas mudadas.
- Testes rodados aqui: `tests.test_fechar_ref_por_nome` e `tests.test_fechar`, 104 OK. `shellcheck bin/forge-fechar` sem saída.
- A1 (recomendado) segue como estava; sem achado novo.

## Revalidação (delta a47ef67b..ccb76134)
Aprovado no head ccb76134, instância que não fez a entrega. Delta lido por `forge-check parecer delta` (sem o que veio da develop): `bin/forge-testes`, `tests/mutantes/mp1311-fechar-cartao-2.json`, `tests/test_fechar_base_andou.py`, `tests/test_qa_lote_l08.py`.
- `bin/forge-testes`: regra MAPA-FORGE-FECHAR com todos os 25 `tests/test_fechar_*.py` (conferido contra `ls tests/test_fechar*.py`) e todo módulo de `tests/` que cita `forge-fechar`; nenhum módulo listado inexiste. `bin/forge-testes --listar bin/forge-fechar` devolve os 33 módulos. A linha `test_ritmo` do diff veio da develop (2b454e7e).
- Testes: a asserção do E8 passa a esperar `refs/heads/<branch>`, coerente com o `ref_check` já aprovado no delta anterior; o teste do QA de duas branches no mesmo sha é dividido em sem a branch local (sha ambíguo para) e com ela (o nome decide). O teste do QA mudou: a revalidação dele é do QA.
- Mutantes: M6 e M8 mortos (`bin/forge-mutante --processos 1 tests/mutantes/mp1311-fechar-cartao-2.json`, rev ccb7613465a8); a âncora `then ref_check="refs/heads/$ref"; else` ocorre uma vez (linha 826).
- Testes rodados aqui: `tests.test_fechar_base_andou` e `tests.test_qa_lote_l08`, 62 OK. A suíte inteira fica no CI do PR 539; o e2e de instalação vermelho é infraestrutura do runner (npm), tratado em outra etapa.
- A1 segue; A2 (recomendado) novo; sem bloqueante.

## Revalidação (delta ccb76134..768896fc)
Aprovado; commit segue ccb76134 (head de código, Revisar-sha do brief da E1.52), instância que não fez a entrega. Delta lido por `forge-check parecer delta`: "nenhum arquivo do domínio mudou"; de ccb76134 até 768896fc só mudaram os pareceres (`docs/qa/`, `docs/reviews/`, `docs/security/`) e o merge 497d3569. A1 e A2 (recomendados) seguem; sem achado novo.
