---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pp1-aplicado-dono
commit: 4aadad19d27ec28ce467a05a61bd070e3497b003
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-pp1-aplicado-dono (v0478 E52.3)

Escopo lido: `0f6034ea..4aadad19` (`bin/forge-check`, `tests/test_conf_escopo.py`, os dois arquivos de mutantes, o fragmento do changelog), contra as quatro condições da DECISÃO DO DONO de 18/11 15:03 (pedido v0478) e a de 20/11 09:43. Suíte: não rodada (brief: sem suíte local); o CI do head não foi conferido aqui. Rodados: a classe nova `PatchRevisadoDoDono` contra o código da base, para medir o afrouxamento, e as sondas S1 e S2 abaixo.

## Gatilhos
Gatilhos: guarda da conferência de entrega (portão do escopo), arquivo em vigor (.githooks/, .claude/, .forge/config.json, .forge/versao), identidade do autor do commit.

## Tamanho do afrouxamento e o que aperta
- **No código, o afrouxamento é zero.** Na base `0f6034ea`, `isencao_do_dono` já isentava qualquer arquivo em vigor com a linha `patch do dono aplicado` e a `DECISÃO DO DONO` que cita o sha40 e o caminho (`caminho_isentavel` não exclui `.githooks/` nem `.claude/`). Prova: os testes novos rodados contra a base dão `escopo: ok (patch do dono f59aab5, DECISÃO DO DONO exemplo:16) ".githooks/pre-push"` sem patch nem e-mail; os casos de recusa falham na base (19 falhas).
- **O que aperta** (só no arquivo em vigor, `bin/forge-check:2202`): além do que já valia, (a) o commit do dono tem de ser, na árvore inteira e no modo, o `.patch` da branch aplicado sobre o pai (`bin/forge-check:2258-2268`, índice temporário; o índice do repositório fica intacto); (b) autor e committer em `emails_do_dono`; (c) a conferência grava sha256 do patch e sha40 do commit. Arquivo fora da lista em vigor segue a regra antiga, sem mudança. Política ilegível conta todo arquivo como em vigor (falha fechada).
- **O que aceita a mais, no processo:** o caminho em vigor passa a ser usado de propósito (PP1, A3); o portão real continua a `DECISÃO DO DONO` com o sha40 em `docs/pedidos/` (só o Jarvis grava, e a entrega que mexe nessa pasta é recusada).

## Ameaças avaliadas
- **Forja de autor/committer:** o e-mail é declarável (`git -c user.email=... commit --author=...`, como o próprio teste faz). A condição (b) não autentica ninguém; filtra só o erro honesto. O `.mailmap` não ajuda o forjador: `%ae` não o aplica (S2: `%ae=agente@x`, `%aE=dono@exemplo`, recusado). Com (a) correto, a forja só produz os bytes revisados; por isso fica recomendação (A2), não bloqueio.
- **Origem de `emails_do_dono`:** lido do disco da raiz (`bin/forge-check:2231`). No Forge, `.forge/` não é versionado (lista local do dono). No projeto, `templates/projeto/.forge/config.json` é versionado: conferida na worktree da branch, a lista vem da própria branch revisada (A2).
- **Patch adulterado:** linha a mais, modo diferente e patch que não se aplica são recusados (testes da classe nova). Só que o patch é lido de `<commit>^1:<caminho>`, sem amarrar ao blob que os pareceres leram; quem amarra hoje é a releitura por delta e a DECISÃO com o sha40 (A3).
- **Patch aplicado sobre o pai e não sobre a develop atual:** a decisão de 18/11 diz "aplicado sobre a develop atual". Aplicado sobre o pai, um commit anterior da branch que altera o arquivo em vigor fica lavado pelo commit do dono (A1, S1).

## Achados
- A1 (bloqueante) bin/forge-check:2264 · (a) aplica o patch sobre `<commit>^1`, não sobre a develop atual (decisão de 18/11): commit anterior de outro autor que cria ou muda o arquivo em vigor passa lavado pelo commit do dono (S1, rc=0). Exigir cada caminho do patch igual no pai, no Base-sha e na develop atual; git que falha recusa.
- A2 (recomendado) bin/forge-check:2231 · (b) não autentica: o e-mail é declarável e a lista vem do disco da raiz (no projeto, versionada na branch revisada). Ler `emails_do_dono` da árvore do Base-sha, não do disco, e registrar no comentário e no changelog que (b) não prova autoria; prova real seria commit assinado.
- A3 (recomendado) bin/forge-check:2258 · o .patch vem de `<commit>^1` sem amarrar ao blob revisado: troca do patch depois dos pareceres só é pega pela releitura por delta. Comparar o blob do patch no pai com o do head revisado (Revisar-sha do parecer de segurança aprovado) ou com sha256 citado na DECISÃO.

### Detalhe
**A1.** Caminho: um agente (ou qualquer commit da branch, inclusive merge trazido) põe no arquivo em vigor uma linha que nenhum revisor vê, porque o `.patch` revisado é o diff a partir desse estado; o dono aplica o patch revisado, o commit dele confere com o pai e o head mantém a linha. Ganho: código arbitrário no `.githooks/pre-push` ou no `.claude/settings.json` (roda na máquina de todos os projetos depois do merge). Severidade alta. Correção mínima, em `patch_revisado_do_dono`: para cada caminho de `git diff --name-only -z --no-renames <commit>^1 <commit>`, a entrada (modo e blob, ou ausência) em `<commit>^1` igual à do Base-sha e à da develop atual (`base_ref` resolvido; sem resolver, recusa); senão, motivo "o arquivo em vigor mudou na branch antes do commit do dono". Teste: o caso S1 recusado. Dono: tech-lead.
**A2.** Esforço P. Dono: tech-lead.
**A3.** Esforço P. Dono: tech-lead.

## Sondas
- S1 · commit de agente@x cria .githooks/pre-push com `echo NAO-REVISADO`; .patch revisado só acrescenta `# revisado`; dono aplica e declara ` patch docs/notas/pp1.patch` · espera: rc=1, não isenta · obtido: rc=0, escopo: ok (patch do dono b87edef) e head com NAO-REVISADO

## Plano em cartões
- A1, A2 e A3: tech-lead, em `bin/forge-check` e `tests/test_conf_escopo.py`, nesta branch; volta por delta a este parecer.

## Riscos aceitos
Nenhum.
