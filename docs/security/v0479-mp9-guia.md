---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-mp9-guia
commit: 862d9ecb792c30e0b66e82d30f3794a19828cc65
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-mp9-guia (v0478 E24.17, revalidação)

Revalidação por delta da rodada E24.12 (head `abb581a5`, aprovado; texto no git).

## Gatilhos
Gatilhos: guarda (lista CITACOES_CONHECIDAS da reval-delta, C-2), texto que ensina escape de controle (FORGE_CARGA_LIVRE=1, R-TETO), comando que reescreve `.forge/config.json`

## Delta lido
`forge-check parecer delta`: intervalo `abb581a5..862d9ecb`.
- No domínio, `bin/forge-testes:175` e `:250`: `test_guia_varios_projetos` entra em `LEITORES_DE_TEXTO` e na regra de `README.md` do `MAPA`. Só acrescenta módulo ao plano dirigido; nenhuma regra sai nem se estreita, e nenhum portão chama o script (o CI do PR roda a suíte inteira). Conferido com `bin/forge-testes --listar` para `README.md`, `hooks/agentes.py` e `templates/projeto/CLAUDE.md`: os três planos trazem o módulo.
- Fora do domínio, `tests/test_guia_varios_projetos.py:42`: `import agentes` dentro do `try`, com `sys.path` restaurado no `finally`; `hooks/agentes.py:1398` guarda o `main` em `if __name__ == "__main__"`, então o import não executa o hook. Sem efeito em guarda.

## Achados anteriores
- A1 (recomendado) tests/test_reval_delta.py:140: corrigido em `a8d4dce4` (E24.7); intacto no head.

## Riscos aceitos e ferramentas
Sem risco aceito. Rodado localmente no head `862d9ecb` só o módulo tocado: `python3 -m unittest tests.test_guia_varios_projetos` (4 testes, OK). Suíte inteira: fica para o CI do PR. Varredura de segredos e SAST sem ferramenta no PATH (lacuna); o delta não traz credencial.
