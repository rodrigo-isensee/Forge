---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-placar-varredura
commit: 3907f4bb628f8a919a6b756ce8db7c321514f776
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 (E20.22, melhoria/v0479-placar-varredura)

## Parecer
Aprovado. A `fundo_demais` do `bin/forge-placar` passa a um passe só (estado de string, escape e nível), custo linear; as duas regexes quadráticas saem e nada mais as usa. O resultado muda só no caso de string sem fecho: antes as aspas soltas deixavam os colchetes contar, agora a string engole o resto. Esse texto é JSON inválido e o `json.loads` seguinte o recusa, então a entrada continua rejeitada.

O teste não usa relógio: um iterável que conta prova que cada caractere é lido uma vez, e os casos de escape, string sem fecho e teto conferem o resultado. A suíte `SemTeste` roda verde (6 testes). Os mutantes M42 a M49 morreram, rodados com `bin/forge-mutante --ids M42..M49 --processos 1`, um por guarda mudada (R-REVIEW). O fragmento de changelog existe e cabe no escopo. Arquivos do diff: 4, código de produção com cerca de 20 linhas (H1 respeitado). Sem achados.
