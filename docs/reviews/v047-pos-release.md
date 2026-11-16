---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-pos-release
commit: fb7dccb4f31f290b147879709dafff67cebc7038
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (pós-release em script único, E2.223; review E2.224)

## Achados
- A1 (bloqueante) templates/projeto/scripts/pos-release:31 · O glob `[[:space:]]*'#'*` pula toda linha recuada com # em qualquer posição: um passo recuado com comentário no fim some calado e o resumo diz OK (S1). Pular só vazia ou com # como 1º não branco; o resto cai na recusa da :32. Mesmo defeito do A1 da segurança.
- A2 (bloqueante) templates/projeto/scripts/pos-release:32 · Guarda sem mutante nem teste do ramo de falha (R-QA, AR-1): trocar `|| recusar "linha que não entendo` por `|| continue` deixa os 17 testes verdes (S2). Declarar o mutante e testar uma linha fora do formato (rc=2, nada roda).
- A3 (recomendado) templates/projeto/scripts/pos-release:42 · O ramo do nome vazio (`passo:  :: cmd`) não tem teste; o PR10 cobre só o comando vazio na mesma linha. Um caso a mais no teste de passo mal formado fecha o ramo.
- A4 (recomendado) templates/projeto/scripts/pos-release:55 · Máscara deixa parte da senha com @ (sondado: `db://u:p@ss@h/...` sai `db://***@ss@h/...`); já é o A2 da segurança, citado e não refeito.
- A5 (recomendado) tests/mutantes/v047-pos-release.json:1 · Os dois commits da entrega têm a mesma mensagem; o segundo (fb7dccb4) tira o export e o PR16. Na volta, mensagem que diga o que o commit muda (Conventional Commits).

## Sondas
- S1 · passos `passo: um :: echo um`, `   passo: migrar :: echo MIGROU   # aplica a migração`, `passo: dois :: echo dois`; ALVO descartável, modo ensaio · espera: rc=2 ou 3 de 3 passos · obtido: rc=0, `pos-release: OK · 2 de 2 passos`, migrar não rodou
- S2 · mutante na :32 `|| recusar "linha que não entendo` → `|| continue; : "linha que não entendo`, `python3 -m unittest tests.test_pos_release` · espera: algum teste falha · obtido: 17 testes OK

## Parecer
Reprovado no head fb7dccb4. Intervalo `9d10894f..fb7dccb4` (Base-sha igual ao merge-base), 2 commits; o remoto já trazia o parecer de segurança (9982e820), integrado aqui por avanço rápido.

O que muda: `templates/projeto/scripts/pos-release` lê os passos e as regras do alvo de `docs/devops/pos-release.passos`, confere o alvo antes do primeiro comando (vazio, valor padrão, modo sem regra que case, regra ambígua), roda os passos na raiz com stdin fechado, para no primeiro erro e termina numa linha `pos-release:`. O `.md` só explica. Faz o que o cartão POS-RELEASE-SCRIPT-UNICO (Q5) pede, sem nada de projeto (R-NEUTRO); o `forge-init` copia o bit de execução (`bin/forge-init:164`).

A1 é defeito provado no controle que existe para o dono não perder passo: a linha de passo recuada com comentário some e o resumo diz OK. Correção: `[[ "$linha" =~ ^[[:space:]]*(#|$) ]] && continue` no lugar do `case` da :31, com o mutante que volta o glob antigo e o teste da S1. A2: o brief da E2.223 pede mutante por guarda, e a :32 não tem; com o A1 corrigido, a :32 passa a ser a guarda que recusa a linha recuada, então o teste do A1 pode matar os dois.

Testes do item: `python3 -m unittest tests.test_pos_release` na raiz do clone, 17 OK. `shellcheck templates/projeto/scripts/pos-release` limpo. `bin/forge-mutante --cobertura --base 9d10894f` lista o script e o `.passos` como "não coberto" (a cobertura não mede o shell do modelo); os mutantes declarados (PR1 a PR15, PR17, PR18) batem com as linhas do head, sem o AR-12. Subprocessos dos testes com ambiente limpo (PATH, LC_ALL e a variável do alvo). Suíte inteira: fica para o CI do PR, que não existe ainda; não rerrodada.

Tamanho (M14): conta só `tests/test_pos_release.py`, 148 linhas (o modelo fica fora da lista contada), um comportamento só. Fragmento `changelog.d/v047-pos-release.md` presente. Parecer de segurança (E2.225) reprovado no mesmo head, com o A1 igual; QA (E2.226) pendente.
