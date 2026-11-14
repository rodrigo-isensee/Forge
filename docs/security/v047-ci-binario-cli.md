---
tipo: revisao-seguranca
contrato: 1
pedido: v047-ci-binario-cli
branch: melhoria/v047-ci-binario-cli
commit: 4baade0eb738f0b40b0bc331a14a341f0fe6da69
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047-ci-binario-cli

## Gatilhos
CI/CD (`.github/workflows/ci.yml`) e execução de script de instalação de pacote no runner (`R-SEGURANCA`). Intervalo revisado: `origin/develop..114fd11b` (código em `4baade0e`; `114fd11b` só toca o parecer de devops).

## Achados
- A1 (recomendado) .github/workflows/ci.yml:329 · A autorização de script na instalação global ficou sem efeito no gerenciador atual e o instalador do binário agora roda explícito; se o gerenciador voltar a rodar o postinstall, ele roda duas vezes. Retirar a autorização quando confirmado, nas três linhas (329, 516, 620).

## Sondas

## Detalhe dos achados
Sem achado bloqueante. Conferido no diff `e60183d0..114fd11b` (5 arquivos; código em `.github/workflows/ci.yml` e `tests/test_ci_local.py`):

- Mesma origem, mesmo código: as três linhas (`.github/workflows/ci.yml:329`, `:516`, `:620`) acrescentam, depois da instalação global do pacote do CLI fixado em `2.1.296`, a execução do script instalador que vem dentro desse mesmo pacote, no caminho da raiz global. É o código que o postinstall já rodava com a autorização revisada em `docs/security/ci-postinstall-cli.md`; não entra fornecedor, pacote nem versão novos, e não há curinga. O `&&` impede rodar o instalador se a instalação falhar; a nova tentativa repete as duas etapas.
- Sem ganho de privilégio: o workflow tem `permissions: contents: read` no topo (`ci.yml:24-25`) e nos jobs `bateria` e `verificacoes`; `instalacao-quatorze` herda o do topo. Os três passos não recebem segredo nem `env:` novo; checkout com `persist-credentials: false`; gatilhos `pull_request`/`push`/`workflow_dispatch`, sem `pull_request_target`. SHAs das ações intactos.
- Ordem preservada contra `claude` falso: no job `verificacoes` o passo do CLI continua antes de qualquer código da branch (comentário em `ci.yml:615`), e a resolução da raiz global usa o modo global, que ignora a configuração de projeto do diretório de trabalho; nos outros dois jobs o código da branch já roda no mesmo runner, então não há fronteira nova.
- Verificação: `claude --version` logo depois falha o passo se o binário não ficou instalado. O teste `InstalacaoDoCliTest` (`tests/test_ci_local.py:570`) exige as três instalações com o instalador depois do pacote, na função `instalar`; rodado aqui: `Ran 1 test ... OK`.
- Custo (`R-CUSTO`): nenhum; pacote público e runner já em uso.
- Residual (informativa): o binário baixado pelo instalador é responsabilidade do script do fornecedor (integridade não reproduzida aqui); a versão fixa limita a janela, e subir a versão pede revisar o script de novo.

A1 em detalhe: evidência `ci.yml:329/516/620`; sem caminho de ataque (mesmo pacote nomeado e fixado), por isso recomendação; correção mínima: retirar a autorização de script das três linhas depois de um CI verde sem ela; esforço P; dono `devops-engineer`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte: a inteira roda no CI do PR (ainda sem execução nesta branch, PR não aberto); a prova funcional do passo é o e2e de instalação desse CI. Local: só `tests.test_ci_local.InstalacaoDoCliTest`. Lacunas: o runtime da stack, o gerenciador de pacotes, `actionlint`, `zizmor` e `gitleaks` ausentes no ambiente (rodam no CI: `actionlint` e `zizmor` no job `bateria`).
