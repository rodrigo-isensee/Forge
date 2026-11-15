---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-conferencia-dois-pedidos
commit: 4865f8f27d29281f5886261a607ba44efcf0385b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047 (E1.290, conferência com briefs de dois pedidos)

Intervalo `origin/develop..a7872bf5` (Base-sha `c5c3a449`, um commit, E1.277): `bin/forge-check` (`etapas_dos_briefs_da_branch`, `pedido_da_conferencia`, `parecer_mandado_pelo_portao` e o ramo novo em `linhas_de_entrega`), `tests/test_conferencia_dois_pedidos.py`, dois arquivos de mutantes e o fragmento do changelog.

## Gatilhos
`R-SEGURANCA`: mudança em controle do Forge (a conferência de entrega e a escolha do pedido do `forge-check pr`, que alimentam o portão de promoção). A pergunta do brief: a mudança afrouxa a conferência (`R-PROVA`)?

## Achados
- A1 (recomendado) bin/forge-check:1386 · A escolha do pedido com dois pedidos usa o `Etapa:` de briefs sem conferir o selo; um brief de codigo não selado (rascunho, ou de pedido antigo com a mesma branch) decide o pedido. Correção: contar só briefs selados do pedido, como em `briefs_selados_da_entrega`.

## Sondas

## Detalhe dos achados
**Conclusão sobre `R-PROVA`:** a mudança troca duas falhas fechadas por aceites ancorados, sem afrouxar a âncora.

1. `pedido_da_conferencia` (bin/forge-check:1384-1388). Antes, dois pedidos nos briefs da branch reprovavam sempre; agora vale o único com brief de `Etapa: codigo`, e zero ou dois ou mais com codigo seguem reprovando com a mesma mensagem. A escolha só diz **qual** pedido é conferido: o `forge-check pr` continua exigindo a `entrega conferida` do head nesse pedido, que só o Jarvis grava (`docs/pedidos/`, protegido pelo hook `conformidade`). Escolher o pedido errado reprova (não há a linha do head nele); não há caminho em que a escolha aprove sem a conferência registrada. Um brief plantado por quem não é o Jarvis só pode pôr um segundo codigo e voltar à falha fechada (DoS do próprio autor, sem ganho).
   - A1, detalhe: evidência `bin/forge-check:1386` com os testes `PedidoDaConferencia` usando briefs não selados. Caminho: só o Jarvis escreve `docs/briefs/` (hook `conformidade`, `FORGE_CHECK_ESCRITAS`), então o caso realista é acidente (brief gravado e não selado, ou nome de branch reutilizado por pedido antigo), não ataque; o efeito é a conferência ir ao pedido errado e reprovar por falta de registro. Severidade baixa · correção mínima: filtrar `etapas_dos_briefs_da_branch` pelos briefs selados no `docs/pedidos/<id>.md` de cada id (`briefs_selados`) · esforço P · dono: tech-lead (dono do `bin/forge-check`).
2. `parecer_mandado_pelo_portao` (bin/forge-check:2579-2604). Só decide se um parecer de portão commitado na branch está **no escopo** da entrega de código; não o torna parecer válido do portão (a validade segue com `forge-check pr`/`R-REVIEW`). Mantém todas as travas do `parecer_de_portao_da_branch`: `tipo` da pasta, `branch:` igual, veredito `aprovado|reprovado`, arquivo sem controle (`com_controle`), nenhum veredito trocado no mesmo `commit:` desde o Base-sha (`veredito_trocado`). O que relaxa: o `pedido:` pode ser o de outro pedido cujos briefs citam a branch, e o `commit:` pode ser um `commit: <sha40>` do Entregar. Os dois vêm do texto **selado** do brief (sha256 no `docs/pedidos/<outro>.md`), do papel certo (`Agente destino:`), do mesmo pedido (`mesmo_pedido`), da etapa do portão do tipo e que declara o arquivo no Entregar. A lista de `outro` sai de briefs não selados, mas cada um só ancora pelo selo; brief sem selo e selo no pedido errado ficam fora (testes `test_brief_do_outro_pedido_sem_selo_nao_ancora`, `test_brief_selado_no_pedido_errado_nao_ancora`). O frontmatter forjado pelo autor com os campos do brief já passava no caminho antigo; o que barra a autoria alheia é o hook `conformidade` (escrita exclusiva da pasta pelo papel), inalterado.
3. Entrada não confiável na saída: o nome dos pedidos na mensagem passa por `nome_seguro` (bin/forge-check:1388); a leitura de brief ilegível é pulada (`OSError`, `UnicodeDecodeError`), sem derrubar a conferência.
4. Custo: `etapas_dos_briefs_da_branch` lê todos os briefs das raízes uma vez por parecer que cai no ramo novo (depois dos outros ramos falharem); sem risco de segurança, só tempo.

## Revalidação no head 4865f8f2 (E2.65, delta 4cc74cb3..4865f8f2)
`forge-check parecer delta` (intervalo a7872bf5..4865f8f2, sem o que veio da develop): no domínio só `bin/forge-testes`, que põe `test_conferencia_dois_pedidos` no mapa `FORGE_CHECK` (o teste passa a rodar quando o `bin/forge-check` muda); sem efeito em controle, só amplia a seleção. Fora do domínio: o teste e `tests/mutantes/v047-conferencia-dois-pedidos-2.json`.
A isenção de mutante da guarda `len(ids) > 1` da base (bin/forge-check:1378 na develop) é correta: a guarda foi reescrita em `if len(ids) != 1 and etapas:` (bin/forge-check:1386), e a falha fechada segue coberta. Sondas locais na cópia do head (`tests.test_conferencia_dois_pedidos`, 19 testes, OK sem mutação): trocar a condição por `False` (1 falha, 1 erro), por `len(ids) > 1 and etapas` (erro em `test_dois_pedidos_sem_codigo_falha_fechado`) e por `len(ids) != 1` (2 falhas): os três mutantes morrem. A1 segue `recomendado`, sem mudança de critério. Parecer mantido: aprovado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte: o PR ainda não existe (a integração espera a decisão do dono sobre a 0.47.1), então não há CI no head; a suíte inteira roda no CI do PR antes do merge (`R-REVIEW`). Rodei local, no head `a7872bf5`, `tests.test_conferencia_dois_pedidos` (19 testes, OK) e `tests.test_selo_e_entrega` (104 testes, OK; o módulo das conferências de entrega e anexos de portão). Revisão estática por leitura do diff e dos chamadores (`briefs_selados`, `caminho_do_pedido`, `raizes_de_pedidos`, `veredito_trocado`, `escopo_declarado`). Sem segredo no diff. Ferramentas de varredura de segredo e SAST não estão no PATH deste ambiente (lacuna; rodam no CI).
