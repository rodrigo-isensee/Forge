---
tipo: review
contrato: 1
pedido: lote-forge-fechar
branch: melhoria/lote-forge-fechar
commit: e5ef160da1bfd40a598d8f49e6f7ca5d13c5301a
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Review: lote do bin/forge-fechar (log endurecido, número das execuções, limpeza com --limpar)

Escopo: `10083383..e5ef160` (3 commits: c2ed46b C1, c1eaef9 C2, e5ef160 C3), contra o desenho `docs/propostas/aq/lote-forge-fechar.md` e o pedido. Revisor: instância separada da do autor (D-ETAPAS-INST). Segurança (L1 a L4 e a recusa do `--limpar` sem prova de merge) é do parecer do `security-engineer` em `docs/security/`; não refeita aqui.

## Achados
- A1 (bloqueante) agents/tech-lead.md:31 · A menção ao forge-fechar não diz que o código 3 é fechado com limpeza pendente nem cita o --limpar; o desenho (Riscos, item do código 3) pede o ajuste no mesmo PR. Quem trata saída diferente de 0 como falha vai ler o merge feito como erro.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_fechar`: 79 testes, OK (rodado nesta revisão, 15 s).
- Suíte do pre-push e `scripts/validar-plugin.sh`: verdes na entrega E1.1 (histórico do pedido, conferência R-PROVA em e5ef160).
- `shellcheck`: não instalado nesta máquina; fica com o CI do PR (pendência, não review manual).

## Checklist (leitura)
1. Pedido e desenho: C1 (pasta por usuário 700, sem link, do dono; `mktemp`; máscara ampliada sem tocar prosa; retenção 14 dias só na pasta; `fim: código <n>` também em `die`; `[err]` e `flock`), C2 (contagem só na mudança, `run`/`job` lidos do link sem chamada nova, `head:` e `merge:`; nenhuma decisão do passo 4 muda) e C3 (função única `limpar_entrega` chamada do passo 7 e do `--limpar`; ordem worktree, branch, remota; prune só com o diretório ausente; branch e remota só com sha mesclado ou na base; código 3 só para limpeza pendente) atendidos. Falta só A1.
2. Fluxo e regras: nada usa opção que força; `--limpar` recusa sem PR MERGED na develop (falha fechada) e herda a recusa de `main|develop|homolog` da validação inicial; `--dry-run` não apaga. R-CUSTO e R-NEUTRO preservados. Fragmento em `changelog.d/`, sem tocar o `CHANGELOG.md`.
3. Legibilidade: funções pequenas e com comentário de contrato (`mascarar`, `registrar`, `fim`, `sha_confere`, `limpar_entrega`).
4. Erros: `ler`/`repetir` só em leitura e no `push --delete`; `ls-remote` com falha vira pendente, não `ok`.
7. Testes: 22 testes novos com nome por item (L1 a L6, C2, C3), incluindo EBUSY com e sem diretório, worktree suja, commit além do mesclado, `--limpar` repetido e parcial, e o 3 restrito à limpeza.
9. Commits: um por item, Conventional Commits em português.
10. Mecanismo novo (`--limpar`): o desenho traz "Por que o existente não basta" com evidência (pedido `limpeza-pos-merge-2026-10-21`) e critério de reversão, repetido em `docs/fechamento-integrador.md`.
11. Testes de ausência: os textos procurados existem no script novo.

## Recomendações (não bloqueiam)
- `bin/forge-fechar`, `limpar_entrega`: o awk do `git worktree list --porcelain` lê `$2` e corta caminho com espaço (já existia antes); se tocar o arquivo de novo, usar `substr($0, 10)`.
- `sha_confere` usa a ancestralidade em `$base` local sem `git fetch`; é conservador (base velha só deixa pendente), vale uma linha no doc.

## Volta (Entregar)
- Atualizar `agents/tech-lead.md:31` com o código de saída (0 fechado e limpo, 1 parou, 3 fechado com limpeza pendente) e o `forge-fechar <pedido> --ref <branch> --limpar` para terminar a limpeza. Revalidação por delta (`forge-check delta`) só sobre esse arquivo.
