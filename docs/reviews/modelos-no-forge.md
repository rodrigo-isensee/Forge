---
tipo: review
contrato: 1
pedido: modelos-no-forge
branch: melhoria/modelos-no-forge
commit: d7052be4d5b18552f527023029af762bb2cb58cf
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Parecer de code review: modelos de parecer achados no repositório do Forge

Escopo: `1008338..d7052be`. Volta 2: li só o delta `2987242..d7052be` (`bin/forge-testes` e `tests/test_modelos_citados.py`); já lido em 2987242: `agents/tech-lead.md`, `agents/qa-engineer.md`, `templates/projeto/docs/security/_modelo.md` e o fragmento do changelog. O Forge não tem `docs/engineering/praticas.md`; vale como sem regras de prática.

## Achados

## Leitura
- A1 da volta anterior resolvido: `test_modelos_citados` entrou na tupla `CONTEUDO` de `bin/forge-testes` (alcança `agents/`, `stacks/`, `docs/` e, por `PUBLICADO`, `templates/`), e o teste de igualdade voltou aos literais `RAIZ / "docs/security/_modelo.md"` e `RAIZ / "templates/projeto/docs/security/_modelo.md"`; o comentário que justificava o desvio saiu.
- Sondas numa cópia em `$TMPDIR` (`git archive` do HEAD): `test_modelos_citados` 3 OK; `test_testes_tocados` (contém `MapaCobreOQueOsTestesLeem`) 29 OK.
- Efeitos de E1 e E2 conferidos antes: cláusula só acrescenta texto, invariantes intactos, deriva do modelo de segurança fechada.
- Segurança: parecer próprio do `security-engineer` (`docs/security/modelos-no-forge.md`); não o refiz.

## Parecer
Aprovado.

Recomendações (não bloqueiam):
- `tests/test_modelos_citados.py:8-9`: duas linhas em branco entre `CITACAO` e `CLAUSULA`; basta uma.
- ARCH-MODELO-CITADO (`agents/software-architect.md:20`) é o mesmo problema num terceiro agente; fica a critério do Jarvis trazê-lo.
