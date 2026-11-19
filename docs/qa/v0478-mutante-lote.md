---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-mutante-lote
commit: 5520fd0d156beede30c54efb16227559be919e85
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 mutante em lote (E17.4)

Diff `0c47762a..b11631b2`: `bin/forge-mutante` (`--ids`, isenta velha e fora do diff, isenta da condição nova por ocorrência), skill `qa-testing`, 2 specs novas (`v0478-mutante-lote*.json`) e 7 specs antigas realinhadas, `tests/test_forge_mutante.py`. Obrigações: E17.1 (`--ids`, cobertura com isenta velha rc 1, isenta fora do diff, erro sob mutante) e `R-QA`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `--ids` roda só os pedidos | `Execucao.test_ids_roda_so_os_mutantes_pedidos` | ordem dos ids, mutante fora da lista | passa; vermelho na base |
| id desconhecido ou vazio sai 2 sem rodar | `Execucao.test_id_que_a_spec_nao_declara_recusa_com_a_lista_e_nada_roda` | id inexistente, `""`, `"M1,"` | passa; vermelho na base |
| `--ids` sem SPEC recusado e na ajuda | `Execucao.test_ids_vem_com_spec_e_aparece_na_ajuda` | `--cobertura` com `--ids` | passa; vermelho na base |
| isenta velha à parte, rc 1, cobertura inteira | `Cobertura.test_isenta_velha_sai_a_parte_depois_da_cobertura_inteira_e_1`, `..._para_arquivo_de_shell_e_velha_e_sai_1`, `..._pelo_texto_que_nao_casa_o_no_fica_solta` | trecho fora do nó, outro arquivo, além do nó | passa; vermelho na base |
| isenta da spec da base é `fora do diff`, fora do rc | `Cobertura.test_na_volta_a_isenta_da_spec_da_base_fica_fora_do_rc_e_a_nova_velha_conta` | isenta nova que não casa segue velha | passa; vermelho na base |
| isenta vale para cada condição nova do trecho | `Cobertura.test_isenta_vale_para_cada_condicao_nova_com_o_mesmo_trecho` | duas ocorrências, trecho que passa do nó | passa; vermelho na base |
| caminho da apagada repetida (sem `nova`) | `Cobertura.test_isenta_da_apagada_repetida_com_trecho_alem_do_no_e_velha` | trecho além do nó e começando antes | passa; vermelho na base |
| skill diz o que a ferramenta faz | leitura do diff da skill contra o código | n/a | confere |

## Provas
- Módulo: `python3 -I -m unittest discover -s tests -p test_forge_mutante.py` com TMPDIR: `Ran 144 tests in 238.914s · OK`. Suíte inteira não rodada (vale o `bateria` do CI no mesmo sha).
- Vermelho: `forge-testes --vermelho 0c47762a... --modulos test_forge_mutante` saiu 0: `vermelho: base=0c47762a6a9d head=b11631b2e9e5`, revertidos à base `bin/forge-mutante`, changelog e skill; `contagem: não prova (passa na base)=135; prova (asserção)=9`. Os 9 que provam são os da tabela, com `H=ok · B=falha`; nenhum cai no HEAD.
- Mutantes: `forge-mutante tests/mutantes/v0478-mutante-lote.json tests/mutantes/v0478-mutante-lote-2.json --processos 4` saiu 0, 16 de 16 `morreu` (M1-M11, M13-M17; linhas 1138, 1179, 1180, 1049, 1050, 1055, 596, 598, 598, 827, 645, 608, 819, 842, 818, 834). Nenhum sobrevivente, nenhum equivalente declarado.
- Cobertura: `forge-mutante --cobertura --base 0c47762a...` rc 0, base=mb=0c47762a, 12 linhas `coberta` (596, 598, 608, 818, 827, 842, 1049, 1050, 1055, 1138, 1179, 1181), nenhuma `sem mutante`, `apagada` ou `isenta velha`. Conferido contra o diff: toda condição mudada tem mutante.
- `forge-mutante --conferir --base 0c47762a...`: `conferidas: o trecho de cada spec do diff está no lugar`.
- Simulação de merge não feita (o brief pede só testes dos arquivos tocados).

## Observação (não bloqueia)
A linha 645 (`nova=True` em `analisar_com_textos`) e o rótulo `--ids` ficam cobertos por M11 e pelos testes de ajuda; sem lacuna vista.

## Revalidação (E17.9, delta `b39110b2..5520fd0d`)
Delta: `forge-check parecer delta` lista `bin/forge-mutante`, changelog, 5 specs de mutante e `tests/test_forge_mutante.py`. Mudança: a isenta da condição nova vale só para as cópias da mesma condição (`cruza` com `nós`, `cabe`, `ocorrencias`). Obrigação: E17.5 (S1 da segurança) e `R-QA`.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| isenta de trecho comum não libera outra condição, cópia fora do hunk nem comentário | `Cobertura.test_isenta_de_trecho_comum_nao_libera_outra_condicao_copia_fora_do_hunk_nem_comentario` (3 subtestes) | trecho em outra condição, fora do hunk, em comentário | passa; vermelho na base `b39110b2` |
| isenta vale para cada cópia da mesma condição (E17.1, mantido) | `Cobertura.test_isenta_vale_para_cada_condicao_nova_com_o_mesmo_trecho` | duas ocorrências | passa |

## Provas da revalidação
- Módulo: `python3 -I -m unittest discover -s tests -p test_forge_mutante.py` com TMPDIR: `Ran 145 tests in 111.352s · OK`. Suíte inteira não rodada (vale o `bateria` do CI).
- Vermelho: `forge-testes --vermelho b39110b2 --modulos test_forge_mutante` saiu 0: `vermelho: base=b39110b2aa92 head=eb857686a5a1`; `...test_isenta_de_trecho_comum_... · H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=144; prova (asserção)=1`. Nenhum cai no HEAD.
- Mutantes: `forge-mutante tests/mutantes/v0478-mutante-lote.json tests/mutantes/v0478-mutante-lote-2.json tests/mutantes/v0478-mutante-lote-3.json --processos 4` saiu 0, 17 de 17 `morreu` (M1-M11, M13-M18; linhas 1151, 1192, 1193, 1062, 1063, 1068, 607, 610, 610, 840, 657, 620, 832, 855, 831, 847, 587). Nenhum sobrevivente, nenhum equivalente. M18 (`cabe`, linha 587) é novo; M7-M17 foram refeitos nas linhas novas.
- Cobertura: `forge-mutante --cobertura --base 0c47762a...` rc 0: 14 linhas `coberta` de `bin/forge-mutante` (587, 607, 610, 620, 657, 831, 840, 855, 1062, 1063, 1068, 1151, 1192, 1194), nenhuma `sem mutante` nem `isenta velha`; as linhas `spec editada` são as specs antigas realinhadas (M58 e IL11). `--conferir --base 0c47762a...`: `conferidas: o trecho de cada spec do diff está no lugar`.
- Merge `eb857686` (documentos de review e segurança) fora do domínio do QA: nada relido.
