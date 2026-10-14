### Adicionado
- **Changelog por fragmentos:** cada PR grava a entrada em `changelog.d/<branch>.md` (`bin/forge-changelog novo`), sem editar o `CHANGELOG.md`, e a release junta e apaga (`bin/forge-changelog release`); acaba o conflito entre PRs paralelos. O CI exige o fragmento novo (a linha em `[Não publicado]` segue aceita na transição) e o PR de release exige `changelog.d/` vazio.
