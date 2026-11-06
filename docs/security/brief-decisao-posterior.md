---
tipo: revisao-seguranca
contrato: 1
pedido: versao-035
branch: melhoria/brief-decisao-posterior
commit: 90a57d43ad227effc0c2f5938743f0ca4f4cedeb
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-05
---
# Review de segurança: versao-035, E5 BRIEF-DECISAO-POSTERIOR

Etapa E2.5. Diff lido: `d9b26bb...90a57d4` (`bin/forge-check`, `bin/forge-testes`, `changelog.d/brief-decisao-posterior.md`, `tests/test_decisao_aprovacao_raiz.py`, `tests/test_testes_tocados.py`). Na branch, depois de 90a57d4, só o parecer do review (`7f5a1dc`, `docs/reviews/`), sem código. Referência: `docs/security/ameacas/versao-035.md`, seção E5, com a revisão do T-7 de 15:52.

## Gatilhos
`controles do Forge` (R-SEGURANCA): o E5 amplia o alcance da P-N4, que afrouxa o portão de decisões do dono no `forge-check brief`. Não toca autenticação, dado pessoal, webhook, banco, CI, Docker nem dependência.

## Achados
- A1 (recomendado) bin/forge-check:5173 · candidato (a) aceita a raiz de qualquer brief em `<x>/docs/briefs/`, mesmo fora da `--raiz`, da raiz principal e de RAIZES_DE_BRIEF; limitar (a) a essas raízes (realpath) basta para o caso real
- A2 (recomendado) tests/test_decisao_aprovacao_raiz.py:70 · faltam casos de abuso 6 (`docs` como link, não só `docs/kanban`), 11 (brief fora de docs/briefs não lê quadro vizinho) e 12 (brief por link): o código os cobre, nenhum teste os prende

## Conferência dos controles (modelo de ameaças, E5)
| Controle | Código | Teste que prende |
|---|---|---|
| C-1 sem `aprovado` válido não ganha exceção; hora vem sempre de uma linha | `bin/forge-check:5175-5176` devolve None sem quadro válido; `:5179-5183` só horas de linhas; `:5258` sem `brief` ou `pedido_id` dá None | `test_decisao_aprovacao.py` `test_sem_aprovacao_cobra_tudo`, `test_reprovacao_outro_brief_...`; `test_decisao_aprovacao_raiz.py:61` (reprovado no quadro do brief, rc 1) |
| C-2 `c[1].casefold() == pedido_id.casefold()`, id de `avaliar_brief` | `:5180`; `pedido_id` de `:5481-5482` (frontmatter `id:` do pedido), repassado em `:5483`; comparação inteira, sem `startswith`/`in` (T-1 ok) | `test_decisao_aprovacao_raiz.py:52` (`EXEMPLO` vale; `outro`, `exemplo-x`, `exemplo.md` reprovam) |
| C-3 `mtime` exigido, sem folga | `:5178` e `c[0] >= escrita` em `:5182`, inalterados | `test_decisao_aprovacao_raiz.py:61` (09:59 com brief às 10:00, rc 1); `test_decisao_aprovacao.py` (retrodatada) |
| C-4 ordem fixa, primeiro que existe, sem mesclar | `:5173-5174`: raiz do brief (pai `docs/briefs`, `resolve()`), `raiz`, `RAIZES_DE_BRIEF`; `next(...)` com `lexists`, uma tabela só (T-3, T-5 ok: sem glob) | `test_decisao_aprovacao_raiz.py:66` (quadro do brief reprovado decide, o do clone aprovado não soma) |
| C-5 link ou fora de `docs/kanban` não vale e não cai | `lexists` escolhe o candidato antes de olhar o tipo (link pendente também para a busca); `:5175` `dentro_da_raiz` com `realpath` recusa diretório-link; `_tabela_segura` (`:2812`) abre com `O_NOFOLLOW` o arquivo-link; ambos dão None sem tentar o seguinte (T-2 ok). Diretório no lugar do arquivo: leitura falha, None | `test_decisao_aprovacao_raiz.py:70` (arquivo-link e `docs/kanban`-link para quadro forjado, com quadro bom no clone: rc 1) |
| C-6 decisão sem hora segue cobrada | `decisao_posterior` (`:5186-5189`) inalterada | `test_decisao_aprovacao.py` `test_decisao_sem_hora_segue_cobrada` |
| C-7 só briefs já aprovados | Modo `brief` e resultado aprovado exigidos (`:5181`); os chamadores sem `brief` (`:1959`, `:5943`) seguem sem aprovação | `test_decisao_aprovacao.py` (modo `entrega`, `reprovado`, outro nome) |
| C-8 aperto no mesmo PR | Item 2 em `ee42558`, item 1 em `f001dda`, mesma branch | os dois testes acima |
| C-9 aviso visível | saída `decisões: decisão posterior à aprovação` inalterada | `test_decisao_aprovacao_raiz.py:43-45` |
| C-10 rótulo `afrouxa-regra` | é do PR (E2.7/E2.8), fora deste diff | não se aplica aqui |

**T-7 (fronteira do diff em `bin/forge-check`).** Os três trechos tocados são exatamente os autorizados: `hora_da_aprovacao` (assinatura com `pedido_id` obrigatório e corpo), em `decisoes_cobradas` só o parâmetro `pedido_id=None`, a frase da docstring e o `return` com falha fechada, e em `avaliar_brief` só a chamada. 26 linhas no `forge-check` (teto 30), 83 no teste (teto 85). `tests/test_decisao_aprovacao.py` não foi tocado; o novo teste só importa dele.

**Afrouxamento dentro do autorizado (decisão do dono de 15:20).** A exceção continua restrita a brief com linha `aprovado` do próprio pedido, modo `brief`, hora no formato e não anterior ao `mtime`; o que muda é só onde o quadro é lido, e o item 2 aperta (linha de outro pedido deixa de valer, o que antes valia). Nenhuma classe nova de brief ganha exceção. A única largura além da letra "quadro em `~/.forge-contrib`" é a do A1, que o C-4 do modelo de ameaças já admitia e cujo caminho de ataque exige que quem escreve o brief também escreva um quadro ao lado dele e que o conferente receba esse caminho: mesmo nível de confiança de quem já escreve o brief, sem ganho real. Por isso recomendação, não bloqueio.

## Detalhe dos achados
**A1.** Evidência: `bin/forge-check:5173-5174`; `cmd_brief_conferir` (`:5524-5527`) aceita o brief por qualquer caminho do cwd. Caminho de ataque: um brief em `/tmp/x/docs/briefs/b.md` com `/tmp/x/docs/kanban/conferencias.md` plantado (linha `aprovado` do pedido certo, hora posterior ao `mtime`) faz a decisão posterior virar aviso. Exige escrever o brief e o quadro e levar o conferente a esse caminho; o hook barra a escrita do quadro real, não a de um quadro em `/tmp` (é o A2 do modelo de ameaças, "plantado em clone ou em `/tmp`"). Severidade: baixa. Correção mínima: usar o candidato (a) só se `realpath(real.parents[2])` for um de `realpath(raiz)`, `realpath(raiz_principal(raiz))` ou `realpath(r)` para cada `r` em `RAIZES_DE_BRIEF` (hoje só `~/.forge-contrib`); o caso real (brief e quadro em `~/.forge-contrib`, `--raiz` no clone) continua valendo. Esforço: P. Dono: forge:tech-lead, em cartão posterior (não devolve esta branch).

**A2.** Evidência: `tests/test_decisao_aprovacao_raiz.py:70-80` cobre arquivo-link e `docs/kanban`-link; não há caso para `docs` como link (abuso 6, variante), brief fora de `docs/briefs` com quadro vizinho (abuso 11) nem brief acessado por link (abuso 12). Pela leitura, `dentro_da_raiz` e o teste `parent.name == "briefs"` cobrem os três. Caminho de ataque: nenhum hoje; o risco é regressão sem teste que a pegue. Severidade: informativa. Correção mínima: três subcasos no mesmo arquivo (teto do teste: hoje 83 de 85, então em arquivo próprio ou com o teto revisto). Esforço: P. Dono: forge:qa-engineer (casos de abuso) na E2.6.

## Riscos aceitos e ferramentas
Nenhum risco aceito: parecer aprovado. Testes dos módulos tocados rodados neste HEAD (D-5, sem a suíte inteira): `python3 -m unittest tests.test_decisao_aprovacao_raiz tests.test_decisao_aprovacao tests.test_testes_tocados`, 98 testes, OK. Ferramentas ausentes no PATH (lacuna, nenhuma instalada, R-CUSTO): gitleaks, semgrep, osv-scanner, zizmor, actionlint, trivy; o diff não traz dependência, workflow nem segredo, e a leitura manual cobriu os três.
