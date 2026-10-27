---
tipo: revisao-seguranca
contrato: 1
pedido: prop-tempo-cpu
branch: melhoria/prop-tempo-cpu
commit: fe9dfb26221b1de4f68e8efd43899a663d1a52c0
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: prop-tempo-cpu

Diff revisado: `9620160fc7ce0c0a3e411cb0bc52d1d9716e6fa4...fe9dfb26221b1de4f68e8efd43899a663d1a52c0` (3 commits, 9 arquivos). Os 4 testes de desempenho da volta única passam a medir CPU (`MedidaDeCpu`: `time.process_time()` mais `RUSAGE_CHILDREN`) contra os mesmos limites. O limite do corpus passa a ser 60 s de CPU por trabalhador do lote.

## Gatilhos
- Controles do Forge: os testes que provam o desempenho dos hooks `conformidade` e `parecer`, e o mapa `FORGE_CHECK` de `bin/forge-testes`, que diz o que o pre-push roda.

## Achados
- A1 (recomendado) tests/apoio_volta_unica.py:44 · o teto somado (60 s x trabalhadores) perde sensibilidade a um texto caro sozinho: com 4 trabalhadores só reprova quando ele gasta mais de 147 s de CPU (antes, 37 s); medir a CPU por texto no driver e limitar o pior
- A2 (recomendado) tests/test_hooks_volta_corpus.py:114 · o relógio fica só no texto da mensagem; uma regressão que espera, sem gastar CPU (sono, trava, espera de rede), passa até o timeout de 900 s do lote; um teto largo de relógio (por exemplo 300 s) guardaria travamento sem voltar à instabilidade

## Detalhe dos achados
Os três pontos pedidos no brief:

1. **Hook lento de verdade.** Os filhos de `decidir_em_lote` e `decidir_na_guarda` rodam por `subprocess.run` dentro do bloco medido (`tests/apoio_volta_unica.py:397`, `:767`). Eles são esperados, então a CPU deles e a dos netos esperados (o git, o bash) entram em `RUSAGE_CHILDREN` (`:54`). Um hook que fica mais caro em CPU, ou que chama mais subprocessos, continua contando. Os mutantes M1 a M3 provam as três parcelas da medida. Quem guarda o prazo de 10 s do Claude Code (o ponto em que um hook lento vira liberação) continua no relógio: `test_t_orcamento_por_numero_de_palavras` (menos de 3 s por decisão, com o vigia de produção) e `test_t_vigia_de_prazo_recusa_com_marcador_e_libera_sem`. Mais o `limite_de_tempo(5)` do teste linear (`tests/test_hooks_volta_propriedades.py:149`). Medir CPU não abre caminho de desvio do controle. O que se perde é a sensibilidade a regressões de espera (A2), que só custam tempo ao usuário: o vigia de produção continua a recusar a chamada com marcador que passa do prazo.
2. **Limite por trabalhador com muitos trabalhadores.** `trabalhadores_do_lote` é limitado a 4 (`tests/apoio_volta_unica.py:39`), então o teto máximo é 240 s, e `test_limite_do_corpus_e_60_s_por_trabalhador` prova o caso de 64 núcleos. Medição local (sonda com `os.cpu_count` trocado, só o teste do corpus):
   - 4 trabalhadores: CPU 93,3 s, relógio 23,5 s, contra 240 s;
   - 2 trabalhadores: CPU 76,2 s, relógio 66,0 s, contra 120 s;
   - 1 trabalhador: CPU 70,1 s, relógio 70,0 s, contra 60 s.

   A folga relativa no total é a mesma de antes (com 4 trabalhadores, 23/60 no relógio e 93/240 em CPU, cerca de 2,6x), então o teto não fica mais frouxo para a carga uniforme. A perda está no texto isolado (A1): a soma esconde um trabalhador lento atrás dos rápidos. Isso é perda de sensibilidade de teste, e não desvio: o texto caro ainda passa pelo vigia de prazo em produção, que recusa com marcador. Correção mínima: o `DRIVER_DOS_HOOKS` devolve o `process_time` de cada decisão, como o `DRIVER_DA_GUARDA` já faz com o relógio (`:747`), e o teste limita o pior. Esforço P. Dono: `tech-lead`.
3. **Asserções de recusa.** Nenhuma saiu. Contagem de `self.assert*` antes e depois: corpus 59 e 59, lançador 113 e 113, propriedades 38 e 38, apoio 13 e 13. Só mudou o operando das 4 asserções de tempo. `assertEqual(executar_em_lote(casos), len(casos))`, `liberadas`, `erradas` e as contagens mínimas (`>= 10_000`) ficaram iguais. A linha nova em `FORGE_CHECK` (`bin/forge-testes:73`) só faz o pre-push rodar um módulo a mais; a contagem exata de `tests/test_testes_tocados.py:61` sobe para 26 e continua exata.

A2. Evidência: `tests/test_hooks_volta_corpus.py:114`, `tests/test_hooks_volta_lancador.py` (as duas propriedades). Caminho de ataque: nenhum direto, porque o prazo de produção tem testes próprios no relógio. Severidade: baixa. Correção mínima: `assertLess(medida.relogio, 300)` junto da asserção de CPU. Esforço P. Dono: `tech-lead`. O pedido aceitou deixar o relógio "só como teto de travamento", e hoje esse teto é o timeout do subprocesso (900 s no lote, 600 s na guarda).

Informativo, sem achado: a CPU de um neto órfão (filho de um hook morto pelo prazo de 10 s em `rodar(..., como_o_claude_code=True)`) não entra em `RUSAGE_CHILDREN`. O efeito é limitado pelo próprio prazo de 10 s e só vale para os textos de mais de 50 mil caracteres.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, os testes do item (`tests.test_medida_cpu` e `test_corpus_nos_dois_hooks`, verdes) e uma sonda local de CPU por número de trabalhadores. `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH (lacuna). O diff não toca workflow, dependência nem segredo.
