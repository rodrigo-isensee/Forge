---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-ci-binario-cli
commit: 4baade0eb738f0b40b0bc331a14a341f0fe6da69
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047-ci-binario-cli

Escopo (E1.144): intervalo `origin/develop..114fd11b` (base e60183d0). Mudança de código: três linhas de `.github/workflows/ci.yml` (329, 516, 620) e o teste `InstalacaoDoCliTest` em `tests/test_ci_local.py`, com quatro mutantes. Sem especificação de UX nem contrato de API (correção de CI): a obrigação é a do pedido, o CLI instalado com binário nativo nas três instalações. Instância que não fez a entrega.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Cada instalação global do CLI roda o `install.cjs` em seguida (E1.134) | `InstalacaoDoCliTest.test_toda_instalacao_global_do_cli_roda_o_instalador_do_binario_em_seguida` | exatamente 3 instalações; instalador depois do pacote; função e `; }` intactos | passou (H=ok, base=falha) |
| Nenhuma das três instalações perde o instalador (M1, M2, M3) | mesmo teste | uma instalação por mutante | mutantes morreram |
| Ordem: instalador depois do pacote (M4) | mesmo teste | ordem trocada | mutante morreu |

## Cenários e resultado real
- Teste novo local: `python3 -m unittest tests.test_ci_local.InstalacaoDoCliTest` → `Ran 1 test ... OK`.
- Vermelho antes do verde: `forge-testes --vermelho origin/develop --modulos tests.test_ci_local` (rc=0):
  - `vermelho: base=e60183d0a41d head=114fd11b894f módulos=test_ci_local (restrito por --modulos)`
  - `revertidos à base: .github/workflows/ci.yml, changelog.d/v047-ci-binario-cli.md, docs/devops/v047-ci-binario-cli.md`
  - `tests.test_ci_local.InstalacaoDoCliTest.test_toda_instalacao_global_do_cli_roda_o_instalador_do_binario_em_seguida · H=ok · B=falha · prova (asserção)`
  - `contagem: não prova (passa na base)=73; prova (asserção)=1`
- Mutação (`bin/forge-mutante tests/mutantes/v047-ci-binario-cli.json`, rc=0): `rev=114fd11b894f`; M1 morreu (ci.yml:329), M2 morreu (:516), M3 morreu (:620), M4 morreu (:516). Nenhum sobrevivente.
- Cobertura de mutantes (`forge-mutante --cobertura --base e60183d0`, rc=0): `não coberto: .github/workflows/ci.yml` (YAML não é Python, a checagem não lê); conferido à mão: as três linhas mudadas têm um mutante cada (M1 a M3) e a ordem tem M4.
- Borda do teste: afirma exatamente 3 ocorrências, então instalação nova do CLI sem o instalador, ou uma removida, derruba o teste (guarda contra suíte vazia).
- Lacuna declarada: a prova de que o binário nativo existe de fato é o job e2e do CI do PR (`claude --version` depois da instalação); local não há runtime JavaScript nem o gerenciador de pacotes. Sem PR aberto ainda, não há check-run `bateria` a citar; a suíte inteira roda no CI do PR (R-QA).
- Ordem `A && B; }` seguida de `instalar || { ...; instalar; }`: a nova tentativa cobre as duas etapas (lido, não executado).
