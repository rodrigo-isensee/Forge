---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-pesos-gerados
commit: f9fa7be39c883bc3da77a43669223e8e50813f32
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E19.9, #909, PESOS-GERADOS, volta por delta)

Delta lido: `git diff cb924113..f9fa7be3`. Fora dos pareceres, o único arquivo é `tests/mutantes/v0481-pesos-gerados.json` (+12 linhas): o bloco `isentas` com as duas guardas que o A1 do review apontou. A 1.ª rodada (aprovada em `cb924113`) fica no git.

Gatilhos: controle do Forge (`--registros` e `--regerar` de `bin/forge-testes`, a cobertura de mutantes), afrouxamento de regra (PR-VERDE C1; R-CONFORMIDADE).

- ci: f9fa7be39c883bc3da77a43669223e8e50813f32 verde

CI (run 45832767268) no head exato, lido ao fechar: as 10 partes da suíte (3.12 e 3.14) e as outras baterias estão verdes. Vermelhos, pela leitura do log:
- `bateria (pareceres)`: no head, os pareceres de review e de QA ainda são os reprovados da rodada anterior (R-REVIEW, R-QA). As voltas deles correm em paralelo a esta.
- `bateria`: é o agregador e cai pela de pareceres.
- `Catraca` (run 45832767176): só por R-CONFORMIDADE. As asserções caem de 17860 para 17858, e `tests/test_testes_tocados.py` e PesosDaSuite têm testes renomeados ou com menos asserções. É o afrouxamento da C1 que o dono aceitou em 26/11; falta no PR o rótulo `afrouxa-regra`, que é do dono. A queixa da guarda apagada sem mutante (o A1) saiu do log da catraca.

## O que aperta, o neutro e o que afrouxa (no delta)
- **Neutro:** as duas isentas descrevem código que de fato saiu. Os trechos `not isinstance(pesos, dict)` e `a and a.group(1) not in pesos` existem na base (`bin/forge-testes:965` e `:967` em `8ae4d6c6`) e não aparecem no head (0 ocorrências). O `forge-mutante` só aceita isenta de apagada quando o texto aparece menos vezes que no merge-base. A isenção não esconde nenhuma condição viva. O motivo das duas (módulo novo sem peso vale a mediana) é a regra que o dono aceitou afrouxar.
- **Aperta:** nada novo. A cobertura passa a sair 0, e as guardas vivas continuam com mutante morto (PG1 a PG4).
- **Afrouxa:** nada além da C1 já aceita pelo dono. A avaliação de segurança dela, feita na 1.ª rodada, não muda: o peso só ordena a divisão da suíte e nunca tira módulo da execução.

Achados anteriores: nenhum da segurança. O A1 do review e o do QA foram corrigidos no delta.

## Provas locais
- `bin/forge-mutante --cobertura --base origin/develop`: rc 0, com `coberta · bin/forge-testes:979 · PG2` e `isenta · bin/forge-testes:965(base)` e `:967(base)` com os motivos.
- `bin/forge-mutante tests/mutantes/v0481-pesos-gerados.json`: PG1, PG2, PG3 e PG4 morreram (rev `f9fa7be39c88`).

## Riscos aceitos e ferramentas
Nenhum risco aceito de segurança. O afrouxamento da C1 é decisão do dono e depende do rótulo `afrouxa-regra` (R-CONFORMIDADE, R-DECISAO). O delta é uma spec JSON: não traz dependência, segredo nem workflow. O varredor de segredos, o SAST e o auditor de dependências não se aplicam.
