---
tipo: revisao-seguranca
contrato: 1
pedido: v047-teste-carga
branch: melhoria/v047-teste-carga
commit: 3da64e122b71a831b97c1f33987950f353a0e5e7
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v047-teste-carga (E5.6, parecer da E5.2)

branch: melhoria/v047-teste-carga · head revisado: 3da64e122b71a831b97c1f33987950f353a0e5e7

## Gatilhos
Toca teste de desempenho de hook de conformidade (a guarda de `gh` pendurado e o corpus dos hooks); sem produção, sem segredo, sem workflow. Gatilho: controle do Forge (R-SEGURANCA), pelo lado de não afrouxar guarda.

## Achados
- A1 (recomendado) tests/test_hooks.py:1035 · com carga 2x o teto do teste do gh pendurado vai a 18 s, acima do prazo de 10 s do hook; ainda pega o `sleep 30`, mas não um atraso de 10 a 18 s. Documentar que o teste prova "não espera o gh", não "sai antes do prazo".
- A2 (recomendado) tests/test_hooks.py:635 · a carga é a do hospedeiro (load average) e os núcleos vêm da afinidade; contêiner com quota de CPU pode ler carga alta e ficar sempre em 2x. Efeito limitado ao teto de 2x.
- A3 (recomendado) tests/test_medida_cpu.py:49 · o arquivo de mutantes tests/mutantes/v047-teste-carga.json ainda não existe no head (etapa do QA); conferir os mutantes da fórmula quando vier.

## Sondas

## Detalhe dos achados
Conferido por leitura e execução:
- Fórmula `min(2, max(1, carga/núcleos))` (test_hooks.py:631-640): sonda com carga nan, negativa e núcleos 0 dá 1.0; inf dá 2.0; carga 15 em 12 núcleos dá 1.59. A falha de `os.getloadavg` (OSError) dá 1.0, e há teste (test_medida_cpu.py:57). O teto é constante nomeada e o teste da fórmula prende 999 a 2x.
- Regressão real: o limite de CPU do corpus no máximo dobra (180 s por trabalhador); defeito de custo maior que o dobro falha mesmo sob carga. O teto de 2x é razoável; ninguém controla o limite pelo ambiente (sem variável de ambiente nem leitura de `FORGE_NPROC`).
- A carga é lida antes do lote (test_hooks_volta_corpus.py:122), sem inflar a própria medida.
- Um atacante que gere carga no runner só dobra o limite do teste, não desliga a guarda; nenhum controle de produção muda (diff sem hooks nem bin).
- Testes rodados: `test_medida_cpu` (8 OK) e o grupo do gh pendurado em `test_hooks.Hooks` (7 OK). Suíte inteira só no CI; sem PR ainda (a verificação do CI fica para o PR). Máquina com carga ~14 em 12 CPUs.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: só leitura e testes locais; gitleaks e demais varreduras não se aplicam (sem segredo nem dependência no diff).
