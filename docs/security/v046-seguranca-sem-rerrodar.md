---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/seguranca-sem-rerrodar
commit: 157c1da96cbf8f49abd3aef4b6e41b9b37cf4a58
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-11
---
# Review de segurança: v046 (frente SEGURANCA-SEM-RERRODAR, E4.1)

Head revisado: `157c1da96cbf8f49abd3aef4b6e41b9b37cf4a58` (revalidação da volta 2, só o delta `6b77a7c7..157c1da9`: commit `157c1da9`, 2 arquivos, uma linha cada: `agents/security-engineer.md:14`, `skills/cyber-security/SKILL.md:31`). Pareceres anteriores: aprovado em `8a96dd12`, reprovado em `6b77a7c7` (A4). Suíte não rerrodada; rodado só o teste que prova o fechamento da A4.

## Gatilhos
Nenhum gatilho formal da `R-SEGURANCA` no diff (não toca `hooks/`, `docs/regras/`, `tests/catraca.py`, `tests/config.json` nem `.github/`). É texto do próprio papel de segurança e afrouxa a prática de execução local do revisor, com rótulo `afrouxa-regra` declarado no fragmento do changelog. Invariantes de `tests/config.json` (linhas 335 e 486 no head): o trecho "suíte inteira roda só no CI" protege os dois arquivos; no `8a96dd12` estava presente, no `6b77a7c7` saiu dos dois (A4) e no `157c1da9` voltou aos dois.

## Achados
- A1 (recomendado) agents/security-engineer.md:14 · resolvido em 6b77a7c7: o texto manda rodar o teste novo de abuso e o que tirar dúvida, e o item 3 (sondas, PAR-P1) segue intacto.
- A2 (recomendado) skills/cyber-security/SKILL.md:31 · resolvido em 6b77a7c7: a skill agora traz o teste novo de abuso, a dúvida e o devolver sem prova, alinhada ao agente.
- A3 (recomendado) agents/security-engineer.md:14 · resolvido em 6b77a7c7: os dois arquivos e o changelog exigem o PQ conferido.
- A4 (recomendado) agents/security-engineer.md:14 · resolvido em 157c1da9: o trecho protegido "suíte inteira roda só no CI" voltou a este arquivo e a skills/cyber-security/SKILL.md:31; o teste de invariantes passa e o changelog volta a ser verdadeiro.

## Sondas
- S1 · `python3 -m unittest tests.test_forge.RegrasInviolaveis.test_trechos_obrigatorios` no worktree em 6b77a7c7 · espera: OK · obtido: FAILED (failures=2), subtestes arquivo='agents/security-engineer.md' e arquivo='skills/cyber-security/SKILL.md', trecho='suíte inteira roda só no CI'
- S2 · `python3 -m unittest tests.test_forge -k trechos_obrigatorios` no worktree em 157c1da9 · espera: OK · obtido: Ran 1 test in 0.192s, OK

## Detalhe dos achados
**Revalidação (volta 2, 157c1da9).** A4 resolvida: as duas linhas trazem de novo o literal "a suíte inteira roda só no CI" (sonda S2 passa) e o sentido da volta 1 se mantém (CI verde ou PQ conferido, teste novo de abuso, dúvida, devolver sem prova). Na skill saiu o "do autor" depois de "PQ conferido"; sem efeito de segurança, porque o PQ conferido já é o do autor pelo agente e pelo changelog. O fragmento `changelog.d/seguranca-sem-rerrodar.md` não mudou e a frase "nenhum trecho de `invariantes` mudou" volta a ser verdadeira. Nada novo no delta. Veredito: aprovado. A S1 fica como registro histórico da prova do bloqueante, agora fechado (o rótulo virou `recomendado` resolvido; parecer aprovado não leva bloqueante aberto).

**Revalidação (volta 1, 6b77a7c7).** A1, A2 e A3 resolvidos pelo texto novo; nenhum deles é promovido. A4 é nova e nasceu do delta (o corte por teto de instrução no `6b77a7c7`).

**A4.** Evidência: `agents/security-engineer.md:14` ("só o CI roda a suíte inteira", ordem trocada) e `skills/cyber-security/SKILL.md:31` (a frase sumiu) contra `tests/config.json:335` e `:486` (invariante "suíte inteira roda só no CI", motivo `R-QA` em `:712` e `:720`); sonda S1 prova a falha. `changelog.d/seguranca-sem-rerrodar.md:2` diz "nenhum trecho de `invariantes` mudou (o 'suíte inteira roda só no CI' segue)", o que deixou de ser verdade. Caminho: não há atacante externo; é defeito provado em trecho protegido de regra da fábrica (`R-CONFORMIDADE`): o CI do PR quebra e, se o invariante fosse ajustado para passar, a remoção de trecho protegido entraria sem destaque no título nem motivo. Severidade: média (processo; bloqueia por defeito provado e por tocar invariante). Correção mínima (sem mudar o sentido nem crescer o texto), restaurar a frase literal nos dois arquivos: agente linha 14 → "**Suíte:** a suíte inteira roda só no CI; cite-o ou o PQ conferido; rode o teste novo de abuso e o que tirar dúvida; sem CI ou PQ, devolva."; skill linha 31 → "**Suíte:** a suíte inteira roda só no CI; cite o CI verde ou o PQ conferido do autor; rode o teste novo de abuso e, na dúvida, o que a tira; sem eles, devolva." Alternativa (não recomendada): mudar o invariante, o que exige o destaque no título do PR e o motivo, e decisão do dono (`R-DECISAO`). Esforço P. Dono: `tech-lead` (autor da E4.1).

**Histórico (parecer em 8a96dd12):**
**A1.** Evidência: `agents/security-engineer.md:14` (novo) e `skills/cyber-security/SKILL.md:31` (novo) contra o item 3 do mesmo agente (sondas em entrega de analisador ou hook, PAR-P1). Caminho de ataque: não há atacante externo; o risco é de processo. Num pedido de guarda ou hook, o revisor que segue o texto à letra deixa de executar a sonda que provaria um desvio, e o bloqueante vira "não provado", logo `recomendado` (`R-REVIEW`); um controle defeituoso passa com parecer aprovado. Severidade: baixa. Correção mínima (texto, nos dois arquivos): "a suíte inteira roda só no CI do PR; cite o CI verde ou o PQ conferido do autor e não rerrode no mesmo SHA o que eles já rodaram; rode o teste novo dos casos de abuso, as sondas que provam um achado e, havendo dúvida, o teste que a tira". Esforço P. Dono: `tech-lead` (autor da E4.1).

**A2.** Evidência: `skills/cyber-security/SKILL.md:31` vs `agents/security-engineer.md:14`. Caminho: divergência entre a skill (carregada em outros papéis e nos projetos) e o agente; quem segue a skill não roda os casos de abuso que o `qa-engineer` escreveu. Severidade: baixa. Correção mínima: a mesma frase da A1 nos dois arquivos. Esforço P. Dono: `tech-lead`.

**A3.** Evidência: `agents/security-engineer.md:14` ("cite o CI verde ou o PQ do autor") e `agents/qa-engineer.md:15` ("nunca o `.verde` local (I5)"). Caminho: autor (agente) com relato errado ou injetado no relatório; a segurança cita como prova um PQ não conferido. O impacto é contido porque o CI do PR segue obrigatório para o merge (`R-QA`), por isso não bloqueia. Severidade: baixa. Correção mínima: "o PQ do autor conferido pelo conferente (entrega conferida no histórico do pedido)" ou alinhar à forma do QA (check-run do mesmo sha quando o PR já existe). Esforço P. Dono: `tech-lead`.

Fora dos achados: o fragmento do changelog declara o afrouxamento, a medida (tempo de segurança por pedido) e o critério de reversão; coerente com o rótulo `afrouxa-regra` exigido pelo pedido.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: só `git` (diff, grep, ls-remote) e leitura de `tests/config.json` no head; nenhuma varredura necessária (diff só de texto, sem segredo, dependência nem workflow). Suíte não rerrodada (diretriz 15); na volta 1, só a sonda S1; na volta 2, só a S2 (um teste, 0,2 s).
