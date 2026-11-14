---
tipo: revisao-devops
contrato: 1
pedido: v047
branch: melhoria/v047-ci-binario-cli
commit: 4baade0eb738f0b40b0bc331a14a341f0fe6da69
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-14
---
# Review de devops: v047-ci-binario-cli

## Achados

## Detalhes
Aprovado. Causa: no gerenciador de pacotes 11.19.1 do runner o `--allow-scripts` deixou de rodar o postinstall do `@anthropic-ai/claude-code`, e o `claude` saiu sem o binário nativo ("claude native binary not installed", job 132396975978, passo "marketplace add" do e2e). Correção em `.github/workflows/ci.yml` (três ocorrências, linhas 329, 516 e 620): a função `instalar` roda o `install.cjs` do pacote global depois da instalação global, o comando que a própria mensagem de erro indica. Versão continua fixada (2.1.296); o passo seguinte `claude --version` confere o binário; a nova tentativa por rede cobre as duas etapas. Nenhum passo afrouxado ou pulado, `permissions:` e SHAs das ações intactos.
Teste (E1.134): `tests/test_ci_local.py` `InstalacaoDoCliTest` falha se alguma das três instalações do CLI não roda o `install.cjs` depois da instalação do pacote; quatro mutantes em `tests/mutantes/v047-ci-binario-cli.json` (um por instalação e a ordem trocada) morrem. Sem mudança no domínio do parecer desde 49a8aab (`forge-check parecer delta`: nenhum arquivo do domínio mudou).
Ferramentas: `shellcheck` presente, não aplicável ao trecho inline; `actionlint`, o runtime JavaScript e o gerenciador de pacotes ausentes no ambiente (lacuna): a prova é o CI do PR. Parecer escrito pelo mesmo agente que entregou a mudança, sem revisão independente.

## Custo e rollback
Sem custo novo (R-CUSTO): segundos de CI por job. Rollback: reverter o commit; o e2e volta a falhar com o gerenciador atual.
