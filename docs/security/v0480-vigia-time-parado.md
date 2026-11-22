---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-time-parado
commit: 3821ad143130324a498d684791a557929056af69
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E105.4, VIGIA-TIME-PARADO)

Revisão completa única do diff 900bfdfe..3821ad14 (`hooks/vigia.py`, `tests/test_vigia_parado.py`, duas fixtures com HOME isolado, duas specs de mutante, fragmento do changelog).

Gatilhos: hook de controle (o vigia passa a decidir o `Stop` da sessão e a escrever texto ao modelo).

## Achados
- A1 (bloqueante) hooks/vigia.py:620 · o Stop bloqueado com `reason` põe texto no contexto do modelo ("retome sem esperar o dono"), o que a ADR 0003 item 1 proíbe (a emenda da exceção é proposta e só cobre o SessionStart); a docstring em hooks/vigia.py:24 ainda diz que a saída é só systemMessage
- A2 (recomendado) hooks/vigia.py:542 · `ler_quadro` abre o KANBAN.md com `open()`, segue link e espera FIFO: um KANBAN.md que é FIFO prende o hook até o timeout de 10 s em cada Stop; usar a abertura de `agentes.ler_estado` (O_NOFOLLOW, O_NONBLOCK, só arquivo regular)
- A3 (recomendado) hooks/vigia.py:529 · só três marcas de dependência; no quadro real, 40 dos 76 cartões tidos por livres têm na Obs. "depois do", "DECISÃO DO DONO", "espera" ou "bloqueado"; o aviso manda retomar sem esperar o dono e pode apontar cartão que depende de decisão (R-DECISAO)
- A4 (recomendado) hooks/vigia.py:578 · o bloqueio vale para o Stop de qualquer sessão principal no projeto ou no clone do Forge, não só a do Jarvis: uma sessão aberta pelo dono para outra coisa recebe a ordem de retomar cartões sem esperá-lo

## Sondas
- S1 · python3 -m unittest tests.test_vigia_parado.TimeParado.test_principal_bloqueia_o_stop_com_o_aviso · espera: saída sem texto ao modelo (ADR 0003 item 1) · obtido: OK; stdout {"decision": "block", "reason": "Forge: time parado: 1 cartões disponíveis, primeiro LIVRE-1; retome sem esperar o dono"}

## Detalhe dos achados
**A1.** Evidência: `hooks/vigia.py:618-622` monta `{"decision": "block", "reason": ...}`; o `reason` do Stop bloqueado é entregue ao modelo como instrução para continuar. A ADR 0003 (citada no brief como decisão em vigor), item 1: hook nunca injeta contexto; a seção da emenda diz que nenhum hook injeta contexto até o PR dela, e a exceção proposta é só o `SessionStart` com a saída do `forge-check proximo`, com parecer de segurança da classe H11 e critério de reversão por mudança de comportamento da sessão. Este hook existe justamente para mudar o comportamento da sessão. A ordem do dono de 22/11 05:30 pede que o vigia "acuse" o time parado; não traz a emenda da ADR. Caminho: não há atacante externo (o texto é fixo e o ID passa pelo filtro `_ID_DO_CARTAO`, o que está bem feito); o defeito é de requisito: um controle novo que contraria a ADR vigente sem decisão registrada. Severidade: média (governança dos hooks). Correção mínima, uma das duas: (a) acusar por `systemMessage` ao dono, sem `decision`/`reason`, como o resto do vigia; ou (b) emenda da ADR 0003 aceita pelo dono que autorize o bloqueio do Stop com texto fixo (a E104.2 já emenda a ADR para outro hook e pode levar esta exceção), com a docstring de `hooks/vigia.py:24` e `:28-33` alinhada. Esforço: P (a) ou M (b). Dono: tech-lead (código); software-architect (emenda), decisão do dono (R-DECISAO).

**A2.** Evidência: `hooks/vigia.py:539-549`. Sonda local: KANBAN.md criado com `mkfifo` numa pasta temporária, `ler_quadro` ainda preso depois de 3 s; link para arquivo fora da raiz é seguido. O git não versiona FIFO, então o caminho exige escrita local na raiz; o link versionado só aponta para um arquivo cujo conteúdo sai como contagem e um ID filtrado (sem vazamento útil). Severidade: baixa (atraso de 10 s por Stop, depois o Claude Code mata o hook). Correção mínima: abrir como `agentes.ler_estado` (`hooks/agentes.py:419-426`): `os.open` com `O_RDONLY | O_NOFOLLOW | O_NONBLOCK`, `fstat` exigindo arquivo regular, e tratar o resto como "sem quadro". Esforço: P. Dono: tech-lead.

**A3.** Evidência: `MARCAS_DE_DEPENDENCIA` em `hooks/vigia.py:529` = "depende de", "espera o dono", "aguardando o dono". Sobre o `~/.forge-contrib/KANBAN.md` real (só leitura), `cartoes_livres` devolve 76 cartões; 40 deles têm na Obs. marcas não reconhecidas: "depois do" (ex.: G2-PARECER-COMO-STATUS "depois do G1", G3-TESTES-UMA-VEZ "depois do G2"), "DECISÃO DO DONO", "espera", "bloqueado". Hoje o primeiro é livre de fato (G1-REVISAO-COMPLETA-SO), então o efeito imediato é pequeno; o risco é a frase "retome sem esperar o dono" apontar um cartão que depende do dono quando a ordem do quadro mudar. Correção mínima: ler a dependência pela mesma regra da fila provada (E106.1, `docs/kanban/fila-livre-2211.md`) ou acrescentar ao menos "depois d", "decisão do dono", "bloquead", e tirar "sem esperar o dono" do texto quando a classificação não é provada. Esforço: P. Dono: tech-lead.

**A4.** Evidência: `hooks/vigia.py:578-581` só filtra o evento e `stop_hook_active`. O hook roda no Stop de toda sessão em projeto do Forge e no clone (`clone_do_forge=True`), inclusive a sessão aberta pelo dono sem o Jarvis. Caminho: o dono abre uma sessão para uma consulta; ao fim da resposta, o modelo recebe "retome sem esperar o dono" e pode começar trabalho que ninguém pediu naquela sessão. Correção mínima: restringir à sessão do Jarvis (marcador da sessão gravado no `SessionStart` do Jarvis, ou `agent_type` quando o cliente o envia) e, na dúvida, calar. Esforço: P a M. Dono: tech-lead.

**O que está bem:** o ID que vai ao modelo passa por `fullmatch` de formato de ID (teste `test_id_fora_do_formato_nao_vai_ao_modelo`); a contagem é inteira; o laço é limitado por `stop_hook_active`; o `SubagentStop` não bloqueia; registro ilegível, sem diretório comum, quadro ausente ou acima de 4 MB calam e vão ao erros.log; a leitura do registro reaproveita `agentes.ler_estado` (sem seguir link, sem esperar FIFO). As fixtures com `HOME` isolado evitam que o teste leia o quadro real.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados: `tests.test_vigia_parado` (15 testes, OK), sondas locais de FIFO e link sobre `ler_quadro` e `cartoes_livres` sobre o quadro real (só leitura). Suíte inteira: fica para o CI do PR (por brief). Ferramentas de SAST e varredura de segredos não estão no PATH: lacuna registrada.
