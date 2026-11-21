---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-mp9-guia
commit: e266490b885f01366dfd6abb80ef65950ffa90e5
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-mp9-guia (v0478 E24.22, revalidação)

Revalidação por delta da rodada E24.17 (head `862d9ecb`, aprovado; texto no git).

## Gatilhos
Gatilhos: guarda (lista CITACOES_CONHECIDAS da reval-delta, C-2), texto que ensina escape de controle (FORGE_CARGA_LIVRE=1, R-TETO), comando que reescreve `.forge/config.json`

## Delta lido
`forge-check parecer delta`: intervalo `862d9ecb..e266490b`, o merge da develop (`65a3f0a9`). Separado da develop com `git diff origin/develop HEAD`: o que a branch soma à develop segue igual ao aprovado em `862d9ecb`.
- No domínio, `bin/forge-testes:175`: conflito resolvido mantendo os dois itens em `LEITORES_DE_TEXTO` (`test_guia_varios_projetos` da branch e `test_retro_pendentes` da develop). Contra a develop, a branch só acrescenta o módulo nessa tupla e na regra de `README.md` do `MAPA` (`:251`); nada sai nem se estreita. `bin/forge-testes --listar` traz os dois módulos.
- Guarda C-2, `tests/test_reval_delta.py:132-142`: conflito resolvido mantendo os dois lados. Contra a develop, a única linha nova é `("tests/test_guia_varios_projetos.py", "README.md"): (1, "teste-le")` (`:141`), a mesma aprovada antes; a contagem bate com a única leitura em `tests/test_guia_varios_projetos.py:23`. Nenhuma entrada da develop sumiu nem teve a contagem mudada pela branch (`test_forge` 16, `test_retro_pendentes` e `bin/forge_comparar.py` vêm da develop); `MOTIVOS` e `LE_CONTEUDO` intactos. A guarda não afrouxou.

## Achados anteriores
- A1 (recomendado) tests/test_reval_delta.py:141: corrigido em `a8d4dce4` (E24.7); intacto no head.

## Riscos aceitos e ferramentas
Sem risco aceito. Rodado no head `e266490b` só o que tira a dúvida: `python3 -m unittest tests.test_reval_delta tests.test_guia_varios_projetos` (14 testes, OK). Suíte inteira: fica para o CI do PR. Varredura de segredos e SAST sem ferramenta no PATH (lacuna); o delta não traz credencial.
