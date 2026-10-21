---
tipo: review
contrato: 1
pedido: erros-no-brief
branch: melhoria/erros-no-brief
commit: 8f03c9c43e84752cf596ce36142eb9fb09e83727
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Review: ERROS-NO-BRIEF (E1 a E5; etapa E1.2)

Escopo: `10c838f...f5d78db` (base 10c838fa35c96229d04ca96b0897cec19cbaa631), 6 arquivos em 4 commits (`efa986f`, `265c415`, `d7e4efb`, `f5d78db`). O revisor não é o autor (outra instância, D-ETAPAS-INST). Comparei o diff com o Entregar de `erros-no-brief-tech-lead-1.md`, com o desenho do aq (`docs/propostas/aq/erros-no-brief.md`) e com o modelo de ameaças (`docs/propostas/security/erros-no-brief.md`, T1 a T9).

Veredito sobre `f5d78db` (rodada 1): **REPROVADO**, por um achado bloqueante de documentação (A1). Veredito sobre `8f03c9c` (volta 1): **APROVADO**; ver "## Volta 1". O código segue o desenho e o modelo de ameaças, e cada caso tem teste. Este revisor não corrige o diff.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_erros_no_brief tests.test_conferencia_registrar` numa cópia limpa de `f5d78db` (`git archive` em `$TMPDIR`): `Ran 47 tests in 12.141s` / `OK`.
- A suíte inteira: 1234 OK segundo a entrega da E1.1 (Histórico do pedido, 01:20). O `pre-push` deste push a roda de novo. O `scripts/validar-plugin.sh` fica com o QA e o CI.
- Segurança (R-SEGURANCA): o `security-engineer` dá parecer próprio em `docs/security/erros-no-brief.md`, em paralelo. Não refiz.

## Conferido e ok
- E1 (OK-7). `CLASSES_DE_FALHA` tem 10 classes, com `outra`, e o texto "evita" fixo (`bin/forge-check:1404-1415`). `--classe` é obrigatória quando reprova ou não cumpre e só aceita o catálogo. Com aprovado ou cumpriu, grava `—` e recusa `--classe`. `--autor` tem padrão por modo (`:1449-1463`). A linha tem 10 células. O arquivo antigo de 8 colunas recebe a linha nova sem que os bytes anteriores mudem, e os leitores antigos dão a mesma saída (testes `Registrar`).
- Recorrência. Conta briefs distintos por `(classe, quem)`. Ignora linha antiga, forjada, futura, fora da janela ou `outra` (`falhas_do_registro`, `recorrencias`). A proposta só imprime, com texto fixo, e não muda o rc nem grava arquivo (T4). `conferencia classes` tem rc 0.
- Caso 9: a nota, a classe e o autor passam por `recusa_do_campo`, que pega Cf, U+2028 e delimitador, e a recusa cita o campo, não o valor (T2). Caso 10: `_tabela_segura` não segue link simbólico e tem teto de 1 MiB, com aviso e sem contagem (T8).
- Caso 5 (T5): `agente_do_brief` usa o pedido da própria linha como prefixo exato e confere contra `agents/*.md` e as stacks.
- E2. Até 3 linhas fixas no fim de "Decisões e restrições", com limiar de 2 briefs, ordem por contagem e, no empate, pela mais recente. Valem no `gerar` e no `gerar --volta`, e a volta troca as linhas do brief anterior pelas de agora. O `forge-check brief` reprova uma linha editada à mão ou uma quarta linha (caso 6, T6). Nota hostil nunca aparece na saída (T1).
- E3. `Tipo:` vem da etapa, com dedução para brief antigo. Os lembretes `jarvis-recorrente:` saem só no stderr de `gerar`, `mensagem` e `brief <arquivo>`, como pede o Entregar da E1.1. O stdout do `mensagem` fica igual byte a byte, verificado por sha256, e o do `brief <arquivo>` também (T7).
- E4 (PA-7). O arquivo vivo existe no Forge e no modelo `templates/projeto/`. O formato tem só classe, ID de regra, contagem e `arquivo:linha`, com teto de 20 linhas e aviso em stderr para linha fora do formato (casos 11 e 12, T9). A linha do arquivo entra em `## Ler` nas etapas `codigo` e `volta`. Não segue link simbólico.
- E5. O fragmento `changelog.d/erros-no-brief.md` existe. Nenhum `agents/*.md` foi tocado, conforme a decisão do dono de 2026-10-21 00:35. Também não foram tocados `docs/regras/`, `tests/config.json` nem os hooks (R-NEUTRO e R-CUSTO preservados).

## Achados da rodada 1 (resolvidos na volta 1)
- A1 (resolvido em `8f03c9c`) docs/transcricoes.md:33 · a referência de `conferencia registrar` dizia "linha de 8 colunas" e não trazia `--classe` nem `--autor`; `conferencia classes` não aparecia em nenhum doc.

## Recomendações (não bloqueiam)
- R1 `agents/jarvis.md:64`: o comando de registro que o Jarvis segue não traz `--classe`, então toda reprovação registrada por ele recebe rc 1 até o PR da E6. A recusa lista as classes, então dá para corrigir na hora. Leve isso ao PR da E6 como primeiro item.
- R2 `docs/melhoria-continua.md`: o passo 7 do desenho pede que a retro parta de `conferencia classes`, e o critério de reversão do aq (mais de 10% em `outra`) depende disso. Cabe junto com o A1.
- R3 `bin/forge-check:3930` (`--dias`): aceita 0 ou valor negativo e imprime "janela de -1 dias" sem contagem. Recusar `< 1` seria mais claro.

## Riscos
- O Jarvis classifica os próprios erros (viés que o aq já aceitou). A retro audita uma amostra.
- O caso 4 (supressão por edição do registro) é risco aceito pelo dono (2026-10-21 01:17): o git local em `~/.forge-contrib/docs`.

## Volta 1
Escopo: `f5d78db...8f03c9c`, um commit (`8f03c9c`), lido por `forge-check delta --parecer docs/reviews/erros-no-brief.md`:
- delta lido: `docs/melhoria-continua.md:10-10` (+1 -0) e `docs/transcricoes.md:33-35` (+3 -1).
- já lido na rodada 1, sem mudança: `bin/forge-check`, os testes, `templates/projeto/`, `changelog.d/erros-no-brief.md` e o arquivo vivo de achados. Os pareceres de segurança (`271caf0`) e o da rodada 1 (`b6f3898`) só entram no intervalo como documentos e não foram relidos. A segurança aprovou a entrega e não se repete nesta volta.

Conferido contra o código (sondas numa raiz vazia em `$TMPDIR`, sem trocar o HEAD da worktree):
- A1 resolvido. `docs/transcricoes.md:33` traz `--classe` e `--autor` na sinopse, a linha de 10 colunas, o catálogo das 10 classes na ordem de `CLASSES_DE_FALHA`, os autores de `AUTORES_DE_FALHA` e o padrão por modo (`jarvis` no `brief`, `destino` na `entrega`), tudo igual ao `bin/forge-check`. `conferencia classes` ganhou parágrafo próprio (`:35`), com janela padrão de 30 dias, rc 0, `outra` ignorada e proposta a partir de 3 briefs.
- R2 atendida. O passo 5 de `docs/melhoria-continua.md:10` faz a retro partir de `conferencia classes`, audita uma amostra e traz o critério de reversão do aq (mais de 10% em `outra`).

Veredito sobre `8f03c9c`: **APROVADO**. Nada bloqueia.

## Achados

## Recomendações da volta 1 (não bloqueiam)
- R4 `docs/transcricoes.md:35`: o parágrafo novo foi inserido no meio do de `registrar`. Por isso a frase "Sem `KANBAN.md` na `--raiz` recusa (rc 1 ...)" e a busca do pedido em `~/.forge-contrib` ficaram sob `conferencia classes`. Sonda: `conferencia classes --raiz <pasta sem KANBAN.md>` dá rc 0 ("nenhuma falha classificada"), e `registrar` na mesma pasta dá rc 1. Basta pôr o parágrafo de `classes` depois do resto do de `registrar`. Fica para a próxima mudança nesse doc, como no PR da E6. O texto continua na seção e nenhum comportamento muda.
- R1 e R3 da rodada 1 continuam valendo como recomendação. O R1 é o primeiro item do PR da E6.
