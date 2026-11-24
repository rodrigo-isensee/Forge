---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp-desenhos
commit: ebdb647363fe7b62cd98da749af4014ed6219d9e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E142.5, PR #830, desenhos BP1 a BP3, revalidação)

Classe T: só documento (três desenhos em `docs/propostas/` e o fragmento `changelog.d/v0480-bp-desenhos.md`), sem código, hook ou teste tocado. Base `develop` em `789fc141`; head revisado `ebdb6473`. O parecer anterior (E142.3) aprovou `d9256544`.

## Revalidação
- Delta lido por `forge-check parecer delta docs/reviews/v0480-bp-desenhos.md`: intervalo `d9256544..ebdb6473`, sem o que veio da base; no domínio só `docs/propostas/v0479-bp3-sessao-duravel.md` (4 linhas trocadas).
- O merge `9eb3590f` traz a `develop` (`forge-fechar`, merge-tree limpo) e não muda os arquivos do PR.
- `ebdb6473` troca `python-backend` por "o backend da stack" no público (linha 3) e nas linhas S3, S4 e S5 da tabela de itens; o sentido do desenho fica o mesmo, e a forma segue a do desenho anti-erro.
- Nenhum `python-backend` resta nos arquivos do PR (`grep` vazio).
- Teste do arquivo tocado, `test_forge.NeutralidadeDoNucleo` e `test_forge.Neutralidade`: no head, 6 testes `OK`; com o arquivo em `9eb3590f`, `FAIL: test_nucleo_sem_termos_de_stack ... termo='python-backend'`. A volta corrige a falha do CI (job 138227044646).
- Commit único, Conventional Commits em português, mensagem com o motivo; H1 não se aplica (zero linha de código).
- CI do PR #830 no head `ebdb6473`: `árvore já provada na develop` passou; as partes da suíte estavam pendentes na hora do parecer. Suíte não rerrodada (regra da suíte só no CI).

## Parecer
Aprovado. A volta troca só o termo de stack pelo papel neutro, e o teste de neutralidade passa no head. O merge segue com o CI verde no head.
