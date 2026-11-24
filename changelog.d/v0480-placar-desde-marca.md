### Corrigido
- **Placar desde a marca (v0478 E138.3):** `scripts/placar-mutacao.py --desde` aceita a marca anterior na develop (o último commit que mudou a versão do manifesto) sem aviso, e a release do `bin/forge-changelog` sugere essa marca (ou a tag dela) em vez da última tag ancestral, que na develop era a v0.45.5.
