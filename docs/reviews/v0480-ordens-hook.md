---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-hook
commit: fe14fb1ea179e325195005e2cab46a2bc95d4eaa
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E123.15, 3ª volta do hook ordens)

Revalidação pelo delta (H3, `R-REVIEW`): `forge-check parecer delta docs/reviews/v0480-ordens-hook.md`, intervalo `8e84ef3b..fe14fb1e`. Lido só o código e os testes do domínio do commit `fe14fb1e` (E123.14). Parecer anterior: aprovado em `8e84ef3b` (`781ac440`). A volta responde ao A4 da segurança E123.12 (`e29c3dbd`); o mérito de segurança é do `security-engineer`. Aqui confiro só correção, consistência e teste.

## Delta lido
- Só listas e constantes mudam, sem lógica nova. `NO_PROJETO` passa a `.forge/ordens/ordens-em-vigor.md` (`hooks/ordens.py:20`). O mapa de donos troca o arquivo pela pasta `.forge/ordens/` (`hooks/conformidade.json:66`). `PELA_COPIA_PRINCIPAL` vira `(".forge/ordens/",)` (`hooks/conformidade.py:3818`), e os `ignorados` do `bin/forge-init:222` passam a guardar a pasta.
- A pasta casa pelo mesmo `achou` de prefixo que já guarda `docs/ordens/` no Forge, então o curinga no nome (`ordens-em-vigo?.md`, `[r]`, `*`) não escapa. As 11 fixtures `ordens-a4-*` provam isso: 9 bloqueiam (S1 a S3, `cp` e `rm` na pasta) e 2 liberam (o `cat` do dev e o `cp` do jarvis).
- Nenhum teste foi afrouxado. As fixtures e os testes que já existiam mudam só o caminho. O teste novo `test_conformidade_recusa_curinga_no_nome_das_ordens_do_projeto` exige no mínimo 11 fixtures e confere os códigos esperados, e o teste do modelo de projeto passa a afirmar que a pasta `ordens` não existe nele.
- A ADR 0003 (itens 1 e 6), o fragmento do changelog e a docstring do `ordens` batem com o código. Fora dos pareceres e das fixtures S4, nenhum arquivo cita mais `.forge/ordens-em-vigor.md` (`git grep`). O índice `docs/hooks-fixtures.md` está atualizado: `tests.test_indice_fixtures` saiu OK.
- Mutantes: as 3 constantes novas têm M29, M30 e M31 (`tests/mutantes/v0480-ordens-hook-5.json`), e M26 foi reescrito para a pasta.

## Provas
- `python3 -m unittest tests.test_hooks.OrdensEmVigor tests.test_forge.ForgeInit` (`env -i`): `Ran 36 tests in 17.034s OK`. `tests.test_indice_fixtures`: `Ran 7 tests OK`.
- `bin/forge-mutante tests/mutantes/v0480-ordens-hook-5.json`: M29, M30 e M31 `morreu`. `--ids M26` na spec `-4`: `morreu · (erro)`, porque o `git check-ignore` levanta exceção sob o mutante, e é esse o desenho do teste.
- Suíte inteira: fica no CI do PR e não foi rodada de novo.

## Parecer
Aprovado. O A4 da segurança E123.12 foi tratado só com listas e constantes, cada uma coberta por um mutante que morre e por fixtures de comportamento. Nenhum teste foi afrouxado, e a documentação acompanha o código.
