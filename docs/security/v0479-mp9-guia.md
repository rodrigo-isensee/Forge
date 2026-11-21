---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-mp9-guia
commit: a8d4dce419e55c32c4d3fcf37e02b13db7ea8a18
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-mp9-guia (v0478 E24.7, revalidação)

Revalidação por delta da rodada E24.3 (head `2054ef3b`, aprovado com A1 recomendado; texto no git).

## Gatilhos
Gatilhos: guarda (lista CITACOES_CONHECIDAS da reval-delta, C-2), texto que ensina escape de controle (FORGE_CARGA_LIVRE=1, R-TETO), comando que reescreve `.forge/config.json`

## Delta lido
`forge-check parecer delta`: intervalo `2054ef3b..a8d4dce4`, nenhum arquivo do domínio mudou; fora do domínio só `tests/test_reval_delta.py`, relido por ser a guarda C-2 (controle do Forge). O resto do intervalo são os pareceres de review, QA e segurança (`docs/`).

## Achados anteriores
- A1 (recomendado) tests/test_reval_delta.py:140: **corrigido** em `a8d4dce4`. O diff troca uma linha só e apaga apenas o comentário duplicado `# v047 E2.222: ...`; a entrada `("tests/test_guia_varios_projetos.py", "README.md"): (1, "teste-le")`, as demais entradas, as contagens e `MOTIVOS` ficam intactos. A guarda não foi afrouxada.

## Sondas

## Riscos aceitos e ferramentas
Sem risco aceito. Rodados localmente só o teste novo e a guarda no head `a8d4dce4`: `python3 -m unittest tests.test_guia_varios_projetos tests.test_reval_delta.Guarda` (6 testes, OK). Suíte inteira: fica para o CI do PR (sem PR aberto nesta rodada). Varredura de segredos e SAST sem ferramenta no PATH (lacuna); o delta é um comentário em teste, sem credencial.
