---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-testes-prazo
commit: 318721dbbb87ab4db3db719d6f0207e8def10423
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478-testes-prazo

Revalidação (E12.9) por delta: `forge-check parecer delta` de `bf3ce6af..318721db`. No domínio: `.github/workflows/ci.yml` e `tests/test_hooks.py`; o critério movido para `tests/prova_de_carga.py` foi lido junto, por ser a decisão do teste de controle. Já lido na rodada de `bf3ce6af` (no git): `bin/forge_sempre_atual.py`, `tests/sem_claude_ancestral.py`, a 1ª forma do teste do prazo. Classe C, como antes.

## Gatilhos
Gatilhos: nenhum item da lista da R-SEGURANCA; parecer pela classe C (teste de controle do hook `parecer` e passo novo do CI).

## Resumo
- A1 (recomendado, rodada anterior): **resolvido**. `.github/workflows/ci.yml:93-98`, `:211-216`, `:399-404` e `:476-481` contam as linhas `PRAZO-CARGA fixture=` do `suite.log` no resumo, nas quatro matrizes da suíte, sem reprovar. Passo sem `${{ }}` no `run` (nenhuma injeção de expressão), sem permissão nova, sem segredo; `grep` sem achado cai em `0` e o `|| true` segura o `pipefail`. Além do aviso, o critério fechou a causa do A1: a espera bloqueante (E/S, sono) agora reprova pelo aproveitamento.
- Critério novo (`tests/prova_de_carga.py:61-70`): só acrescenta condições ao anterior (referência com parcela ≤ 0,5 e aproveitamento da CPU ≥ 0,5), então a direção segue fechada: a função só converte uma recusa em passagem, nunca uma liberação em recusa aceita, e só é chamada para os fixtures que esperam liberar (`tests/test_hooks.py:1180-1186`). Liberação indevida não passa.
- Resíduo examinado: regressão de CPU do hook em carga passa como carga só se `cpu + sono ≤ prazo − 1 s` (`tests/prova_de_carga.py:68`); a mesma regressão, com a máquina livre, decide dentro do prazo e libera, então não esconde recusa de produção. Medida falha (referência morta, `parede ≤ 0`) vira `None` e reprova (`:47-52`, `:66`).
- Testes do critério rodados no head 318721db: `test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo_com_disputa_provada`, `test_referencia_da_cpu_mede_a_parcela_do_relogio`, `test_liberar_ou_provar_a_carga_aceita_so_a_recusa_explicada_pela_carga` e `test_liberar_ou_provar_a_carga_recusa_a_sonda_s1` (a sonda S1 do review, real): 4 OK em 12,3 s.

## Achados

## Sondas

## Detalhe dos achados
Sem achado novo. Observação sem caminho de ataque: o processo de referência gasta CPU durante cada merge que libera; numa máquina de um núcleo livre a parcela fica perto de 0,5 e a recusa eventual reprova (falha fechada, só estabilidade do teste, dono `qa-engineer` se aparecer no resumo do CI).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira: não rodada (brief); nenhuma execução de CI no head 318721db até este parecer (sem PR), o CI fica como portão próprio da classe C. Ferramentas: o varredor de segredos e os linters de workflow não estão no PATH (lacuna); o passo novo foi revisto à mão.
