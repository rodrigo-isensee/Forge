---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-ci-binario-cli
commit: 4baade0eb738f0b40b0bc331a14a341f0fe6da69
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 (E1.142, code review da E1.130/E1.134, CI-NPM-BINARIO)

Intervalo `origin/develop..114fd11b` (base e60183d0); o código revisado é o do 4baade0e, e o 114fd11b só traz o parecer de devops. Instância que não fez a entrega. Diff que conta (M14): 21 linhas (`.github/workflows/ci.yml` 3+/3-, `tests/test_ci_local.py` 15+), um comportamento só.

## O que está certo
- A causa e a correção batem com o pacote publicado: o `package.json` do `@anthropic-ai/claude-code@2.1.296` no registro declara `"postinstall": "node install.cjs"` e o tarball traz `package/install.cjs`. A função `instalar` passa a rodar esse mesmo comando de forma explícita depois do `npm install -g`, nas três instalações (e2e :329, validação do plugin :516, portão das provas :620). Versão segue fixada.
- `install.cjs` é idempotente (`placeBinary` trata `EEXIST` e sobrescreve), então rodar de novo onde o postinstall já rodou não quebra. O `&&` faz a falha do pacote cair na nova tentativa existente, e `claude --version` segue como conferência final.
- Nenhum passo afrouxado, sem permissão nova e sem custo (`R-CUSTO`); parecer de devops aprovado no mesmo código (4baade0e).
- O teste novo exige exatamente três instalações (afirma o mínimo, checklist 11), o `install.cjs` depois de `claude-code@` e a forma da função. Os quatro mutantes declarados cobrem cada instalação e a ordem.

## Ferramentas (citadas, sem refazer)
- `python3 -m unittest tests.test_ci_local.InstalacaoDoCliTest` no head: `Ran 1 test`, `OK`.
- Mutação e cobertura: ver `## Detalhes`. Sem shell tocado fora do `run:` inline (sem `shellcheck` aplicável).
- CI: a branch não tem PR nem run (`gh run list --branch`: vazio). A prova de que o e2e volta a passar é o CI do PR, obrigatório para o merge (`R-FLUXO`).

## Achados
- A1 (recomendado) tests/test_ci_local.py:575 · O teste lê o texto do ci.yml, não executa a instalação; aceitável porque executar exige rede e o registro, mas a prova do comportamento fica no e2e do CI do PR, que precisa sair verde antes do merge (R-FLUXO).

## Sondas

## Detalhes
Mutantes: `bin/forge-mutante tests/mutantes/v047-ci-binario-cli.json` em b44accb7 (o 4baade0e mais pareceres, sem código novo): M1 `ci.yml:329`, M2 `:516`, M3 `:620` e M4 (ordem, `:516`) `morreu`. `--cobertura --base e60183d0`: `não coberto: .github/workflows/ci.yml`, a saída fixa da ferramenta para arquivo que não é Python; as três linhas mudadas têm mutante declarado e morto, então não há guarda sem mutante.
Checagem do `&&`: com falha do `npm install`, o `install.cjs` não roda e `instalar` sai com erro, o que leva à nova tentativa; trocar `&&` por `;` daria o mesmo código de saída (o `install.cjs` ausente também falha), mutante equivalente, sem achado.

## Parecer
Aprovado. A correção é a mínima, usa o próprio postinstall do pacote, cobre as três instalações e tem teste e mutantes. A1 não devolve: só lembra que o merge depende do e2e verde no CI do PR.
