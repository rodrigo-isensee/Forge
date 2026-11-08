### Alterado
- **CHANGELOG-BRANCH:** a regra "o fragmento do changelog tem o nome da branch" sai do teste que lia o estado do git e passa ao `bin/forge-changelog conferir`, com `--branch` (senão `GITHUB_HEAD_REF`, senão o HEAD), conferida antes de todo atalho do `conferir`; em `melhoria/*`, fragmento novo com outro nome sai com rc 1 (decisão 2 do estudo-custo-suite).
