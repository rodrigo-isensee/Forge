---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.1
branch: melhoria/release-0.47.1-b
commit: 5b10ba818345f45e573d3f148c0b3763d4257bcf
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: release 0.47.1 sobre o topo da develop (E2.37)

branch: melhoria/release-0.47.1-b · head revisado: 5b10ba818345f45e573d3f148c0b3763d4257bcf

Escopo: o intervalo `origin/develop..5b10ba81` (base 067b2a9f, um commit: a junção dos fragmentos do #554 e do #561 à entrada [0.47.1]) e, contra a homolog, o topo que vai ser promovido: os 9 itens, a correção do #558, o #554 e o #561, conferidos pelos pareceres de segurança de cada item.

## Gatilhos
`R-SEGURANCA`: a release publica a versão usada por todos os projetos; o conteúdo promovido toca hooks (`hooks/conformidade.py`, `hooks/agentes.py`, `hooks/_comum.py`, `hooks/hooks.json`), o CI (`.github/workflows/ci.yml`), `bin/`, a migração 0.47.1 e o modelo de projeto (`templates/projeto/.githooks/`).

## Achados

## Sondas

## Detalhe dos achados
Verificações no head, estáticas e locais:
- Intervalo `origin/develop..5b10ba81`: só `CHANGELOG.md` (+2 linhas na [0.47.1]) e a remoção de `changelog.d/mp1311-pre-envio-fabrica.md` e `changelog.d/v047-heredocs-orcamento.md`; o texto movido é igual ao dos fragmentos. Sem código, hook nem workflow.
- Cobertura por item (12 pareceres de segurança, todos `aprovado`): o `commit:` de cada um é ancestral do head e o tree fora de `docs/` e `changelog.d/` entre ele e o lado da branch no merge é igual (mp1311-pre-envio-modelo, mp1311-fechar-cartao, v047-ci-binario-cli, v047-develop-vermelho, v047-fila-suite-espera, v047-fixture-pid-sandbox, v047-heredocs-orcamento, v047-hook-erro-libera, v047-placar-mutacao), com três ressalvas conferidas:
  - mp1311-pre-envio-fabrica (#554): depois do parecer (f30ac8d2) a branch só mudou testes (`48bf85e8`, `6035e27c`: `tests/test_pre_envio_brief.py`, `tests/mutantes/mp1311-pre-envio-fabrica-2.json`) e trouxe a develop por merge; o código do PR (`bin/forge-check`, `bin/forge-testes`) é o revisado.
  - v047-ambiente-sem-auto-update: delta pós-parecer só em `tests/test_reval_delta.py` (registro de citação), revalidado por delta pelo QA e pelo review.
  - mp1311-modelo-seguranca (#551, squash): `migrations/0.47.1/migrar` e `LEIA.md` iguais ao commit do parecer (c734a22a); diferença só em `tests/test_forge.py`.
- Manifesto e versão: `.claude-plugin/plugin.json` em 0.47.1, igual à primeira entrada versionada do CHANGELOG; `changelog.d/` só com o README.
- `hooks/hooks.json`: 18 hooks, todos `python3` com `-s -E` (HOOK-ERRO-LIBERA mantido no topo).
- `.github/workflows/ci.yml` contra a homolog: só o `install.cjs` do pacote já fixado (`@anthropic-ai/claude-code@2.1.296`, `--allow-scripts` restrito a ele) nas três instalações; `permissions`, gatilhos e gate não mudam (coberto pelo parecer v047-ci-binario-cli).
- Varredura do diff `origin/homolog..HEAD` por padrões de segredo (token de forja, chave de nuvem, chave privada, token de chat) e por caminho pessoal (`/home/<usuário>`, `/Users/`): sem ocorrência.
- `forge-check docs`: sem erro. Suíte inteira: roda no CI do PR da release (sem PR aberto agora); este parecer não substitui o CI verde do head promovido.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Lacuna: `gitleaks`, `actionlint` e `zizmor` ausentes do PATH; substituídos pela leitura do diff e pela varredura por padrões.
