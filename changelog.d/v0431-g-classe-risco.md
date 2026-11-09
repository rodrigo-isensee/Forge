### Adicionado
- `forge-check classe [--base REF] [--head REF] [--json]`: classifica o diff da branch em T (trivial: só documentação comum, só testes ou até 20 linhas), N (normal) ou C (controle: PROTEGIDOS e SENSIVEIS da catraca, regras, agentes, skills, pipeline e infraestrutura, `.claude/`, `.mcp.json` e os testes de controle, EXT-B1), com o motivo, os portões e os pareceres exigidos; na dúvida a classe sobe (P5 da 0.43.1, rigor proporcional ao risco, decisão do dono de 2026-11-08).

### Alterado
- `forge-check pr` (e com ele o `forge-fechar`, o hook `parecer` e a catraca do CI, que o chamam) exige os pareceres pela classe: T só review, N review e QA, C review, segurança e QA; devops e segurança dos gatilhos de hoje somam por cima, e a classe nunca exige menos que eles (P5, versao-0431).
