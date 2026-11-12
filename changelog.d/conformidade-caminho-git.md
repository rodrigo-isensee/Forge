### Corrigido
- Hook conformidade: escrita pelo Bash com `$(…)`, crase ou variável antes de um nome do diretório do git (`$(git rev-parse --git-common-dir)/forge/…`, `d=<raiz>/.git; cp x $d/config`) passa a cair nas regras de `.git/forge/`, `.git/config`, `.git/hooks/` e `.git/` (A2 da segurança, v046 E20.6).
