---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-sieg-g1-gravar
commit: 9f833cd6d8290f0d0aeeb2306ef1f16fa56f9b67
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 E90.11 (SIEG-G1 G1.2a, `forge-check autorizacao gravar`, volta E90.10)

Revalidação por delta do parecer aprovado 44b4a481 (Decisão 1 do dono, 23/11). Li o `forge-check parecer delta`, intervalo `d7c1a53b..9f833cd6`. No domínio: `bin/forge-check`, `bin/forge_autorizacao.py`, `changelog.d/v0479-sieg-g1-gravar.md`, `docs/adr/0018-autorizacao-do-dono-gravada.md`, `tests/mutantes/v047-sieg-g1-autorizacao-6.json`, `tests/mutantes/v0479-sieg-g1-gravar-7.json`, `-8.json`, `-9.json` e `tests/test_autorizacao_gravar.py`.

## Achados
- A1 (recomendado) bin/forge_autorizacao.py:157 · Travessão e aspas curvas (que o corretor do celular e do macOS insere) agora contam como fora do vocabulário: "pode aplicar o rótulo no “pr 5”" nasce pendente. A falha é fechada; incluir `—–“”‘’…` na classe de pontuação comum

## Conferido
- **A1 anterior (ADR):** `docs/adr/0018-autorizacao-do-dono-gravada.md:53-59` agora diz que a origem **não** está provada, porque `CLAUDE_CODE_SESSION_ID` vem do chamador e a pasta aceita escrita direta, e que só o corte do hook a prova. A casa sai de `pwd.getpwuid` (`:282-284`). O teste `test_home_e_sessao_do_chamador_nao_escolhem_a_transcricao` roda o forge-check noutro processo com `-I` e o ambiente limpo, e traz o controle positivo. Fechado.
- **A2 anterior:** `(?!\w|\.\w)` aceita "PR 5." e "0.47.3." e mantém "pr 5.1" fora do pr 5 (`:319`, teste com os três casos). Fechado.
- **A3 da segurança:** o `estado` do ler trata fala no futuro como `adulterada` (`:242`). Antes disso, `problemas` já passou pelo `limite`, que valida a hora; o `instante` não levanta exceção ali.
- **A6 da segurança:** "até o fim deste pedido" só nasce ativa com `docs/pedidos/<id>.md` (`pedido_para_anotar`) e sem o `F-<Pedido>` (`:380-382`, `:401-403`). Sem `pedido_existe` ou com `--pedido` vazio, a concessão nasce pendente, e o motivo não herda o "nenhum".
- **Mutantes:** `bin/forge-mutante --processos 1` sobre `-8.json` e `-9.json` matou M55 a M63. Com `--ids`, M44, M50 e M54 realinhados também morreram. O trecho `de` do M44 agora é único.
- **Testes:** rodei `python3 -m unittest tests.test_autorizacao_gravar tests.test_autorizacao`: 49 testes, OK. A suíte inteira roda no CI.
- **Tamanho (H1):** o delta tem cerca de 20 linhas de código em `bin/`, dentro do teto.

## Parecer
Aprovado (`R-REVIEW`). Os dois recomendados do review anterior estão fechados, e os da segurança que este review alcança (A3, A4 e A6) vêm com teste do ramo de falha e mutante morto. O A1 é falha fechada e vira cartão depois do merge.
