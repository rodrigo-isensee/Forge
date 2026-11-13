---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.0
branch: melhoria/release-0.47.0-b
commit: 0867f7157f37ca5ea76ef31824cbb159c215086f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: release 0.47.0, marca refeita (E2.22)

branch: melhoria/release-0.47.0-b · head revisado: 0867f7157f37ca5ea76ef31824cbb159c215086f

Escopo: a entrada 0.47.0 do CHANGELOG depois da junção dos PRs 541, 544, 542 e 543 (e dos quatro fragmentos) e, contra a main, o domínio de segurança. Substitui o parecer anterior da marca (branch `melhoria/release-0.47.0`, head 72bb4008), que cobria o delta até ali.

## Gatilhos
`R-SEGURANCA`: a release publica a versão usada por todos os projetos; o delta toca o CI (`.github/workflows/ci.yml`, só comentários), o script de varredura de contribuição e a regra do Jarvis.

## Achados
- A1 (recomendado) tests/test_hooks.py:1011 · com carga 2x o teto do teste do gh pendurado passa do prazo do hook; ainda pega o `sleep 30`. Registrado no parecer v047-teste-carga (A1); sem caminho de ataque.

## Sondas

## Detalhe dos achados
Verificações no head, estáticas e locais:
- CI: o delta do PR 542 em `.github/workflows/ci.yml` (`:432-437`, `:557-559`) é só comentário; `permissions`, `needs`, gate e agregador não mudam. A mudança de comportamento desse PR está em testes (`tests/test_ci_local.py`), que fixam o hash do `run` do gate.
- `scripts/verificar-contribuicao.sh:55`: a troca de `@` por `@/` devolve a barra ao home do runner. Sondado com o regex `pessoal` do script: `/home/runner/work/x` passa; `/home/runner//home/joao/x` e `/home/runner/home/joao/y` são acusados, então o mascaramento não abre contorno do bloqueio de caminho pessoal. `python3 -m unittest -q test_forge.VerificarContribuicao`: 15 testes, OK.
- `agents/jarvis.md` e skills: só texto de processo (criar a worktree antes de delegar; sem nome de stack). Nenhum hook, `bin/`, `stacks/` nem manifesto muda neste delta; `plugin.json` segue 0.47.0, JSON válido, igual ao topo do CHANGELOG.
- Entrada do CHANGELOG: afrouxamentos declarados com motivo (PR-HOOK-PRAZO confia em arquivo local gravado com o sha256 do `forge-check` do plugin; testes de tempo pela carga com teto 2x) e as guardas de produção não afrouxadas no delta.
- Varredura do diff por padrões de segredo (token de forja, chave de nuvem, chave privada, senha): sem ocorrência. Caminhos pessoais nas linhas adicionadas: só descrição em docs/qa e docs/reviews.
- `forge-check docs`: sem erro. Suíte inteira: roda no CI do PR da release (sem PR aberto agora).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Lacuna: `gitleaks`, `actionlint` e `zizmor` ausentes do PATH; substituídos pela leitura do diff.
