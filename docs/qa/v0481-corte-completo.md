---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-corte-completo
commit: 8e814a7337637b561c53fe9b66ba4fd54966b1ec
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 (forge-fechar --corte: marca pronta para a promoção, #887, E13.17)

Classe C. Diff lido contra a base `5fb8e328667e`: `bin/forge-fechar` (+105), `tests/test_fechar_corte.py`, duas specs de mutante, fragmento de changelog e `docs/fechamento-integrador.md`. A suíte inteira fica para o check-run `bateria` do CI do PR (R-QA); aqui rodei o módulo do item, as 16 specs de mutante e o vermelho restrito.

## Critério → teste → resultado
| Critério (do brief) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Data da seção é o dia local | `test_data_da_secao_e_o_dia_local` (date falso: local e UTC diferem) | local x UTC | passou; M4 morre |
| Corpo da marca traz a linha de teto e os três pareceres release-<versão>; a tela imprime a classe | `test_marca_nasce_com_o_teto_os_pareceres_release_e_a_classe` | 151 linhas | passou |
| Sem a linha de teto no limite | `test_marca_no_teto_sai_sem_a_linha_de_teto` | 150 linhas (teto) | passou; M2 morre |
| Marca que não mede não é enviada | `test_marca_que_nao_mede_nao_envia` | git falha no numstat | passou; M1 e M3 morrem |
| Fragmento posterior ao corte entra na seção (merge da develop e `--anexar`) | `test_fragmento_depois_do_corte_entra_na_secao_da_versao` | só o fragmento ausente da base comum; segunda volta não faz nada | passou; M6, M7 morrem |
| Anexo não leva fragmento de outra versão | o mesmo teste (`changelog.d/` do ramo só com README; seção só com o novo) e `test_anexar_que_falha_para_sem_enviar` | `comm -23 develop base-comum` | passou |
| Anexar, buscar, merge-base ou corpo que falham param sem enviar | `test_anexar_que_falha_para_sem_enviar`, `test_leituras_do_ramo_da_marca_que_falham_param`, `test_corpo_que_nao_refaz_para` | cada leitura e o envio | passou; M9 a M12 morrem |
| `--dry-run` só avisa | `test_dry_run_so_avisa_o_fragmento_novo` | ramo no origin inalterado | passou; M8 morre |
| V3 com `afrouxa-regra` imprime o pedido ao dono por `gh pr view --web`; sem script de rótulo | `test_promocao_com_afrouxa_regra_pede_o_rotulo_na_main` | nome exato (não substring), vazio, leitura que falha | passou; M13 a M15 morrem |
| Nenhum passo mescla sem checks verdes | leitura do diff: o código novo só faz `git merge` local na worktree descartável, `git push` de avanço no ramo da marca e `gh pr edit --body`; nenhum `gh pr merge` | n/a | confere |
| Nada que barra hoje deixa de barrar | os 18 testes antigos do módulo passam (H=ok), incl. `test_ramo_da_marca_ja_no_origin_nada_faz` (M5 morre); leitura que falha (`erro`) segue sem anexar | ramo existente, leitura falha | passou |

## Cenários e resultado real
- Módulo: `python3 -I -m unittest discover -s tests -p test_fechar_corte.py` → `Ran 28 tests ... OK`.
- Mutantes: `bin/forge-mutante tests/mutantes/v0481-corte-completo.json tests/mutantes/v0481-corte-completo-2.json --processos 3` → `pedido=v0481-corte-completo rev=036a78a16d09`, M1 a M16 todos `morreu`, nenhum sobrevivente, nenhum equivalente.
- Cobertura: `bin/forge-mutante --cobertura --base 5fb8e328667e` → `não coberto: bin/forge-fechar` (shell, fora da checagem Python, que o brief já cobre com 16 mutantes à mão, um por guarda nova: medida estrita, teto, ordem medir-antes-de-enviar, data, ramo existente, anexar, dry-run, leituras, corpo, rótulo, worktree), `spec editada · tests/mutantes/v0480-d4-corte-contador-4.json` (ajuste de trecho `de`, sem mutante a menos) e `não coberto: tests/pesos-d4.json` (dado).
- Vermelho: `bin/forge-testes --vermelho 5fb8e328667e --modulos test_fechar_corte` (a lista completa de 252 módulos fica para o CI) → rc 0:
  `vermelho: base=5fb8e328667e head=036a78a16d09 módulos=test_fechar_corte (restrito por --modulos)`; `contagem: não prova (passa na base)=18; prova (asserção)=10`. Os 10 novos caem na base e passam no HEAD (os 18 que passam na base são os anteriores do módulo).
- Suíte e check-run `bateria` do sha: a conferir no CI do PR (#887); não rodei a suíte local.

## Notas sem bloqueio
- O clone `/root/.forge-contrib/wt/v0481-corte-completo-qa` foi feito com `git clone --shared` porque `git worktree add` falha no sandbox (`.git/worktrees` somente leitura).

## Revalidação por delta (E13.21): 036a78a1 a 8e814a73
`forge-check parecer delta` lista no domínio: `bin/forge-fechar`, `docs/fechamento-integrador.md`, `tests/mutantes/v0481-corte-completo-3.json`, `tests/test_fechar_corte.py`, `tests/test_reval_delta.py`. Li o diff dos cinco.

| Mudança do delta | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Mensagem do V5 diz que o mesmo comando não refaz o corpo e aponta a medida em `$tmp/nova-medida` (o `tmp` não é removido no caminho de `die`) | `test_corpo_que_nao_refaz_para` (asserção nova `ajuste o corpo à mão com a medida em `) | edição do PR que falha | passou; cai na base, prova |
| Leitura do `ls-remote` do origin em erro sai em 0, sem buscar, enviar nem refazer o corpo | `test_leitura_do_origin_que_falha_nao_anexa` (ramo no origin igual ao de antes; nenhuma edição nem criação de PR) | leitura do origin que falha | passou; M17 morre |
| Contagem de citações de `README.md` em `test_fechar_corte.py` de 2 para 3 | `test_reval_delta` (módulo inteiro, 10 testes) | citação nova do nome sintético | passou |
| Limite do `--laco` e mensagem de erro no manual | leitura: o texto confere com o código (anexo só quando um `--corte` roda entre o fragmento e o merge da marca) | n/a | confere |

- Módulos: `test_fechar_corte` → `Ran 29 tests ... OK`; `test_reval_delta` → `Ran 10 tests ... OK`.
- Vermelho: `bin/forge-testes --vermelho 036a78a16d09 --modulos test_fechar_corte,test_reval_delta` → rc 0; `contagem: não prova (passa na base)=38; prova (asserção)=1` (`test_corpo_que_nao_refaz_para`). O teste de M17 passa na base de propósito: guarda comportamento que já existia (o ramo de erro do `ls-remote`); a prova dele é o mutante, não o vermelho.
- Mutantes: `bin/forge-mutante` nas três specs (`v0481-corte-completo.json`, `-2`, `-3`) com `--processos 3` → `rev=8e814a733763`, M1 a M17 todos `morreu`, nenhum sobrevivente.
- CI do head `8e814a73` (PR #887, run 45554026272), lido na hora do parecer: parte 3/5 do python 3.14 `pass`; a do 3.12 ainda `pending`; partes 2/5 e 5/5 do 3.12 e 5/5 do 3.14 `pass`; `bateria (passos)`, `bateria (verificações longas)`, `catraca` e `instalação` `pass`. `bateria (pareceres)` está `fail` porque os pareceres ainda apontam o sha anterior: é o que esta regravação conserta. O check-run `bateria` final do sha decide o merge; não rodei a suíte local.
