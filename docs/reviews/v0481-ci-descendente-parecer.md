---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-descendente-parecer
commit: 523b0065035b3e0ce068d94360966ce20ed1c4d4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 E8.19 (2ª volta, delta aa26249f..523b0065 do #895)

## Parecer
Aprovado. O A1 do parecer anterior (no aa26249f) está fechado sem enfraquecer teste.

- **Delta lido:** `forge-check parecer delta` deu `revalida: sim` (este parecer barrou) e, no domínio, `bin/forge-check` e as duas skills. Li `git diff aa26249f..523b0065`. O único commit do autor é f8839529, que toca as duas skills. Os dois merges da develop (fc029f85, 523b0065) não têm trecho de resolução no `git show --cc`. O patch da branch sobre a base (`git diff 6cc4cd5a 523b0065`) é linha a linha igual ao do aa26249f sobre a eeb81062 em `bin/forge-check`, nos testes, nas duas specs de mutante e no fragmento do changelog. O `bin/forge-check` do delta é só o que veio da develop (#874).
- **A1 anterior, fechado:** `tests.test_metricas_texto` e `tests.test_orcamento_instrucao` passam juntos no 523b0065 (10 testes OK). `tests/fixtures/metricas-texto.json` e `tests/config.json` não mudam na branch (`git diff 6cc4cd5a 523b0065 --stat` vazio para os dois), então nenhum teto subiu.
- **Skills:** as duas frases G3.7 seguem dizendo o mesmo: `- ci: <sha40> verde` com o `gh pr checks` do `commit:` verde fora `bateria (pareceres)`, `bateria` e `catraca`, PARECER-LE-O-CI, a forma `verde via <sha40 do descendente>` (G3.7), "sem CI verde, não aprova" e "não rerroda o SHA". Saíram "o merge exige todos" (engineering-practices) e "classes" e "os" (qa-testing), sem trecho de `invariantes` nem ID de regra. A forma 'via' foi aceita pelo dono (decisão de 25/11 07:27). `tests.test_forge` (RegrasInviolaveis, Skills, Neutralidade, NeutralidadeDoNucleo, RegrasComId, Referencias, AntiDuplicacao, Orcamento): 22 OK. `test_aq1_texto`, `test_comando_pronto`, `test_pre_envio_brief`, `test_medidas_m14b`, `test_jarvis_nucleo` e `test_modelos_projeto`: 181 OK.
- **Mutantes:** `bin/forge-mutante --conferir --base 6cc4cd5a` dá "o trecho de cada spec do diff está no lugar" depois dos merges. A guarda não mudou no delta, então a mutação não foi rodada de novo.
- **CI do #895 no 523b0065 (run 45696404571):** as 10 partes da suíte (3.12 e 3.14), `teto de pulados` (3.12 e 3.14), `bateria (python 3.14)`, `bateria (passos)`, `bateria (verificações longas)`, `instalação (python 3.14)` e `árvore já provada na develop` estão verdes. `bateria (pareceres)` cai por R-REVIEW e R-QA, porque os pareceres desse momento não aprovam. `bateria` cai só pelo agregado `pareceres: failure`. A `catraca` (run 45696404450) cai por R-CONFORMIDADE, "mudança em bin/forge-check": ela pede o rótulo `afrouxa-regra` do dono depois do último push.
- ci: 523b0065035b3e0ce068d94360966ce20ed1c4d4 verde
