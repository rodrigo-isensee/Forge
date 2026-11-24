---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-2-delta
commit: 55a57bdef7c790c1b35971abb8c1d91a6c89c3a3
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E140.15), revalidação por delta do #812 no head 55a57bde

Volta E140.12: leituras em lote em `parecer_anterior`, saída antecipada em `fora_do_delta`, mutantes FD23 a FD29 e o texto G1.2 encurtado em `R-REVIEW` e `R-SEGURANCA`. A rodada anterior (head 41820406, aprovada) fica no git.

## Achados
- A1 (recomendado) bin/forge-check:4188 · herdado (A7 da g1-2-3): a repetição é reconhecida só por (id, arquivo). Estado: aberto, vira cartão.
- A2 (bloqueante) bin/forge-check:4182 · a saída antecipada deixa o FD10 (guarda :4192) sobrevivente: o teste declarado, só com recomendado, sai antes do laço. A guarda segue viva (sonda S1). Correção: pôr o bloqueante repetido A1 src/a.py:5 no teste de :101.

## Sondas
- S1 · rodada 2 com `- A1 (bloqueante) src/a.py:5` e `- A2 (recomendado) src/a.py:2`, `fora_do_delta` com e sem a troca do FD10 · espera: 0 recusas no original, 1 no mutante · obtido: original 0, mutante 1

## Revalidação (head 55a57bde)
**Delta lido:** `forge-check parecer delta docs/reviews/v0480-g1-2-delta.md`, intervalo 41820406..55a57bde. Saída: `revalida: sim (desatualizado: agents/qa-engineer.md mudou depois do parecer)`. Os commits da branch no intervalo são 5c62c8ce, 05f5c9f9, 07b89dc8, fb9f4347 e 55a57bde; o resto veio dos merges da develop (806e59a1, c447f35b, b3998275, 17a44ed4).

**Patch da branch sobre a develop (701f5bfd..55a57bde) comparado com o revisado (216413c9..41820406), arquivo por arquivo:**
- Iguais: `agents/tech-lead.md`, `bin/forge-testes`, `tests/pesos-d4.json`, `rigor-por-classe.md`, `tests/test_testes_tocados.py` e `v047-docs-pareceres-2.json`.
- `agents/qa-engineer.md`: as mesmas trocas da branch, agora sobre o texto que a develop já tinha encurtado. Só muda o contexto do merge.
- `agents/security-engineer.md`: "Em entrega de analisador ou hook" passa a "Em analisador ou hook" (fb9f4347). O alcance é o mesmo.
- `bin/forge-check`, os mutantes e o teste: a volta E140.12, lida abaixo.

**A decisão da checagem não muda:**
- `versoes_em_lote` devolve o mesmo texto que o `git show <ref>:<rel>` em modo texto: troca `\r\n` e `\r` por `\n` e faz o `strip`. A versão apagada (` missing`), o lote que falha e a resposta truncada ou fora do protocolo dão `None`, que vira `{}` como o show que falhava. Os mesmos 30 commits do `log`, na mesma ordem.
- A única diferença está no UTF-8 inválido: o show em modo texto estourava `UnicodeDecodeError`, e o lote troca o byte. Não muda nenhum caso válido.
- A saída antecipada em `fora_do_delta` (:4182) devolve `[]` sem bloqueante. É o mesmo resultado de antes, já que o laço pulava todo achado não bloqueante. O lado ruim está no A2: ela tira do alcance o teste que matava o FD10.
- As 21 recusas de `Revalidacao` seguem verdes.

**O texto encurtado não afrouxa:**
- `R-REVIEW.md:17`: "O bloqueante novo fora dele" passa a "Bloqueante novo fora dele". O sujeito, o alcance e o destino (cartão) são os mesmos.
- `R-SEGURANCA.md:17`: "a nova vira cartão e o bloqueante pede `explorável: S<n>`" passa a "a nova vira cartão; o bloqueante pede `explorável: S<n>`". Continuam as duas condições.
- Nenhum trecho de `invariantes` (`tests/config.json`) cita essas frases.

**Tamanho (H1):** 92 linhas a mais em `bin/forge-check` sobre a develop, com as docstrings, e 1 em `bin/forge-testes`. Fica dentro do teto, com um comportamento só.

**Verificadores no head 55a57bde:**
- `python3 -m unittest tests.test_parecer_fora_do_delta`: 29 testes, OK. `forge-testes --listar` pede a suíte completa, porque o arquivo de teste não está no mapa.
- `bin/forge-mutante --cobertura --base 701f5bfd`: rc=0. Toda guarda mudada (4127 a 4200) tem mutante declarado.
- `bin/forge-mutante tests/mutantes/v0480-g1-2-delta-4.json --processos 1`: FD23 a FD29 mortos (o FD29 por erro do teste).
- `v0480-g1-2-delta-3.json`: FD17 a FD22, FL1 e FL2 mortos.
- `v0480-g1-2-delta-2.json`: **FD10 sobreviveu** (A2). O FD16 foi morto.
- CI do #812 no head 55a57bde: as 5 partes da suíte, `catraca`, `instalação`, `passos` e `verificações longas` passaram. `bateria (pareceres)` falha porque os pareceres estão presos ao head anterior, como se espera numa volta.

## Parecer
Reprovado pelo A2: há uma guarda de controle com mutante sobrevivente. A correção é só no teste e não muda o código. Na volta, rode `bin/forge-mutante tests/mutantes/v0480-g1-2-delta-2.json --processos 1`.
