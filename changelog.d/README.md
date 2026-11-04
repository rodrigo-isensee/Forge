# changelog.d

Guarda os fragmentos de changelog de cada PR para a `develop` (ADR 0006), um arquivo `<branch-sem-prefixo>.md` por PR.
Crie um fragmento com `bin/forge-changelog novo <tipo> "<texto>"`.
A release junta os fragmentos no `CHANGELOG.md` e os apaga (`bin/forge-changelog release <versão> <data>`), mas não este arquivo, que o `forge-changelog` ignora.
Este arquivo mantém a pasta no git depois da release: agentes e skills a citam e o teste de referências a exige.
