---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp2-i1-conserto
commit: 971c60537d114c95b5b5918b5202669aaf9b8b9b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Code review: `forge-fechar --conserto` (BP2 I1, E38.5, revalidação)

Revalidação no head 971c6053. Delta lido: `forge-check parecer delta docs/reviews/v0479-bp2-i1-conserto.md`, intervalo `b96357e9..971c6053`, sem o que veio da develop (merge 04ca0e72, base 0f6034e); no domínio só `tests/mutantes/v047-integracao-em-lote-3.json`, `-7.json` e `-8.json`. O commit 971c6053 só realinha o `de`/`para` de IL-M18, IL-M19, IL-M22, IL-M51 e IL-M57 ao `bin/forge-fechar` do `--conserto`; a guarda, o teste e o sentido de cada mutante seguem os mesmos. `bin/forge-mutante --processos 1 --ids IL-M18,IL-M19,IL-M22,IL-M51,IL-M57` nas três specs, no 971c6053: os cinco morrem (bin/forge-fechar:1027, 1028, 1040, 1599, 136). `--conferir --todas` não aponta nenhuma das três specs. Nada muda no parecer anterior, que segue abaixo.

Revalidação do parecer reprovado em d816262d. Delta lido: `forge-check parecer delta docs/reviews/v0479-bp2-i1-conserto.md`, intervalo `d816262d..b96357e9`, no domínio `bin/forge-fechar`, `changelog.d/v0479-bp2-i1-conserto.md`, `tests/mutantes/fechar-conserto-7.json` e `tests/test_fechar.py`; só esse delta foi relido.

## Achados
- A2 (recomendado) tests/test_fechar.py:1345 · o gh falso do C4 segue aceitando qualquer `--commit` no `run list` do CI do PR (bin/forge-fechar:1100); confira no falso o sha igual ao head do PR (checklist 12). Vira cartão depois do merge.

## Sondas
- S1 · anotações `tests/test_b.py<TAB>test_b.Caso.test_um (entrada='f()'): AssertionError` e `tests/test_c.py<TAB>test_c.K.test_dois: AssertionError` no sed de bin/forge-fechar:1090 · espera: os dois ids · obtido: test_b.Caso.test_um e test_c.K.test_dois

## Parecer
Aprovado. O A1 está corrigido: o sed da linha 1090 toma o id até o primeiro espaço ou `:` (S1 refeita, os dois ids saem), com o caso `test_c4_subteste_com_parentese_no_parametro_e_conferido` e o mutante CS45 que volta ao padrão antigo. Na mesma volta, o C4 passou a parar também com o teste pulado pela classe (`setUpClass`/`tearDownClass`) ou pelo módulo (`setUpModule`/`tearDownModule`/`ModuleSkipped`) e com o método apagado no head (`git grep` em `$remoto_sha`, falha fechada se o arquivo do módulo não casar), cada guarda com teste do ramo de falha e mutante declarado (CS46 a CS49) e o caso negativo de outra classe ou módulo. A correção dos achados da segurança e do QA fica com esses portões; aqui só o código e os testes do delta.

Tamanho (H1): o delta soma 11 linhas de código em `bin/forge-fechar`, dentro do teto do item. Commit `b96357e9` em Conventional Commits.

Ferramentas: `shellcheck` fora do PATH desta estação (o CI do PR o roda). Suíte: não rodada (o CI do PR é o portão). Rodados aqui: `tests.test_fechar.Conserto`, 42 testes OK em 83,7 s no head b96357e9, e a sonda S1.
