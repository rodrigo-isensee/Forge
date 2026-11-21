---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-b2-regerar
commit: 8e4888290286ba9a46948d19583ba90e9fc90363
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E57.38 (PR-VERDE B2, `forge-testes --regerar`)

Escopo: `bin/forge-testes` (+76 linhas), `tests/test_testes_tocados.py` (classe `Regerar`), duas specs de mutantes. Sem suíte local; o CI do PR confere a bateria.

## Critério → teste → resultado
| Critério (obrigação) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Nada tocado: nada a regerar, apagado entra na fotografia | `test_nada_tocado_nada_a_regerar` | diff sem fonte | passou |
| bin/ tocado regera só o índice | `test_bin_tocado_regera_so_o_indice` | fonte única | passou |
| Subpasta funda de bin/ não é fonte | `test_pasta_funda_de_bin_nao_e_fonte_do_indice` | logo fora do limite | passou |
| Módulo novo sem peso é medido | `test_modulo_novo_sem_peso_e_medido_e_o_indice_fica` | peso novo | passou |
| Gerador vermelho sai 1 | `test_gerador_vermelho_sai_1` | rc do gerador | passou |
| Escrita fora da lista fechada sai 2 (controle limpo e arquivo já alterado) | `test_escrita_fora_da_lista_fechada_sai_2` | permissão (lista fechada) | passou |
| Link no derivado ou na pasta: recusa sem rodar | `test_link_no_derivado_ou_na_pasta_recusa_sem_rodar_o_gerador` | link | passou |
| Sem veredito (base, pesos ilegíveis) e aviso da busca | `test_sem_veredito_sai_2_e_a_busca_que_falha_avisa` | entrada inválida | passou |
| Git ilegível depois do gerador sai 2 | `test_git_ilegivel_depois_do_gerador_sai_2` | falha de dependência | passou |
| `--regerar` só combina com `--base` | `test_regerar_so_combina_com_base` | 10 combinações | passou |
| Lista fechada sem arquivo de controle; geradores existem | `test_lista_fechada_sem_arquivo_de_controle_e_geradores_que_existem` | lista fechada | passou |

## Cenários e resultado real
- Local: `python3 -I -m unittest discover -s tests -p test_testes_tocados.py -k Regerar` -> Ran 11 tests, OK.
- Vermelho (`R-QA`), saída colada:
```
vermelho: 1 módulos em duas cópias, em série; prazo de 600 s por módulo e cópia (teto 1200 s)
(10 testes de Regerar) H=ok · B=falha · prova (asserção)
test_lista_fechada_sem_arquivo_de_controle_e_geradores_que_existem · H=ok · B=erro · prova (API ausente)
contagem: não prova (passa na base)=174; prova (API ausente)=1; prova (asserção)=10; pulado=1
```
  rc=0; nenhum teste cai no HEAD. O `pulado` é `MedidaDaVagaPesada` (já existente, fora do diff).
- Mutação: `bin/forge-mutante tests/mutantes/v0479-pv-b2-regerar.json tests/mutantes/v0479-pv-b2-regerar-2.json` -> G1 a G16 todos `morreu`, rc=0.
- Cobertura: `forge-mutante --cobertura --base ed5bfa0284c3bbf2ac006d546daf96b1346886ff` -> `base=ed5bfa02… mb=ed5bfa02… rev=c5815650…`; só linhas `coberta`, nenhuma condição sem mutante.
- Diff conferido: sem mudança de escopo; AR-12 (`except` do R6 do B1 intacto) atendido.

## Revalidação (delta c5815650..8e488829)
Domínio: `bin/forge-testes` (fotografia com `--ignored=traditional` e `SEM_BYTECODE`), o teste de caminho ignorado e a spec `-3` (G17, G18). Aviso do `forge-check parecer delta`: o merge 8a5c17a não está na origin/develop local; o que ele trouxe contou inteiro e nada fora do domínio foi relido.

| Critério (obrigação) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Escrita em caminho ignorado (`.forge/`, existente ou novo) sai 2; `__pycache__` não conta (A1 da segurança) | `test_escrita_em_caminho_ignorado_sai_2_e_o_bytecode_nao` | ignorado arquivo a arquivo; bytecode fora | passou |

- Local: `python3 -I -m unittest discover -s tests -p test_testes_tocados.py -k Regerar` -> Ran 12 tests, OK.
- Vermelho (`--modulos test_testes_tocados`): `vermelho: base=c5815650ef8c head=8e4888290286 módulos=test_testes_tocados (restrito por --modulos)`; `test_escrita_em_caminho_ignorado_sai_2_e_o_bytecode_nao · H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=185; prova (asserção)=1; pulado=1`; rc=0.
- Mutação do delta: `base=c5815650ef8c81b24ca7d466b7a23f04239458b6 mb=c5815650… rev=8e4888290286…`; G1 a G18 todos `morreu` (G17 bin/forge-testes:1005, G18 bin/forge-testes:990), rc=0.
- Cobertura (`--cobertura --base ed5bfa02…`): 14 linhas, todas `coberta`; nenhuma condição sem mutante; as duas linhas novas (argumentos e constante do pathspec) não são condição e têm G17 e G18.
