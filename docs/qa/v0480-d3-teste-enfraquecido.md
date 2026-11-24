---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-d3-teste-enfraquecido
commit: e7a71a8e2f87ef83fc7cb3708396ac05e87ba65d
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 E174.23 (D3, catraca recusa teste afrouxado; PR #867)

## Achados
- A1 (bloqueante) tests/test_catraca.py:1026 · o vermelho sai rc 2 (sem veredito): TestesNoCi.test_funcoes_do_i7_so_leem_pelo_git_e_pelo_ast dá erro na base por citar regra_testes_afrouxados, que só existe no head. R-QA: rc 2 volta ao autor; tratar o teste para o vermelho dar rc 0.

## Critério → teste → resultado
Pedido sem especificação de UX; a obrigação é a decisão do dono de 24/11 (D3) e R-CONFORMIDADE.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| D3: asserção a menos barra (soma compensada entre testes) | test_assercao_levada_a_outro_teste_barra_com_a_soma_igual | asserção movida de teste | prova (asserção), passou no head |
| D3: pulo, vazio, apagado barram | test_skip_no_teste_na_classe_ou_skiptest_barra, test_teste_sem_assercao_esvaziado_barra, test_teste_apagado_renomeado_afrouxado_ou_modulo_ilegivel_barra | módulo ilegível, classe pulada | prova (asserção), passou |
| D3: valor trocado só listado na 1ª entrega | test_valor_esperado_trocado_na_primeira_entrega_nao_barra_e_fica_listado, test_lista_dos_valores_sai_na_catraca_e_no_resumo_sem_mudar_o_codigo_de_saida | código de saída inalterado | prova (API ausente), passou |
| D3: valor trocado barra na volta | test_valor_trocado_na_volta_contra_a_versao_aprovada_barra, test_na_volta_vale_a_versao_aprovada_mais_nova_de_qualquer_revisor, test_parecer_que_nao_e_aprovacao_da_branch_nao_vale_como_volta | parecer reprovado, SHA fora da branch | prova, passou |
| D3: renomeado de mesmas asserções passa | test_teste_renomeado_com_as_mesmas_assercoes_passa, test_teste_novo_serve_de_renomeado_a_um_teste_so, test_teste_movido_de_modulo_passa_e_afrouxado_na_mudanca_barra | um novo serve a um só | passou |

## Cenários e resultado real
Vermelho (`bin/forge-testes --vermelho aabc476c5dbad3b3efced688e578bb5c71c5f722 --modulos tests.test_catraca`, 463 s):

    vermelho: base=aabc476c5dba head=e7a71a8e2f87 módulos=test_catraca (restrito por --modulos)
    revertidos à base: changelog.d/v0480-d3-teste-enfraquecido.md, tests/catraca.py
    contagem: não prova (passa na base)=387; prova (API ausente)=6; prova (asserção)=11; sem veredito=1
    sem veredito: tests.test_catraca.TestesNoCi.test_funcoes_do_i7_so_leem_pelo_git_e_pelo_ast · H=ok · B=erro
    rc=2

Os 17 testes de TestesAfrouxados falham na base e passam no head; o único sem veredito é o A1.

Mutação: `bin/forge-mutante --processos 4` nas 7 specs (46 mutantes D3A a D3G): 46 morreram, nenhum sobrevivente, rc=0. `forge-mutante --cobertura --base aabc476c...` sem condição descoberta. Alguns morreram por erro do teste declarado (D3E5, D3E8, D3F1, D3F7), aceito pela regra do controle verde.

CI: a suíte inteira roda no CI do PR; o review já a cita e reprovou por falso positivo na volta (A1 dele), fora do domínio do QA e não refeito aqui.
