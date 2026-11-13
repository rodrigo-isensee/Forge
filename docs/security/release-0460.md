---
tipo: revisao-seguranca
contrato: 1
pedido: v0457
branch: melhoria/release-0460
commit: 0f86e07e71bf8ca8473f689fec645a5b4177a344
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v0457 (release 0.46.0, E23.64)

Escopo: o commit de release 0f86e07e sobre a develop no a1318e88 (diff a1318e88..0f86e07e, PR #508), lido numa worktree destacada própria. A 0.46.0 é a develop no a1318e88 mais este commit (decisão do dono de 12/11 16:30, E23.61).

## Gatilhos
`R-SEGURANCA`: o PR é classe C pelo manifesto do plugin (`.claude-plugin/plugin.json`), que é o que todos os projetos instalam. O commit não muda código, hook, workflow nem dependência.

## Achados

## Sondas

## Detalhe dos achados
Sem achados. O que foi conferido:

- Pai do commit: `0f86e07e^` é `a1318e88`, a ponta da `origin/develop` na hora do review.
- Arquivos mudados (`git diff --stat a1318e88 0f86e07e`): `CHANGELOG.md`, os 26 fragmentos de `changelog.d/` apagados (fica só `changelog.d/README.md`), `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json`. Nada além disso.
- Manifestos: nos dois arquivos, a única linha mudada é `"version": "0.45.5"` para `"0.46.0"` (`.claude-plugin/plugin.json:3`, `dev/.claude-plugin/plugin.json:3`); as duas versões batem. Nenhum outro campo (hooks, agentes, comandos) mudou.
- Changelog: a entrada `## [0.46.0] - 2026-11-12` (`CHANGELOG.md:7`) tem 62 itens; os 26 fragmentos em `a1318e88` têm 62 itens. Comparados linha a linha (ordenados), os dois conjuntos são iguais, e cada item fica na mesma seção do fragmento (5 Adicionado, 14 Alterado, 12 Corrigido como cabeçalhos de origem). Nenhum item perdido nem inventado. `## [Não publicado]` fica vazio acima da entrada.
- Segredo e caminho pessoal: `scripts/verificar-contribuicao.sh` no head revisado sai "ok: nenhum segredo nem caminho pessoal no diff contra origin/develop". A busca por padrões de token, chave e caminho de usuário nas linhas acrescentadas só achou a palavra "tokens" (custo em tokens) e os marcadores `/Users/<nome>/` e `/home/<nome>/` do item da varredura (`CHANGELOG.md:72`), que são texto de exemplo, não caminho real.
- `bin/forge-changelog conferir --base a1318e88`: reconhece PR de release (versão 0.45.5 para 0.46.0).
- Os itens de afrouxamento que o changelog registra (envio leve, revisores sem rerrodar, R-TETO em 2 partes, pulos do sandbox, R-DECISAO) já passaram pelos pareceres das suas etapas; este review não os reabre: o release só os junta.
- PA-7 (`docs/engineering/achados-recorrentes.md`): AR-1 a AR-12 tratam de código, testes, hooks e mutantes; o commit não toca nenhum, então nenhum se aplica.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: git, `scripts/verificar-contribuicao.sh`, `bin/forge-changelog conferir`, comparação dos itens em script local. Faltaram no ambiente: gitleaks, osv-scanner, semgrep, zizmor e actionlint (lacuna; as varreduras do CI do PR #508 seguem como portão).
