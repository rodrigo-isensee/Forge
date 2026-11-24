---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-sieg-g1-gravar
commit: d4960f8e7e8e428d5eea5726f380740be9f51081
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 E90.21 (SIEG-G1, G1.2a, `autorizacao gravar`), volta por delta

Gatilhos: autorização do dono (ADR 0018), controle do Forge (`R-SEGURANCA`).

## Resumo
Esta volta revalida o parecer aprovado fe0ef7d4 (head 3e653044) depois do merge da develop (d4960f8e, E90.19). A rodada anterior fica no git. Li o delta com `forge-check parecer delta`, no intervalo `3e653044..d4960f8e` e sem o que veio da develop. Dentro do domínio estão `bin/forge-check` e `bin/forge-testes`. Fora do domínio estão `tests/pesos-d4.json` e `docs/indice-forge.md`.

- **Resolução do conflito:** está correta e não muda a lógica. Comparei a contribuição da branch contra a develop (`fc488261..d4960f8e`) com a contribuição que ela trazia antes do merge (`1593627..3e653044`). Os arquivos são os mesmos e as linhas são idênticas, menos em três casos. `bin/forge-testes` muda só porque a develop acrescentou `test_trilha_forge_check` e `test_prepush_lote_pp1` à mesma linha. Ali a branch segue acrescentando só `test_autorizacao_gravar` em `FORGE_CHECK`. Os pareceres em `docs/` mudaram depois de 3e653044. `tests/pesos-d4.json` ganha uma entrada, e não há código nele.
- **Código do item:** `bin/forge_autorizacao.py`, `tests/test_autorizacao_gravar.py`, a ADR 0018 e os mutantes `v0479-sieg-g1-gravar*` são byte a byte iguais aos de 3e653044 (`git diff --quiet`). O regex `marcado` (`bin/forge_autorizacao.py:319`) continua idêntico ao da linha `:311` da 2d5efbe8.
- **O que veio da develop:** nada toca `forge_autorizacao.py`. Nada mexe nas funções que o `ctx` da autorização usa: `pedido_para_anotar`, `raiz_principal`, `sem_controle`, `escritor_do_resultado` e `modulo_do_bin`. Nada nos hooks consome `.forge/autorizacoes/`. A única mudança que encosta na palavra "autorização" é a de `bin/forge_quarentena.py:28` (`A-[0-9]+`, só dígito ASCII), e ela também aperta.
- **Achados anteriores:** A3, A4, A5, A6 e o afrouxamento do A2 do review continuam fechados, porque o código deles não mudou.

**Só aperta? Sim, por escrito.** No head d4960f8e o item só acrescenta recusa ou pendência em relação à base 2d5efbe8. O merge da develop não reabriu nada. As sondas S1 e S2 dão os mesmos estados do parecer fe0ef7d4. Pelo lado da segurança, o rótulo "só aperta" vale para este item no head d4960f8e.

**Explorável antes dos próximos cortes?** Não. Nada consome concessão ainda.

## Sondas
- S1 · leitura do head com "pode aplicar o rótulo no PR 5." e "pode mesclar a main 0.47.3." · espera: pendente nos dois · obtido: pendente-confirmacao (fora do vocabulário: 5; 0, 3, 47)
- S2 · leitura do head com "pr 5.1", "pr 5._" e "pr 5" · espera: pendente, pendente, ativa · obtido: pendente-confirmacao, pendente-confirmacao (alvos diferentes), ativa

## Riscos aceitos e ferramentas
Nenhum risco aceito. A suíte inteira não rodou aqui e não há CI do PR: o brief pede só os testes dos arquivos tocados, e o CI do PR será o portão. Rodei `tests/test_autorizacao_gravar.py` (32 OK) e `tests/test_autorizacao.py` (17 OK). Não rodei `gitleaks` nem `semgrep`: o delta é a resolução de um conflito em listas de testes, sem segredo nem dependência.
