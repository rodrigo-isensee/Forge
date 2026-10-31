---
tipo: revisao-seguranca
contrato: 1
pedido: impl-forge-check-a
branch: melhoria/impl-forge-check-a-a1
commit: 0ba0a57a138dab4390afb9362047ee69da4f4506
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-30
---
# Review de segurança: impl-forge-check-a (branch a1)

Diff lido: `234dbe0..0ba0a57` (1844275 C1, d4eea24 C2, 0ba0a57 fragmento), contra o modelo de ameaças `docs/security/ameacas/forge-check-a.md` (controles C-1 a C-11, casos A1 a A9 e B1 a B6).

## Item entregue e M14
- Item: E1 e E2 do pedido (FC-ENTREGA-PEDIDO-CAMINHO, FC-PEDIDO-CAMINHO, FC-PEDIDO-CAMINHO-DUPLO), o caminho do Pedido pelo realpath do arquivo do pedido e o `caminho_do_pedido` sem caminho duplo.
- M14 (agents/tech-lead.md:19): `git diff --numstat --no-renames` dá `bin/forge-check` 37+7 e `tests/test_forge.py` 86+2, 132 linhas, abaixo de 150; o fragmento fica fora. Um comportamento (a leitura do caminho do Pedido, que o C1 compara com o arquivo que o C2 resolve). Cumpre.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `bin/forge-check` é o portão de escopo do conferente, e a união de briefs decide o que entra no escopo conferido.

## Achados
- A1 (bloqueante) bin/forge-check:983 · C-4 do modelo não cumprido: mesmo_pedido usa valor.removeprefix fora do try; brief sem a linha Pedido: faz a exceção sair de uniao_de_briefs (bin/forge-check:1009) e a conferência termina sem linha de veredito. Guarde valor vazio (return False) e teste o caso.

## Detalhe dos achados
**A1.** Evidência: `bin/forge-check:980-989` (`mesmo_pedido`; o try só começa em `:985`), chamado em `:1009` com `achados["Pedido"]`, que é None quando o cabeçalho do brief não tem `Pedido:`. Na base 234dbe0 o `if achados["Pedido"]:` deixava o None seguir até `achados != esperado` e a união reprovava com a linha de escopo; agora a chamada levanta erro de atributo (reproduzido em processo: `mesmo_pedido(None, "p1", "/x/p1.md")` levanta). O modelo exige no C-4 que nenhuma exceção saia de `uniao_de_briefs` fora do try da leitura. Caminho de ataque: o autor de um brief (texto não confiável para o conferente) omite ou desloca a linha `Pedido:`; o conferente recebe rc 1 com a pilha de erro e nenhuma linha `escopo:`. A falha é fechada (rc diferente de 0), então o ganho do atacante é só negar a conferência e quebrar o contrato de saída lido por máquina; severidade baixa, mas é controle obrigatório do modelo com gatilho, por isso bloqueante (requisito). Mesmo achado do code review (A1 de `docs/reviews/impl-forge-check-a.md`), um cartão só. Correção mínima: `if not valor: return False` no começo de `mesmo_pedido`, e o caso "sem Pedido" na tabela de `test_pedido_do_brief_por_caminho_vale_so_pelo_realpath_do_pedido_conferido` com rc 1 e sem pilha de erro no stderr. Esforço P. Dono: tech-lead (autor da E1.1).

**Conferido e cumprido** (nada a corrigir): C-1 (igualdade de string do realpath dos dois lados, `:987`); C-2 (só absoluto ou `~/`, por `is_absolute` depois da expansão); C-3 e C-10 (só o prefixo `~/` pelo `HOME`, `:986` e `:795-796`; o teste com a base de contas trocada cobre `~usuario`); C-4 para NUL e erro de sistema (o try de `:985-989`; caso NUL no teste); C-5 (o `-REV` pela pasta do pedido resolvido, `:1010`); C-6 (regra de texto sobre o valor inteiro, `:983`); C-7 (a reprovação não ecoa o valor); C-8 (`dentro_da_raiz` com `docs/pedidos` nas raízes, `:800-803`; testes B1, B2, B4); C-9 (cwd e absoluto como antes); C-11 (`arquivo_existe` captura erro de sistema e de valor, `:782-787`). Casos A1 a A9 e B1 a B5 estão nos testes; `EntregasParalelas` e `CaminhoDoPedido` rodados na worktree, 15 testes, OK.

**Recomendação (não devolve):** o laço do id puro em `caminho_do_pedido` (`:805-807`, inalterado desde a base) ainda usa `is_file` direto; um id de mais de 255 bytes levanta erro de sistema antes da leitura. Vem só do argumento da linha de comando de quem roda o conferente, sem ganho para terceiro e com falha fechada; trocar por `arquivo_existe` no mesmo cartão da volta é barato. Riscos R-1 a R-4 do modelo seguem fora deste lote (cartões FC-ENTREGA-GIT-FALHA-ABERTA e FC-PEDIDO-FORA-DAS-RAIZES).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática por leitura do diff e reprodução em processo. Ferramentas ausentes no PATH (lacuna, nada instalado): gitleaks, semgrep, osv-scanner, zizmor, actionlint, shellcheck. O diff não tem shell, workflow, dependência nem segredo.
