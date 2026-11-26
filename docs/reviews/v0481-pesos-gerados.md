---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-pesos-gerados
commit: f9fa7be39c883bc3da77a43669223e8e50813f32
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 E19.7, PESOS-GERADOS (#909), revalidação por delta

Delta lido: `forge-check parecer delta docs/reviews/v0481-pesos-gerados.md` (`cb924113..f9fa7be3`). No domínio do parecer mudou só `tests/mutantes/v0481-pesos-gerados.json` (+12 linhas, bloco `isentas`). Os outros arquivos do intervalo são os pareceres de QA, segurança e o meu, que ficam fora do domínio. O intervalo não traz merge da `develop` nem mudança de código.

- ci: f9fa7be39c883bc3da77a43669223e8e50813f32 verde

Leitura do `gh pr checks 909` no head. Estão verdes a suíte 10/10 (3.12 e 3.14, partes 1 a 5), o teto de pulados (3.12 e 3.14), a bateria (passos, verificações longas, python 3.14), a instalação e a árvore já provada. Os vermelhos esperam outra coisa:
- `bateria (pareceres)` e `bateria` esperam os pareceres.
- A `catraca` (run 45832767176) traz só linhas R-CONFORMIDADE, que pedem o rótulo `afrouxa-regra`. O dono aceitou o afrouxamento de PR-VERDE C1 em 26/11.

A linha R-QA das guardas apagadas, que motivou o A1, saiu do log.

## Parecer
Aprovado. O A1 da 1.ª rodada está resolvido.

**A1 (guardas apagadas sem mutante).** As duas entradas `isentas` de `bin/forge-testes` têm motivo `código removido`. Os trechos `not isinstance(pesos, dict)` e `a and a.group(1) not in pesos` existem na base `8ae4d6c6`, nas linhas 965 e 967, e não aparecem no head (`grep` rc=1). A isenção cobre só código que saiu e não esconde nenhuma guarda viva. `bin/forge-mutante --cobertura --base 8ae4d6c6` sai 0. A saída lista `isenta · bin/forge-testes:965(base)` e `:967(base)`, e a guarda nova `:979` aparece coberta pelo PG2.

**A2 e A3 (recomendados).** Seguem como cartões depois do merge, sem mudança neste delta.
