---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae5-retro-pendentes
commit: 8d2efa1fdc94a5962a2323c38592a079a23c1612
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-ae5-retro-pendentes (pedido v0478, etapa E58.103, revalidação)

Revalidação por delta do parecer anterior (commit ad1d8f17, aprovado sobre 2d378b98; a rodada anterior fica no git).

Gatilhos: ferramenta de controle do Forge (bin/forge-check).

## Delta lido
`forge-check parecer delta docs/security/v0479-ae5-retro-pendentes.md`, intervalo `2d378b98..8d2efa1f`, sem o que veio da base. Os merges da develop 1fb80933 e 26b75512 entraram sem resolução à mão (`git show --cc 26b75512` só com o cabeçalho); o que eles trazem (#756, #758) é da base e fica fora. `git diff origin/develop HEAD` confirma que, em código, a branch só acrescenta o `retro --pendentes`; a develop avançou depois (b18d3ea3, #762), o que não pesa nesta branch. Da branch, só o commit 8d2efa1f:
- bin/forge-check:5862-5864: `COBRE_DA_RETRO`, `VERSAO_DA_TAG` e `REF_DA_MAIN` passam de `re.compile(...)` a texto; os quatro usos (bin/forge-check:5896, 5909, 5917, 5927) chamam `re.match`/`re.fullmatch` com o mesmo padrão e o mesmo modo (`match` continua `match`, `fullmatch` continua `fullmatch`). Equivalente em comportamento; `grep` não acha outro uso dos três nomes no repositório.
- tests/mutantes/v0478-ae5-retro-pendentes{,-2,-3}.json: só o `de`/`para` acompanham o texto novo; `forge-mutante --conferir --base 2d378b98`: "o trecho de cada spec do diff está no lugar".

## Achados anteriores
Nenhum aberto.

## Só aperta (confirmação escrita)
Confirmação: só aperta. O delta da branch é refatoração sem efeito: as três expressões e os seus modos de casamento ficam idênticos, então a validação de `--main` (ref sem opção, primeiro caractere alfanumérico, bin/forge-check:5917), de `--desde` e das tags `vX.Y.Z` continua com o mesmo conjunto aceito; nenhum portão, hook ou caminho de escrita muda, e o subcomando segue só de leitura.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira: não rodada aqui (brief: sem suíte local); vale o CI do PR para o merge. Rodados: `tests.test_retro_pendentes` e `tests.test_reval_delta` (30 OK). A execução dos mutantes foi barrada pelo hook R-TETO (fila de tarefa pesada) e não foi contornada; fica com o QA. Ferramenta ausente no ambiente: gitleaks, semgrep e osv-scanner (lacuna; delta de 16 linhas no domínio lido à mão, sem segredo nem dependência nova).
