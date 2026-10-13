---
tipo: review
contrato: 1
pedido: pendencias-0.7.0
branch: melhoria/pendencias-hooks-0.7
commit: 4d4d7fb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Code review: pendências dos hooks e migração 0.7.0

Escopo: `origin/develop..4d4d7fb` (1 commit): `hooks/agentes.py`, `hooks/parecer.py`, `hooks/_comum.py`, `bin/forge-init`, `migrations/0.7.0/`, `stacks/node-react/pesados.json`, `templates/projeto/.forge/config.json`, `docs/hooks.md`, ADR 0001, `CHANGELOG.md` e testes. A referência é o que ficou pendente em `docs/reviews/release-0.5.0.md` (itens 12 e 14 a 17) e as ADRs 0003 e 0005. Além da leitura, rodei a suíte inteira (88 testes, verde) e conferi no git real que `git checkout <branch> --` troca de branch.

Parecer: **aprovado**. Não há achado crítico nem alto. O achado médio já existia antes desta branch e não veio dela; vira cartão.

## O que está correto
- **Migração 0.7.0 (ADR 0005):** só apaga `teto_agentes` quando o valor é o inteiro 3 (`migrations/0.7.0/migrar:19`, `type(valor) is int`). Por isso `true`, `3.0`, `"3"`, 2 e 4 ficam intactos, como mostram as fixtures `tests/migracoes/0.7.0/`. Se o config não existe, não é um objeto ou está ilegível, sai com 0 e não toca no arquivo. Rodar duas vezes deixa os bytes iguais, e quando não há o que mudar o arquivo nem é reformatado; o teste cobre os dois casos. O `forge-upgrade` aplica as migrações em ordem. Um projeto que vem da 0.0.0 recebe da 0.5.0 o modelo atual, já sem `teto_agentes`, e a 0.7.0 não encontra nada para fazer.
- **Falha aberta (ADR 0003):** `calcular_teto` não ganhou nenhum caminho de exceção novo (`hooks/agentes.py:62-67`). `teto_maximo` já chega validado como inteiro maior ou igual a 1 por `_comum.config`. `RESERVA["pesados"] = []` faz o hook `pesado` não bloquear nada, que é o lado seguro.
- **Item 14 (checkout de arquivo):** com mais de um posicional, a linha passa a ser lida como restauração de arquivo, que é a semântica do git: `git checkout <ref> <arquivo>` não troca de branch. Isso não abre buraco no portão. A branch considerada continua sendo a atual, e um merge feito estando na integração continua bloqueado. As formas que criam branch (`-b`/`-c`) são tratadas antes. `git switch a b` falha no próprio git.
- **Itens 15 a 17:** registrados em "Limites conhecidos" de `docs/hooks.md`, com o motivo (falso bloqueio no `cherry-pick`, formas demais no `rebase`/`reset`).
- **Item 12 e neutralidade:** a lista saiu do núcleo e foi para `stacks/node-react/pesados.json`, como pede a ADR 0001, agora atualizada. O exemplo em `docs/hooks.md` é neutro. O `forge-init` grava a lista só no config que ele mesmo acabou de criar (`bin/forge-init:86`); uma config que já existia fica como está, o que tem teste. O teste de pacote valida o formato do `pesados.json`.
- **Projetos existentes:** todo modelo anterior (0.5.0 e 0.6.0) gravava `pesados` explicitamente, então os projetos já criados mantêm a lista que têm. A mensagem do teto deixou de mentir sobre "padrão 3" e "limitado", e há fixtures para os dois casos.

## Achados

### Crítico
Nenhum.

### Alto
Nenhum.

### Médio
1. `hooks/parecer.py:48`: `"--" in args` faz a linha ser tratada sempre como restauração de arquivo. Só que `git checkout develop --` (sem nenhum caminho depois do `--`) **troca** de branch, como conferi no git. Com isso, `git checkout develop -- && git merge feature/x`, executado a partir de uma branch de trabalho, passa sem parecer. Este é o lado inseguro, e o problema já existia antes desta branch. Sugestão: tratar como restauração só quando houver algum posicional depois do `--`. Se não houver, o nome antes do `--` é a branch. Acrescentar a fixture correspondente. Não bloqueia: vira cartão para a próxima versão.

### Baixo
2. `stacks/node-react/pesados.json:1`: a lista de uma stack Node/React traz `pytest -m integration`, que veio do padrão antigo do núcleo. Sugestão: tirar o item ou justificá-lo, porque o pacote de stack deve falar só da própria stack.
3. `CHANGELOG.md:13`: além do projeto que migra da 0.0.0, também perde a lista em silêncio o projeto cuja config não tem a chave `pesados`, porque o padrão do modelo agora é `[]`. Sugestão: ampliar a frase, ou fazer a migração 0.7.0 avisar (sem alterar nada) quando `pesados` estiver ausente ou vazio.
4. Release: a migração só roda quando a versão do plugin for pelo menos 0.7.0 (o `forge-upgrade` compara a pasta com `plugin.json`). A release desta entrada precisa ser exatamente a minor 0.7.0. Fica o lembrete para o PR de release.
