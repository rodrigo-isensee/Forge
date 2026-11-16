---
tipo: review
contrato: 1
pedido: v047-ci-falhas-no-resumo
branch: melhoria/v047-ci-falhas-no-resumo
commit: 8262345394250e8b2f2130950da47af33fac4621
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047-ci-falhas-no-resumo (E2.287, item E2.270)

Parecer completo (não havia parecer anterior) sobre o head 82623453, base 5e74c70e. Diff: `scripts/falhas-no-resumo.py` (novo), `tests/test_falhas_no_resumo.py` (novo), fiação em `.github/workflows/ci.yml` (4 jobs que rodam a suíte), ajustes em `tests/test_ci_local.py` e `tests/test_suite_partes.py`, spec de mutantes e fragmento de changelog.

## Achados
- A1 (recomendado) scripts/falhas-no-resumo.py:30 · mecanismo paralelo ao do suite-paralela: SEGREDO de lá (:75) é mais amplo (glpat-, sk-, xox), causa_da_falha (:339) já acha o local em tests/ e o resumo já lista os caídos (:625); reuse ou ponha no PR "Por que o existente não basta" (R-DECISAO).
- A2 (recomendado) tests/test_falhas_no_resumo.py:58 · subprocesso herda o ambiente: o unittest de registro_real e o bash de :243 (BASH_ENV entra) usam o env do CI; Execucao (:173) só tira GITHUB_*. Passe env mínimo (PATH, LANG, HOME) (AR-4, R-REVIEW).
- A3 (recomendado) tests/mutantes/v047-ci-falhas-no-resumo.json:1 · forge-mutante --cobertura lista 34 condições sem mutante; das guardas, :180 (len(argv)), :189 (texto is None), :199 (destino) e :162 (teto) só têm o return ou nada; declare um por linha de guarda (R-QA, AR-1, a cargo do QA).
- A4 (recomendado) tests/test_falhas_no_resumo.py:239 · assertNotIn("write") no ci.yml inteiro sem comentários quebra com qualquer nome de passo ou texto futuro que tenha "write"; restrinja às chaves de permissions (R-REVIEW).
- A5 (recomendado) scripts/falhas-no-resumo.py:1 · 498 linhas de código e teste (git diff --numstat, M14): o corpo do PR precisa de `teto: excedido, 498 linhas, <motivo>` (R-REVIEW).

## Sondas

## Verificações citadas
- Testes do item na raiz do clone: `python3 -m unittest tests.test_falhas_no_resumo tests.test_suite_partes tests.test_ci_local` · `Ran 119 tests` · `OK`.
- Mutantes declarados: `bin/forge-mutante --processos 1 tests/mutantes/v047-ci-falhas-no-resumo.json` · F1 a F14 `morreu`, rc=0.
- `bin/forge-mutante --conferir --base 5e74c70e` · "conferidas: o trecho de cada spec do diff está no lugar".
- `bin/forge-mutante --cobertura --base 5e74c70e` · 34 `sem mutante`, `.github/workflows/ci.yml` não coberto (base do A3).
- Suíte inteira: não rerrodada (fica no CI do PR); não há PR aberto nem CI do head para citar.
- `docs/engineering/praticas.md` não existe no Forge: sem regras "leitura" nem "ferramenta" a aplicar; checklist da skill.

## Parecer
Aprovado. O leitor faz o que E2.270 pede: teste, módulo, arquivo:linha e primeira linha do erro de cada falha no `GITHUB_STEP_SUMMARY` e em `::error`, com tetos, nos jobs `rapida`, `rapida-quatorze`, `partes-doze` e `partes-quatorze`. O `set -o pipefail` antes do `tee` preserva o código da suíte (teste de comportamento em :241); o passo do leitor roda com `!cancelled()`, sai sempre com 0 e não toca `permissions`. Escapes de comando de workflow (`%`, CR, LF, `::`, `:` e `,` nas propriedades) e de Markdown estão cobertos por teste e mutante. A extração usa a saída real do `unittest` (falha, erro, subteste, setUpClass, formato do 3.11), e o formato do `suite-paralela`/`suite-partes` (blocos do `printErrors` e `Ran N tests` por processo) é o que o leitor espera (`scripts/suite-paralela.py:313-314`).

Os cinco achados são recomendados: nenhum defeito provado. O A1 é o principal: o Forge já tem redação de segredo e local da falha no `suite-paralela`, e o novo script repete os dois com regex própria; a escolha vale, mas o PR precisa dizer por que o existente não basta. O A2 repete a classe AR-4 (linha atualizada em `docs/engineering/achados-recorrentes.md`).
