---
tipo: engenharia
pedido: v0478
etapa: E57.39
branch: melhoria/v0479-pv-b3-pre-push
base: 20bbbd8d5ba5f13bcd15fe6d3f8dec18c9553bf2
autor: devops-engineer
data: 2026-11-20
---
# PR-VERDE B3: o envio local confere os registros (patch do `.githooks/pre-push`)

O `.githooks/pre-push` é arquivo em vigor e travado para os agentes; o item B3 do desenho `docs/propostas/v0479-pr-verde-de-primeira.md` vai como patch, `docs/engineering/v0479-pv-b3-pre-push.patch` (35 linhas acrescentadas, nenhuma removida), e só o dono aplica (D6; decisão do dono de 20/11 no pedido v0478: recomendações do desenho aceitas). O B1 (`bin/forge-testes --registros`) já está na `develop`.

## O que muda
Em `checagens_baratas`, depois das checagens que já existem (que não são tocadas), entra a conferência `python3 -I bin/forge-testes --registros --base origin/develop`. Só roda quando o HEAD é a ponta de uma branch enviada (a mesma regra do changelog). Ela só lê, busca a `origin/develop` antes e cobre o teto dos agentes, o índice, as specs de mutante, o mapa de testes, os pesos e o changelog.

| Situação | Saída | Efeito no envio |
|---|---|---|
| em dia | 0 | segue (imprime só o aviso, se houver, e o resumo `registros rc=`) |
| registro desatualizado | 1 | recusa, com as linhas `registro desatualizado:` |
| sem rede | 0 com aviso | segue; confere contra a base local, o CI confere (D6) |
| `bin/forge-testes` ausente ou link | (não roda) | aviso e segue, como as checagens de hoje (D6) |
| sem veredito (2), estouro do prazo (124), erro do intérprete | qualquer outra | recusa (falha fechada: caso de abuso do B3, nunca verde por defeito da conferência) |

O prazo padrão é 180 s (`FORGE_REGISTROS_PRAZO`, em segundos), com `timeout` quando existe. `--no-verify` segue proibido (`R-VERIFY`); o patch não adiciona opção de pular.

## Aplicar (dono, na cópia principal)
Com a branch `melhoria/v0479-pv-b3-pre-push` buscada (`git fetch origin`), em branch nova a partir da `develop`:
```bash
cd ~/Forge && git switch develop && git pull --ff-only origin develop
git switch --no-track -c melhoria/pv-b3-aplicar
git show origin/melhoria/v0479-pv-b3-pre-push:docs/engineering/v0479-pv-b3-pre-push.patch > "$TMPDIR/b3.patch"
git apply --check "$TMPDIR/b3.patch" && git apply "$TMPDIR/b3.patch"
git add .githooks/pre-push
git commit -m 'feat(pre-push): envio confere os registros (PR-VERDE B3)'
```
Como o arquivo é protegido, a catraca vai pedir o rótulo `afrouxa-regra` no PR (não afrouxa: só soma uma recusa).

## Testar
Numa cópia temporária (o que foi feito aqui) ou na própria árvore depois de aplicar:
```bash
git clone -q --no-hardlinks <repo> "$TMPDIR/prova" && cd "$TMPDIR/prova"
git update-ref refs/remotes/origin/develop <sha-da-develop>
git apply --check docs/engineering/v0479-pv-b3-pre-push.patch && git apply docs/engineering/v0479-pv-b3-pre-push.patch
git switch -q --no-track -c melhoria/prova
echo "refs/heads/melhoria/prova $(git rev-parse HEAD) refs/heads/melhoria/prova 0000000000000000000000000000000000000000" > "$TMPDIR/stdin.txt"
.githooks/pre-push origin <url> < "$TMPDIR/stdin.txt" ; echo rc=$?
```
Resultados medidos (base 20bbbd8d; sem `shellcheck` na estação, o que é aviso do próprio hook):
1. árvore em dia: rc 0, `registros rc=0 em 34 s`, o envio leve termina;
2. módulo de teste novo sem peso: `registro desatualizado: ... sem peso`, rc 1, `checagens baratas reprovadas`;
3. `tests/pesos-d4.json` ilegível: saída 2, recusa com "não deu veredito";
4. `bin/forge-testes` ausente: aviso e segue, rc 0;
5. `FORGE_REGISTROS_PRAZO=2`: saída 124, recusa.

## Riscos e pontos para o dono
- **Tempo:** 34 a 45 s medidos nesta estação, acima da meta do desenho (p95 abaixo de 20 s, R3). Não é defeito do patch (a conferência é do B1), mas o R3 manda cortar a conferência mais lenta para o CI e registrar. Sugestão: o `tech-lead` abrir cartão para paralelizar ou cortar o grupo mais lento de `REGISTROS`.
- **Falha fechada em saída fora de 0 e 1:** um defeito do B1 passa a barrar o envio até ser corrigido; a saída é rodar a conferência à mão. Escolhido pelo caso de abuso do desenho.
- **Sem rede:** o aviso vem do `forge-testes`, não do hook; a conferência segue contra a `origin/develop` local.
- O parecer de segurança do B3 (hook) é do `security-engineer`; o parecer de devops do patch fica em `docs/devops/`, em etapa própria.
