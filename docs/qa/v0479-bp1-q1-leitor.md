---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp1-q1-leitor
commit: 4dec77902f90f0db3c7887085ab0f4294d55f2e8
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-bp1-q1-leitor

Módulos tocados: `bin/forge_quarentena.py`, `tests/quarentena.json` (vazio), `tests/test_forge_quarentena.py`. Sem suíte local; cenários locais com `python3 -I`. Revalidação no head eec2c1c1 (delta de `forge-check parecer delta`, base d0619ab2).

## Achados
- A1 (recomendado) bin/forge_quarentena.py:15 · `\d` aceita dígitos Unicode: `OK_DO_DONO.fullmatch("A-١")` casa (reproduzido); `DATA` casa, mas `fromisoformat` rejeita (falha fechada). Usar `[0-9]` no OK do dono.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Arquivo nasce vazio | Carregar.test_o_arquivo_do_repositorio_nasce_vazio | lista vazia | passou |
| Arquivo ausente, ilegível, fora do formato = nenhuma entrada (falha fechada) | Carregar.test_ausente_ilegivel_e_fora_do_formato_nao_deixam_entrada | ausente, `{`, `[]`, tipo errado | passou |
| Campos obrigatórios, classe, formato AAAA-MM-DD | Validar.test_campo_faltando, test_classe_fora_da_lista, test_data_fora_de_aaaa_mm_dd | campo vazio, data inválida | passou |
| Prazo de até 7 dias | Validar.test_prazo_de_ate_sete_dias_e_nao_antes_de_desde | 0 e 7 dias; -1 e 8 dias | passou |
| Autorização A-n | Validar.test_autorizacao_so_a_n | formato | passou |
| Prorrogação única, até 7 dias, OK novo | Validar.test_prorrogacao_* (3) | +1/+7 dias; +0/+8; mesmo OK; não objeto | passou |
| Teto de 3 ativas; vencida não conta | Validar.test_no_maximo_tres_entradas_ativas, test_vencida_nao_conta_no_teto | 3 e 4 | passou |
| Vale até o prazo inclusive; vencida sai sozinha | AtivasEVencidas.test_vale_ate_o_prazo_inclusive, test_vencida_sai_sozinha_*, test_prorrogacao_estende_a_validade | dia do prazo e dia seguinte | passou |
| Erro em qualquer entrada zera ativas e vencidas | AtivasEVencidas.test_com_erro_nao_exclui_nada_* | uma ruim entre boas | passou |
| Data sempre injetada | AtivasEVencidas.test_o_leitor_nao_tem_padrao_de_data | sem padrão | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_forge_quarentena.py`: Ran 20 tests, OK. Nenhum teste lê o relógio nem usa skip.
- Vermelho antes do verde: na base 004ce869 `bin/forge_quarentena.py` não existe; o módulo de teste copiado para a base falha na carga (`ModuleNotFoundError`; FAILED errors=1, cópia em `$TMPDIR`). O `forge-testes --vermelho` ficou na fila da trava `R-TETO` e não deu veredito neste prazo.
- Mutação: `forge-mutante` nas 3 specs, 17 mutantes, todos `morreu` (Q7 e Q13 por erro do teste declarado, com controle verde). `--cobertura --base 004ce869`: toda condição Python mudada tem mutante (`coberta`); só `tests/quarentena.json` sai `não coberto` (dado, sem regra).
- Bordas exploradas à mão: dígitos Unicode (A1); `desde` inteiro, `prorrogacao` nula ou `{}` caem em erro, sem exceção.

## Revalidação no head eec2c1c1 (delta d0619ab2..eec2c1c1)
Delta no domínio: `bin/forge_quarentena.py` (link, teto de 64 KiB, chave repetida, id de teste, `desde` futuro, repetido, `RecursionError`), 7 testes novos, mutantes Q18-Q23 e M42. A1 segue aberto, recomendado, sem mudança (`\d` nas linhas 20-21).
- `python3 -I -m unittest discover -s tests -p test_forge_quarentena.py`: Ran 27 tests, OK.
- Vermelho: `forge-testes --vermelho d0619ab2 --modulos test_forge_quarentena`: 7 provam (asserção=5, API ausente=2: teto, aninhado fundo, link, chave repetida, `desde` futuro, id, repetido); 20 "passa na base" são herdados.
- Mutação: `forge-mutante --base d0619ab2 tests/mutantes/v0479-bp1-q1-leitor-4.json`: Q18 a Q23 `morreu`; `v0479-quarentena-s1-5.json`: M41 e M42 `morreu` (M42 por erro do teste, controle verde). `--cobertura --base 004ce869`: toda condição Python mudada `coberta`; só `tests/quarentena.json` `não coberto` (dado).
- Bordas à mão, sem exceção: `teste` lista ou dict, bytes não UTF-8, dict aninhado 20000 níveis (cai no teto), diretório e `/dev/null` como arquivo, prazo igual a `desde`.
- Contrato dos CA da tabela acima: inalterado; a troca de ids `t.A.tN` por `test_N` nos testes só segue o novo formato.

## Revalidação no head 4dec7790 (delta eec2c1c1..4dec7790)
Delta no domínio: `bin/forge_quarentena.py` (aninhamento medido por `fundo_demais` de `hooks/_json_raso.py`, sem `RecursionError`), `tests/test_forge_quarentena.py` (+1 teste, 64 passa e 65 é ilegível), `tests/test_json_raso.py` (novo), mutante M42 reescrito. A1 segue aberto, recomendado, sem mudança.
- `python3 -I -m unittest discover -s tests -p test_forge_quarentena.py`: Ran 28 tests, OK. `test_json_raso.py`: Ran 2 tests, OK.
- Vermelho: `forge-testes --vermelho eec2c1c1 --modulos test_forge_quarentena`: prova (asserção)=1 (`test_aninhamento_medido_pelo_leitor_no_teto_de_json_raso`); os outros 27 passam na base (herdados).
- Mutação: `forge-mutante --base eec2c1c1 tests/mutantes/v0479-quarentena-s1-5.json`: M41 `morreu`, M42 `morreu` (`bin/forge_quarentena.py:49`), rc 0.
- Contrato dos CA da tabela: inalterado.
