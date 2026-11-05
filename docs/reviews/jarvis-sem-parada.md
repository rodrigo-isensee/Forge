---
tipo: review
contrato: 1
pedido: jarvis-sem-parada
branch: melhoria/jarvis-sem-parada
commit: a00a5437f5d5fa0001f3438846192f45b21703b7
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-05
---
# Review: jarvis-sem-parada

## Achados
- A1 (recomendado) tests/config.json:206 · o invariante prende só o texto de `R-SEMPARADA`; a citação do ID em `agents/jarvis.md` e na skill `trabalho-em-paralelo` (E2) não tem frase fixada, e pode sumir sem o teste reprovar.

## Parecer
Aprovado. Revisão da branch inteira, 360186e..a00a543 (6 arquivos, 24 linhas; só `tests/config.json` conta no teto da M14, 6 linhas, dentro de `R-TETO` e do teto por PR).

- E1: `docs/regras/R-SEMPARADA.md` traz a folga no teto, o que puxar (etapa seguinte de outro cartão, próxima versão em dual-track, voltas recomendadas, cartões que destravam o fluxo, retrospectivas), os dois casos de parada e o aviso ao dono de qual deles é. Não contradiz `R-TETO` (a folga é a dele, e `R-WIP` e os portões seguem valendo) nem as regras de decisão do dono: não pede decisão nova, o Jarvis só deixa de esperar. Entrada nova no `docs/regras/README.md`.
- E2: o ID é citado em `agents/jarvis.md` ("Trabalho em paralelo (padrão)") e em `skills/trabalho-em-paralelo/SKILL.md`, sem copiar o texto da regra (`R-NEUTRO`/ADR 0002 preservados). O invariante de `agents/jarvis.md:51` (linha) segue valendo; o diff mexeu só nessa linha, no mesmo parágrafo.
- E3: `docs/regras/R-SEMPARADA.md` entrou em `invariantes` (3 frases) e em `invariantes_motivo` (regra e porquê); remover o texto da regra reprova o teste de invariantes. A citação não está presa (A1, recomendação, pois o Escopo E3 pede só que a regra não suma).
- Changelog: fragmento `changelog.d/jarvis-sem-parada.md`, seção `### Adicionado`, sem mexer no `CHANGELOG.md` (ADR 0006).
- Sem `R-NEUTRO`, `R-CUSTO` nem segurança a apontar; sem código novo.
- `python3 -m unittest tests.test_forge`: `Ran 512 tests in 599.888s`, `OK`.
