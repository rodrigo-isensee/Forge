---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g3-testes-uma-vez
commit: ef45eec579f148d70ee8b885b183087351817fbc
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481

## Achados
- A1 (bloqueante) bin/forge-check:9637 · a regra pede `gh pr checks` todo verde no Revisar-sha, mas nesse sha o job `bateria (pareceres)` (ci.yml:739) falha por falta dos pareceres, e a catraca falha sem o rótulo pós-último push. Ninguém grava `- ci:` honesto: trava ou linha falsa (S1). Nomeie os checks que contam.
- A2 (recomendado) agents/tech-lead.md:38 · o texto ainda manda abrir o PR em rascunho depois dos pareceres aprovados, e agora review e QA não aprovam sem PR. O PR já aponta isso como cartão G3.4. Feche-o antes da release que leva a regra aos projetos.
- A3 (recomendado) bin/forge-check:2186 · não há transição para as branches abertas com review ou QA aprovado sem a linha `- ci:` (há 11 PRs abertos na develop). Com a release, o passo 1 do `forge-fechar` passa a recusar todas elas. Um corte por `data:` ou `contrato: 2` evita uma volta por branch.

## Sondas
- S1 · `gh pr checks 893` no head ef45eec579f1 (o Revisar-sha) · espera: todos verdes, para gravar `- ci:` · obtido: `bateria (pareceres)` fail (parecer ausente, ci.yml:739), `catraca` fail (R-CONFORMIDADE: rótulo `afrouxa-regra` depois do último push), partes da suíte pendentes
- S2 · `bin/forge-mutante --processos 1 --base 220ba3fa` com as specs v0481-g3-testes-uma-vez{,-2}.json · espera: M1 a M14 mortos · obtido: os 14 morreram; o M13 morreu por erro (TypeError em `COMMIT.match(None)`), que é a guarda que ele declara
- S3 · mutantes realinhados, `--ids` mp1311 M6,M7 e v0479 M13,M16,M17 · espera: mortos, com a mesma guarda · obtido: os 5 morreram; `--conferir --base 220ba3fa`: o trecho de cada spec está no lugar; `--cobertura --base 220ba3fa`: toda condição mudada tem mutante

## Parecer
O aperto em si está correto. `suite_do_parecer` mantém os retornos antigos e só soma `sem_ci`. A prova `- suíte:` continua sem dispensar o CI verde e sem afrouxar nada. A linha `- ci:` também não solta o que a `- suíte:` segurava, porque `falta_na_prova` e `ci_verde_no_head` ficaram iguais. No `adiar`, onde antes nada se cobrava, agora a linha é cobrada. A catraca (`suite=None`) e o caso fora do Forge não mudam.

Os mutantes realinhados guardam a mesma condição de antes:
- mp1311 M6 (`pr == {}`), agora pela etapa de segurança;
- mp1311 M7;
- v0479 M13 (`e_o_forge`);
- v0479 M16 (`ref or "HEAD"`);
- v0479 M17 (o CI verde).

Ainda assim, o critério da linha não se cumpre no fluxo real (A1). O CI do Revisar-sha nunca fica todo verde antes dos pareceres. Por isso o review e o QA ou travam ou gravam a linha `- ci:` sem lastro, e é exatamente isso que a regra quer impedir.

Sem o CI verde no head, este parecer não grava a linha `- ci:`. Também não grava a `- suíte:`, porque a suíte inteira fica para o CI do PR. Rodei à mão só os mutantes do diff e os realinhados (S2, S3).
