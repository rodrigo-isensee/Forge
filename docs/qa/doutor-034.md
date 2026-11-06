---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/doutor-034
commit: fab2bfa93ae3b717f9775547638a51f9e6c10e2a
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: doutor-034 (AVISO-VERSAO-UMA-VEZ)

Testado: 5bd8bdc (head do autor) mais o commit de teste do QA 606b86e (só `tests/test_qa_doutor_034.py`; código de produção intocado). Review e segurança aprovados em 5bd8bdc, não repetidos aqui. Escopo: o módulo da branch (D-5), não a suíte inteira.

## Achados

## Critério → teste → resultado
| Critério (cartão) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A mesma versão nova avisa uma vez só | `test_tres_dias_seguidos_avisa_so_no_primeiro_e_o_atraso_segue_provado` (QA, hook real, 3 dias por FORGE_HOJE); `test_a_mesma_versao_nova_nao_avisa_de_novo_no_dia_seguinte` (autor) | dia 2 e dia 3 | passou |
| Versão ainda mais nova volta a avisar (uma vez) | `test_versao_ainda_mais_nova_avisa_e_depois_cala` (QA); `test_versao_ainda_mais_nova_avisa_no_dia_seguinte` (autor) | `ultima` muda; depois do aviso, cala de novo | passou |
| Mudar a versão em uso com a mesma `ultima` volta a avisar | `test_versao_em_uso_diferente_com_a_mesma_ultima_avisa_no_dia_seguinte` (autor) | `atual` muda | passou |
| Falha (OSError) do relógio não come o aviso de versão | `test_falha_do_relogio_no_stop_nao_come_o_aviso_de_versao` (autor, subprocesso) | OSError no relógio | passou |
| O cache continua provando o atraso ao forge-check | `test_o_forge_check_le_o_atraso_do_cache_mesmo_calado` (QA: `comparar_com_o_cache_do_projeto` real sobre o cache gravado pelo hook, dia 2 calado) e a asserção `defasado/atual/ultima` do teste de 3 dias | cache calado ainda `atrasada` | passou |
| Borda: consulta sem rede no meio | `test_sem_rede_no_dia_do_meio_nao_perde_o_silencio_nem_o_aviso_futuro` (QA, remoto git removido de verdade) | falha preserva `avisado`+par; versão mais nova depois avisa | passou |
| Borda: cache adulterado | `test_cache_adulterado_nao_derruba_o_hook_nem_cala_o_aviso` (QA: `avisado` "true" e 1, JSON inválido, lista) | só `True` literal silencia; hook sai 0 | passou |

## Cenários e resultado real
- Os testes do QA rodam o `hooks/doutor.py` como subprocesso, com remoto git local (`FORGE_REPO_URL`), HOME e raiz descartáveis, e viram o dia por `FORGE_HOJE` sem editar o cache (os do autor editam a data do cache).
- Vermelho antes do verde (teste original 606b86e): com `hooks/doutor.py` da base b45e40a caem 3 de 5 e no head passam os 5. Revalidado no teste enxugado em "Revalidação".
- Observação do teste de sem-rede: após a falha, a repetição só ocorre depois de `ESPERA_APOS_FALHA`; o teste zera `falhou_em` no cache para simular a passagem do tempo (o comportamento de espera já é do cartão anterior e está coberto pelos testes do autor).
- `python3 -I -m unittest discover -s tests -p test_doutor.py` em 5bd8bdc: 75 testes, OK (58 s, `test_abrir_em_menos_de_cem_ms_em_media` passou). Módulo novo `test_qa_doutor_034.py`: 5 testes, OK.
- `bin/forge-mutante tests/mutantes/doutor-034.json` (rev=606b86e500fa): M1, M2, M3 morreram em `hooks/doutor.py:105`; M4 morreu em `hooks/doutor.py:188`; rc 0.
- Conferência da spec contra o diff: `bin/forge-mutante --cobertura --base b45e40a` lista `coberta · hooks/doutor.py:105 · M1, M2, M3`; o `except OSError` (linha 188) tem o M4. Linha de guarda sem mutante: nenhuma. Condição `defasada and` da linha 105: sem efeito observável (sem versão nova o texto é vazio e nada avisa), não vira achado.
- Bugs abertos: nenhum.

## Revalidação
O review enxugou meu teste para o teto M14 em fab2bfa93ae3b717f9775547638a51f9e6c10e2a (`tests/test_qa_doutor_034.py`, de 106 para 85 linhas). Conferi o delta 606b86e..fab2bfa: os 5 testes mantêm o nome e as asserções; o cache adulterado virou laço sobre os mesmos 4 casos (`avisado` "true", `avisado` 1, JSON inválido, lista) nos mesmos dias; o teste do forge-check ganhou a asserção de aviso no dia 1 e silêncio no dia 2. A cobertura é a mesma, mais essa asserção. A cobertura do parecer acima vale para o teste enxugado.
- `python3 -I -m unittest discover -s tests -p test_qa_doutor_034.py` no HEAD: 5 testes, OK.
- `python3 -I -m unittest discover -s tests -p test_doutor.py` no HEAD: 75 testes, OK (58 s).
- Vermelho: com `hooks/doutor.py` de b45e40a, caem 4 de 5 (`tres_dias`, `ainda_mais_nova`, `sem_rede`, `forge_check_le_o_atraso`, este agora pela asserção nova do dia 2). Só `cache_adulterado` passa na base, por ser guarda contra silenciar demais. Árvore restaurada ao HEAD.
- Mutantes: sem mudança em `hooks/` desde a rodada anterior (M1 a M4 mortos, rc 0 em 5bd8bdc/606b86e).
