---
tipo: revisao-devops
contrato: 1
pedido: v047-sessao-automatica
branch: melhoria/v047-sessao-automatica
commit: 5f0547cc0864a1830cd32f51f6695b35fc772703
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-14
---
# Review de devops: v047-sessao-automatica

## Achados
- A1 (recomendado) bin/forge-fechar:856 · o mínimo do gh (2.47) e o parse da versão repetem-se em forge-fechar e preparar-estacao.sh (GH_MINIMO); ao subir o mínimo, os dois precisam mudar juntos. Fonte única seria melhor.

## Detalhes
Aprovado. Intervalo origin/develop...5f0547cc, classe C (SESSAO-AUTOMATICA, GH-VERSAO-MINIMA). Não toca `.github/`, `Dockerfile*`, `compose*` nem IaC; o parecer cobre scripts de estação e o passo 1 do forge-fechar.
- scripts/jarvis e jarvis-forge: só acrescentam `--permission-mode auto` aos args; sem mudança de privilégio fora do desejado (diretriz 28), sem interpolação nova.
- preparar-estacao.sh: `garantir_gh` usa o repositório oficial do GitHub CLI por https com keyring `signed-by`, só via `como_root`/`fazer`; respeita `--simular`; versão ilegível conta como antiga; o gh saiu da lista apt do Ubuntu (2.45) e ganhou passo próprio, com `feitos/faltas` zerados depois. Sem segredo, sem custo (`R-CUSTO`).
- forge-fechar passo 1: confere gh >= 2.47 antes de abrir ou mesclar qualquer coisa (`R-MAIN` intacto), usa `$gh` (FORGE_GH só em teste), busca `origin/homolog` somente leitura e sem `--force` (`R-VERIFY`). A falha da busca vira aviso; o forge-check decide.
- templates/projeto/CLAUDE.md: seção Sessão, sem termo de projeto (`R-NEUTRO`).
Ferramentas: shellcheck sobre os quatro scripts, rc=0; `bash -n` ok; `forge-check docs` rc=0; tests/test_sessao_automatica.py (10 testes) e tests/test_fechar_gh_versao.py (9 testes) OK. `actionlint` não consultado (sem mudança em workflow). A suíte completa roda só no CI.

## Custo e rollback
Sem minutos de CI novos nem recurso pago. Volta: reverter o commit 5f0547cc; a estação que já atualizou o gh segue com a versão nova, sem efeito colateral.
