---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-integracao-em-lote
commit: 13cb874d23ef51f505f3dfcb3248c78c6ffea22c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 (E1.264, volta do lote do forge-fechar)

Revalidação por delta `c6b0b788..13cb874d` (`forge-check parecer delta docs/reviews/v047-integracao-em-lote.md`, domínio código e testes): `.github/workflows/ci.yml`, `bin/forge-fechar`, `changelog.d/v047-integracao-em-lote.md`, `scripts/arvore-testada.py`, `tests/catraca.py`, `tests/mutantes/{est-m7-verificador-decisao,v047-integracao-em-lote-4,-9,-10,-11}.json`, `tests/test_arvore_testada.py`, `tests/test_catraca_promocao.py`, `tests/test_fechar.py`, `tests/test_fechar_lote.py`. Revisor: instância que não fez a entrega.

## Achados
- A4 (recomendado) changelog.d/v047-integracao-em-lote.md:2 · pendente: a medida no forge-check metricas (E1.119) e o aviso ao dono com o PR para a main verde (E1.121, ponto 3) seguem fora do diff; o Jarvis confirma se ficam para outro item e o PR registra.
- A5 (recomendado) bin/forge-fechar:144 · a marca FORGE_FECHAR_LOTE_PAI=$PPID barra o uso por engano do --item-de-lote, não quem a põe à mão no ambiente: é guarda de uso (FECHAR-ESPERA-CI-DEVELOP), não de segurança; basta dizê-lo no comentário do cabeçalho.

## Sondas
- S1 · catraca --modo degrau, promocao/0.47.1 -> homolog, head = origin/develop, repos iguais · espera: rc=0 · obtido: rc=0
- S2 · idem com head 13cb874d (fora da develop) · espera: rc=1 · obtido: rc=1
- S3 · develop -> homolog de fork (HEAD_REPO f/r) · espera: rc=1 · obtido: rc=1
- S4 · melhoria/x -> homolog; promocao/0.47.1x -> homolog; promocao/0.47.1 -> main · espera: rc=1 · obtido: rc=1 nos três
- S5 · develop -> homolog, homolog -> main, melhoria/x -> develop · espera: rc=0 · obtido: rc=0 nos três
- S6 · head `--` e `--all` · espera: recusa · obtido: rc=2 (argparse), não promoção
- S7 · catraca.eh_promocao(promocao/0.47.1 -> homolog) com head na develop / fora dela / de fork · espera: True, False, False · obtido: True False False

## Verificadores
- Delta lido: os 14 arquivos do domínio listados acima.
- Testes do item (ambiente limpo, `env -i`): `tests.test_catraca_promocao`, `tests.test_arvore_testada`, `tests.test_fechar_lote.Promover`, `.Lote` e os dois `EsperaCiDevelop` do --item-de-lote · 74 testes, OK, 85 s. A suíte inteira fica no CI do PR (sem PR ainda; não rerrodada).
- `shellcheck bin/forge-fechar` · rc=0.
- Mutantes declarados: IL-M73 em diante em `tests/mutantes/v047-integracao-em-lote-10.json` e IL-M81 em diante em `-11.json`, M7 ajustado em `est-m7-verificador-decisao.json`; a mutação é do autor (V2), não refeita aqui.
- Tamanho (M14): 1188 linhas de código e teste (`git diff --numstat --no-renames origin/develop...13cb874d` em bin, scripts, .github e tests/*.py); o corpo do PR leva `teto: excedido, 1188 linhas, <motivo>`.
- Pipeline e catraca: o passo "Nada pula degrau" tem parecer do `devops-engineer` (docs/devops/v047-integracao-em-lote.md) e a catraca, da segurança (docs/security/v047-integracao-em-lote.md); citados, não refeitos.

## Parecer
Aprovado. A1 resolvido: o par `promocao/X.Y.Z -> homolog` entra na tabela única `PROMOCOES` (`tests/catraca.py`), com o head exigido ancestral de `refs/remotes/origin/develop` (falha fechada em erro do git e em sha que não é texto), e a mesma tabela é lida pelo passo "Nada pula degrau" (modo `degrau`, executado da cópia da develop do servidor, nunca do PR; checkout com `fetch-depth: 0`), por `eh_promocao` e `_violacoes_de_pareceres`, pelo `scripts/arvore-testada.py` (com `HEAD_SHA` no `env:` do passo) e pelo `forge-fechar --promover` no P1 (`par_de_promocao`). O degrau ficou mais estrito que antes: `develop` de fork para a homolog agora é recusada (S3). A2 resolvido: o `gh pr create` falso passa o par pelo modo `degrau` real, e um teste confronta pares recusados e aceitos (checklist 12). A3 resolvido: o lote acompanha o CI do topo da develop do servidor, com aviso e o último merge quando a leitura falha, e há teste do merge antigo. No delta, além dos achados: o P5 descarta PR de fork (`isCrossRepository`) e o `--item-de-lote` exige a marca do pai, ambos com teste do ramo de falha. A4 e A5 não devolvem (R-FLUXO, R-REVIEW).
