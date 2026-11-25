---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-g4-f1-aviso
commit: eb747918dc99b4fd57c67846a28f6e87bc1c4c4d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança por delta: v0481 (E7.43, #885, G4 F1: modo aviso por grupo)

Delta lido: `git diff 3682aeba..eb747918`. Quase tudo é a `develop` trazida (até `7e38f842`, com o #886 e os itens já revistos nos PRs deles); o que é da branch confere pela comparação `6959cec2..3682aeba` contra `7e38f842..eb747918`: em `hooks/` muda só a resolução do `Guarda.barrar` (`hooks/conformidade.py:1607-1619`), e em `tests/mutantes/` as specs M1 (v0478), M15 (v0479-2), M16 (v0481-g4-f1-aviso-2) e M2, M5, M7 (v0481-perfil-fifo) (`e1721df1`, `9b93d179`). Já lido nas rodadas anteriores (no git, em `3682aeba`): o resto da branch.

Gatilhos: controle do Forge (hook `conformidade`, caminho de recusa de todas as regras dele, nas sessões do projeto e do Forge).

## Conferência do delta
- **A2 (bloqueante em 3682aeba): corrigido.** A resolução do merge junta o modo por grupo e o registro da branch com a escolha do texto do #886: `:1610` chama `perfil_iniciante` (`:1538`, cópia principal por `diretorio_comum`, `O_NONBLOCK | O_NOFOLLOW`, só `S_ISREG`, 64 bytes), `:1612` engole o `PrazoVencido` da escolha do texto e `:1617` o do registro; `:1619` recusa com o texto escolhido. O `self.h.iniciante()` saiu do caminho da recusa. Sondas S5 e S6 (detalhe): o que liberava em S3 agora recusa com a regra dela.
- **A1 (bloqueante, corrigido em 3682aeba):** segue corrigido; o `registrar_recusa` (`:1511`) é o mesmo da rodada anterior (S6 cobre FIFO no perfil e no registro juntos).
- **Specs de mutante:** a mesma guarda em cada uma, com o `de` que existe na fonte depois do merge; cada `de` ocorre uma vez e o mutante morre no teste da spec (M1, M15, M16, M2, M5, M7: 6 de 6 mortos, aplicados à mão numa cópia `git archive` do head; o `forge-mutante` estava na fila do hook `pesado`).
- **Por escrito: aperta** a escolha do texto da recusa (FIFO em `.forge/perfil` liberava push na main e `--force` na sessão do Forge; agora recusa, sem `git` nem espera); **neutro** as specs de mutante e a `develop` trazida (sem mudança de guarda na resolução além do `barrar`); **afrouxa: nada** no delta. A chave `modo_por_grupo` da branch (já lida, todos os grupos em `barrar`) segue pedindo o rótulo `afrouxa-regra` do dono para a catraca.
- Testes: `python3 -m unittest tests.test_hooks.ModoPorGrupo tests.test_hooks.RecusaComFifoNoRegistro tests.test_hooks.RecusaComFifoNoPerfil tests.test_hooks.HookSessaoDoForge.test_travas_do_conformidade tests.test_conformidade_verde.EstadoDoAgentesNoClone` → 30 testes, OK.
- CI do PR #885 no head `eb747918` (run 45652397890): suíte 3.12 e 3.14 partes 1 a 5, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, teto de pulados, instalação e árvore já provada verdes. Vermelhos só pelos portões: `catraca` (log: mudança em `hooks/conformidade.py`, chave nova `modo_por_grupo` na política, pulos de `tests/test_hooks.py` e de `tests/` acima da base pelos dois `skipUnless(mkfifo)` da branch; tudo pede o rótulo `afrouxa-regra`), `bateria (pareceres)` (review desatualizado e segurança reprovada) e `bateria`, o agregador, só por `PARECERES: failure`.

## Parecer
- ci: eb747918dc99b4fd57c67846a28f6e87bc1c4c4d verde

## Achados

## Sondas

## Detalhe dos achados
Sem achado novo. Sondas desta rodada (hook do head rodado como em produção, `python3 -s -E`, projeto temporário, nada externo):
- S5: FIFO em `.forge/perfil`, sessões do Forge e do projeto, `git push origin feature/x:main`, `git push --force origin feature/x`, `git commit --no-verify -m x`: código 2 com R-MAIN, R-VERIFY, R-VERIFY em menos de 0,4 s nas seis (em 3682aeba, S3 dava código 0 na sessão do Forge).
- S6: o mesmo, com FIFO também em `.forge/run/comandos.jsonl`: código 2 com a regra dela em menos de 0,4 s nas seis.
- S7 (problema anterior à branch, fora do delta): FIFO em `.forge/perfil` e um ato que pergunta antes do recusado (`git reset --hard && git push --force origin feature/x`, `git clean -fd; git push origin feature/x:main`, `git checkout -- . && git commit --no-verify -m x`): na sessão do Forge recusa com a regra dela; no projeto, código 2 com R-CONFORMIDADE em cerca de 3,6 s (prazo). Falha fechada, sem liberação: vira cartão na `Melhoria vista`, não segura o item.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, os testes dos módulos tocados, os 6 mutantes realinhados e as sondas S5 a S7 (scripts fora do repositório). Varredor de segredos, SAST e auditor de dependências: o delta da branch não traz dependência nem segredo.
