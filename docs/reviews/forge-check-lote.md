---
tipo: review
contrato: 1
pedido: forge-check-lote
branch: melhoria/forge-check-lote
commit: b69dbe961f8359d4c0bede01f0302ad26b36d15c
parecer: aprovado
revisor: forge:tech-lead (outra instância, E1.2)
data: 2026-10-20
---
# Review do FORGE-CHECK-LOTE (E1.2)

Code review (R-REVIEW) da implementação inteira, `0f480c884f8a3f5af1ea8eba861fb937d61f9619..6779d74aaa592a04de124ef0c1068a7bc2c8bc9d` (5 commits, 9 arquivos, +1660 −140). Li o diff de `bin/forge-check`, `agents/conferente.md`, `tests/config.json`, `tests/apoio_versao_defasada.py`, `docs/hooks.md`, `docs/transcricoes.md`, `docs/fechamento-integrador.md` e o fragmento. Em `tests/test_forge.py` li as classes novas que provam os controles. Conferi contra o desenho do aq (`docs/propostas/aq/forge-check-lote.md`), o modelo de ameaças (`docs/propostas/security/forge-check-lote.md`, M1.x a M9.x) e todas as decisões do dono do pedido. A segurança do código é da E1.3 (`docs/security/forge-check-lote.md`) e não a refaço aqui.

## Conferência item a item

| Item | Veredito | Evidência |
|---|---|---|
| E1 (O1 = A) | ok | Em `avaliar_versao`, o marcador `decisão D: não muda o veredito` sai só no ramo `forge` do estado `atrasada`, na mesma linha do aviso (M1.1). O estado `erro` e os projetos ficam iguais (M1.2). `e_o_forge` consulta também `raiz_principal` (M1.3). O conferente.md diz isso nos dois modos e mantém os checks do CI no merge (M1.4). |
| E2 (O3 = B) | ok | `--incluir <parecer>:<id>` só em `gerar --volta`: o parecer é lido da `--ref`, só do bloco `## Achados`, do mesmo pedido e dentro de `PASTAS_DE_PARECER`. A marca é `(incluído ...)` e `conferir_volta` relê o texto e reprova se ele diferir (M2.1 a M2.3). `SECOES_COPIADAS` e a cópia idêntica não mudaram (VOLTA-BLOCO-VELHO = B, M2.4). |
| E3 | ok | Frase `Não rode a suíte` no item 1 do Modo entrega. A linha `PQ-n do autor` continua (condição T3). Invariante novo protege a frase. |
| E4 (CONF-MERGE-ESCOPO = A) | ok | `pr_da_cli` só aceita as bases do fluxo e as lê de `refs/remotes/origin/<base>`. Uma base que contém o head vale só pelo diff literal (M4.2, M4.3). A exclusão é por conteúdo: no `pr`, pelo merge simulado de `arquivos_divergentes`; no `entrega` de merge, por `base_ref..head` (M4.1, M4.5). `desatualizado` cita a base. O teste do dono ("arquivo do pedido mudou → desatualizado") está em `test_a_branch_muda_o_proprio_arquivo_depois_do_parecer`. |
| E5 | ok | `seguranca` entrou em `ETAPAS_DE_CODIGO` e em `ETAPAS_DO_GERAR` (M5.2). `docs/security/aceites/` nunca vira parecer (M5.1). A tabela de etapas ganhou a linha da etapa (M5.3). |
| E6 | ok | Uma função só, `e_linha_de_decisao`, nos quatro pontos e no `gerar_volta`, com a âncora de M6.1. Toda menção fora do início sai como linha informativa (M6.2), com teto de 20 e linha de contagem. O grep de reserva (M6.3) diverge num caso de borda: ver R2. |
| E7 (FC-SAIDA-SANITIZADA = A) | ok | `sem_controle` e `nome_seguro` cobrem Cc, Cf, Zl e Zp (M7.1). Existe a função única `caminho_impresso`. O teste estrutural por `ast` vem com lista de exceções e motivo (M7.2), e há testes de comportamento com `\n`, NEL, U+2028 e U+202E (M7.3). O que ficou fora da lista do teste está em R3. |
| E8 (CUSTO-POR-PEDIDO = A) | ok | As pastas saem da raiz e da cópia principal, nunca de `~/.claude/projects` inteiro (M8.1). `--desde`, `--ate` e `--pedido` funcionam, e o `--pedido` só aceita pedido existente (M8.2). `--entrega` recusa `|` e controle (M8.3). Links para fora são pulados. Nada usa rede (R-CUSTO). |
| E9a | ok | A união só aceita briefs de `docs/briefs/` com a mesma Branch, Base, Base-sha e pedido, lidos do cabeçalho, e imprime o sha256 de cada um (M9.1). O anexo com remoção diz de qual papel é. Pelo conferente.md, a `conferida` só sai se todas as entregas cumpriram (M9.3). |
| E9b | ok | Texto e invariante (`logo depois do \`BRIEF>>>\``). Linha `modo:` fora desse lugar vira `forma: instrução ao conferente` (M9.5, M9.6). |
| E9c | ok | O destino vem do cabeçalho do brief, de exatamente uma linha. Se divergir do `--destino`, rc 2. Vai para `avaliar_brief`, e com isso a checagem `arquivo-caminho` roda sempre (M9.8 a M9.10). |
| E9d | ok | `recusa_do_campo(valor, nome)`: a mensagem traz o nome fixo do campo e o U+XXXX, nunca o valor. No texto do brief, traz linha e coluna (M9.11). |
| E10 | ok | Os testes novos ficaram vermelhos antes do verde (sonda abaixo). O fragmento `changelog.d/forge-check-lote.md` foi criado e `CHANGELOG.md` não foi tocado. |
| E11 | ok | `base_sha_real`: o merge-base da branch com `origin/<base>`, ou `origin/<base>` se a branch ainda não existe. O `aviso: Base-sha ... não está na branch` não reprova. |

Decisões do dono: O1, O3, os 4 cartões, os tokens do conferente.md, BRIEF-BASE-ATUAL, CONF-MERGE-ESCOPO, CUSTO-POR-PEDIDO e FC-SAIDA-SANITIZADA estão cobertas pelos itens acima. "Nada pode custar dinheiro real ou afrouxar o processo": nada usa rede nem serviço pago, e nenhum controle afrouxa além da decisão D e da O1. Os 7 invariantes novos de `tests/config.json` entraram só por acréscimo.

Tamanho do `agents/conferente.md`: de 3036 para 3387 palavras (`wc -w`), +351, dentro do aceito pelo dono (+0,4k a 0,6k tokens por conferência).

Decisão técnica do autor (R<n> aceito no bloco `## Achados`): aceita. O modelo de ameaças, na M2.1, prevê que o bloco ganhe `R<n>` com a mesma gramática e o mesmo teto, e o `ACHADO` faz exatamente isso. A documentação dessa gramática nos agentes ficou para trás: ver R1.

Suposições do autor:
- **`--base` restrito só na CLI:** aceita. O hook `parecer` chama `cmd_pr` sem base (`hooks/parecer.py:182`, modo estrito). A catraca (`tests/catraca.py:848`) passa a base do próprio evento do PR, que o autor da branch não escolhe. O `forge-fechar` usa `origin/develop` por padrão, que `pr_da_cli` aceita.
- **`entrega --brief` repetível para a união:** aceita. É `action="append"`, e sem a opção a saída é a de sempre (`test_sem_brief_a_saida_e_a_de_sempre`).

## Prova por mutação (itens de controle)
Cópia em `$TMPDIR` (`git archive 6779d74`). Para cada mutante, troquei um trecho de `bin/forge-check` e rodei só as classes do item:
- **E1, 4 de 4 mortos:**
  - marcador também nos projetos: 13 falhas;
  - sem a cópia principal em `e_o_forge`: `WorktreeDeProjetoNaoViraForge` falha;
  - marcador também no estado `erro`: 5 falhas;
  - aviso do Forge com a frase velha: 20 falhas.
- **E4, 5 de 6 mortos:**
  - base local na frente da remota: 5 falhas;
  - qualquer `--base` aceita: 7 falhas;
  - sem a guarda do head contido: 1 falha;
  - escopo de merge por nome em vez de conteúdo: 1 falha;
  - merge simulado desligado na CLI: 4 falhas;
  - **vivo:** a ordem invertida em `base_da_entrega`, que não é alcançável pela CLI porque `pr_da_cli` já resolve a base. Ver R4.
- **E6, 4 de 4 mortos:**
  - substring no lugar da âncora;
  - âncora só em `startswith`;
  - menção que some;
  - `gerar_volta` ainda por substring.
- **E9a, 8 de 9 mortos:**
  - a união ignorando, uma de cada vez, Branch, Base, Base-sha e Pedido;
  - união que não reprova;
  - anexo sem o papel;
  - brief fora de `docs/briefs/` aceito;
  - aceite que vira parecer;
  - **vivo:** o cabeçalho trocado pelo texto inteiro (equivalente na prática, porque o cabeçalho vem primeiro). Ver R5.

Vermelho antes do verde: com o `bin/forge-check` da base `0f480c8` e os testes de `6779d74`, as classes `SaidaSanitizada`, `DecisaoAncora`, `PrAposMergeDaBase`, `EntregasParalelas`, `CustoPorPedido`, `BaseShaDoBrief`, `MensagemDestinoDoBrief` e `VoltaComRecomendacao` dão 65 testes e `FAILED (failures=69, errors=5)`. Com o de `6779d74`, essas classes mais `test_volta_por_delta` dão 116 testes e `OK`.

## Saída das ferramentas (sem refazer)
- Suíte do autor (E1.1 ENTREGUE, Histórico do pedido): 1171 OK. O pre-push deste push roda a suíte inteira de novo.
- `.githooks/pre-push --status` antes das sondas: `suíte do Forge rodando` (rc 0). Por isso não rodei a suíte. As sondas usaram só as classes revisadas, na cópia em `$TMPDIR` (R-TETO).

## Achados

## Detalhe dos achados
Nenhum bloqueia. São recomendações para o autor ou para o próximo pedido.

- **R1 (recomendado) · `agents/tech-lead.md:18`, `agents/qa-engineer.md:22`, `agents/security-engineer.md:16`.** A gramática do bloco `## Achados` descrita aos revisores continua só `A<n> (bloqueante|recomendado)`. O código aceita `R<n>`, mas nenhum revisor sabe disso, e os briefs de review pedem `## Achados` só com bloqueantes (este inclusive). Assim as recomendações ficam fora do bloco e o `--incluir` não as acha. A O3 funciona hoje só por `A<n>` recomendado. Sugestão: documentar `- R<n> (recomendado) ...` nos três agentes e alinhar o texto dos briefs. Vira cartão para o Jarvis.
- **R2 (recomendado) · `agents/conferente.md:50`.** O grep de reserva não aceita marcadores aninhados com espaço. Sonda: `- > DECISÃO DO DONO` e `> - DECISÃO DO DONO` dão `True` em `e_linha_de_decisao` e não casam com o grep, então a reserva cobra menos que o comando (M6.3 pede a mesma âncora). Sugestão: `'^[[:space:]]*(([-*+>_]|[0-9]+[.)])[[:space:]]*)*DECISÃO DO DONO'`.
- **R3 (recomendado) · `bin/forge-check:581`, `:3359` e `tests/test_forge.py:3664`.** Argumentos da CLI saem sem sanitizar: `pedido` em `sem parecer para o pedido` e em `Pedido: {pedido}` (do `brief gerar`, que aceita caminho), e `a.ref`, `branch` e `base` no cabeçalho do brief gerado. Esses nomes não estão na `LISTA` do teste `ast`. Além disso, a exceção casa por substring da f-string inteira, e com isso isenta os outros valores da mesma linha. O risco é baixo: é o eco do argumento de quem chama, e o `brief mensagem` recusa controle. Sugestão: pôr `pedido`, `ref`, `branch` e `base` na lista e casar a exceção pelo valor. É matéria da E1.3, que decide.
- **R4 (recomendado) · `bin/forge-check:455` e `tests/test_forge.py:4409`.** A troca para `origin/<base>` primeiro em `base_da_entrega` (M4.4) não tem teste que a prenda: o mutante sobrevive porque a CLI chega com a base já resolvida. Sugestão: teste direto de `gatilhos(raiz, p, ref, "develop")` com a develop local movida para o head.
- **R5 (recomendado) · `bin/forge-check:745` e `tests/test_forge.py:4564`.** Falta o caso do brief com `Base-sha:` ou `Branch:` só no corpo, fora do cabeçalho, que precisa reprovar a união. Hoje o mutante que lê o texto inteiro sobrevive.
- **R6 (cartão para a segurança) · `bin/forge-check:547`.** Quando `origin/<base>` já contém o head (M4.3), `cmd_pr` recebe `base=None`, e `gatilhos` cai em `BASES` (`origin/develop`), cujo diff de três pontos fica vazio: o parecer de segurança deixa de ser exigido nesse estado. O comportamento é anterior ao lote (com `--base origin/develop` já era assim) e não é regressão. Levo à E1.3 como cartão.

## Volta 1
Re-review do delta `f1dbe1087c075ca08fa94575b00229dd0ff165e9..9c09ae01ce0dba86cf150d1853a695f111837ffd` (2 arquivos, +13 −7), sobre o achado A1 da segurança. Lido: o delta inteiro. Já lido: o restante da branch, no parecer acima, sem mudança no que o delta não toca.

- `gatilhos()` imprime `caminho_impresso(quais[0])` (`bin/forge-check:495`). `grep quais` mostra que é o único uso na saída.
- Teste `ast` (`SaidaSanitizada`): `quais` entrou na `LISTA`, e `nome_de` e o teste-sonda passam a enxergar índice e fatia pela base do `Subscript`. O teste-sonda exige que `{real}`, `{quais[0]}` e `{quais[:9]}` crus sejam pegos e que as versões com `caminho_impresso` não sejam.
- Sonda de mutante (cópia em `$TMPDIR`, `git archive 9c09ae0`): a classe `SaidaSanitizada` dá 8 testes OK; revertendo a linha para `{quais[0]}` cru, falha 1. Mutante morto.
- O delta não muda mais nada. As recomendações R1 a R6 do parecer anterior seguem como estavam, nenhuma bloqueia.
- Suíte inteira: não rodei, o pre-push deste envio roda.

Parecer: aprovado.

## Volta 2
Re-review do delta `f85b3446ac4670cf79e66e4287e6b7806cbe53dd..b69dbe961f8359d4c0bede01f0302ad26b36d15c` (1 arquivo, `tests/test_forge.py`, +3 -2), a correção do achado da bateria do PR #252 (caminho pessoal literal em `tests/test_forge.py:4693`). Lido: o delta inteiro. Já lido: o restante da branch, nos pareceres acima, sem mudança no que o delta não toca.

- `test_nada_do_prompt_nem_caminho_vai_a_saida` afirma o mesmo de antes: a sentinela `TOKEN-SENTINELA` continua indo ao prompt (`extra=`, agora com o caminho pessoal montado por concatenação em `pessoal`), e o laço de asserção continua proibindo na saída `TOKEN-SENTINELA`, o mesmo caminho (agora `pessoal`, que vale `/home/pessoa`, conferido por execução), `str(self.raiz)` e `str(self.home)`.
- O delta não muda mais nada: `git diff --stat` mostra só esse arquivo e só essas linhas; `bin/forge-check`, hooks e `agents/conferente.md` ficam intactos.
- Sonda (cópia em `$TMPDIR`, `git archive b69dbe9`): o teste isolado dá OK.
- Suíte inteira: não rodei; o pre-push deste envio roda (antes: `--status` rc=1, nenhuma rodando).
- Segurança e QA não se repetem, conforme a decisão técnica do Jarvis de 2026-10-21 (R-REVIEW, R-SEGURANCA).

Parecer: aprovado.
