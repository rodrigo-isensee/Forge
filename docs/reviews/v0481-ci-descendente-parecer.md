---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-descendente-parecer
commit: aa26249f6f12bb20aa2b8d3023bd820293eaad48
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 E8.15 (G3.7, delta 2364a43b..aa26249f do #895)

## Achados
- A1 (bloqueante) skills/engineering-practices/SKILL.md:54 · `test_metricas_texto` cai: engineering-practices 7113 caracteres, teto 6982 (+131); qa-testing 11774, teto 11761 (+13) em `tests/fixtures/metricas-texto.json`. Suíte parte 1/5 vermelha (py3.12 e 3.14) no aa26249f; base eeb81062 passa. Encurte mais.

## Sondas
- S1 · `python3 -m unittest tests.test_metricas_texto` no aa26249f e no eeb81062 · espera: OK nos dois · obtido: FAILED no aa26249f (2 estouros acima), OK no eeb81062

## Parecer
Reprovado por um bloqueante (A1). O A1 anterior (branco inicial do 1º caminho) está corrigido; o encurtamento das skills ficou dentro do teto do agente, mas não do teto por arquivo.

- **Delta lido:** `forge-check parecer delta` deu `revalida: sim` (este parecer barrou). Li `git diff 2364a43b..aa26249f`: `so_pareceres_ate` em `bin/forge-check`, as duas skills, as duas specs de mutante e `LeOCiVia`.
- **A1 anterior, corrigido:** `so_pareceres_ate` lê o diff com `bruto=True` e `nomes_z`, como o resto do arquivo, e passa `--ignore-submodules=none` (o A2 recomendado do QA). `test_branco_no_inicio_do_caminho_nao_vale` recusa espaço, tab e quebra de linha iniciais (` docs/reviews/x.py`, `\tdocs/security/x.py`, `\ndocs/qa/x.py`), e `test_gitlink_fora_das_pastas_nao_some` recusa o gitlink com `diff.ignoreSubmodules=all`. O falso do git em `test_erro_do_git_diff_falha_fechado` devolve bytes, como o git real com `bruto=True`.
- **Skills:** nenhum trecho de `invariantes` (`tests/config.json`) presente nas duas skills da base sumiu (59 conferidos), e nenhum ID de regra saiu. O que saiu do QA ("a suíte inteira roda no CI do PR" e "a ele e à segurança") segue em `agents/qa-engineer.md:15`. `test_orcamento_instrucao` passa. O que falha é `test_metricas_texto` (A1), uma métrica por arquivo diferente do teto por agente; o QA e a segurança não a citaram, e ela já é a mesma família do A2 da segurança.
- **Mutantes:** `bin/forge-mutante --processos 1` nas duas specs deu M1 a M11 mortos (M9 por erro, que é o ramo que ele guarda: sem `commit:`, não quebra). `--cobertura --base 2364a43b` deu a linha 2199 coberta (M4, M5); M3, M10 e M11 cobrem a 2198. `--conferir --base eeb81062`: trechos no lugar. `--conferir --todas` no head deu a mesma saída da base, byte a byte (26 linhas, specs antigas de outros pedidos).
- **Testes:** `tests.test_forge_check_pr` passou, 71 testes OK; `LeOCiVia` com `test_orcamento_instrucao`, 18 OK.
- **CI do #895 no aa26249f:** `suíte (python 3.12, parte 1/5)` e `suíte (python 3.14, parte 1/5)` vermelhas pelo A1. `bateria` e `bateria (python 3.14)` também estão vermelhas, e `bateria (pareceres)` e `catraca` estão vermelhas por construção. Sem CI verde, a linha `- ci:` não se aplica.
- **Na volta:** encurte as frases G3.7 das duas skills até `test_metricas_texto` e `test_orcamento_instrucao` passarem juntos, sem mexer em teto. Rode os dois antes do push.
