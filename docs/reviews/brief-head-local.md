---
tipo: review
contrato: 1
pedido: versao-034
branch: melhoria/brief-head-local
commit: 10c3703330bdbf0d6d813523cd0fb3bd3d6c1a21
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-05
---
# Review: versao-034, E2 BRIEF-HEAD-LOCAL

Delta lido: `360186e..10c3703` (8939e23 forge-check e testes; 10c3703 R-BRIEF, conferente e test_forge). Primeira rodada, sem delta anterior.

## Achados
- A1 (recomendado) bin/forge-check:4926 · O mutante que tira o `e_ancestral` de `so_pareceres_a_frente` sobrevive aos testes novos: o divergente reprova pelo D de `docs/reviews/outro.md`. Falta um caso de amend (árvore do remoto mais um parecer, sem descender dele) que só o C-2 pega.
- A2 (recomendado) tests/test_etapa_do_brief.py:568 · O C-7 do modelo de ameaças pede um teste de que o parecer só local dá "sem parecer" em `forge-check pr --ref origin/<b>` até o envio; ele não veio. O `cmd_pr` não mudou (T-4 cumprido), então fica para o caso de abuso 14 do QA.
- A3 (recomendado) bin/forge-check:4967 · Quando o motivo não é arquivo ("não descende de origin", "falha do git"), a reprovação imprime "fora de pareceres: \"não descende de origin\"". Sugestão: rótulo próprio para o motivo.
- A4 (recomendado) tests/test_etapa_do_brief.py:419 · O commit "historico" entrou também em cinco testes antigos (419, 476, 494, 604, 650) sem necessidade: com essas linhas removidas, o módulo passa igual (72 testes OK). Ruído no diff; não enfraquece os testes.
- A5 (recomendado) agents/conferente.md:99 · A coluna Comando segue só com `git ls-remote origin <b>`; o C-9 pedia o comando que prova o "à frente só pareceres". Sugestão: citar `forge-check brief` na coluna, já que a pré-condição manda copiar a linha dele.

## Conformidade
- Desenho (E2) e modelo de ameaças divergem num ponto: o desenho manda reusar `LIVRES`; o modelo de ameaças proíbe (C-4, T-2). O código segue o modelo de ameaças, com lista própria igual ao `so_parecer` do pre-push e teste que amarra as duas fontes. Correto.
- C-1: a exceção só com `conferido` True (mutante "aceita conferido False" morre no teste do ref de rastreio). C-2: ancestralidade conferida (ver A1). C-3: `git diff --raw -z --no-renames --no-ext-diff --no-textconv`, árvore e não log; `com_controle` reprova. C-4: lista branca exata, sem modelos `_*`, `ameacas/`, `aceites/`, kanban, ux; prefixo `docs/securityx/` reprova. C-5: só A e M com modo 100644/100755; D, symlink e gitlink reprovam. C-6: só `review`, `seguranca`, `qa`. C-7: `commit_vale` e `cmd_pr` intocados. C-8: linha `aviso:` que não reprova, com os dois sha7 e a contagem. C-9: conferente muda junto (ver A5). T-1 a T-5: nenhum presente.
- Mutantes que rodei à mão sobre os testes novos: tirar o filtro de etapa (3 falhas), tirar `conferido` (1), aceitar qualquer pasta (7), aceitar `ameacas`/`aceites` (2), aceitar qualquer tipo e modo (2): todos morrem. Tirar a ancestralidade sobrevive (A1). Pendência de ferramenta: a spec `tests/mutantes/brief-head-local.json` não está no diff; a mutação do autor (V2) fica sem prova anexada.
- Texto: R-BRIEF é a fonte da própria regra e ganhou a exceção no item `commit:`; o conferente não copia frase de regra. Fragmento `changelog.d/brief-head-local.md` presente, em "Alterado", citando `afrouxa-regra`. O rótulo `afrouxa-regra` e o aceite do dono ficam para o E1.8.
- Teto M14: 143 linhas (bin 37, tests 106), um comportamento, nada em `hooks/` nem em `PROTEGIDOS`.
- O Forge não tem `docs/engineering/praticas.md`: sem regras "ferramenta" ou "leitura" próprias a citar.
- Testes: `bin/forge-testes bin/forge-check` rc=1, 1563 testes, 6 falhas, todas subtestes de `test_hooks.Hooks.test_muitos_heredocs_recusam_dentro_do_orcamento` (o hook estoura o prazo sob carga). O diff não toca `hooks/`, e o mesmo teste falha na base 360186e (5 falhas isolado): é anterior à mudança e fica com o QA e o CI. `tests.test_etapa_do_brief` isolado: 72 testes OK.

## Parecer
Aprovado. A exceção cumpre a leitura estreita do cartão e os controles C-1 a C-9: o código revisado continua exigido no remoto por `ls-remote`, e só pareceres de A ou M em pastas de parecer ficam locais. Os cinco achados são recomendações e não devolvem.
