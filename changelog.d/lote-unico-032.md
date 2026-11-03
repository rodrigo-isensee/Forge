### Adicionado
- ADR 0014 (fluxo de três degraus nos projetos) e ADR 0015 (porta de entrada do onboarding), as duas como proposta, e emendas propostas das ADRs 0003 (retomada com pedido aberto) e 0009 (sandbox nos projetos, oráculo do portão, dois conferentes); só texto, nenhum controle muda até os PRs das fases C e E (lote-unico-032, L00)

### Alterado
- CI: o gate do job `bateria` trata como commit só de parecer também `docs/security/`, `docs/devops/` e `docs/ux/` (com a bateria verde no commit anterior ainda exigida); modelos `_*` e `docs/security/{ameacas,aceites}/` rodam a bateria inteira, e o caminho leve passa a rodar `NeutralidadeDoNucleo` (pedido VEL-P6-GATE, lote V3 do plano VEL).
- forge-fechar: o PR aberto em rascunho pelo autor na entrega é reusado só com o head conferido (um PR só, base develop, sem fork) e o marcar-como-pronto roda preso ao head antes do merge; head diferente ou mais de um PR aberto para no passo 3; tech-lead.md e jarvis.md mandam o autor abrir o rascunho (lote-unico-032, L02, D-1)
- forge-check movimento recusa coluna que não está no KANBAN.md (rc 1, nada gravado), com a lista das colunas válidas na mensagem (lote-unico-032, L04, LOTE-FORGE-CHECK-032 E2)
- forge-check pr aprovado imprime a linha `pr: veredito: aprovado · <pedido> · exigidos … · head … · base …` (rc 0 continua o mesmo; com violação nada muda); a lista do cmd_pr sai de `exigidos_do_pr` (lote-unico-032, L05, LOTE-FORGE-CHECK-032 E1)
- agents/jarvis.md manda gravar o Histórico do pedido e a decisão, pergunta ou ordem do dono por `forge-check anotar`, nunca à mão (lote-unico-032, L06, LOTE-FORGE-CHECK-032 E3)

### Corrigido
- brief gerar --volta grava a linha `Etapa:` (e `Cobre:`) do brief anterior, e o `brief mensagem --entrega` deixa de recusar a volta (lote-unico-032, L03, LOTE-FORGE-CHECK-032 E5)
