---
tipo: revisao-devops
contrato: 1
pedido: release-0.47.1
branch: melhoria/mp1311-554-revalidacao
commit: 6e837bf759ebc43e4f960d6cf348ef1e42e7d1d4
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-14
---
# Review de devops: release-0.47.1

Diferença `origin/main..6e837bf7` nos caminhos de devops: `.github/workflows/ci.yml`, `scripts/placar-mutacao.py`, `.claude-plugin/plugin.json`.

## Detalhes
Aprovado, sem achados.

- `.github/workflows/ci.yml` (3 trechos, mesma mudança): depois da instalação global do Claude Code 2.1.296 (versão fixada, `--allow-scripts` já existente), roda `node "$(raiz global)/@anthropic-ai/claude-code/install.cjs"` encadeado por `&&` dentro de `instalar()`. A nova tentativa por falha de rede continua valendo e `claude --version` confere o resultado. Não muda `permissions`, segredos, SHAs de ações, gatilhos nem `concurrency`; nada escreve na `main` (R-MAIN); sem `continue-on-error` nem check pulado (R-VERIFY); sem custo novo (R-CUSTO). A entrada não é interpolada de contexto não confiável: o caminho vem do diretório global de pacotes no runner. Segue o precedente do parecer `ci-postinstall-cli`.
- `scripts/placar-mutacao.py`: acrescenta aviso de `--desde` e contagem de `falhas`; só leitura de git (`rev-parse`, `tag --list`) com `--end-of-options`, sem rede, sem segredo, saída 0 mantida (placar, não portão). Sintaxe Python conferida (`ast.parse`).
- `.claude-plugin/plugin.json`: versão 0.47.0 para 0.47.1, só esse campo.

Ferramentas: `shellcheck` presente no PATH, mas sem script de shell alterado; `actionlint` ausente no ambiente (lacuna registrada); o CI do PR roda a bateria completa no sha. Não executei o `install.cjs` (sem instalação do pacote aqui e sem rede para o registro).

## Custo e rollback
Sem minutos nem recursos novos além da etapa extra de poucos segundos por job de CLI. Rollback: reverter o commit da release (reimplantar a 0.47.0); nenhuma migração envolvida.
