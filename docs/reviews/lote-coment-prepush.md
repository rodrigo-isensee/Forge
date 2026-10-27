---
tipo: review
contrato: 1
pedido: lote-coment-prepush
branch: melhoria/lote-coment-prepush
commit: 1c1d68de42a42eae7f354cb173b1496f441e165e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: lote-coment-prepush (COMENTARIOS-PREPUSH, pedido LOTE-COMENT-PREPUSH-REV, E1.1, volta 2)

Revalidação por delta do parecer anterior (d1d59a1, head 70ba6c6), conforme a decisão B do dono de 2026-10-27 08:33 (regra fechada no README e asserção estrutural no lugar do teste de termos soltos). Referência de comportamento: `.githooks/pre-push` da develop 739b0b0, igual no head (`git diff --quiet 739b0b0 1c1d68d -- .githooks/`).

## Delta lido
`bin/forge-check delta --parecer docs/reviews/lote-coment-prepush.md`, intervalo `70ba6c6..1c1d68d`:
- `README.md`:68 (+1 -1)
- `tests/test_forge.py`:299, 303 e 306-317 (+14 -8)

Já lido nas rodadas anteriores, sem mudança no delta: o resto de `README.md`, `bin/forge-testes`, `tests/test_testes_tocados.py` e `changelog.d/lote-coment-prepush.md`. Os pareceres de segurança e QA entram no intervalo, mas não são deste review.

## Garantido por ferramenta
- `python3 -m unittest tests.test_forge.PrePushSoOsAfetados tests.test_testes_tocados.NaoEPortao` em 1c1d68d: `Ran 10 tests`, `OK`.
- A asserção nova (`test_readme_so_diz_afetados_para_o_envio_simples_e_o_resto_e_suite_inteira`) numa cópia da árvore com o `README.md` de 70ba6c6: `FAIL` (`'uma só ref' not found`, e o mesmo para `árvore limpa`, `HEAD igual ao commit enviado` e `` `origin/develop` ``).
- A mesma asserção com o mutante que reintroduz "em `melhoria/*` esse envio segue a regra acima" no README do head: `FAIL` (`'segue a regra acima' unexpectedly found`).
- Teto M14: `git diff --numstat --no-renames 739b0b0...1c1d68d` dá 42 linhas de código e teste (`bin/forge-testes` 4+3, `tests/test_forge.py` 23, `tests/test_testes_tocados.py` 12; `README.md` fica fora por ser `.md`). Dentro do teto, sem `hooks/` nem `PROTEGIDOS`.
- Suíte completa não rodada (brief: só os testes do item); fica no pre-push e no CI do PR. `docs/engineering/praticas.md` não existe no Forge; checklist da skill por leitura. Achados recorrentes (PA-7): lista vazia.

## Achados

## Situação dos achados anteriores
- A1 · fechado. O `README.md`:68 diz que só o envio simples de `melhoria/*` (uma só ref, árvore limpa, HEAD igual ao enviado, `origin/develop` presente, todo caminho com regra no mapa, sem tocar `bin/forge-testes`, `tests/config.json` nem `.githooks/`) roda os afetados, e que "qualquer outro envio roda a suíte inteira". Conferido contra `dirigido()` em `.githooks/pre-push`:249-268 (ref única 251, `melhoria/*` 252, HEAD 256, árvore limpa 257, base 259-260, autojulgamento 265, plano 266-267) e contra `planejar()` em `bin/forge-testes`:150-169 (`ALTERA_O_MAPA` é só `bin/forge-testes` e `tests/config.json`). A exceção do só parecer bate com `so_parecer()` (pre-push:210-236: branch já existente 214-217, prova 218 e 222-224, HEAD 219, árvore limpa 220, sem apagar 226, `_*`, `ameacas/` e `aceites/` 230), e a frase "fora dessas condições o envio segue a regra de cima" agora é verdadeira, porque a regra de cima é fechada. Os casos de borda que o texto não lista (`bin/forge-testes` ausente ou link, diff vazio, módulo de teste sem arquivo) vão para a suíte inteira no hook, e o complemento "qualquer outro envio" os cobre. O texto também diz que a fonte é o hook (`so_parecer` e `dirigido`).
- A5 · fechado. O teste cobra a estrutura: toda frase com "só os testes afetados" traz as quatro condições, o complemento "Qualquer outro envio roda a suíte inteira" está presente, os textos do defeito (`árvore suja`, `mais de uma ref`, `HEAD diferente`, `segue a regra acima`) estão ausentes, e a fonte é citada. O teste falha no README de 70ba6c6 e pega o mutante (ver "Garantido por ferramenta").

## Parecer
Aprovado, sem achados. A1 e A5 estão fechados pelo delta, e o texto segue a opção B da decisão do dono de 2026-10-27 08:33. Se a classe "README descreve o pre-push errado" voltar, a reversão é a opção C (tabela executada contra o hook), já registrada na decisão.

Checklist (delta): o escopo não tem nada a mais, só texto e os testes dele. `R-NEUTRO`: sem termo novo. `R-CUSTO`: nada pago. As regras invioláveis estão preservadas. Um commit em Conventional Commits em português. O teste de ausência (item 11) foi relido: os quatro proibidos não estão no README do head e estavam no de 70ba6c6, e a lista de frases com "só os testes afetados" tem mínimo afirmado (`assertTrue(com_afetados)`). Segurança: só texto, com parecer próprio na branch. Devops: sem pipeline no diff.
