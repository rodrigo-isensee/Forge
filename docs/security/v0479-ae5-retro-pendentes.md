---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae5-retro-pendentes
commit: c38abefad5b1b87c04628b6524c579f87b6bd529
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-ae5-retro-pendentes (pedido v0478, etapa E58.112, revalidação)

Revalidação por delta do parecer anterior (commit ac6127f6, aprovado sobre 8d2efa1f; a rodada anterior fica no git).

Gatilhos: ferramenta de controle do Forge (bin/forge-check).

## Delta lido
`forge-check parecer delta docs/security/v0479-ae5-retro-pendentes.md`, intervalo `8d2efa1f..c38abefa`, no domínio: bin/forge-check e bin/forge-testes; fora: tests/pesos-d4.json e tests/test_reval_delta.py. O único commit novo é o merge c38abefa, que traz a develop 8caa7f3d (#763, AE7.1 `forge-check comparar`). Separação da base:
- `git diff origin/develop HEAD` (origin/develop = 8caa7f3d): em bin/forge-check e tests/test_retro_pendentes.py, as linhas `+`/`-` são idênticas às de `git diff a6baf239 8d2efa1f` (a mudança própria aprovada no parecer anterior). O subparser `comparar` e o despacho para bin/forge_comparar.py que o delta mostra vêm da base e ficam fora; `git diff 8caa7f3d HEAD` não toca bin/forge_comparar.py, hooks/, .githooks/, .github/ nem scripts/.
- bin/forge-testes:160, resolução à mão (`git show --cc c38abefa`): a tupla `FORGE_CHECK` fica com os dois itens, `test_retro_pendentes` (da branch) e `test_comparar` (da develop). Os dois módulos existem; o arquivo segue com sintaxe válida (`ast.parse`); `test_comparar` aparece uma vez só.

## Achados anteriores
Nenhum aberto.

## Só aperta (confirmação escrita)
Confirmação: só aperta. A resolução é a união das duas listas: mudar bin/forge-check (e os módulos da linha 194) passa a selecionar os dois testes, nenhum some da seleção de afetados; nenhum portão, hook, caminho de escrita ou validação de entrada muda, e o código próprio da branch é idêntico ao aprovado em 8d2efa1f.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira: não rodada aqui (brief: sem suíte local); vale o CI do PR para o merge. Nenhum teste rodado: o delta próprio é uma entrada numa tupla de seleção, conferida por leitura e `ast.parse`. Ferramenta ausente no ambiente: gitleaks, semgrep e osv-scanner (lacuna; delta de 1 linha no domínio lido à mão, sem segredo nem dependência nova).
