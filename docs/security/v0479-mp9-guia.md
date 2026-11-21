---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-mp9-guia
commit: 048b5baa53dc327d642bece4b0b90310b19b28dd
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-mp9-guia (v0478 E24.27, revalidação)

Revalidação por delta da rodada E24.22 (head `e266490b`, aprovado; texto no git).

## Gatilhos
Gatilhos: guarda (lista CITACOES_CONHECIDAS da reval-delta, C-2), texto que ensina escape de controle (FORGE_CARGA_LIVRE=1, R-TETO), comando que reescreve `.forge/config.json`

## Delta lido
`forge-check parecer delta`: intervalo `e266490b..048b5baa`, "nenhum arquivo do domínio mudou"; fora do domínio só `tests/test_conferir_reversao.py`. Lido mesmo assim, por ser teste de controle:
- `tests/test_conferir_reversao.py:61`: o `setUp` do repositório falso passa a gravar `tests/test_guia_varios_projetos.py` (teste trivial), módulo que a regra de `README.md` do `MAPA` (`bin/forge-testes:251`) já pede. Só alinha o fixture ao plano dirigido; nenhuma asserção sai nem afrouxa, e o acoplamento descrito no comentário (`:20-23`) segue valendo (MAPA mudou, o caso quebra alto).
- Demais arquivos do intervalo: pareceres de review, QA e segurança (documentação).

## Achados anteriores
- A1 (recomendado) tests/test_reval_delta.py:141: corrigido em `a8d4dce4` (E24.7); intacto no head.

## Riscos aceitos e ferramentas
Sem risco aceito. Rodado no head `048b5baa` só o que tira a dúvida: `python3 -m unittest tests.test_conferir_reversao` (13 testes, OK). Suíte inteira: fica para o CI do PR. Varredura de segredos e SAST sem ferramenta no PATH (lacuna); o delta não traz credencial.
