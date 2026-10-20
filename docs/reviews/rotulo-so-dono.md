---
tipo: review
contrato: 1
pedido: rotulo-so-dono
branch: melhoria/rotulo-so-dono
commit: b458a5752c1e4eb3406b02c7bf9f960580d4ff81
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-19
---
# Review: o rótulo afrouxa-regra só do dono do Forge (E1.2, revalidação da volta 1)

Revisor independente (outra instância do `tech-lead`, D-ETAPAS-INST = A); o autor da E1.1 e da E1.1v não revisa. Este parecer substitui o anterior (aprovado sobre `11d9196`). Diff lido: só o delta da volta 1, `4120acb...b458a57` (2 commits: `a0c2d6e` hook, testes, invariantes e R-CONTRIB; `b458a57` nota na ADR 0009). O que o delta não alcança segue como no parecer anterior.

## O que foi conferido
- **E1 (regra, texto único):** o item do `R-CONTRIB` ganhou só o trecho "e só cria ou renomeia um rótulo com esse nome (`gh label create|edit`, `gh api` em `labels`, `createLabel`/`updateLabel`)"; continua num lugar só (`grep` de "só do dono do Forge" e "só cria ou renomeia" fora de `changelog.d/` e dos pareceres acha só `docs/regras/R-CONTRIB.md:12`). A proibição expressa para qualquer outro contribuidor e a falha fechada ficaram intactas. Em `invariantes` (`tests/config.json`), só acréscimos: a frase nova da regra e cinco âncoras do hook; nenhuma remoção.
- **E2 (hook), itens da volta:**
  - A1: `conta_do_gh` usa `Popen` em grupo próprio com `TIMEOUT_DA_CONTA = 5` s (abaixo dos 10 s de todo hook em `hooks.json`), mata o grupo no limite e devolve vazio (barra); `lru_cache(maxsize=1)` faz uma consulta por processo do hook. O teste estrutural `test_timeout_de_rede_dos_hooks_abaixo_do_hooks_json` percorre todos os `hooks/*.py` pela AST e exige mínimo de 5 scripts e 1 subprocesso de rede achado (item 11 do checklist cumprido).
  - A2 e R4: `endpoint_normalizado` / `e_graphql` tiram `?…`, `#…`, esquema e host e o prefixo `api/`/`api/v3/`; valem no caminho do rótulo e na comparação GraphQL da sessão de projeto (`gh_contrib`), que antes só reconhecia `graphql` exato.
  - A3: o REST com query string, fragmento ou URL completa cai na regex normalizada, que agora também cobre `labels[/<nome>]`.
  - A4: `conteudos_de_crase` extrai o conteúdo das crases fora de aspas simples, e cada um passa pelo mesmo caminho do `$(...)`; crase sem par levanta `ValueError` e, se a linha cita o rótulo, exige o dono.
  - R2: `gh label create|edit` que cita o nome e `createLabel`/`updateLabel` exigem a conta do dono.
  - Recomendação 4 do parecer anterior: `principal` envolve o caminho novo num `except Exception` que barra só se a linha cita o rótulo (`CITA_ROTULO`) e relança o resto. `barrar` sai por `sys.exit(2)` (`SystemExit`, fora de `Exception`), então a recusa normal não vira "erro interno".
- **O caminho novo em `principal` só analisa o rótulo:** a condição de entrada e a de retorno (`not (com_lista and na_sessao_do_forge)`) não mudaram; o `try` novo só acrescenta a falha fechada da linha que cita o rótulo e relança qualquer outro erro para o `executar`, como antes. Na sessão de projeto, a única mudança de comportamento é a do R4 (`/graphql` e a URL completa valem como `graphql`), que só endurece uma regra que já existia; nenhuma outra regra muda.
- **Testes:** as 12 fixtures `tests/hooks/conformidade/rotulo-so-dono-*.json` continuam as mesmas (o delta não toca `tests/hooks/`). A volta acrescenta 5 métodos em `tests/test_hooks.py`: formas alternativas (20 que barram outra conta, 8 que passam, 12 que passam com a conta do dono, com `minimo(casos, 40)`), `gh` pendurado com filho segurando a saída (decide antes do timeout do hook), o teste estrutural de timeout, erro inesperado que falha fechado (inclusive com a conta do dono) e o GraphQL por caminho na sessão de projeto. Cobrem cada bloqueante da segurança e as bordas declaradas.
- **ADR 0009 e CLAUDE.md:** a nota da exceção entrou no fim da seção 6, item 6, citando `R-CONTRIB` sem repetir a regra (recomendação 1 do parecer anterior, atendida). O `.claude/CLAUDE.md` do Forge não descreve o alcance do hook `conformidade` (cita a ADR 0009 só pelo sandbox), então não precisa de nota.
- **Ferramentas (saída citada, não refeita):** `python3 -m unittest tests.test_hooks -v` nesta worktree, sobre `b458a57`: `Ran 25 tests in 61.406s OK` (os 20 de antes e os 5 novos; `test_fixtures` inclui as 12). A suíte completa (875 OK) é do autor, na E1.1v. A catraca segue apontando o rótulo do dono por mudança em `hooks/conformidade.py` (parecer anterior; o delta não muda isso).
- **Regras da fábrica:** `R-CUSTO` (nada pago; `gh api user` só quando a linha cita o rótulo), `R-NEUTRO` (o login do dono só em fixture e teste; no código, vem do `plugin.json`), invariantes preservadas, fragmento `changelog.d/rotulo-so-dono.md` intacto, sem `CHANGELOG.md` nem versão. Commits limpos, Conventional Commits em português, um por mudança coerente.
- **Segurança:** o parecer é do `security-engineer` (E1.3, revalidação em paralelo, `docs/security/rotulo-so-dono.md`); citado e não refeito. Os pontos 1 e 2 abaixo vão para ele.

## Achados

## Detalhe dos achados
1. `hooks/conformidade.py`, `conteudos_de_crase` · a aspa simples de um comentário abre o estado "entre aspas simples" e esconde a crase das linhas seguintes. Reproduzido chamando `Guarda.rotulo_na_sessao_do_forge` com `exigir_dono` trocado por um registro: `echo hi # don't` seguido, na linha de baixo, de ``x=`gh pr edit 70 --add-label afrouxa-regra` `` passa, enquanto a mesma linha sem o comentário barra. Não é regressão (antes da volta a crase passava sempre, A4) e a catraca segue exigindo o evento `labeled` com ator igual ao dono, então o portão não se abre por aqui · ignorar `#` em início de palavra fora de aspas (como o shell faz) ou tratar a aspa simples sem par no fim como linha que não se analisa (`ValueError`, que já exige o dono quando a linha cita o rótulo), com um caso a mais em `test_rotulo_so_dono_formas_alternativas` · levar ao `security-engineer` (revalidação da E1.3) para decidir se fecha nesta volta ou vira limite declarado · severidade: recomendado.
2. `hooks/conformidade.py`, `aplica_afrouxa_regra` · `gh label clone <repo-origem>` (e `--force`) cria ou sobrescreve no Forge os rótulos de outro repositório, inclusive um `afrouxa-regra`, sem citar o nome na linha; a regra nova no `R-CONTRIB` fala em "cria ou renomeia". Mesmo raciocínio da catraca: criar o rótulo não gera o evento `labeled` do dono · incluir `label clone` entre os subcomandos que exigem o dono (o texto da regra já cobre "cria") ou declará-lo como limite · severidade: recomendado.
3. `hooks/conformidade.py`, regex `labels(/[^/]+)?` em `aplica_afrouxa_regra` · `gh api -X DELETE repos/o/r/issues/70/labels/afrouxa-regra` (tirar o rótulo) passa a exigir o dono, enquanto `gh pr edit --remove-label afrouxa-regra` passa (fixture `remover-rotulo-libera`). O erro é para o lado fechado, então não há risco, só incoerência entre duas formas do mesmo ato · se for intencional, uma linha no docstring basta · severidade: recomendado.
4. Recomendação 3 do parecer anterior (dono lido do `plugin.json`, não da URL do remoto, como o E2 dizia) continua de pé: registrar no corpo do PR, como a decisão técnica do Jarvis no pedido prevê · severidade: recomendado.

## Pendências para o merge (não são do review)
- Rótulo `afrouxa-regra` do dono, na conta dele, depois do último push (a catraca exige por `hooks/conformidade.py`).
- Sobreposição com o teto adaptativo em `tests/test_hooks.py` (anotada no pedido): o merge espera o do teto e traz a `develop` antes; se o patch mudar, `forge-check pr` aponta o alcance da revalidação.
- Parecer de segurança da revalidação (E1.3) aprovado.

## Parecer
Aprovado: a volta 1 fecha A1 a A4, R2, R4 e a recomendação 4 do parecer anterior, sem mudar outra regra, e põe a nota da exceção na ADR 0009. As quatro recomendações acima não impedem o QA; a 1 e a 2 são do `security-engineer` decidir.
