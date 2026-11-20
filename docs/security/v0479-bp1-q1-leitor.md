---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp1-q1-leitor
commit: df0251cab7badbc83f17f494a457bad66e2f263f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: BP1 Q1, leitor da quarentena (v0478, E37.45), revalidação

Volta por delta. A rodada anterior (reprovada no head `d0619ab2`) fica no git. Lido: `forge-check parecer delta` de `d0619ab2..df0251ca`; no domínio só `bin/forge_quarentena.py` (relido por inteiro, 118 linhas); fora do domínio, conferidos só como prova das correções: `tests/test_forge_quarentena.py` e `tests/mutantes/v0479-bp1-q1-leitor-4.json` (Q18 a Q23). Requisitos e mitigações como na rodada anterior (modelo Q0, `docs/security/ameacas/bp1-quarentena.md`).

Gatilhos: autorizacao, ci-cd, controles-do-forge.

Estado dos achados anteriores:
- A1 corrigido: `bin/forge_quarentena.py:76` reprova `desde > hoje` (M13.1, C12); teste `test_desde_no_futuro_e_erro`, mutante Q22; S1 refeita.
- A2 corrigido: `:23` e `:67`, `teste` tem de ser `str` e casar `ID_DE_TESTE` com `fullmatch` (ASCII, ao menos 3 partes, método com prefixo `test` minúsculo); teste `test_teste_e_o_id_de_um_teste_so` (os sete de S2 e mais três), mutante Q21; S2 refeita com seis entradas novas. Com `discover -s tests` (`.githooks/pre-push:612`), nenhum módulo ou classe do corpus atual casa o padrão (`tests/evals` é o único pacote, `evals.test_placar` é recusado; nenhuma classe começa por `test`); a existência no discover segue na Q2 (M5.1, segunda metade).
- A3 corrigido: `:26` a `:30` e `:40`, `object_pairs_hook` levanta `ValueError` em qualquer nível; teste `test_chave_repetida_em_qualquer_nivel_nao_deixa_entrada`, mutante Q20; S3 refeita.
- A4 corrigido: `:36` a `:39`, `O_NOFOLLOW` e leitura de no máximo `TETO_BYTES + 1` (64 KiB, constante); testes `test_link_simbolico_nao_e_seguido` e `test_arquivo_acima_do_teto_nao_e_lido` (no teto passa, acima não), mutantes Q18 e Q19; S4 refeita. `O_NOFOLLOW` só cobre o último componente: pasta-mãe como link fica com quem chama, que passa o caminho fixo (como já dito na rodada anterior).
- A5 corrigido: `:100` e `:101`, `teste` repetido é erro; teste `test_teste_repetido_e_erro`, mutante Q23; S5 refeita.

## Achados
- A6 (recomendado) bin/forge_quarentena.py:42 · JSON aninhado fundo (30 mil colchetes, abaixo do teto de 64 KiB) faz `json.loads` levantar `RecursionError`, fora do `except`: `carregar` quebra em vez de dar `([], [motivo])` (M4.1, S6). Pré-existente. Incluir `RecursionError` no `except` e testar.

## Sondas
- S1 · `validar` e `ativas` com `desde=2026-12-30`, `prazo=2027-01-06`, hoje 2026-11-21 · espera: erro de `desde` no futuro e nenhuma ativa · obtido: erro `desde` no futuro e `ativas` vazio
- S2 · `validar([entrada(teste=t)], hoje)` com os sete valores de S2 da rodada anterior e mais `evals.test_placar`, `"...test_x\n"`, `...test_x?`, `test_á...`, `test_a..test_x`, `...A.Test_x` · espera: erro em cada um · obtido: erro nos treze
- S3 · `carregar` com `autorizacao` repetida na entrada e com `entradas` repetida no topo · espera: `([], [motivo])` · obtido: `([], ['quarentena ilegível: chave repetida no JSON'])` nos dois
- S4 · `carregar(link.json)` com link para JSON válido; arquivo de 64 KiB + 16 bytes; arquivo de exatamente 64 KiB; uma pasta · espera: recusa, recusa, aceita, recusa · obtido: `[Errno 40]`, `arquivo acima de 65536 bytes`, `([], [])`, `[Errno 21]`
- S5 · `validar` com duas entradas do mesmo `teste` · espera: erro de repetido · obtido: ``['test_a.A.test_x: `teste` repetido na quarentena']``
- S6 · `carregar` de `{"entradas":` + 30000 `[` + 30000 `]` + `}` · espera: `([], [motivo])` · obtido: exceção `RecursionError` (igual no head `d0619ab2`)

## Detalhe dos achados
- **A6** · evidência `bin/forge_quarentena.py:42` (o `except` pega `OSError, ValueError, KeyError, TypeError`; `RecursionError` é `RuntimeError`) · ataque: o autor do PR de quarentena grava um `tests/quarentena.json` aninhado; o runner da Q2 e a catraca da Q3 recebem exceção em vez do motivo. Sem ganho de exclusão (a exceção não devolve entradas), por isso recomendado: o risco é a Q2 ou a Q3 tratarem exceção de modo diferente do contrato "erro dá `([], [motivo])`" (M4.1) · severidade baixa · correção mínima: acrescentar `RecursionError` à tupla do `except` da `:42`; caso no teste de `carregar` com o aninhamento de S6 · esforço P · dono: `tech-lead`.

## Riscos aceitos e ferramentas
- Nenhum risco aceito.
- Teste do módulo rodado no head `df0251ca` (`python3 -m unittest tests.test_forge_quarentena`: 26 testes, OK). Suíte inteira não rodada (brief: sem suíte local); CI do head não consultado (credencial do `gh` fora do sandbox): lacuna registrada.
- Sondas locais em pasta temporária, com o módulo importado isolado (`python3 -I`); nada explorado fora da máquina; nenhuma ferramenta instalada.
