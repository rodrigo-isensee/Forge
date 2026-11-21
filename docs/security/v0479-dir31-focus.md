---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-dir31-focus
commit: 0b933f1d9d842824a4ec05d9457e1df645a17d15
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-dir31-focus (DIR-31, visão de foco), head 0b933f1d

Revalidação (E67.7) por delta sobre o parecer anterior (commit `9298d75b`, aprovado no `0d5826f9`). A rodada anterior fica no git.

Gatilhos: execução de comando no atalho (`scripts/jarvis`), configuração do modelo de projeto (`templates/projeto/.claude/settings.json`), ambos sem mudança neste delta.

## Delta lido
- `forge-check parecer delta`: intervalo `0d5826f9..0b933f1d`, sem o que veio da base (merge `0b6ebc0c` da `develop` `c8e8a08d`); "nenhum arquivo do domínio mudou"; fora do domínio: `tests/test_reval_delta.py`.
- `tests/test_reval_delta.py:132` (commit `0b933f1d`): `("tests/test_forge.py", "README.md")` passa de 15 para 16, motivo `teste-le` mantido. Lido mesmo fora do domínio, porque é a guarda C-2 da lista `TEXTO` do `forge-check`.

## Achados

## Sondas

## Detalhe dos achados
Sem achados. A guarda não afrouxou:
- **A contagem é real:** `grep -c README.md tests/test_forge.py` dá 15 na `develop` `c8e8a08d` e 16 no head. A linha nova é do teste DIR-31 da própria branch (`(RAIZ / "README.md").read_text(...)`), que é um teste lendo o README e não um controle.
- **O mecanismo não mudou:** `conferir_citacoes` (`tests/test_reval_delta.py:144-158`) continua comparando por igualdade (`achadas != conhecida` reprova nos dois sentidos), restringe `teste-le` a `tests/` e mantém a checagem (d) de leitura fora de `tests/`. `TOLERADOS`, `PASTAS` e `CORPUS` não mudaram.
- **Teste rodado:** `python3 -m unittest tests.test_reval_delta` no head: 10 testes, OK. A suíte inteira roda no CI do PR, e o merge depende dele verde.
