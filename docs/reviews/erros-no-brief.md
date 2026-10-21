---
tipo: review
contrato: 1
pedido: erros-no-brief
branch: melhoria/erros-no-brief
commit: f5d78db45fd9c57053635cf898b095b632ec69bc
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Review: ERROS-NO-BRIEF (E1 a E5; etapa E1.2)

Escopo: `10c838f...f5d78db` (base 10c838fa35c96229d04ca96b0897cec19cbaa631), 6 arquivos em 4 commits (`efa986f`, `265c415`, `d7e4efb`, `f5d78db`). O revisor não é o autor (outra instância, D-ETAPAS-INST). Comparei o diff com o Entregar de `erros-no-brief-tech-lead-1.md`, com o desenho do aq (`docs/propostas/aq/erros-no-brief.md`) e com o modelo de ameaças (`docs/propostas/security/erros-no-brief.md`, T1 a T9).

Veredito sobre `f5d78db`: **REPROVADO**, por um achado bloqueante de documentação (A1). O código segue o desenho e o modelo de ameaças, e cada caso tem teste. Este revisor não corrige o diff.

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

## Achados
- A1 (bloqueante) docs/transcricoes.md:33 · a referência de `conferencia registrar` ainda diz "linha de 8 colunas" e não traz `--classe` (obrigatória quando reprova) nem `--autor`; `conferencia classes` não aparece em nenhum doc. A definição de pronto pede o doc afetado na mesma entrega.

## Recomendações (não bloqueiam)
- R1 `agents/jarvis.md:64`: o comando de registro que o Jarvis segue não traz `--classe`, então toda reprovação registrada por ele recebe rc 1 até o PR da E6. A recusa lista as classes, então dá para corrigir na hora. Leve isso ao PR da E6 como primeiro item.
- R2 `docs/melhoria-continua.md`: o passo 7 do desenho pede que a retro parta de `conferencia classes`, e o critério de reversão do aq (mais de 10% em `outra`) depende disso. Cabe junto com o A1.
- R3 `bin/forge-check:3930` (`--dias`): aceita 0 ou valor negativo e imprime "janela de -1 dias" sem contagem. Recusar `< 1` seria mais claro.

## Riscos
- O Jarvis classifica os próprios erros (viés que o aq já aceitou). A retro audita uma amostra.
- O caso 4 (supressão por edição do registro) é risco aceito pelo dono (2026-10-21 01:17): o git local em `~/.forge-contrib/docs`.
