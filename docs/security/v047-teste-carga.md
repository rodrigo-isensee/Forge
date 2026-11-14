---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-teste-carga
commit: 171232b97fb8f5a84b426b2fabc5f2a5f1ef5170
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v047-teste-carga (E5.6, parecer da E5.2)

branch: melhoria/v047-teste-carga · head revisado: 171232b97fb8f5a84b426b2fabc5f2a5f1ef5170 (revalidação por delta desde 3da64e12, E5.16)

## Gatilhos
Toca teste de desempenho de hook de conformidade (a guarda de `gh` pendurado e o corpus dos hooks); sem produção, sem segredo, sem workflow. Gatilho: controle do Forge (R-SEGURANCA), pelo lado de não afrouxar guarda.

## Achados
- A1 (recomendado) tests/test_hooks.py:1035 · com carga 2x o teto do teste do gh pendurado vai a 18 s, acima do prazo de 10 s do hook; ainda pega o `sleep 30`, mas não um atraso de 10 a 18 s. Documentar que o teste prova "não espera o gh", não "sai antes do prazo".
- A2 (recomendado) tests/test_hooks.py:635 · a carga é a do hospedeiro (load average) e os núcleos vêm da afinidade; contêiner com quota de CPU pode ler carga alta e ficar sempre em 2x. Efeito limitado ao teto de 2x.
- A3 (recomendado) tests/mutantes/v047-teste-carga.json:1 · atendido na E5.16: o arquivo existe e os 14 mutantes morrem; sem pendência.

## Sondas

## Detalhe dos achados
Conferido por leitura e execução:
- Fórmula `min(2, max(1, carga/núcleos))` (test_hooks.py:631-640): sonda com carga nan, negativa e núcleos 0 dá 1.0; inf dá 2.0; carga 15 em 12 núcleos dá 1.59. A falha de `os.getloadavg` (OSError) dá 1.0, e há teste (test_medida_cpu.py:57). O teto é constante nomeada e o teste da fórmula prende 999 a 2x.
- Regressão real: o limite de CPU do corpus no máximo dobra (180 s por trabalhador); defeito de custo maior que o dobro falha mesmo sob carga. O teto de 2x é razoável; ninguém controla o limite pelo ambiente (sem variável de ambiente nem leitura de `FORGE_NPROC`).
- A carga é lida antes do lote (test_hooks_volta_corpus.py:122), sem inflar a própria medida.
- Um atacante que gere carga no runner só dobra o limite do teste, não desliga a guarda; nenhum controle de produção muda (diff sem hooks nem bin).
- Testes rodados: `test_medida_cpu` (8 OK) e o grupo do gh pendurado em `test_hooks.Hooks` (7 OK). Suíte inteira só no CI; sem PR ainda (a verificação do CI fica para o PR). Máquina com carga ~14 em 12 CPUs.

## Revalidação por delta (E5.16, até 171232b9)
- Delta no domínio: só `tests/test_hooks.py` (a fórmula saiu de lá e entra por import no fim do arquivo); o resto é teste fora do domínio. A fórmula é a mesma, movida a `tests/apoio_volta_unica.py` (texto idêntico: piso 1, teto 2, OSError dá 1.0, afinidade sem `FORGE_NPROC`). Nenhum hook, bin nem workflow tocado.
- Import circular conferido nas duas ordens (`apoio_volta_unica` primeiro e `test_hooks` primeiro): ambos importam.
- `forge-mutante tests/mutantes/v047-teste-carga.json`: M1 a M14 morreram (M10 com a observação de erro do teste sob o mutante, que passa sem ele; o mutante morre do mesmo jeito). Conferi à mão M13 e M14: o teste declarado falha sob o mutante.
- Testes rodados: `test_medida_cpu` (12 OK) e `PoolDosFixtures` (3 OK). Suíte inteira só no CI; sem PR (conferir no PR). Carga ~7,6 em 12 CPUs.
- A1 e A2 seguem recomendados (sem promoção); nenhum achado novo.

## Revalidação por delta (E5.19, até o head da branch)
- `forge-check parecer delta` (171232b9..80d80a7f): nenhum arquivo do domínio mudou; os três arquivos novos são pareceres de QA, review e segurança. Os arquivos citados no brief (`tests/apoio_volta_unica.py`, `tests/test_hooks.py`) já estão cobertos pelo delta da E5.16 (171232b9), sem mudança depois.
- Campo `pedido:` corrigido para `v047`. A1 e A2 seguem recomendados; nenhum achado novo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: só leitura e testes locais; gitleaks e demais varreduras não se aplicam (sem segredo nem dependência no diff).
