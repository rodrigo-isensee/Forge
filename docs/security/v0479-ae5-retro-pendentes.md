---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae5-retro-pendentes
commit: 2d378b98dfa98a5f3be4879335985a04c4093b7e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-ae5-retro-pendentes (pedido v0478, etapa E58.87, revalidação)

Revalidação por delta do parecer anterior (commit 7014e1a6, aprovado sobre e375c67a; a rodada anterior fica no git).

Gatilhos: ferramenta de controle do Forge (bin/forge-check) e guarda C-2 de `TEXTO` (tests/test_reval_delta.py).

## Delta lido
`forge-check parecer delta docs/security/v0479-ae5-retro-pendentes.md`, intervalo `e375c67a..2d378b98`. Separado com `git diff c9d69234 HEAD`: o merge da develop (f324dfa4) entrou sem resolução à mão (`git show --cc f324dfa4` vazio); o que veio da develop em bin/forge-check (docstring de `entrega`, `conferido_mais_novo`, `vale_pelo_conferido`, `vindos_do_remoto_da_base`) é da base e fica fora desta revalidação. Da branch, só o commit 2d378b98:
- bin/forge-check:5912: a docstring de `cmd_retro_pendentes` deixa de citar o caminho `docs/retrospectivas/`; nenhuma linha de código muda.
- tests/test_reval_delta.py:134: entrada nova em `CITACOES_CONHECIDAS`, `("tests/test_retro_pendentes.py", "docs/retrospectivas/"): (1, "teste-le")`. Conferido: a única citação é tests/test_retro_pendentes.py:115, que lê o modelo de `templates/` para compará-lo ao da raiz (teste que lê texto, motivo certo).

## Achados anteriores
Nenhum aberto (o A1 de 600bbecf já estava corrigido em e375c67a).

## Só aperta (confirmação escrita)
Confirmação: só aperta. A lógica da guarda (`conferir_citacoes`, `MOTIVOS`, `LE_CONTEUDO`, `TOLERADOS`, `PASTAS`, `CORPUS`) não muda; a entrada nova tem contagem exata 1 (uma citação a mais ou a menos reprova), motivo `teste-le`, que a guarda só aceita sob `tests/`, e não alcança código de produção; `TEXTO` (bin/forge-check:630) não muda; a docstring de bin/forge-check é só prosa, sem efeito em execução. A leitura de `docs/retrospectivas/` por `cmd_retro_pendentes` (caminho montado por partes, bin/forge-check:5931) já estava no head aprovado e375c67a, é só de leitura e informativa (rc 1 com pendente, sem consumidor em hooks/, .githooks/, .github/ nem scripts/); uma retro tratada como `texto` não muda portão nenhum.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira: não rodada aqui (brief: sem suíte local); vale o CI do PR para o merge. Rodados: `tests.test_reval_delta` (10 OK) e `tests.test_retro_pendentes` (OK). Ferramenta ausente no ambiente: o varredor de segredos (lacuna; delta de 2 linhas no domínio lido à mão, sem segredo).
