### Adicionado
- ADR 0014 (fluxo de três degraus nos projetos) e ADR 0015 (porta de entrada do onboarding), as duas como proposta, e emendas propostas das ADRs 0003 (retomada com pedido aberto) e 0009 (sandbox nos projetos, oráculo do portão, dois conferentes); só texto, nenhum controle muda até os PRs das fases C e E (lote-unico-032, L00)

### Alterado
- CI: o gate do job `bateria` trata como commit só de parecer também `docs/security/`, `docs/devops/` e `docs/ux/` (com a bateria verde no commit anterior ainda exigida); modelos `_*` e `docs/security/{ameacas,aceites}/` rodam a bateria inteira, e o caminho leve passa a rodar `NeutralidadeDoNucleo` (pedido VEL-P6-GATE, lote V3 do plano VEL).
- forge-fechar: o PR aberto em rascunho pelo autor na entrega é reusado só com o head conferido (um PR só, base develop, sem fork) e o marcar-como-pronto roda preso ao head antes do merge; head diferente ou mais de um PR aberto para no passo 3; tech-lead.md e jarvis.md mandam o autor abrir o rascunho (lote-unico-032, L02, D-1)
