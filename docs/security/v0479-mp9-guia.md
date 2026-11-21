---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-mp9-guia
commit: abb581a5b7e513cafa3cb5d391ccd4b516c19f73
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-mp9-guia (v0478 E24.12, revalidação)

Revalidação por delta da rodada E24.7 (head `a8d4dce4`, aprovado, A1 corrigido; texto no git).

## Gatilhos
Gatilhos: guarda (lista CITACOES_CONHECIDAS da reval-delta, C-2), texto que ensina escape de controle (FORGE_CARGA_LIVRE=1, R-TETO), comando que reescreve `.forge/config.json`

## Delta lido
`forge-check parecer delta`: intervalo `a8d4dce4..8c313a97`, sem o que veio da base. Fora do domínio: `tests/pesos-d4.json` (`abb581a5`, uma linha `"test_guia_varios_projetos": 0.1`, peso de agendamento da suíte, sem efeito em guarda). No domínio a ferramenta lista `templates/projeto/CLAUDE.md`, mas as linhas mostradas ("Conferência de registros", "Versões do intérprete") vêm da `develop` (`bead3e53`), trazidas pelo merge `3efc67aa`, não da branch.

Conferência do merge `3efc67aa` (pais `9c1f7ddf` e `bead3e53`, o Base-sha): `git diff bead3e53 abb581a5` toca só os arquivos da branch, e as linhas mudadas de `README.md`, `templates/projeto/CLAUDE.md`, `tests/test_guia_varios_projetos.py`, `tests/test_reval_delta.py` e `changelog.d/v0479-mp9-guia.md` são idênticas às de `a8d4dce4` contra a sua base antiga (`0c47762a`). A resolução do merge não alterou nem afrouxou nada do já aprovado; a guarda C-2 segue como em E24.7.

## Achados anteriores
- A1 (recomendado) tests/test_reval_delta.py:140: corrigido em `a8d4dce4` (E24.7); intacto no head.

## Sondas

## Riscos aceitos e ferramentas
Sem risco aceito. Rodado localmente no head `abb581a5` só o teste do módulo: `python3 -m unittest tests.test_guia_varios_projetos` (4 testes, OK). Suíte inteira: fica para o CI do PR. Varredura de segredos e SAST sem ferramenta no PATH (lacuna); o delta é uma linha de peso, sem credencial.
