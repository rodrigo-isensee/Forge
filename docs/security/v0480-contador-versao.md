---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-contador-versao
commit: 362b45ad31e23cc33af7abe42f7d08758ba7e37c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E103.9, revalidação do CONTADOR-DA-VERSAO)

Volta única. Rodada anterior: parecer `aprovado` em `fb4d5390` (commit `f70754f7`, no git). Delta lido por `forge-check parecer delta`: `fb4d5390..362b45ad`, no domínio só `bin/forge-contador` e a linha da skill `fluxo-do-pedido`; fora do domínio, os specs de mutantes, o teste e o fragmento do changelog.

Gatilhos: nenhum (sem autenticação, segredo, dependência, rede, CI, banco nem controle do Forge).

## Detalhe
Achados anteriores: nenhum. As duas observações de robustez repassadas ao `tech-lead` e ao `qa-engineer` estão resolvidas no head (sondas locais num repositório temporário):

- `--data 9999-12-31` com vazão positiva: `forge-contador: date value out of range`, saída 2 (`bin/forge-contador:143`, `OverflowError` capturado). `--data 0001-01-01` idem, saída 2.
- Quadro com bytes fora de UTF-8 (`\xff\xfe`): `forge-contador: bad.md: não é UTF-8`, saída 2 (`:117`); o mesmo para o histórico. `.forge/config.json` fora de UTF-8 também sai com 2 (`UnicodeDecodeError` é `ValueError`, `:67`).

O que mudou, pelo lado da segurança:
- **Contagem por PRs sem `changelog.d/`** (`:51-58`): `git log --first-parent --format=%s <marca>..<ref>`, por lista de argumentos, sem shell, só leitura; a marca vem de `tag --list v[0-9]*` (não começa com `-`). `ls-tree -z` evita a citação de nomes com bytes especiais. A saída imprime só números ou o literal "sem contagem".
- **`errors="replace"` no git** (`:20`): só decodificação; nada é executado a partir da saída.
- **`--ref` iniciado por `-`:** `--ref=--output=<dir>/x` continua saindo com 2 em `git tag --merged` (objeto malformado), nenhum arquivo criado. O argv é do próprio operador; sem fronteira de confiança, segue como endurecimento opcional (`rev-parse --verify` antes do uso).
- **`--historico` sem `--quadro`:** recusado pelo argparse, saída 2.
- **Skill:** só troca `bin/forge-contador` por `forge-contador` no PATH do plugin; sem efeito de segurança.

Teste: a suíte inteira fica no CI; o teste novo não foi rodado nesta volta (o delta do teste está fora do domínio); as sondas acima cobrem as duas saídas pedidas.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura do delta e sondas locais; o varredor de segredos não está no PATH desta estação (lacuna registrada, sem instalação); o delta não traz credencial nem padrão de segredo à leitura.
