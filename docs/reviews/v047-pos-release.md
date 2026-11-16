---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-pos-release
commit: ddc16953b247ade5bb8a1b33a0ade9096fc04f20
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (pós-release em script único, E2.223; review E2.224, revalidação E2.239, E2.375 e E2.400)

## Achados
- A1 (recomendado) templates/projeto/scripts/pos-release:31 · Corrigido no head 76e00f85: só linha vazia ou que começa por # é pulada; a linha recuada com comentário no fim cai na recusa da :32 (S1 repetida: rc=2, nada roda). Mantido como registro; não bloqueia mais.
- A2 (recomendado) templates/projeto/scripts/pos-release:32 · Corrigido no head 76e00f85: PR20 declarado e morto por test_linha_recuada_ou_com_comentario_no_fim_nao_e_pulada (S2 repetida). Mantido como registro; não bloqueia mais.
- A3 (recomendado) templates/projeto/scripts/pos-release:40 · Corrigido no head 76e00f85: test_passo_com_nome_vazio_e_recusado e PR21, morto.
- A4 (recomendado) templates/projeto/scripts/pos-release:56 · Corrigido no head 76e00f85: máscara até o último @ e password/senha/token sem caixa (PR22, PR23); o resto da máscara fica com o parecer de segurança (A2 dela).
- A5 (recomendado) tests/mutantes/v047-pos-release.json:1 · Corrigido no head 76e00f85: o commit da volta tem mensagem própria que diz o que muda.

## Sondas
- S1 · passos `passo: um :: echo um`, `   passo: migrar :: echo MIGROU   # aplica a migração`, `passo: dois :: echo dois`; ALVO descartável, modo ensaio · espera: rc=2 ou 3 de 3 passos · obtido: rc=0, `pos-release: OK · 2 de 2 passos`, migrar não rodou
- S2 · mutante na :32 `|| recusar "linha que não entendo` → `|| continue; : "linha que não entendo`, `python3 -m unittest tests.test_pos_release` · espera: algum teste falha · obtido: 17 testes OK
- S3 · S1 no head 76e00f85 · espera: rc=2, nada roda · obtido: rc=2, `pos-release: RECUSADO · linha que não entendo ... · nenhum comando rodou`
- S4 · PR19 a PR23 com `bin/forge-mutante --processos 1 tests/mutantes/v047-pos-release-3.json` no head 76e00f85 · espera: morrem · obtido: os 5 morreram

## Parecer
Aprovado no head ddc16953 (revalidação E2.400, por delta). Delta lido: `forge-check parecer delta docs/reviews/v047-pos-release.md`, intervalo `0eb2dfeb..ddc16953`, sem o que veio da base; no domínio: `bin/forge-testes`.
- `bin/forge-testes:178` (commit 777e9f28): uma entrada no `MAPA` liga `templates/projeto/docs/devops/pos-release.md`, `pos-release.passos` e `scripts/pos-release` a `test_pos_release`, antes da regra genérica de `templates/`. `bin/forge-testes --listar` com os três caminhos inclui `test_pos_release`. Sem guarda nova (só dado do mapa), sem mutante a declarar.
- Junção da develop (ddc16953, merge de 3d3c9224): sem resolução de conflito (`git show --cc` sem bloco `@@@`); o patch do item não muda e fica fora do domínio do delta.
Conferido no head ddc16953: `python3 -m unittest tests.test_pos_release` com 20 OK. Sem achado novo; nenhuma classe repetida, `docs/engineering/achados-recorrentes.md` sem linha nova. A bateria inteira fica para o CI do PR.

## Parecer anterior
Aprovado no head 0eb2dfeb (revalidação E2.375, por delta). Delta lido: `forge-check parecer delta docs/reviews/v047-pos-release.md`, intervalo `76e00f85..0eb2dfeb`, sem o que veio da base; no domínio: `changelog.d/v047-pos-release.md`, `tests/test_pos_release.py`.
- `tests/test_pos_release.py:125`: a fixture `"db://h/descartavel-3?password" "=XYZ123&x=1"` vira duas literais concatenadas pelo Python; o valor em execução é o mesmo, o caso de teste não muda. Só tira o par chave=valor literal que a varredura de segredo do CI barrava.
- `changelog.d/v047-pos-release.md:2`: a linha troca a citação literal das chaves `password`, `senha` e `token` seguidas do sinal de atribuição por "o valor das chaves `password`, `senha` e `token` na consulta"; mesmo sentido, sem par literal.
- Junção da develop (472a09f4, merge de 48edd3c6): sem resolução de conflito (`git show --cc` vazio); o patch do item não muda e fica fora do domínio do delta.
Conferido no head 0eb2dfeb: `python3 -m unittest tests.test_pos_release` com 20 OK. Sem achado novo; nenhuma classe repetida, `docs/engineering/achados-recorrentes.md` sem linha nova. A bateria inteira fica para o CI do PR.

Anterior a esse: aprovado no head 76e00f85 (revalidação E2.239, volta 1). Delta lido: `forge-check parecer delta docs/reviews/v047-pos-release.md`, intervalo `fb7dccb4..76e00f85`, no domínio: `changelog.d/v047-pos-release.md`, `docs/engineering/achados-recorrentes.md`, `templates/projeto/docs/devops/pos-release.md`, `templates/projeto/docs/devops/pos-release.passos`, `templates/projeto/scripts/pos-release`, `tests/mutantes/v047-pos-release-3.json`, `tests/mutantes/v047-pos-release.json`, `tests/test_pos_release.py`.

Achados da volta anterior, todos resolvidos no head:
- A1: a :31 passa a `[[ "$linha" =~ ^[[:space:]]*(#|$) ]] && continue`; a S1 repetida no head sai com código 2 e `pos-release: RECUSADO · linha que não entendo ... · nenhum comando rodou`. O mutante PR19 (volta o glob antigo) morre.
- A2: PR20 declarado na :32, morre em `test_linha_recuada_ou_com_comentario_no_fim_nao_e_pulada` (recuada, com # no fim e sem chave recusadas; vazia, `#` e `#` recuado ignorados).
- A3: `test_passo_com_nome_vazio_e_recusado` e PR21 (:40), morre.
- A4: máscara até o último `@` e o valor das chaves `password`, `senha` e `token` sem caixa (PR22, PR23 e PR15 ajustado); sondado `db://u:p@ss@h/descartavel-1?Token=abc&x=1` sai `db://***@h/descartavel-1?Token=***&x=1`. Parecer de segurança revalidado e aprovado no mesmo head (aba9c83b), citado.
- A5: o commit da volta tem mensagem própria (`fix(modelo): pos-release só ignora linha vazia ...`).

Conferido no head 76e00f85: `python3 -m unittest tests.test_pos_release` com 20 OK; `shellcheck` limpo; `bin/forge-mutante --processos 1 tests/mutantes/v047-pos-release-3.json` com PR19 a PR23 mortos; `bin/forge-mutante --conferir --base fb7dccb4` diz que o trecho de cada spec do diff está no lugar (sem AR-12). O `.md` e o `.passos` acompanham o script (glob com host literal, `alvo-variavel` igual à variável que os passos leem). A bateria inteira fica para o CI do PR, sem nova rodada aqui.

Histórico da volta anterior: reprovado no head fb7dccb4. Intervalo `9d10894f..fb7dccb4` (Base-sha igual ao merge-base), 2 commits; o remoto já trazia o parecer de segurança (9982e820), integrado aqui por avanço rápido.

O que muda: `templates/projeto/scripts/pos-release` lê os passos e as regras do alvo de `docs/devops/pos-release.passos`, confere o alvo antes do primeiro comando (vazio, valor padrão, modo sem regra que case, regra ambígua), roda os passos na raiz com stdin fechado, para no primeiro erro e termina numa linha `pos-release:`. O `.md` só explica. Faz o que o cartão POS-RELEASE-SCRIPT-UNICO (Q5) pede, sem nada de projeto (R-NEUTRO); o `forge-init` copia o bit de execução (`bin/forge-init:164`).

A1 é defeito provado no controle que existe para o dono não perder passo: a linha de passo recuada com comentário some e o resumo diz OK. Correção: `[[ "$linha" =~ ^[[:space:]]*(#|$) ]] && continue` no lugar do `case` da :31, com o mutante que volta o glob antigo e o teste da S1. A2: o brief da E2.223 pede mutante por guarda, e a :32 não tem; com o A1 corrigido, a :32 passa a ser a guarda que recusa a linha recuada, então o teste do A1 pode matar os dois.

Testes do item: `python3 -m unittest tests.test_pos_release` na raiz do clone, 17 OK. `shellcheck templates/projeto/scripts/pos-release` limpo. `bin/forge-mutante --cobertura --base 9d10894f` lista o script e o `.passos` como "não coberto" (a cobertura não mede o shell do modelo); os mutantes declarados (PR1 a PR15, PR17, PR18) batem com as linhas do head, sem o AR-12. Subprocessos dos testes com ambiente limpo (PATH, LC_ALL e a variável do alvo). Suíte inteira: fica para o CI do PR, que não existe ainda; não rerrodada.

Tamanho (M14): conta só `tests/test_pos_release.py`, 148 linhas (o modelo fica fora da lista contada), um comportamento só. Fragmento `changelog.d/v047-pos-release.md` presente. Parecer de segurança (E2.225) reprovado no mesmo head, com o A1 igual; QA (E2.226) pendente.
