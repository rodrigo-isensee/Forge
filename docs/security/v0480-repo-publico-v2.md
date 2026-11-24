---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-repo-publico-v2
commit: 85f870f554dd9e67093a5b7a1f0c0ad8b89530fe
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0480-repo-publico-v2 (PR #837, v0478 E148.3)

O PR substitui o #829. Este parecer não reaproveita os pareceres do #829 por veredito; as sondas S8 a S18 e as de tempo vêm do último parecer de segurança da branch antiga (`git show 815cfc28`, `789a1174`, `1d160afd`, `b1f93153`) e foram refeitas aqui. Escopo do diff `20630351..85f870f5` no domínio: `hooks/conformidade.py` (`GH_DA_VISIBILIDADE` e `visibilidade_do_gh` :354 a :361, `gh repo create`/`new` :3414, `api_publica` :3429, `graphql_publica` :3502, `MarcadorDaPolitica.marca` :4419), as fixtures novas em `tests/hooks/conformidade/` e `tests/test_hooks.py:3070`. Relidos `marcado`, `prazo_vencido` e `executar` de `hooks/_comum.py` (:2775, :2853, :2881). `CRITICO` (:61) não muda em relação à base. Fora do domínio: mutantes, `docs/hooks-fixtures.md` e o fragmento do changelog.

Método: o hook rodado direto, com o JSON de PreToolUse, num projeto descartável (`.forge/versao`, branch `feature/x`), prazo de produção, `PATH=/usr/bin:/bin`, e o gh nunca executado. Papéis: um papel de desenvolvimento, `forge:tech-lead` e a sessão principal. Para comparar, a base `20630351` e o head aprovado do #829 (`eebdfef6`), por `git archive`, rodados do mesmo jeito.

**Só aperta ou neutro: sim, contra a base.** Rodei 54 entradas: S8 a S18, 6 de tempo, 17 legítimas, 13 com variável ou crase no endpoint e 7 com o `gh` escrito entre aspas. Toda entrada que a base barra, o head também barra. O head barra a mais todas as formas de repositório público que a base liberava: S8, S13 a S18, a string aberta na mesma consulta, 40 KB num campo que não é `query`, o bloco aberto, 20000 pares `""`, a continuação com 4000 linhas, `visibility=$V` e `private=$P`. **Contra `eebdfef6`:** o head só libera o que aquele head barrava por custo de uso, nunca uma forma pública. São as leituras com variável, crase ou `\` + quebra (`gh api repos/$OWNER/proj/pulls`, ``repos/`echo dono`/proj/pulls``, `gh api graphql -f query="$Q"`), as linhas longas que citam `gh` e `repo` ou `api`, e um `gh issue create` com corpo de 30 KB. Nenhuma delas cria ou edita repositório.

**S8 a S18 refeitas no head:** as 11 saem 2 com `R-CONFORMIDADE: tornar o repositório público` nos três papéis. S18, a mais pesada, decide em 1,3 a 1,6 s com a máquina carregada (carga de 11 a 19 em 12 núcleos). As legítimas saem 0 nos três papéis, como em `eebdfef6`: literal `visibility:PRIVATE`, a mutação por variável com `i[visibility]=PRIVATE`, a privada com `\"` escapado, `gh repo new novo --private`, REST com `private=true`, `gh issue list`, `gh api repos/dono/proj/pulls` e `gh repo view`.

**A9 da branch antiga fechada.** O marcador das formas de visibilidade saiu do `CRITICO` e está só em `MarcadorDaPolitica.marca` (:4419). A busca é linear: um `re.search` por termo, por linha. Medi `visibilidade_do_gh` isolada, sem casar: 1 MB de `gh repo `, de `gh api ` ou de `gh ` seguido de `repo ` decide em 0,22 a 0,32 s; 8 KB, em menos de 0,005 s (em `eebdfef6`, 8 KB de `gh repo ` custavam 84 s). O marcador ainda cobre todas as formas que a A9 listou:
- `gh repo create` e `gh repo new`, pela 1ª forma;
- `gh repo edit`, pelo `edit` do `CRITICO`;
- `gh api` com `graphql`, `user/repos`, `orgs/<o>/repos`, `repos/<o>/<r>/generate` ou `repos/<o>/<r>`, pela 2ª forma, também com a continuação juntada e com `command gh` ou `/usr/bin/gh`.

**Prazo vencido com forma de visibilidade recusa.** 200 KB de `gh repo ` seguidos de `create x --public` vencem o prazo de 3 s e saem 2 com "o hook não decidiu em 3 s a chamada com ação crítica" nos dois papéis rodados. As oito fixtures `trava-prazo-*-bloqueia` (create, new, graphql, graphql com continuação, orgs/repos, user/repos, generate, PATCH) passam com o prazo forçado. A fixture de tempo `trava-gh-marcador-linear-libera` decide abaixo de metade do prazo.

Suíte: `tests.test_hooks.Hooks.test_fixtures_do_repo_publico` OK (11 s). `test_prazo_do_merge` falhou só em três fixtures do hook `parecer` (`v0455-merge-com-git-lento-*`, `v0456-merge-*-prazo-longo`), que este diff não toca, sob a carga acima. Na primeira rodada falhou em mais um ponto, com o mesmo padrão de carga. A suíte inteira é do CI: na leitura, o run sobre `d3d30703` (que só soma o parecer do review) tinha `bateria (passos)`, `instalação` e `verificações longas` verdes, as partes da suíte pendentes, e `bateria (pareceres)` e `catraca` vermelhas à espera dos pareceres.

## Gatilhos
Gatilhos: controle de acesso do agente (hook de conformidade), exposição de código e histórico, ação irreversível no GitHub.

## Detalhe dos achados
Sem achado nesta rodada.

**Cartões que seguem cartão (decisão do dono, `R-DECISAO`; não bloqueiam):**
- **C1, expansão do shell no texto que decide.** A família continua aberta e é a mesma na base e em `eebdfef6`. `gh api graphql -f query="$Q"` libera. ``gh api user/re`echo pos` -f name=n`` também sai 0 nos três: o endpoint com crase não casa `API_CRIA_REPO`/`API_DO_REPO`, então a promessa do comentário de :331 ("valor que o hook não lê no endpoint falha fechado") vale só para `$`, e não para crase no meio do segmento. O endpoint com `$` sai 2 (`user/repos$S`, `orgs/$O/repos`, `repos/$O/$R/generate`, `$E`).
- **Política do vigia.** O marcador do prazo lê as formas que `formas_que_o_shell_le` devolve. Nessas formas, `"g"h repo create`, `g\h repo new` e `gh re""po cr""eate` não casam nem `visibilidade_do_gh` nem `CRITICO`. Se a decisão dessas formas vencer o prazo, ela libera; em `eebdfef6` era igual. Não achei entrada que faça a decisão passar do prazo nessas formas. Com 200 KB e 1 MB de descrição, 20000 a 60000 continuações, um heredoc de 20000 linhas e 50000 `\"` num campo, todas saem 2 em até 2,6 s: pelo teto de linha, ou pela própria trava. Fica como dimensão para a política do vigia: o marcador ler a palavra já sem as aspas.
- **C2 e C3 do #829:** como estavam. C2 é a mensagem da recusa por valor ilegível. C3 é criar com `input:$j` e `$i` declarado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: o hook rodado localmente com projeto descartável, a base e o head anterior por `git archive`, e o marcador medido isolado. O gh ficou fora do PATH das sondas e nunca foi executado. gitleaks, semgrep e zizmor não foram usados: não se aplicam a este diff.
