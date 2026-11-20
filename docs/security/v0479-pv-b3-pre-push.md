---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-b3-pre-push
commit: cb4f48b5e4bcad520fec12b58109c6b6ca30290a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0478 E57.48 (revalidação do patch PR-VERDE B3 do pre-push)

Revalidação por delta (`R-REVIEW`): `forge-check parecer delta` de `081067f0..cb4f48b5`; no domínio só `docs/engineering/v0479-pv-b3-pre-push.patch`. Lido também o delta de `docs/engineering/v0479-pv-b3-pre-push.md` (fora do domínio da ferramenta, mas é onde estavam A2 e A3). A rodada anterior (head `081067f0`, reprovado) fica no git. O patch não foi aplicado na branch; só numa cópia descartável em `$TMPDIR`, a partir da `origin/develop` (blob do hook `f9443600`, igual ao da base), onde `git apply --stat` lista só `.githooks/pre-push` (38 linhas acrescentadas, nenhuma removida), `bash -n` passa e o blob resultante é `f54dabe`, o mesmo do cabeçalho do patch.

Gatilhos: hook de envio (controle do Forge, arquivo protegido), execução de código da árvore no envio, variável de ambiente que decide o controle.

## Estado dos achados anteriores
- A1 (bloqueante) corrigido. Patch:17-19: `prazo` só aceita dígitos (`''|*[!0-9]*` recusa com `falhas=1` e esvazia `envios_reg`, então a conferência não roda e o envio cai); patch:26 chama `timeout -- "$prazo"`. Vazio cai no padrão 180 pela expansão `:-` e a conferência roda. Sondas S1 a S6 abaixo.
- A2 (recomendado) corrigido. Doc:28-34: o patch vem de `<sha-revisado>` (o commit revisado, nunca a ponta móvel), `git apply --stat` antes, com o aviso de que só `.githooks/pre-push` pode mudar, e `"${TMPDIR:-/tmp}"`.
- A3 (recomendado) corrigido. Doc:23-25: o texto descreve a validação só de dígitos e o `--`; doc:56-58 soma o caso 6 ao roteiro de teste, com a nota do bare vazio.

## Sondas
- S1 · FORGE_REGISTROS_PRAZO=--help .githooks/pre-push origin ../vazio.git, HEAD com tests/test_sonda_sem_peso.py sem peso · espera: rc 1, recusa sem rodar a conferência · obtido: rc 1, "deve ser um número de segundos inteiro (veio '--help')", checagens baratas reprovadas
- S2 · mesma cópia, FORGE_REGISTROS_PRAZO=--version · espera: rc 1 · obtido: rc 1, mesma recusa
- S3 · mesma cópia, FORGE_REGISTROS_PRAZO=-5 e =abc · espera: rc 1 · obtido: rc 1 nos dois, mesma recusa
- S4 · mesma cópia, FORGE_REGISTROS_PRAZO= (vazio) e sem a variável · espera: rc 1, registro desatualizado · obtido: rc 1 nos dois, "test_sonda_sem_peso sem peso em tests/pesos-d4.json"
- S5 · mesma cópia, FORGE_REGISTROS_PRAZO=2 · espera: rc 1, estouro · obtido: rc 1, "não deu veredito (saída 124)"
- S6 · corpus legítimo: commit sem o teste sem peso, FORGE_REGISTROS_PRAZO=180 e =99999999999999999999999 · espera: rc 0 · obtido: rc 0 nos dois, checagens baratas ok, envio leve

## Detalhe
**Só aperta?** Sim. O delta só troca o prazo cru pelo validado e acrescenta `--`; nenhuma linha removida do hook, `falhas` só recebe 1. `prazo` e `envios_reg` não estão na lista `local` de `checagens_baratas` (`.githooks/pre-push:339`), mas nenhum outro trecho do hook usa esses nomes e o hook não usa `set -u`; sem efeito de segurança (estilo, do `tech-lead`). A mensagem de recusa ecoa o valor da variável sem filtrar caracteres de controle: o valor vem do próprio ambiente de quem envia, sem ganho para ninguém; não é achado. Prazo enorme ou `0` equivale a sem limite, mas a conferência roda (S6); não é desvio.

`<sha-revisado>` no roteiro: é o commit deste ciclo de pareceres; este parecer vale para `cb4f48b5`. Se o patch mudar depois dele, o `parecer delta` o reabre.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check parecer delta`, `git apply --stat/--check`, `bash -n`, sondas no hook aplicado numa cópia descartável. Lacunas: `shellcheck` e `gitleaks` fora do PATH desta estação (o CI roda a bateria). Suíte não rodada localmente; o parecer não substitui o CI do PR que aplicar o patch.
