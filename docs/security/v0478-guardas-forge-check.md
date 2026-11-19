---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-forge-check
commit: 63326514fc2bd1ba092acc22455176f04c0c6963
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (E2.4, guardas do forge-check)

Escopo lido: `4182a6b9..63326514` (f8b81f8f FC-PR-PARECER-FORJADO, 63326514 FILTROS-L08-G2-ORIGIN-LOCAL); o CONFIG-TETO-SEM-GUARDA fica fora desta branch.

## Gatilhos
Gatilhos: controle do portão (forge-check pr, escolha do parecer vigente), guarda de escopo da conferência (ref local reescrita pelo autor)

## Achados
- A1 (recomendado) bin/forge-check:2344 · merges_nao_conferidos ainda tira o merge cujo outro pai é ancestral da origin/<base> local sem âncora; com a ref reescrita, as recusas M9 (aceite trazido) e C-11 (parecer/*) somem, embora o escopo agora reprove o arquivo (fora do declarado)

## Sondas

## Detalhe dos achados
**FC-PR-PARECER-FORJADO** (`bin/forge-check:1943`, `:2013`, `pareceres_divergentes` em `:1987`): o grupo comparado é o mesmo conjunto de onde sai o vigente (mesmo `documentos`, mesmo filtro de pedido e de branch), então não há caminho para o forjado vencer sem entrar no grupo. Variações conferidas na leitura: veredito, revisor ou `commit:` diferentes recusam; forjado idêntico nos três não ganha nada; forjado com outro `branch:` fica fora do `da_branch` na branch de trabalho. A troca ou remoção do arquivo único segue coberta pelo blob do `parecer conferido` (`:1928`) e pelo registro de autoria (`:1954`). Corpus de legítimos: varredura de `docs/{reviews,security,qa,devops}` do clone (1259 grupos tipo/pedido/branch) achou 3 grupos divergentes, todos de pedidos antigos e de convenção extinta (`-independente`, `-desenho`); nenhum caminho do processo atual gera dois arquivos por branch. Teste: `tests/test_fc_pr_parecer_forjado.py` (7 casos, incluído o P5 do tipo não exigido).

Residual, sem caminho de ganho: sem branch (catraca, promoção) o grupo é só o da branch do vigente; um forjado com `branch:` inventado e `data` mais nova vira o vigente da promoção, mas nada reprovado chega à develop pelos portões da branch de trabalho, então não esconde veredito.

**FILTROS-L08-G2-ORIGIN-LOCAL** (`na_base` em `:2637`, uso em `:2669`, `:2729`, `:2732`; filtro montado em `:3017`): as âncoras são o Base-sha do brief selado e os Base-sha de briefs selados depois (`bases_seladas_depois`, `:9543`), registros do Jarvis que o autor não reescreve; `ancoras=None` só no `entrega` manual, sem brief, como antes. Testes: `tests/test_filtros_l08_g2_ancora.py` (L08, G2, E2 e o caminho legítimo ancorado) e os ajustes em `tests/test_selo_e_entrega.py` e `tests/test_conferida_por_branch.py`, que trocam o "sai do escopo" sem âncora por "segue no escopo", na direção segura.

A1, severidade baixa: o mesmo padrão (confiar na `origin/<base>` local) segue em `merges_nao_conferidos` (`:2344`), chamado na conferência (`:3073`). Caminho: o autor cria uma lateral com `docs/security/aceites/<pedido>.md` ou um parecer, faz `git update-ref refs/remotes/origin/develop <lateral>` e mescla; o merge sai do filtro de `outros`, e as recusas M9/C-11 não aparecem. Sondado (abaixo): com esta branch, a conferência reprova mesmo assim, pelo "fora do declarado no brief", porque o filtro G2 agora deixa o arquivo no escopo; por isso é recomendação, não bloqueio. Correção mínima: em `:2344`, trocar `e_ancestral(raiz, q, base_ref)` por `na_base(raiz, q, base_ref, filtro)` passando o mesmo `filtro` de `:3017` (e `None` fora da conferência). Esforço P. Dono: tech-lead (dono do bin/forge-check).

Sondas executadas (não provam bloqueante; ficam aqui): repositório temporário pela classe `FiltrosAncorados`, lateral com `docs/security/aceites/p.md` e com `docs/reviews/p.md`, `origin/develop` reescrita para a lateral, merge e conferência: rc 1, `escopo: fora do declarado no brief "<arquivo>"` e a linha `merge da "develop" sem âncora`; sem a linha M9.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados localmente: `tests.test_fc_pr_parecer_forjado`, `tests.test_filtros_l08_g2_ancora`, `tests.test_conferida_por_branch` (15 testes, OK) e a sonda acima; a suíte inteira fica para o CI do PR (sem PR nesta etapa, brief E2.4). Ferramentas ausentes do PATH, não instaladas: gitleaks, semgrep, osv-scanner, zizmor, actionlint (a mudança não toca workflow, dependência nem segredo).
