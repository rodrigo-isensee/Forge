---
tipo: review
contrato: 1
pedido: hook-falha-fechada
branch: melhoria/hook-falha-fechada
commit: f2961f9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: conformidade falha fechada com a política inteira

Parecer do autor da mudança; o review independente fica a cargo de outro revisor antes do merge.

- **O que muda:** `politica()` valida a forma de toda a política (`papeis`, `sem_agent_type`, `papel_padrao`, `acoes` com as cinco ações usadas, `pacotes`, `flags_congeladas`, `caminhos`) e de JSON ilegível; qualquer desvio chama `bloquear` ("política de conformidade inválida", saída 2).
- **Vermelho antes:** 20 subcasos falhavam sem a mudança (inclui `qa` rodando `npm install x` com `pacotes` malformado); `caminhos` ausente já bloqueava.
- **Verde depois:** 271 testes passam e `scripts/validar-plugin.sh` passa; a política vigente passa na validação (teste dedicado).
- **Riscos:** política futura com ação nova só em `acoes` continua válida; remover uma das cinco ações conhecidas passa a bloquear (intencional). Altera `hooks/conformidade.py`: exige o rótulo `afrouxa-regra` do dono.
