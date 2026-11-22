---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-esperar-estado-pasta
commit: be805bc832dbce125ef69637d62fc35229bf08ee
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E120.2, frase "rode na pasta do repositório" devolvida à skill esperar-estado)

Base 38c37de9, head be805bc8. Item só de texto: por decisão do dono, este review é o único parecer.

## O que foi conferido
- Diff: `skills/esperar-estado/SKILL.md:19` (1 linha) e o fragmento `changelog.d/v0480-esperar-estado-pasta.md` (Corrigido). A troca na skill é idêntica à do commit perdido 489d249e (mesmo `-`/`+`) e a base 38c37de9 não tem a frase (`grep -c` = 0).
- Mérito: o `gh pr view` e o `gh pr checks` do laço resolvem o repositório pela pasta atual; rodar fora dela dá `fim=erro`. A instrução é correta e não duplica outra regra.
- Teto de texto: `wc -m` 4274 contra 4324 em `tests/fixtures/metricas-texto.json`; `tests.test_metricas_texto` rodado: 2 testes, OK. Invariante `kill -0` (`tests/config.json:761`) intacta.
- Fragmento no nome da branch sem prefixo, tipo Corrigido; `CHANGELOG.md` não editado. Commit em Conventional Commits, um só.
- `R-NEUTRO`: nada de projeto. Sem código, sem guarda, sem mutante devido.
- Suíte inteira: só no CI do PR (`R-REVIEW`); não rerrodada aqui.

## Parecer
Aprovado. A frase volta ao lugar de onde o corte a tirou, cabe no teto e o fragmento descreve a correção.
