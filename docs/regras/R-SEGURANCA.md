---
id: R-SEGURANCA
titulo: Parecer de segurança quando há gatilho
verificada_por: `forge-check classe` e `forge-check pr`; hook `parecer` (no PR e no merge)
---
# R-SEGURANCA: Parecer de segurança quando há gatilho

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time.

Revisar em: 2027-01-07
Medida: 50 de 51 branches juntadas sem parecer de segurança na versao-035 (estudo 0.43.1)

- Entrega que toca um **gatilho** tem parecer do `security-engineer` em `docs/security/<pedido>.md`, na mesma passada do review e do QA, em qualquer classe. Sem gatilho, a classe C também o pede.
- Gatilhos: autenticação ou autorização; dados pessoais (LGPD); segredos e configuração (`.env*`, variáveis do CI, credenciais); dependência nova ou versão maior; webhook ou endpoint externo; banco (migração, permissão, consulta com entrada); CI/CD (`.github/`); Docker, Compose e IaC; controles do Forge (`hooks/conformidade.json`, `docs/regras/`, `tests/catraca.py`, `tests/config.json`). Quem os acha: `skills/engineering-practices/rigor-por-classe.md`.
- `riscos-aceitos` só vale com o **aceite do usuário** em `docs/security/aceites/<pedido>.md`, escrito à mão por ele para o `commit` do parecer; nenhum agente grava essa pasta.
- O parecer só vale gravado pelo papel `seguranca`; o QA e o `tech-lead` não declaram "seguro".
- **O que bloqueia:** o achado só é `bloqueante` quando toca um gatilho desta regra, inclusive em qualquer arquivo de `hooks/` ou em caminho de `PROTEGIDOS` de `tests/catraca.py`, ou quando é defeito de comportamento provado. Sempre com evidência: repro, teste ou `arquivo:linha` com o caminho de ataque. O resto é recomendação, que volta e é corrigida antes do merge (G1.2: fora do delta, a nova vira cartão; o bloqueante pede `explorável: S<n>`); promovê-la a bloqueante pede a marca `critério mudou:` com o motivo (`R-REVIEW`).
