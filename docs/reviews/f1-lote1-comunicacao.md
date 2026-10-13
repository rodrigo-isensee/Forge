---
tipo: review
contrato: 1
pedido: f1-lote1-comunicacao
branch: melhoria/f1-lote1-comunicacao
commit: 1bee730
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: lote 1 da fonte F1 (comunicação do Jarvis)

Escopo: complemento em `docs/regras/R-DECISAO.md` (teste de bloqueante, escada, base declarada, decisão só vale gravada), passo 1, relatório e comunicação em `agents/jarvis.md`, linha de gravação imediata em `docs/retomada-de-sessao.md`, decisões do dono no estudo, invariantes em `tests/config.json` e linha em `[Não publicado]`.

Conferido: 281 testes verdes; `scripts/validar-plugin.sh` passa. Sem mudança em hooks, catraca ou `.github/`; invariantes só acrescentam proteção, então não pedem rótulo. `jarvis.md` segue abaixo do limite de linhas. Texto sem termos de projeto nem nome da fonte (`R-NEUTRO`) e sem custo (`R-CUSTO`). O texto da regra fica só em `R-DECISAO`; o Jarvis cita o ID (ADR 0002).

Parecer de autor, feito pelo mesmo agente que escreveu a mudança; o review independente fica a cargo do `tech-lead` no PR.
