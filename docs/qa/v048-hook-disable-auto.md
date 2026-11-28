---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-hook-disable-auto
commit: 897d2036179082df5f238d938e182316a13b307c
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: v048 HOOK-DISABLE-AUTO (E13.2, E13.35)

- ci: 897d2036179082df5f238d938e182316a13b307c NÃO verde: o job "suíte (python 3.12, parte 1/5)" falhou; demais jobs verdes fora "bateria", "bateria (pareceres)", "catraca" e "catraca (conferência)", que esperam parecer ou rótulo.

## Achados
- A1 (bloqueante) tests/testes_tocados.py:153 · módulo novo test_hooks_desarma_auto não entra no mapa FORGE_CHECK nem no lote de test_hooks; a suíte falha em MapaDoForgeCheck.test_mapa_lista_todo_modulo_que_usa_o_forge_check e CaminhoFiltroEAviso.test_test_hooks_pelo_caminho_roda_quem_reaproveita_o_lote_dele. Reproduzido local.

## Critério → teste → resultado
O pedido não traz CA-n de UX; as obrigações são HOOK-DISABLE-AUTO (E13.2) e o brief.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| desarme --disable-auto por número ou sem parecer passa (rc 0) | test_desarme_passa_sem_parecer (2 fixtures -libera) | n/a | passou (vermelho na base) |
| forma duvidosa segue como merge: =true sozinha, valor de outra opção, =false, --admin, --auto, grupo curto -sb, depois de -- (rc 2) | test_forma_duvidosa_segue_como_merge (7 fixtures -bloqueia) | limite da leitura do gh | passou |
| o mapa de testes conhece o módulo novo | test_mapa_lista_todo_modulo_que_usa_o_forge_check | n/a | FALHOU (A1) |

## Cenários e resultado real
Vermelho antes do verde (bin/forge-testes --vermelho a19718532c83 --modulos test_hooks_desarma_auto):

    vermelho: base=a19718532c83 head=897d20361790 módulos=test_hooks_desarma_auto (restrito por --modulos)
    revertidos à base: changelog.d/v048-hook-disable-auto.md, hooks/parecer.py
    test_desarme_passa_sem_parecer · H=ok · B=falha · prova (asserção)
    test_forma_duvidosa_segue_como_merge · H=ok · B=ok · não prova (passa na base)
    contagem: não prova (passa na base)=1; prova (asserção)=1

Os 7 fixtures que bloqueiam passam na base por natureza (guardam o portão contra afrouxar); quem os prova são os mutantes. Não é defeito.

Mutantes (bin/forge-mutante tests/mutantes/v048-hook-disable-auto.json, rc 0, 8 de 8 mortos, rev=897d20361790): M1 morreu (parecer.py:493), M8 morreu (:493), M2, M3, M4 morreram (:359), M5 morreu (:361), M6 e M7 morreram (:362). Cada linha de guarda do diff tem mutante; nenhum sobrevivente.

Sondagem adversarial pelo hook real (stdin JSON em hooks/parecer.py): --disable-auto por número, sozinho: rc 0; com pipe para cat: rc 0; seguido de outro merge por número (com &&, ponto e vírgula, &, quebra de linha, subshell ou crase): rc 2, o segundo merge segue barrado. Pela função analisar: --auto, --admin, =false, "-b --disable-auto" e "--body --disable-auto" seguem como merge; "-R o/r … --disable-auto" e "--squash --disable-auto" passam. Nada afrouxou além do declarado.

Falha local reproduzida: python3 -m unittest tests.test_testes_tocados.MapaDoForgeCheck.test_mapa_lista_todo_modulo_que_usa_o_forge_check tests.test_testes_tocados.CaminhoFiltroEAviso.test_test_hooks_pelo_caminho_roda_quem_reaproveita_o_lote_dele resultou em FAILED (failures=2): ['test_hooks_desarma_auto'] != [] e o lote de test_hooks sem o módulo novo. A correção é do autor (registrar o módulo no mapa); a lógica do hook e os mutantes estão corretos. Revalidação: forge-check parecer delta.

A catraca em hooks/parecer.py (protegido) espera o rótulo do Jarvis; não é achado.
