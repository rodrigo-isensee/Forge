---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-trilha-forge-check
commit: 95994eec3b874dff23e39f68a6b4e7181d4205d5
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 E91.7 (TRILHA-FORGE-CHECK, revalidação)

Gatilhos: controle do Forge (bin/forge-check: falha fechada do `parecer conferido`, VOLTAS-REVISOR-WT M1/M8).

Delta lido (`forge-check parecer delta`): `a318e97d..95994eec`. No domínio só entrou `bin/forge-check`, com `de_outra_branch` (`:2426-2431`) e o `continue` em `ultimos_do_historico` (`:2442`), que vale para o `pr` (`:2012`), o `check` (`:3360`) e a volta (`conferidos_fora_da_ref`). Os testes e o changelog ficam fora do domínio. A rodada anterior (aprovado em a318e97d, sem achados) está no git e não muda: o restante do diff não foi tocado.

Veredito da mudança: ela não aperta nada. O caminho com P legível não muda. Com P ilegível, a linha que antes reprovava ("rode git fetch") passa a ser ignorada sempre que nenhum parecer citado tem o nome igual ao último segmento da branch. Ignorar a linha equivale a ela não existir, então somem as checagens M1 ("fora da branch, quem retoma a traz") e M8 (blob) do `pr` para aquele arquivo (`:2019`). Isso é falha aberta, não só a cura do falso positivo do K-156.

## Achados
- A1 (bloqueante) bin/forge-check:2431 · de_outra_branch supõe parecer com nome igual ao slug da branch, o que nada impõe: o modelo é docs/<pasta>/<pedido>.md e o Forge tem pareceres com outro nome. A linha da própria branch com P ilegível e outro nome deixa de reprovar e M1/M8 somem (S1-S4)

## Sondas
- S1 · ultimos_do_historico, branch melhoria/v0479-trilha-forge-check, linha `- d: docs/reviews/v0478.md aprovado: parecer conferido dddd(40)` (parecer da branch nomeado pelo pedido) · espera: ilegiveis=1 · obtido: de_outra=True ilegiveis=0
- S2 · mesma branch, linha `- d: docs/security/V0479-Trilha-Forge-Check.md: parecer conferido dddd(40)` · espera: ilegiveis=1 · obtido: de_outra=True ilegiveis=0
- S3 · mesma branch, linha `- d: docs/security/x/v0479-trilha-forge-check.md docs/qa/outra.md: parecer conferido dddd(40)` · espera: ilegiveis=1 · obtido: de_outra=True ilegiveis=0
- S4 · mesma branch, linha `- d: docs/security/v0479-trilha-forge-check-2.md: parecer conferido dddd(40)` · espera: ilegiveis=1 se o arquivo é da branch · obtido: de_outra=True ilegiveis=0

## Detalhe dos achados
**A1.** Evidência: `bin/forge-check:2431` decide "de outra branch" pelo nome do arquivo citado no texto da linha (`branch.rsplit("/", 1)[-1] not in nomes`), e `:2442` descarta a linha. A premissa "o nome é o slug" não vale. O modelo do papel e do `_modelo.md` nomeia o parecer `docs/<pasta>/<pedido>.md`. No próprio Forge, mais de 30 pareceres têm `branch:` diferente do nome (ex.: `docs/reviews/hook-vigia.md`, branch `melhoria/hook-vigia-v2`; `docs/reviews/impl-n-qa.md`, branch `melhoria/impl-n-qa4`). Nos projetos, `pedido != slug` é o caso comum. O comparador também é sensível a maiúsculas e não reconhece subpasta (S2, S3).

Caminho: uma branch retomada sem o commit do parecer conferido. É o alvo do M1: a branch foi recriada da base ou o P ficou fora do fetch. O git não lê o P. Se o parecer não se chama como o slug, a linha é descartada, `ilegiveis` fica vazio e `conferidos` não tem o arquivo. O `pr` (`:2012-2022`) não emite nem "ilegível" nem "fora da branch", e um parecer não conferido pelo Jarvis passa pelo portão. A volta (`conferidos_fora_da_ref`) também não aponta o parecer a trazer. Quem forja a linha não ganha nada que já não tivesse, porque apagar a linha dá o mesmo efeito. O dano vem do erro honesto em que a falha fechada existia para pegar.

Severidade: média, porque é um portão do fluxo da fábrica que abre no caso comum dos projetos. Esforço: P. Dono: o autor da E91.5 (forge-check).

Correção mínima: não decidir pelo nome. A linha só é de outra branch se cada parecer citado (caminho com âncora `(?<![\w/])docs/<pasta>/<nome>.md`, sem subpasta) existe na ref conferida e tem `branch:` no frontmatter diferente da `branch`. Linha sem parecer citado, parecer ausente na ref ou `branch:` igual continuam ilegíveis (falha fechada). O caso do K-156 segue curado: o parecer do item mesclado por squash está na base com a `branch:` dele. Teste de abuso: S1 (nome pelo pedido, `branch:` da própria branch na ref) com P ilegível dá `ilegiveis=1`, e S1 com `branch:` de outra branch na ref dá `ilegiveis=0`.

Sem afrouxamento nos outros casos tentados: linha com pareceres das duas branches, linha sem parecer, nome da branch depois do sha, `branch=None` e prefixo forjado (`xdocs/...` ao lado do parecer da branch) continuam contando como ilegíveis.

Suíte: não rodei a suíte local (o brief diz "sem suíte local"). As sondas chamaram `ultimos_do_historico` e `de_outra_branch` do `bin/forge-check` em 95994eec, sobre um repositório descartável em TMPDIR.

## Riscos aceitos e ferramentas
Sem risco aceito. Não estão no PATH: gitleaks, semgrep, zizmor, actionlint e osv-scanner. Isso é lacuna, sem efeito aqui: o delta não toca workflow, dependência nem credencial.
