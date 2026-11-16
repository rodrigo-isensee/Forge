---
tipo: qa
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-espera-longa
commit: af4bd16fe62731013d82e9e59f0ebcd64e6ea289
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: mp1311-espera-longa

Item 8 do pedido (E2.4): a skill `esperar-estado` ganha a regra 6 (CI longo na sessão principal espera em segundo plano, sem teto de 170 s) e o segundo laço do PR, sem teto. Sem PR aberto: não há check-run `bateria` a citar; rodei só o módulo afetado, o vermelho e os mutantes.

## Achados

## Critério → teste → resultado
O pedido não tem especificação de UX; as obrigações vêm do item 8 (ESPERAR-ESTADO-180S).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Laço sem teto espera além de 5 leituras e sai no estado terminal | `test_laco_longo_espera_alem_de_5_leituras_e_sai_no_estado` (12 OPEN + MERGED, 13 leituras, `fim=MERGED`) | acima do teto antigo de 5 voltas | passou |
| Regra 6 manda segundo plano (`run_in_background`) só na sessão principal e ressalva o subagente | `test_espera_longa_vai_para_segundo_plano_na_sessao_principal` | n/a | passou |
| Laço com teto da regra 2 segue único e inalterado | `laco()` (filtro `seq 1`) + testes de `LacoDoPr` existentes | teto de 170 s | passou |

## Cenários e resultado real
- Módulo afetado: `python3 -m unittest tests.test_esperar_estado` no head: 15 testes, OK.
- Vermelho antes do verde: `forge-testes --vermelho efe7c9e8` abriu com `vermelho: base=efe7c9e83ec2 head=af4bd16fe627`, reverteu `changelog.d/mp1311-espera-longa.md` e `skills/esperar-estado/SKILL.md`, manteve `tests/test_esperar_estado.py`; a saída foi cortada pelo `tail` e não trouxe a linha de veredito, então confirmei à mão: testes do head com a SKILL da base dão 2 falhas (os dois testes novos) em 15.
- Mutação à mão no laço e na regra (cópia limpa de `git archive`): `while :` trocado por `for ... seq 1 5` mata 8 testes; `-eq 8` trocado por `-eq 0` mata 1; regra 6 sem `run_in_background` mata 1; regra 6 sem a palavra `subagente` mata 1; laço sem a saída por estado não-OPEN dá erro (loop barrado pelo timeout). 5/5 mortos. Não é pedido de controle (só skill e teste), sem `forge-mutante`.
- Carga da máquina ~15 em 12 CPUs: suíte inteira não rodada local; fica ao CI do PR.
- Conferência do diff: 3 arquivos (skill, teste, fragmento de changelog), sem escopo além do item 8.
