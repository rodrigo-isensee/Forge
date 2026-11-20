---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-m1-medida
commit: c5c0a232123312a20f5de27be913d57741377a55
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0478 (E57.22, PR-VERDE M1 no head c5c0a232)

Escopo lido, primeira passada completa: `git diff 5ccac0bf..c5c0a232` (`bin/forge-placar` +120, `tests/evals/test_placar.py` +147, 5 specs de mutante, fragmento do changelog, pareceres de review e QA). Suíte não rodada localmente (brief: sem suíte local); a suíte inteira é do CI do PR. Rodei só sondas na ferramenta nova, sem rede.

## Gatilhos
Gatilhos: nenhum (sem `.github/`, `hooks/`, `docs/regras/`, `tests/catraca.py`, `tests/config.json`, segredo, dependência nem endpoint; o subcomando só lê dois arquivos JSON locais gerados fora).

## Achados
- A1 (recomendado) bin/forge-placar:863 · o filtro do dependabot é por substring: `"dependabot" in str(autor).lower()` tira da medida o PR de qualquer login que contenha a palavra (provado: `not-dependabot-fan` com CI vermelho some da taxa). Comparar exato com `app/dependabot` e `dependabot[bot]`.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `bin/forge-placar:863`; sonda local: PR com autor `{"login":"not-dependabot-fan"}`, CI `failure` e Catraca `success` no 1.º head, `--ate 2026-11-20 --dias 7` → `total: nenhum PR aberto na janela` (rc 0); o mesmo PR com autor `fulano` → `verde na 1.ª 0.00% (0/1)`. Caminho: quem abre PR com login que contenha `dependabot` tira o vermelho dele da taxa e infla a medida que o critério de reversão do PR-VERDE lê; ganho pequeno, mas a falha é aberta e mais larga que a D7 ("PR do dependabot, fora"). Severidade: baixa. Correção mínima: `autor in ("app/dependabot", "dependabot[bot]")` e um caso no teste `test_dependabot_e_pr_fora_da_janela_ficam_fora` com login que contém a palavra e continua contando. Esforço: P. Dono: tech-lead (autor do item).

Conferido sem achado:
- Entrada: `lista_do_gh` (`bin/forge-placar:795-813`) falha fechada em `lacuna` rc 2 para não JSON, não lista, item não objeto, campo faltando, `jobs` não lista, data inválida e aninhamento acima do teto (`fundo_demais`, linear). Sondei tipos trocados que passam a validação: `attempt` como texto vira vermelho (nunca verde), `workflowName` como lista vira `lacuna`, `author` nulo conta normalmente; nenhum derruba com exceção.
- A volta do A1 do review (`primeira_execucao`, `:828-834`): só a cancelada do mesmo `headSha` dá lugar à seguinte; uma seguinte com rerun (`attempt` > 1) sai vermelha, não verde. Não abre caminho para contar verde a mais.
- Sem rede, sem subprocesso, sem escrita: só `read_text` dos caminhos passados por argumento (`R-CUSTO` respeitado). A saída `--json` escapa caractere de controle; a de texto imprime nome de job vindo da fonte, que hoje o `gh run list` documentado nem traz (A2 do review), sem caminho realista de abuso.
- Testes rodam com `-I` e ambiente limpo (parecer de QA); sem segredo nos arquivos do diff (leitura manual dos fixtures e specs).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura do diff e sondas locais com o próprio `bin/forge-placar` (`python3 -I`); `gitleaks`, `semgrep` e `zizmor` ausentes do PATH (lacuna registrada; o diff não toca workflow).

## Parecer
Aprovado no head c5c0a232. O A1 é recomendado de segurança: volta ao autor e é corrigido antes do merge (`R-REVIEW`).
