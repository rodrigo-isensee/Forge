---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-clone-nome-unico
commit: 56f3d992094b15b88b6210019abc1104ee4bcf1a
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0480-clone-nome-unico (E172.32, PR #860, delta d33eb54d..56f3d992)

Escopo incremental (`forge-check parecer delta`): `bin/forge-check`, `bin/forge-testes`, `changelog.d/v0480-clone-nome-unico.md`, `tests/mutantes/v0478-clone-nome-unico.json`, `tests/test_forge_copia.py`. Os 10 critérios do parecer anterior (d33eb54d, aprovado) seguem; o delta muda a guarda do id do pedido (agora `valor_de_shell_seguro("pedido", id)`, recusa `-` no início), o texto da linha da cópia e o mapa `FORGE_CHECK` (A1 do review, `test_forge_copia`). Sem suíte local; a inteira fica para o CI do PR.

## Critério → teste → resultado
| Critério (obrigação) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| BRIEF-PEDIDO-ID-CRU: id com hífen no início (`--lote`, `-h`) não vira opção do forge-fechar | test_id_do_pedido_com_hifen_no_inicio_nao_vira_opcao | id começando por `-` | passou |
| BRIEF-PEDIDO-ID-CRU: id com crase vira PREENCHER (segue) | test_id_do_pedido_com_crase_nao_vai_cru_ao_brief | id fora da forma | passou |
| CLONE-NOME-UNICO: linha da cópia com o comando de criação do texto novo | test_brief_gerado_traz_a_copia_sugerida | n/a | passou |
| mapa FORGE_CHECK lista todo módulo que usa o forge-check (A1 do review) | test_testes_tocados.MapaDoForgeCheck | módulo novo fora do mapa | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_forge_copia.py`: 77 testes, OK. `test_testes_tocados.py`: 196 testes, OK (skipped=1, já existente). `test_pre_envio_brief.py`: 21, OK.
- Vermelho (`bin/forge-testes --vermelho d33eb54d678d9032d6901f733797534c6f625ab4 --modulos test_forge_copia`): `vermelho: base=d33eb54d678d head=56f3d992094b módulos=test_forge_copia (restrito por --modulos)`; contagem: não prova (passa na base)=75; prova (asserção)=2 (test_brief_gerado_traz_a_copia_sugerida e test_id_do_pedido_com_hifen_no_inicio_nao_vira_opcao, H=ok B=falha). Os 2 testes mudados/novos provam.
- Mutantes (`bin/forge-mutante tests/mutantes/v0478-clone-nome-unico.json`): `rev=56f3d992094b`; M1, M8, M2, M3, M4, M5, M6, M7 todos `morreu` (M4 e M7 por erro do teste sob o mutante, com controle verde). M8 (volta à guarda antiga `ID_DE_PEDIDO.fullmatch`) morre pelo teste do hífen.
- Cobertura (`--cobertura --base d33eb54d`, delta): `base=d33eb54d678d mb=d33eb54d678d rev=56f3d992094b`; `coberta · bin/forge-check:9567 · M1, M8`. Contra a base original 5f1c6e97 as 5 linhas de guarda (9527, 9537, 9567, 9627, 9628) seguem cobertas. A mudança do texto da linha da cópia não é guarda de decisão.
- Limite visto: o ramo de `merge-integracao` (`forge-fechar {id_impresso}`) segue sem teste próprio com id de hífen; o teste checa `proximo`, `decisões:` e a ausência do id cru. Sem achado.
