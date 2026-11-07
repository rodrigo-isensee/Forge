### Adicionado
- Placar de mutação por release: `scripts/placar-mutacao.py --desde <tag>` roda o `bin/forge-mutante` uma vez por spec da amostra (a fixa `tests/mutantes/placar.json` mais as specs novas desde a tag, até 8) e imprime a linha `placar:`, que o `tech-lead` acrescenta a `docs/engineering/placar-mutacao.md` na release; medida, não portão (M-5, versao-041).
