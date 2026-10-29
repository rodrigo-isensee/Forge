---
tipo: review
contrato: 1
pedido: t6t3-mensagem
branch: melhoria/t6t3-mensagem
commit: e31bf9dc10c1eb8f5693c4b71f3beb44d010f264
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Code review: mensagem ao conferente lida do brief e mensagem do modo entrega (T6T3-MENSAGEM, E1, E2, E4 e E5)

Escopo: pedido T6T3-MENSAGEM-REV, E1.1 (`R-REVIEW`). Rodada 2, revalidação por delta do parecer `f2e03cd` (rodada 1 sobre `0c2ef9c`, reprovado por A1). Segurança (`345e31b`) e QA (`b787e51`) já aprovaram a volta; não os refaço.

## Achados
- A3 (recomendado) agents/jarvis.md:65 · o texto do `Desde:` da mensagem de entrega ainda diz "o sha40 da última linha `conferida`"; o comando agora usa a linha mais recente entre `conferida` e a base fixada pelo dono. Alinhe a frase ao `agents/conferente.md:75`

## Parecer
**Aprovado.** A1 e A2 da rodada 1 resolvidos; A3 é recomendação (texto, sem efeito no comando) e não devolve.

Delta lido: `bin/forge-check delta --parecer docs/reviews/t6t3-mensagem.md` (intervalo `0c2ef9c..e31bf9d`): `agents/conferente.md` 18, 68-75, 80, 98; `bin/forge-check` 4602-4603, 4611, 4616; `tests/mutantes/t6t3-mensagem.json` 63-165; `tests/test_mensagem_conferente.py` 13-14, 57-97. Já lido na rodada 1 e fora do delta: E1 (etapa da linha `Etapa:`), o resto do E2, o E4 no `agents/jarvis.md` e o E5 (`bin/forge-testes`, `tests/test_testes_tocados.py`, fragmento do changelog).

- A1 (rodada 1, bloqueante): resolvido. `bin/forge-check:4611-4616` usa `bases_do_pedido(...)` inteiro e `Desde: {bases[-1][0]}`, a mesma regra do `desde_valido` do `entrega`. O teste `test_desde_e_a_linha_mais_recente_entre_conferida_e_base_do_dono` cobre os três casos pedidos (dono depois da conferida, só a do dono, conferida depois do dono); M10 (filtro só `conferida`) e M16 (`bases[0]`) guardam a regra.
- A2 (rodada 1, recomendado): resolvido. `agents/conferente.md:68-75` traz `Arquivo:` absoluto e um campo por linha, na ordem da saída do comando; o `e31bf9d` só junta linhas (18, 80, 98) para o arquivo caber em 110 linhas, sem mudar texto.
- Testes de recusa separados (QA): cada recusa com teste próprio e a mensagem exata; M7 a M9 e M12 a M15 apontam para eles.

Ferramentas: `python3 -m unittest tests.test_mensagem_conferente tests.test_testes_tocados` → `Ran 92 tests ... OK` (rodado aqui, carga 0,89). Mutação: do autor e do QA (V2); não refeita.

Teto (M14): `git diff --numstat --no-renames d14a713...e31bf9d` nos arquivos que contam (`bin/forge-check` 35+3, `bin/forge-testes` 1+1, `tests/test_mensagem_conferente.py` 101+0, `tests/test_testes_tocados.py` 1+1) = 143 linhas, dentro de 150; sem `hooks/` nem `PROTEGIDOS`.

Commits da volta: 2 (`87d1451`, `e31bf9d`), Conventional Commits em português. PA-7 (`docs/engineering/achados-recorrentes.md`, AR-1 a AR-9) conferido: nenhuma classe repetida neste pedido; sem linha AR.
