# 0005 - Migração iniciada pelo projeto

Estado: vigente. Data: 2026-10-12.
Propósito: definir como um projeto adota uma versão nova do Forge que muda arquivos do projeto. Público: quem mantém o Forge e os projetos. Revisão: 2026-10-12.

## Contexto
Decisão do usuário: **o Forge nunca atualiza quem o usa, só o contrário.** O plugin atualiza com `claude plugin update`, mas os arquivos copiados pelo `forge-init` (`CLAUDE.md`, `KANBAN.md`, `.githooks/`, `docs/`) ficam parados na versão em que o projeto foi criado. As ADRs 0001 a 0004 mudam esses arquivos (seção "Stack", IDs de regra, frontmatter, `.forge/`). Hoje não há como saber em que versão um projeto está nem um caminho repetível para trazê-lo à atual.

## Decisão
1. **`.forge/versao`**: o `forge-init` grava a versão do plugin usada, versionada no git do projeto. `.forge/config.json` (ADR 0003) também é versionado; `.forge/run/` não.
2. **`bin/forge-upgrade`**, rodado **pelo projeto** (pelo usuário ou por um agente a pedido dele), nunca por automação do Forge:
   - recusa se a cópia de trabalho não estiver limpa;
   - cria a branch `forge/upgrade-<versão>` a partir da branch de integração do projeto (nunca na `main`);
   - aplica, em ordem, as migrações com versão maior que `.forge/versao` e menor ou igual à do plugin;
   - atualiza `.forge/versao`, faz um commit por migração e mostra o resumo;
   - o PR segue o fluxo normal do projeto (`gh pr create` permitido; merge do usuário);
   - `--simular` mostra o que mudaria sem gravar.
3. **Migrações em `migrations/<versão>/`**, com um script `migrar` (Python, biblioteca padrão) e um `LEIA.md` curto. Cada migração é **idempotente** (rodar duas vezes não muda nada na segunda), só toca os arquivos que declara, nunca apaga conteúdo do projeto e, se não conseguir mesclar, para e lista o conflito para o humano resolver.
4. **Testes:** cada migração tem um projeto-fixture "antes" e o "depois" esperado; o teste aplica duas vezes e compara.
5. **CHANGELOG:** a entrada da versão marca "**requer migração**" quando houver pasta em `migrations/`.
6. **SemVer:** quebra de formato de arquivo do projeto é **major** (ex.: campo obrigatório novo no contrato da ADR 0004, mudança na seção obrigatória do `CLAUDE.md`). Migração que só acrescenta algo opcional pode ser minor.
7. **Projeto sem `.forge/versao`** (criado antes desta ADR) é tratado como `0.0.0`. A primeira migração só detecta o estado, grava a versão e adiciona o que faltar sem sobrescrever.

## Alternativas consideradas
| Opção | Prós | Contras |
|---|---|---|
| Hook de início de sessão que migra sozinho | Projetos sempre em dia | Fere a decisão do usuário; muda arquivos sem PR |
| `forge-init --forcar` de novo | Já existe | Sobrescreve o que o projeto personalizou |
| Só instruções no CHANGELOG para aplicar à mão | Zero código | Não repetível; cada projeto migra diferente |

## Consequências
- Mais fácil: saber a versão de cada projeto; mudar formato sem deixar projetos para trás.
- Mais difícil: toda quebra de formato vem com migração e fixture de teste.
- Segurança: a migração é código do plugin rodando no projeto, com a mesma confiança do próprio plugin; o controle é a branch separada e o PR revisado pelo usuário.
- Risco: o projeto atualizar o plugin e não rodar o `forge-upgrade`. Mitigação: quando `.forge/versao` é menor que a versão do plugin e existe migração pendente, o `forge-check` avisa, sem bloquear.
