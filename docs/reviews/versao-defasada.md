---
tipo: review
contrato: 1
pedido: versao-defasada
branch: melhoria/versao-defasada
commit: ac07db30731623e60de954ae1518bfaabd314af7
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Code review: versão defasada (E2.2, revalidação da volta 2)

Rodada 2, por delta: `b62c841..ac07db3` (1 commit, 14 arquivos, 193+/33-). Revisor diferente do autor (D-ETAPAS-INST). A segurança de `hooks/`, `bin/` e `scripts/` é da E2.3 (`security-engineer`, R-SEGURANCA), em paralelo, e não é refeita aqui.

Delta lido (`forge-check delta --parecer docs/reviews/versao-defasada.md`, intervalo `2b6abdd..ac07db3`, que inclui só o parecer de segurança `b62c841` além da volta): `README.md:39`; `bin/forge-check:2847-2969`; `changelog.d/versao-defasada.md:2`; `docs/hooks.md:19`; `hooks/doutor.py:109-112`; `hooks/parecer.py:18-20,160-169,177,189-190`; `scripts/jarvis-forge:114,122-124`; `tests/config.json:477-483`; as 3 fixtures de `tests/hooks/parecer/`; `tests/test_doutor.py`, `tests/test_forge.py` e `tests/test_hooks.py` nos trechos alterados. Já lido na rodada 1 e não relido: o resto da guarda (`comparar_com_o_forge`, `versao_da_propria_copia`), o doutor fora das linhas acima, o `jarvis-forge` fora da reanexação e o apoio `tests/apoio_versao_defasada.py`.

Ferramentas rodadas em ac07db3: `python3 -m unittest tests.test_doutor tests.test_forge.FerramentaDefasadaNoForge tests.test_forge.FerramentaDefasadaNoProjeto tests.test_forge.HookParecerGuardaDaVersaoNoProjeto tests.test_forge.HookParecerGuardaDaVersaoNoForge tests.test_hooks` → `Ran 123 tests in 107.161s OK`. A suíte inteira e o `scripts/validar-plugin.sh` não foram refeitos (R-TETO): o autor declarou 922 OK e validar-plugin OK, e o QA os refaz no head. Shellcheck: ausente na máquina, já é critério do merge (E2.5).

## Achados
- A2 (bloqueante) hooks/parecer.py:190 · com código 0 o hook escreve o aviso no stderr, o que fere a ADR 0003, item 1 ("sem violação, sem saída"), e o runner em tests/test_hooks.py:288 foi afrouxado para aceitar isso. Ou o hook fica mudo com código 0, ou a ADR 0003 é emendada por decisão.

## Detalhe dos achados
**A2.** O item 1 da ADR 0003 manda o hook sair com 0 e sem saída quando não há violação, e o contexto da própria ADR registra que, com saída 0, o stderr não chega ao agente. O delta faz o `verificar` imprimir o aviso de versão no stderr com código 0 (`hooks/parecer.py:189-190`). Isso vale no Forge e nos clones (cópia atrasada, ou comparação que falha), e também nos projetos quando a verificação está desligada ou o cache está ilegível. Para o teste passar, o runner de `tests/test_hooks.py:285-290` deixou de exigir `stderr == ""` nas fixtures do `parecer` que declaram `stderr`, e as 3 fixtures do clone passaram a esperar o aviso. É o teste que guarda a ADR 0003, e o brief manda tratar como bloqueante qualquer acréscimo que afrouxe teste. A ADR 0003 não muda neste pedido (restrição do brief). O aviso, além disso, não tem quem o leia: com código 0, o stderr de um `PreToolUse` não chega ao agente e só aparece para a pessoa no modo transcrição.
A lacuna veio do brief da volta (item 2: "no hook parecer [...] stderr, rc inalterado"), não do autor, que seguiu o texto dele.
Saída sugerida, sem afrouxar nada: com código 0, `guarda_de_versao` do hook não devolve texto (o hook só bloqueia, e só nos projetos e com prova positiva). Assim o runner e as 3 fixtures voltam ao que eram. O aviso no Forge continua chegando ao integrador pela saída do `forge-check pr` e do `forge-fechar`, que ele lê, e a decisão D (no Forge a guarda só avisa) segue cumprida pelo `forge-check`. A outra saída seria emendar a ADR 0003 para permitir stderr com código 0. Isso é decisão do arquiteto com o dono (R-DECISAO), e sozinha não resolve a falta de leitor. Precisa de brief de volta (D-ETAPAS-INST).

**R4 (recomendado).** O teste do A1 nos projetos (`HookParecerGuardaDaVersaoNoProjeto`) chama `parecer.guarda_de_versao` direto. Nenhuma fixture de projeto mostra `gh pr create` barrado pelo `verificar` de ponta a ponta com o cache `defasado`. Hoje a chamada é incondicional (`hooks/parecer.py:177`) e o invariante `avaliar_versao` está em `tests/config.json`. Ainda assim, uma fixture de projeto que bloqueia (código 2, `R-CONFORMIDADE`) prenderia a ligação. Pode entrar na mesma volta do A2.

## Itens 1 a 5 da volta contra o A1, o R2 e a decisão D
1. A1: o `verificar` chama a guarda antes dos pareceres e do `cmd_pr`, e por ele passam `gh pr create`, `gh pr ready` (clone) e `gh pr merge`. Num projeto, a prova positiva bloqueia com R-CONFORMIDADE e a mesma frase. Erro de comparação não bloqueia. Há testes de bloqueio, de em dia (silêncio), de erro e do Forge. Conforme, salvo A2 (o caminho de aviso) e R4.
2. Decisão D: `avaliar_versao` só devolve `bloqueio` com `not forge` e em `pr`, `entrega` e `brief gerar`. No Forge, os quatro subcomandos avisam com código inalterado (`test_o_aviso_nao_muda_o_codigo_de_saida`). Nos projetos, o `delta` passou a só avisar (`test_delta_so_avisa_nos_projetos`). Conforme no `forge-check`; no hook, ver A2.
3. R1 da segurança: `FORGE_VERIFICAR_VERSAO=0`, ou `consulta: desligada` no cache, vira `versão não conferida (verificação desligada)`, com cache e sem cache (`test_verificacao_desligada_aparece_na_saida`). Conforme.
4. R3 da segurança: `local data novidades`, com a atribuição separada da declaração, preserva o código do `rev-list`. A falha chama `atrasado`, que diz `ATRASADO desde <data>`, e há teste com `git` falso. Conforme.
5. R2 do review: `README.md:39` descreve a consulta a cada reanexação e o `ATRASADO desde <data>`. `docs/hooks.md:19` descreve a guarda no hook e a diferença entre Forge e projeto. Conforme. Quando o A2 for corrigido, a frase "em todos os subcomandos e no hook" de `docs/hooks.md` muda junto.

## Suposições do autor
- Guarda no hook depois do retorno de "só .md" (e depois das saídas de promoção e de rascunho no clone): aceita. Nesses caminhos o hook não confere nada nem chama o `cmd_pr`, então não há conferência que a cópia atrasada possa enganar. A guarda acompanha o portão já existente.
- `e_o_forge` falso com `.forge/versao` na raiz ou acima: aceita. Segue a mesma ordem de `e_clone_do_forge` (`hooks/_comum.py:70`, o projeto vem antes do Forge). Sem ela, um projeto que escrevesse o manifesto do Forge trocaria o bloqueio por aviso (`test_manifesto_do_forge_num_projeto_nao_o_torna_o_forge`). O erro para o outro lado, um clone tratado como projeto, só endurece. Hoje não há `.forge/versao` acima de `~/.forge-contrib/wt/`.
- Verificação desligada não apaga prova de atraso já gravada: aceita. O doutor mantém `defasado` e `ultima` quando o `atual` é o mesmo (`hooks/doutor.py:111-112`), e o `forge-check` segue bloqueando com `FORGE_VERIFICAR_VERSAO=0` (`test_verificacao_desligada_nao_apaga_a_prova_de_atraso`). Desligar não vira atalho para passar com cópia atrasada (R-CONFORMIDADE).

## Acréscimos fora da lista
- Runner de `test_hooks` aceitando stderr com código 0 no hook `parecer`: afrouxa o teste que guarda a ADR 0003 (A2, bloqueante).
- 3 fixtures do `parecer` esperando o aviso: vêm da mesma causa e voltam a `codigo: 0` sem `stderr` quando o A2 for corrigido.
- Fragmento `changelog.d/versao-defasada.md` atualizado (delta só avisa, hook, verificação desligada): conforme. Muda junto com o A2 se o hook deixar de avisar.

## Texto único e invariantes
- `tests/config.json`: só acrescenta (`hooks/parecer.py`: `avaliar_versao` e `R-CONFORMIDADE`; `docs/hooks.md`: `a guarda só avisa`). Nenhum invariante saiu. O texto `atrás do repositório; a conferência não vale; peça à pessoa:` continua em `bin/forge-check`.
- Regras citadas pelo ID nos docstrings, no `docs/hooks.md` e no fragmento. Sem trecho de regra copiado (AntiDuplicacao).

## Commits
Um, `fix(versao): ...`, Conventional Commits em português, com corpo por superfície. Limpo.

## Parecer
Reprovado por A2. R4 entra na mesma volta, se couber.
