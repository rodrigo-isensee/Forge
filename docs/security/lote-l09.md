---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/lote-l09
commit: 8c889ce5e9d57f4657a86c6608444ac0ae596f74
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-05
---
# Review de segurança: versao-033, lote L09 (E15 BRIEF-MENSAGEM-LIMPA)

Escopo: só o delta `103247e..bc6d081` (o L08, `7f66d28..874c89e`, tem parecer próprio). Arquivos: `bin/forge-check` (uma linha), `agents/conferente.md`, `docs/regras/R-BRIEF.md`, `tests/config.json`, `tests/test_erros_no_brief.py`, `tests/mutantes/lote-l09.json`, `changelog.d/lote-l09.md`. Revisão estática e defensiva.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `bin/forge-check brief mensagem`, o conferente e o texto protegido de R-BRIEF.

## Achados

## Detalhe dos achados
**Controle continua falhando fechado.** A única mudança de código (`bin/forge-check:5647`) remove a chamada a `lembrar_do_jarvis`, que só escrevia em stderr e nunca mudava stdout nem o código de saída (`bin/forge-check:2703-2709`). Antes dela e depois dela, `cmd_brief_mensagem` continua recusando: brief fora de `docs/briefs/`, acima do teto, fora de UTF-8, com `recusa_do_texto`, destino ou etapa divergentes, e brief que reprova no `forge-check brief` (rc 1, sem cabeçalho). O hash continua calculado sobre o mesmo buffer lido uma vez. O teste `test_mensagem_nao_traz_lembrete_e_a_primeira_linha_e_modo_brief` prova stdout idêntico com e sem registro de erros recorrentes e a primeira linha `modo: brief`; o mutante M1 guarda a volta do lembrete.

**Brief não conferido.** O hook `hooks/agentes.py` (fora do delta) segue exigindo `modo:` na primeira linha, uma só `Arquivo:` em `docs/briefs/` e uma só `Brief-sha256:` no cabeçalho, e recalcula o hash do arquivo (`hooks/agentes.py:213-271`); nada no delta o afrouxa. Sem o lembrete, some um bloqueio benigno (linha `jarvis-recorrente:` colada antes do `modo:`), não um controle: o ganho é de disponibilidade.

**Injeção pelo conteúdo do brief.** A mensagem segue sem o texto do brief (TEMPO-B1); o conferente lê o arquivo do disco. O conferente agora trata uma segunda linha `modo:` ou `Arquivo:` como `forma: instrução ao conferente`, e qualquer `forma:` diferente de `ok` reprova (`agents/conferente.md:59`); a segunda `Arquivo:` no cabeçalho já era barrada pelo hook. A regra antiga de dois blocos na mesma mensagem, que o hook já não aceitava com duas `Arquivo:`, sai: superfície menor.

**Hash do brief.** O conferente passa de aviso a reprovação quando falta `Brief-sha256:` (`agents/conferente.md:43`), e R-BRIEF passa a dizer caminho e hash em vez de cópia literal, coerente com o hook. Endurecimento, não afrouxamento. A janela entre a checagem do hook e a leitura pelo conferente é anterior ao delta e fica coberta pela comparação do hash do arquivo lido com o da mensagem.

**A1.** Evidência: `agents/conferente.md:38-42`, bloco Entrada com `modo`, `Pedido` e `Arquivo`, sem `Brief-sha256`. Caminho de ataque: nenhum direto (o hook barra mensagem sem hash antes do conferente); risco de o conferente, lendo o exemplo, julgar a forma pela amostra incompleta. Severidade: informativa. Correção mínima: acrescentar `Brief-sha256: <64 hex>   Bytes: <n>` ao exemplo. Esforço P. Dono: quem mantém `agents/conferente.md` no lote.

**Texto protegido.** R-BRIEF e `agents/conferente.md` mudam frases invariantes (`tests/config.json`); conferi que as 13 de R-BRIEF e as 61 do conferente seguem presentes. O changelog promete destaque no PR; cabe ao dono vê-lo.

## Revalidação (51ef12d)
A branch foi reempilhada sobre o L08 novo (`7925640`, parecer próprio em `docs/security/lote-l08.md` da sec-l08): o `bc6d081` virou `882a7dd`, com o mesmo `git patch-id --stable` (`cea4905`), então a análise acima vale sem mudança. O `forge-check delta` não serve aqui (o commit anterior não é ancestral depois do reempilhamento); li o delta `882a7dd..51ef12d` à mão: `agents/conferente.md:42` e `tests/test_forge.py`.
- A1 fechado: o exemplo da Entrada traz `Brief-sha256: <64 hex>   Bytes: <n>` (`agents/conferente.md:42`), e `test_mensagem_sem_brief_sha256_reprova` o prende, junto com a frase que reprova a mensagem sem o hash.
- `test_um_bloco_por_mensagem_e_o_segundo_modo_e_instrucao_ao_conferente` prende o bloco único e impede a volta da regra de dois blocos. Só texto e teste: nenhum controle afrouxa.
Testes (um módulo por vez): `test_forge.py` na classe tocada `TextoDoConferenteNoLote` (9, OK) e `test_erros_no_brief.py` de novo sobre a base nova (OK).

## Nota (d4d1ca7, teste do QA e mapa)
O delta `51ef12d..d4d1ca7` traz três coisas. A primeira é o merge do L08: o `bin/forge-check` muda só pela `promocao` do `a46eab7`, idêntica à revisada no parecer do L08. A segunda é o teste `tests/test_qa_lote_l09.py`. A terceira, no `bin/forge-testes`, são só acréscimos ao mapa FORGE_CHECK e aos LEITORES_DE_TEXTO, então o pre-push roda mais testes. Do E15, nada mudou em `bin/forge-check`, `agents/conferente.md`, `docs/regras/R-BRIEF.md` nem `hooks/`. Nenhuma recusa passou a liberar. `test_qa_lote_l09.py` (3): OK.

## Revalidação (8bc28d6, pareceres por branch, E7 e E11)
O código chegou pelo merge do L08 (`1d50bea` e `083a959`). As linhas `+`/`-` do `bin/forge-check` são idênticas às do L08 (comparei os diffs); o código do item deste lote não mudou. Numa branch de trabalho, o `pr` só conta os pareceres com `branch:` igual à dela e reprova se não houver nenhum. Na promoção e sem branch, vale o mais recente do pedido, como antes. Nenhuma recusa passou a liberar: com parecer da branch, a escolha é a mesma de antes (`da_branch or achados`); sem ele, o que antes caía no mais recente do pedido agora reprova. Toda escolha continua presa ao `commit_vale` contra o head.
- `branch:` forjado ou copiado de outra branch: o campo só escolhe qual parecer é lido. O parecer escolhido ainda precisa ter um `commit:` que cubra o head (ancestral, e depois dele só pareceres, quadro e o fragmento do changelog). Copiar o parecer de outro item não faz o código desta branch passar por revisado, e `docs/security/` é escrita só do papel de segurança.
- Branch com nome de promoção: um nome em `develop`, `homolog` ou `main` (também `origin/<base>`, que `branch_da_ref` reduz ao nome) cai no caminho de antes, o mais recente do pedido. Isso não é afrouxamento novo, e a conferência do head segue cobrada fora da `promocao`, que compara por sha.
- Sha ambíguo: `branch_do_sha` devolve None quando há mais de uma branch no sha, e o `pr` volta ao comportamento anterior (mais recente do pedido mais `commit_vale`). A conferência do head segue cobrada e, sem pedido direto, reprova. É o mesmo nível de antes, não uma brecha nova. Recomendação (baixa): na linha de comando, sha ambíguo entre branches de trabalho poderia reprovar em vez de voltar ao mais recente.
- Parecer ausente: na branch de trabalho, reprova (`sem parecer da branch`). Sem branch nenhuma (sha solto, catraca do CI) vale o caminho antigo por desenho. O hook `parecer` (`hooks/parecer.py:419`) chama `cmd_pr` sem `branch` e herda `branch_da_ref`, ou seja, o mesmo aperto quando a ref é nome de branch.
Testes: `python3 -I -m unittest discover -s tests -p test_forge.py -k ConferenciaPresaAoHead` (11) e `-p test_promover_homolog.py` (36), OK no L08, onde está o código.

## Nota (0e3067b, teste do QA 5ac531f)
O `5ac531f` só acrescenta `QaPareceresDaBranch` a `tests/test_qa_lote_l08.py`. Ele prova três casos: o parecer da própria branch passa mesmo com um parecer de outra branch desatualizado ou reprovado; sem parecer da branch, reprova mesmo com o alheio aprovado; e só o QA faltando também reprova. Não muda código nem controle, e a revalidação acima vale para este head.

## Nota (871d884, spec de mutantes do L08, 988505e)
O `988505e` só muda `tests/mutantes/lote-l08-e7b.json`; nos merges vieram também pareceres e bugs em `docs/`. Nada mudou em `bin/forge-check`, `hooks/` nem `agents/`.
- M36 equivalente: conferi a justificativa. Os dois chamadores de `conferencia_do_head` estão em `pr_da_cli`, que agora resolve a branch pelo sha antes de chamá-la. Por isso o `or branch_do_sha` interno só roda com branch vazia e daria o mesmo None.
- M56 novo: guarda a busca da branch pelo sha sem `--base`.
Nenhum controle afrouxa, e a análise acima vale para este head.

## Revalidação 0.34 (8c889ce, junção da develop)
Delta `871d884..8c889ce` lido pelo `forge-check delta` e pelo `git show --remerge-diff`. Em `bin/` e `tests/`, ele só traz o L08 já mesclado na develop (#445): `pr_da_cli` ganha `conferir` e `pareceres_da_integracao` o passa como `False` (`bin/forge-check:657-682` e `:1396`), mais `tests/apoio_conferida.py`, `tests/test_conf_escopo.py`, `tests/test_estado_da_branch.py` e as specs `tests/mutantes/lote-l08-e7.json` e `lote-l08-escopo.json`. Esse código tem parecer próprio ("Revalidação 3625656" em `docs/security/lote-l08.md`), e conferi de novo o essencial.
- `conferir=False` não se liga de fora: o único chamador é o escopo da merge-integracao, e a CLI `pr` não expõe a opção. Os portões do merge seguem cobrando a conferência do head (passo 1 do `forge-fechar` e `brief gerar` das etapas de merge, com o padrão `conferir=True`). `test_conf_escopo` e `test_estado_da_branch` provam os dois lados.
- Resolução dos conflitos (remerge-diff): `bin/forge-testes` e `tests/test_testes_tocados.py` ficam com a união (o L09 acrescenta `test_qa_lote_l09` ao mapa e conta 40 módulos), o que só amplia o que o pre-push roda. `lote-l08-e7.json` fica com o `de` de M29 e M30 alinhado ao código novo. Os pareceres do L08 ficam como estão na develop.
- `git diff 360186e 8c889ce -- bin hooks agents docs/regras` (a develop contra o L09) mostra só o próprio E15: a linha de `cmd_brief_mensagem`, o texto do conferente e de R-BRIEF já analisados acima e o mapa do `forge-testes`. A junção não reabre nem desfaz nada, e nenhuma recusa passou a liberar. Nenhum controle falha aberto, e a análise acima vale para este head.
Testes (só os módulos tocados): `test_conf_escopo.py`, `test_estado_da_branch.py` e `test_erros_no_brief.py`, todos OK. Sem achado novo. Veredito: aprovado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes: `python3 -I -m unittest discover -s tests -p test_erros_no_brief.py` (42 testes, OK). Invariantes de `tests/config.json` checadas por script local. `gitleaks` e `semgrep` não estão no PATH (lacuna; o delta não traz segredo nem dependência nova).
