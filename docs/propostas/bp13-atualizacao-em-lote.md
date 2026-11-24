# BP13: atualização do Forge no projeto em lote (desenho)

Pedido v0478, etapa E154.1 (cartão BP13-ATUALIZACAO-EM-LOTE, origem `docs/propostas/boas-praticas-1911.md`, linha BP13). Só desenho: nenhum script, hook, teste, CI, migração nem modelo de projeto foi alterado; a ferramenta fica para depois. Público: o dono e o time. Revisão: 2026-12-24. Base lida: develop e15c8566.

Meta: a atualização do Forge no projeto vira **um PR por lote de versões**, com **um parecer só** quando o conteúdo é exatamente o que o plugin gera, e o modelo de projeto chega **por migração automática**, sem migração escrita à mão para cada arquivo. Custo zero (`R-CUSTO`): só git, biblioteca padrão e o CI que o projeto já roda. Regra do dono de 21/11 (item 3): nenhuma fatia cria trava nova; a C2 troca pareceres por uma conferência mecânica.

## 1. Como o projeto atualiza hoje

| Evidência | O que faz |
|---|---|
| `bin/forge-init:4`, `:166` | copia `templates/projeto` sem sobrescrever o que existe; `:216-218` grava `.forge/versao` |
| `docs/adr/0005-migracao-iniciada-pelo-projeto.md`, Decisão itens 2 e 3 | arquivo do projeto só muda por migração em `migrations/<versão>/`, idempotente, numa branch com PR |
| `bin/forge-upgrade:37-42` | junta **todas** as migrações entre `.forge/versao` e o plugin, em ordem; o lote já existe no código |
| `bin/forge-upgrade:175`, `:188-202` | uma branch `forge/upgrade-<alvo>`, um commit por migração e um de `.forge/versao`; sem push nem merge |
| `bin/forge_sempre_atual.py:808-816` | a abertura prepara `forge/upgrade-<v>` a partir da `origin/develop` quando o plugin passa o modelo; branch já existente (local ou remota) não é refeita, mas a de outra versão é criada |
| `bin/forge-check:10966-10970` | avisa `branch forge/upgrade-<v> pronta, sem PR`; o `tech-lead` envia, abre o PR e mescla com os portões da classe verdes |
| `bin/forge-check:1071`, `:1120-1152` | a classe do PR sai do diff: só `.forge/versao` (1 linha) é T, um parecer; migração que toca `.github/`, `.githooks/`, `.claude/` ou `CLAUDE.md` é C (review, QA, segurança; devops pelo pipeline) |
| `git tag -l 'v*'` (data de criação) | 30 versões de 07/11 a 22/11; a fonte mede 22 atualizações em 40 dias no projeto, cada uma com 4 pareceres |
| `git diff --name-only v0.47.1 e15c8566 -- templates/projeto migrations` | 19 arquivos do modelo mudaram (pre-push, `ci.yml`, `CLAUDE.md`, `settings.json`, modelos de parecer) e nenhuma migração nova: o projeto não recebe nada disso |

## 2. O que falta e o custo real

- **F1, um PR por versão.** Com o PR da v1 aberto, a abertura seguinte cria `forge/upgrade-v2` da `origin/develop`, que ainda está na v0: dois PRs sobre a mesma linha de `.forge/versao`, conflito no segundo e duas rodadas de portões para o mesmo destino. Com 30 versões em 16 dias, o projeto paga portão quase todo dia.
- **F2, parecer sobre conteúdo já revisado.** O que a branch traz é a saída do `forge-upgrade` da versão instalada, cujo código e migrações já passaram pelos portões do Forge (`R-REVIEW`) e pela C-INI (ADR 0017, item 6). O parecer do projeto relê o mesmo conteúdo; só o que um agente mexeu à mão (conflito, ajuste) é novo. A diferença entre os "4 pareceres" da fonte e a classe que o código daria hoje (T sem migração) entra na medida da seção 6.
- **F3, modelo sem migração automática.** Toda mudança do modelo exige migração escrita à mão; sem ela, o projeto fica para trás em silêncio (19 arquivos desde a 0.47.1). O `forge-init --forcar` sobrescreveria o que o projeto personalizou (ADR 0005, Alternativas).

## 3. Corte (fatias independentes, nesta ordem)

**C1, lote: um PR de atualização aberto por vez (não é trava).** Ao preparar `forge/upgrade-<nova>`, a abertura (`bin/forge_sempre_atual.py`) e o `forge-upgrade` olham se há `forge/upgrade-<antiga>` não mesclada (local ou em `origin`). Havendo, a nova nasce da `origin/develop` com todas as migrações pendentes (o `forge-upgrade:37-42` já faz) e o registro marca a antiga como `substituida-por:<nova>`; o `forge-check` passa a dizer `branch forge/upgrade-<nova> pronta; substitui forge/upgrade-<antiga> (feche o PR dela)`. O `tech-lead` fecha o PR antigo com o link do novo e apaga a branch. Dono: `devops-engineer`.
- Pronto quando: (a) com `forge/upgrade-0.6.0` em `origin` sem merge e plugin na 0.8.0, a abertura cria `forge/upgrade-0.8.0` com as migrações de 0.6.0 a 0.8.0 e o aviso cita a substituição; (b) com a antiga já mesclada, nada de substituição; (c) a ferramenta nunca fecha PR nem apaga branch remota (sem `gh`, sem `push`, como hoje); (d) rodar duas vezes não cria uma terceira branch.

**C2, um parecer só quando o conteúdo é o gerado (simplifica; tira pareceres).** Classe nova `U` no `forge-check classe`, só para a branch `forge/upgrade-<v>`: o `forge-check` refaz o `forge-upgrade --base <merge-base>` numa worktree temporária com o plugin da versão `<v>` e compara a árvore com o head da branch. Árvore idêntica e todos os commits com a mensagem `chore(forge): ...` que o `forge-upgrade` grava: classe `U`, só o parecer de review do `tech-lead`, que cita a reprodução e o CI verde. Qualquer diferença (conflito resolvido à mão, arquivo a mais, plugin de outra versão): a classe volta a ser a do diff, como hoje. Dono: `tech-lead` com o `security-engineer` (é afrouxamento da quantidade de pareceres, `R-DECISAO` d).
- Pronto quando: (a) branch gerada sem mudança dá `U` e `forge-check pr` aceita só o review; (b) um byte mudado à mão num arquivo de `.githooks/` volta a C, com o arquivo no motivo; (c) commit com outra mensagem volta à classe do diff; (d) plugin instalado diferente de `<v>` dá a classe do diff, nunca `U`; (e) reprodução que falha ou estoura prazo dá a classe do diff (falha fechada); (f) a sigla `U` não existe fora de `forge/upgrade-*`.

**C3, migração automática do modelo (não é trava).** O `forge-init` grava `.forge/modelo.json` com o sha256 de cada arquivo do modelo como ele ficou no projeto (depois da troca dos marcadores). O `forge-upgrade` ganha um passo fixo, depois das migrações escritas: para cada arquivo do modelo atual, se o do projeto tem o hash registrado (ninguém mexeu), troca pelo novo e registra o hash novo; se o projeto mexeu, não toca e lista o arquivo em `.forge/modelo-pendente.md` para o `tech-lead` mesclar à mão no mesmo PR (ADR 0005, item 3: para e lista). Arquivo novo do modelo entra se o projeto não o tem. Projeto sem `.forge/modelo.json` (todos os de hoje): a primeira passada só grava o hash dos arquivos idênticos ao modelo atual e lista os outros, sem trocar nada. Migração escrita à mão continua para o que não é cópia de arquivo (chave de JSON, `.gitignore`). Dono: `devops-engineer`.
- Pronto quando: (a) arquivo intocado do modelo é trocado e o hash avança; (b) arquivo personalizado fica igual e aparece na lista; (c) projeto sem `.forge/modelo.json` não tem arquivo trocado na primeira passada; (d) rodar duas vezes não muda nada (idempotente, ADR 0005 item 4); (e) arquivo do projeto que é link simbólico nunca é seguido nem trocado; (f) `--simular` mostra a lista sem gravar.

## 4. Decisões do dono

- **D1, a forma do lote.** (a) Substituir o PR aberto pelo da versão nova, um PR de atualização por vez (C1); (b) cadência fixa, um lote por semana, com as versões acumuladas; (c) só abrir PR em versão marcada "requer migração". Recomendação: **(a)**. Não espera versão nem semana, tira o conflito em `.forge/versao` e não afrouxa nada; a (b) deixa o projeto até 7 dias sem conserto de segurança; a (c) perde as mudanças de modelo sem migração (F3). Tokens e tempo: menos portões por versão, não medido.
- **D2, o parecer único (afrouxa a quantidade de pareceres; precisa do dono e da confirmação escrita da segurança).** (a) Classe `U` com reprodução idêntica, um review (C2); (b) todo `forge/upgrade-*` vale T, sem reprodução; (c) manter a classe do diff. Recomendação: **(a)**. A (b) deixa passar com um parecer o que um agente mudou à mão; a (a) só dispensa o que é byte a byte o conteúdo já revisado no Forge. Critério de reversão: um defeito escapado de PR `U` atribuído ao conteúdo da atualização, ou dois em 30 dias de qualquer origem nesses PRs, volta à (c) até nova decisão.
- **D3, a migração automática do modelo.** (a) Trocar só o arquivo intocado e listar o personalizado (C3); (b) só listar, sem trocar; (c) seguir com migração escrita à mão. Recomendação: **(a)**. A (b) mantém o trabalho manual em todo arquivo; a (c) é o atraso de hoje (19 arquivos). Arquivos de controle do projeto (`.githooks/`, `.github/`, `.claude/settings.json`) trocados por (a) chegam pelo PR `U`: com a D2 em (c), eles levam os portões normais.
- **D4, o que vai aos projetos primeiro.** Recomendação: C1 e C3 juntos; a C2 depois de 7 dias de uso no Forge com a medida da seção 6 limpa, no molde da D8 da BP1 (decisão do dono de 20/11 07:47).

## 5. Casos de abuso (para o `qa-engineer`, quando cada fatia for aberta)

- C2: agente edita `.githooks/pre-push` na branch `forge/upgrade-<v>` e mantém a mensagem `chore(forge)` · `forge-check classe` · reprodução difere, classe C.
- C2: branch `forge/upgrade-9.9.9` criada à mão com versão que o plugin não tem · `forge-check classe` · reprodução impossível, classe do diff.
- C2: o plugin instalado é trocado por um mais novo entre a geração e o review · `forge-check classe` · versão difere de `<v>`, classe do diff.
- C3: `.forge/modelo.json` editado com o hash do arquivo personalizado, para forçar a troca · `forge-upgrade` · a troca acontece e aparece no diff do PR; como o diff difere do que o modelo daria sobre o arquivo real, o review lê; limite declarado: o registro é do projeto e se protege pelo PR.
- C3: arquivo do projeto trocado por link para fora da árvore · `forge-upgrade` · não segue, lista.
- C1: duas aberturas ao mesmo tempo · abertura · uma branch só (a trava da própria ferramenta, ADR 0017).

## 6. Como medir

- Pareceres por atualização no projeto: hoje 4 (fonte); meta 1 nos PRs `U`, lido dos `docs/reviews/` do projeto.
- PRs `forge/upgrade-*` abertos ao mesmo tempo: meta no máximo 1.
- Arquivos do modelo atrasados e não personalizados no projeto: meta 0 depois do primeiro lote (o `forge doutor` lê `.forge/modelo.json`).
- Defeito escapado por PR `U` (critério de reversão da D2).

## 7. Fora do corte

Mesclar o PR de atualização sem `tech-lead` (merge automático) fica fora: o merge segue como hoje (`bin/forge-check:10966-10970`). A `main` do projeto segue do usuário (`R-MAIN`). Fusão de três vias do arquivo personalizado com o modelo novo fica para depois da medida da C3: pede a cópia do modelo antigo, que o plugin instalado não guarda.
