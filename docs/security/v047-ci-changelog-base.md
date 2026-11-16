---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-ci-changelog-base
commit: 136cf316b34434dbefc9dbe3dd41ca98c49b3fbb
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v047-ci-changelog-base (E1.52, head 136cf316)

## Gatilhos
Workflow de CI (`R-SEGURANCA`): o passo que barra PR da fábrica sem fragmento de changelog.

## Achados
- A1 (recomendado) .github/workflows/ci.yml:521 · o teste do passo não cobre o caso de conflito (checkout sem commit de junção); sem prova de que HEAD^1 falha fechado ali. Sem caminho de ataque: PR com conflito não é mesclável.

## Sondas

## Detalhe dos achados
A1: com conflito de merge o checkout do evento é a cabeça do PR, não uma junção; HEAD^1 seria o pai do último commit do PR e a checagem ficaria mais fraca. Não há caminho de ataque: o PR não é mesclável nesse estado e o job `bateria` é obrigatório para o merge. Mesmo comportamento da catraca (`.github/workflows/catraca.yml:39`) e dos passos de pareceres (`ci.yml:538,556,603`). Correção opcional: confirmar que o commit é de junção (dois pais) antes de usar HEAD^1. Esforço P. Dono: devops-engineer.

Análise do controle (sem bloqueante):
- O primeiro pai do commit de junção é montado pelo GitHub (ponta atual da base); o autor do PR não o controla. O SHA do evento é que ficava velho.
- O job `bateria` usa checkout com `fetch-depth: 0` (`ci.yml:428-431`), logo HEAD^1 existe. Se não existisse, a atribuição com `$(...)` falha sob o `bash -e` padrão do runner e o passo fica vermelho (falha fechada, não pula).
- O passo mantém `if` idêntico (pull_request com base develop) e a saída vai a `forge-changelog conferir --base "$BASE"` entre aspas; sem entrada de PR em shell (`BASE` vem de git, não de `github.event`), o que reduz superfície de injeção. Permissões do job seguem `contents: read`.
- Não abre caminho para pular a checagem: o `if` não mudou e o teste novo exige o BASE esperado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Provas: o teste novo `test_changelog_compara_com_o_pai_do_commit_de_juncao_e_nao_com_a_base_do_evento` em `tests/test_ci_local.py:946` passou (OK, 1 teste). Sonda manual num repo temporário (develop andou, PR altera `agents/a.md` sem fragmento, commit de junção com `commit-tree`): `forge-changelog conferir --base "$(git rev-parse HEAD^1)"` saiu com erro e a mensagem "Registre a mudança num fragmento novo em changelog.d/"; o passo ainda barra PR sem fragmento. Suíte inteira: só no CI; este parecer não a rodou (sem PR aberto). Ferramentas de varredura (zizmor, actionlint) não rodadas localmente; lacuna registrada, rodam no CI. M1 do arquivo de mutantes ligado ao teste novo (`tests/mutantes/v047-ci-changelog-base.json`).
