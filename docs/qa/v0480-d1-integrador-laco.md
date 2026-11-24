---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-d1-integrador-laco
commit: 0ba10e549428ad4bafbc0139eacbfc870956c89a
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA · D1 integrador em laço, `forge-fechar --laco` (E173.1, PR #865)

Head 8b056d4d, base 8a6f5907. Sem suíte local: a bateria é o check-run `bateria` do CI do mesmo sha; aqui, o módulo tocado, o vermelho e os mutantes. Obrigações (E173.1 e decisão do dono de 24/11: aviso de PR parado há 2 h, só leitura; grupos de até 3 sem arquivo em comum pelo `--lote`; só entram os que passam no `forge-check pr`).

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Grupos de até 3 em ordem de chegada; o resto sozinho, sem `--lote` | `test_grupos_de_ate_3_em_ordem_e_o_ultimo_sozinho_sem_lote` | 4 PRs: 3 + 1 | passou |
| Arquivo em comum abre grupo novo | `test_arquivo_em_comum_abre_grupo_novo` | interseção de 1 arquivo | passou |
| Aviso de parado há mais de 2 h (conflito ou vermelho), só aviso, não entra | `test_parado_ha_mais_de_2_h_avisa_e_nao_entra` | 2 h e 1 s avisa; 2 h exatas não; data vazia ou ilegível avisa | passou |
| Só entram aprovados no `forge-check pr`, `melhoria/*`, com um pedido só no parecer de review da própria branch | `test_so_entram_os_aprovados_com_um_pedido_so` | zero ou dois pedidos, prefixo de branch, nome inválido, branch ausente | passou |
| Diff ilegível deixa o item de fora e o laço segue | `test_diff_ilegivel_fica_de_fora_e_o_laco_segue` | ramo órfão | passou |
| Códigos: 5 para o laço; 1 e 3 seguem; 1 vence 3 | `test_codigos_dos_grupos` | 5 combinações | passou |
| `--dry-run` lê e não fecha | `test_dry_run_le_e_nao_fecha` | zero chamadas de item | passou |
| Lista ilegível para sem mesclar | `test_lista_ilegivel_para` | falha do `gh` | passou |
| `--laco` recusa item, `--ref`, `--lote`, `--limpar` | `test_recusa_o_que_nao_e_do_laco` | combinação proibida | passou |
| Sem `--laco` o fluxo do item não muda | `test_sem_laco_o_fluxo_do_item_segue` | regressão | passou |

Acessibilidade e E2E: n/a (CLI). Permissões: o laço só lê PRs e repassa o fechamento de sempre (CI verde, `--match-head-commit`), sem caminho novo de merge.

## Cenários e resultado real
- Módulo tocado: `python3 -I -m unittest discover -s tests -p test_fechar_laco.py`: `Ran 10 tests in 9.068s · OK`.
- Vermelho antes do verde (`forge-testes --vermelho 8a6f5907 --modulos test_fechar_laco`):
  - `vermelho: base=8a6f59075210 head=8b056d4d81fc módulos=test_fechar_laco (restrito por --modulos)`
  - revertidos à base: `bin/forge-fechar`, `bin/forge-testes`, `changelog.d/v0480-d1-integrador-laco.md`, `tests/pesos-d4.json`
  - `contagem: não prova (passa na base)=1; prova (asserção)=9`. O que passa na base é `test_sem_laco_o_fluxo_do_item_segue`, teste de regressão (o fluxo sem `--laco` deve ficar igual); não é teste de regra nova.
- Mutantes (5 specs, 33 mutantes, `--processos 4`): `M1` a `M33` todos `morreu`, nenhum sobrevivente, nenhum equivalente (`rev=8b056d4d81fc`). Conferi a lista contra o diff: a recusa de argumentos (170, 172), o filtro de conflito/vermelho, o limite de 7200 s, `melhoria/*`, `check-ref-format`, a busca, o pedido único, o `forge-check pr`, o limite de 3, a interseção de arquivos, cada código de saída e a chamada em 1455 têm mutante. `forge-mutante --cobertura --base 8a6f5907` só devolve `não coberto: bin/forge-fechar` e `tests/pesos-d4.json`, o esperado para shell e JSON (cobertura manual acima).
- Prova de suíte inteira: check-run `bateria` do CI do PR, no mesmo sha (não rerrodada aqui).

## Delta 8b056d4d..0ba10e54 (E173.28)
Domínio do QA no delta (`forge-check parecer delta`, base origin/develop a6e81a5, sem o que veio da base): `bin/forge-testes`, `docs/fechamento-integrador.md`, `tests/pesos-d4.json`. `bin/forge-fechar` e `tests/test_fechar_laco.py` não mudaram desde o parecer anterior, então o vermelho e os 33 mutantes de 8b056d4d seguem valendo.
- Manual do `--laco` (`docs/fechamento-integrador.md:103`) conferido contra `bin/forge-fechar`: só `--base`, `--espera`, `--espera-ci`, `--dry-run`; `gh pr list --limit 100` (linha 1299); relógio `FORGE_FECHAR_AGORA` só com `FORGE_FECHAR_TESTE=1` (linha 231); `--espera` 0 a 7200 (linha 219); aviso de parado após 2 h coberto por `test_parado_ha_mais_de_2_h_avisa_e_nao_entra`. Os limites A2 e A3 do review estão descritos e o texto da reversão cita `fechar_laco`.
- Merge da develop: `forge-testes` ganhou `test_forge_copia` (FORGE_CHECK e MAPA, o arquivo existe) e `pesos-d4.json` a entrada `test_hook_decisao` (JSON válido); resolução sem perda dos itens do laço.
- Módulos dos arquivos tocados, local: `test_fechar_laco.py` `Ran 10 tests · OK`; `test_forge_copia.py` `Ran 77 tests · OK`; `test_hook_decisao.py` `Ran 11 tests · OK`; `bash -n bin/forge-fechar` ok.
- Suíte inteira: check-run `bateria` do CI do PR no mesmo sha, não rerrodada aqui.

## Observação
O laço pode pegar PR em rascunho aprovado; o passo 6 do item já converte rascunho em pronto, então não é defeito, só comportamento a saber.
