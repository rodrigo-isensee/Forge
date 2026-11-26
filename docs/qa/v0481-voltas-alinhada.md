---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-voltas-alinhada
commit: 46000ed50e0089fb2818c440c2c5355a6d38dd10
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 (E14.44, E14.59), #902: teto de voltas alinhado (R-QA)

Classe C, sem especificação de UX. Obrigações: `R-QA` (teto, a volta restrita, contagem sem `Volta-de:`), ordem do dono 25/11 07:31 (3 voltas, a 3ª só corrige o apontado) e a de 17:07 (resolver, não cortar; sem última volta; da 4ª, tech-lead e revisor juntos). Diff lido contra o merge-base `34ab6714`.

## Achados
- A1 (bloqueante) bin/forge-check:4507 · Teto e texto seguem a ordem de 07:31, não a de 17:07 (resolver, sem última volta): `recusa_da_volta` recusa a 4ª e oferece "cortar o item"; R-QA:17 e a skill (autor-ate-o-merge.md:10) fixam 3 voltas. Ferramenta e texto devem sair do teto e da opção de corte.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| 3 voltas por item sem o dono; a 4ª recusada, com decisão canônica autoriza uma a mais | `BriefDeVolta.test_volta_quatro_so_com_decisao_do_dono_que_cita_a_branch`, `test_sem_branch_nenhuma_decisao_autoriza`, `test_so_a_forma_canonica_autoriza_e_uma_linha_vale_uma_volta` | volta 3 cabe, volta 4 recusa; sem branch o teto é 1; mesma linha em duas fontes vale uma | passou (mas fixa o teto que a ordem de 17:07 substituiu: A1) |
| 3ª volta traz a restrição no brief e a conferência a cobra | `test_terceira_volta_traz_a_restricao_e_a_conferencia_a_cobra` | volta 2 sem a restrição; brief da 3ª sem a linha reprova | passou |
| 3ª volta: teste removido ou enfraquecido reprova a entrega (falha fechada sem catraca ou com git falho) | `test_terceira_volta_recusa_teste_removido_ou_enfraquecido`, `test_volta_alinhada.TerceiraVoltaNaConferencia` (3 testes) | 2 para 1 testes, asserções que caem, volta 2 isenta, `catraca` None, sha inválido | passou |
| Brief de código em branch com parecer reprovado sem `Volta-de:` é volta e conta | `test_brief_de_codigo_na_branch_com_parecer_reprovado_e_volta` | outra branch, parecer aprovado ou `revalidar`, sem `origin/<branch>`, `Tipo: review` | passou (contorno por brief sem `Tipo:` está no A2 da segurança) |
| Mapa do `bin/forge-testes` e pesos incluem `test_volta_alinhada` (E14.59) | diff de `bin/forge-testes:157` e `tests/pesos-d4.json` | módulo novo roda no plano dirigido (rodou: 51 testes no processo 2) | passou |
| Texto alinhado em R-QA, `agents/jarvis.md` e skill; fragmento do changelog | leitura do diff | 3 voltas nos três lugares | consistente entre si, mas diverge da ordem de 17:07 (A1) |

## Cenários e resultado real
- Módulos tocados, na cópia `/root/.forge-contrib/wt/v0481-voltas-alinhada-qa` no head `46000ed5`: `bin/forge-testes tests/test_volta_alinhada.py tests/test_volta_por_delta.py tests/test_voltas.py` -> `Ran 168 tests ... OK (skipped=1)` (o pulado é de `test_voltas`, da base).
- Vermelho antes do verde: `bin/forge-testes --vermelho 34ab6714 --modulos test_volta_alinhada,test_volta_por_delta` -> rc 0, `vermelho: base=34ab6714cbc1 head=46000ed50e00`; `contagem: não prova (passa na base)=111; prova (API ausente)=1; prova (asserção)=8`. Provam: `test_terceira_volta_que_remove_teste_nao_cumpre`, `test_brief_de_codigo_na_branch_com_parecer_reprovado_e_volta`, `test_conferencia_recusa_a_numeracao_contornada`, `test_conferencia_sem_cobradas_le_as_decisoes_do_pedido`, `test_sem_branch_nenhuma_decisao_autoriza`, `test_so_a_forma_canonica_autoriza_e_uma_linha_vale_uma_volta`, `test_terceira_volta_recusa_teste_removido_ou_enfraquecido` (API ausente), `test_terceira_volta_traz_a_restricao_e_a_conferencia_a_cobra`, `test_volta_quatro_so_com_decisao_do_dono_que_cita_a_branch`.
- Mutantes: `bin/forge-mutante tests/mutantes/v0481-voltas-alinhada.json tests/mutantes/v0481-voltas-alinhada-2.json --processos 2` -> rc 0, VA-M1 a VA-M12 `morreu` (VA-M7 por erro do teste sob o mutante, controle verde: mata, mas o review pediu asserção, A3 dele). `bin/forge-mutante --cobertura --base 34ab6714`: as 8 condições do diff em `bin/forge-check` `coberta`, nenhuma `não coberta` em código (só `tests/pesos-d4.json`, dado); as duas specs `v0480-g1-1-uma-volta*.json` aparecem `spec editada` (só o teste e a constante renomeados; o `de` dos mutantes segue casando com o código).
- Ordem de 17:07 (conferência pedida pelo brief): o dono mandou resolver sem cortar, sem "última volta", e da 4ª volta tech-lead e revisor juntos. O diff mantém `recusa_da_volta` com teto e opção de cortar (`bin/forge-check:4507`), `R-QA.md:17` "Até 3 voltas ... sem o dono" e o texto da skill: A1. O código novo e os testes ainda valem para a restrição da 3ª volta (ordem de 07:31 não revogada pela de 17:07).
- Leitura cruzada: o A2 do parecer de segurança (contagem sem `Volta-de:` só vale com `Tipo: codigo`) é de domínio dela; não o repeti.
- CI (`gh pr checks 902`, head `46000ed5`): suítes 3.12 e 3.14 (partes 1 a 5), tetos de pulados, `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)` e instalação verdes. Vermelhos: `bateria (pareceres)` (espera os pareceres) e `bateria`. `catraca` falha por duas causas, lidas no log do job: (1) `R-CONFORMIDADE: o teste tests/test_volta_por_delta.py::BriefDeVolta.test_volta_dois_so_com_decisao_do_dono_que_cita_a_branch foi apagado ou renomeado` (renomeado para `test_volta_quatro_...`); (2) `mudança em bin/forge-check`. As duas pedem o rótulo `afrouxa-regra` do dono, aplicado depois do último push.
- ci: 46000ed50e0089fb2818c440c2c5355a6d38dd10 verde
- D2 local do autor (falhas só em `test_oraculo_sempre_atual` e `test_fechar.test_shellcheck_fechar_passa_limpo`): não rodei; vale G3 (suítes verdes no CI).
