---
id: R-CONTRIB
titulo: Contribuição ao Forge - projeto abre PR, nunca mescla
verificada_por: hooks parecer e conformidade, rulesets e catraca do CI (ADR 0008)
---
# R-CONTRIB: Contribuição ao Forge - projeto abre PR, nunca mescla

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time, em qualquer projeto. Decisão: `docs/adr/0008-governanca-de-contribuicoes.md`.

Revisar em: 2027-01-07
Medida: sem medida (acesso ao repositório da fábrica)

- **Quem trabalha em um projeto abre PR para a `develop` do Forge e nunca o mescla**; mescla a sessão do próprio Forge e, na `main`, o usuário.
- **Nenhum portão tem exceção, nem para o dono:** os portões da classe da entrega, os checks e os rótulos valem para todos os autores.
- **O rótulo `afrouxa-regra` é só do dono do Forge.** O agente só o aplica, e só cria ou renomeia um rótulo com esse nome, com a conta dona do repositório e decisão do dono registrada; fora disso, aplicar ou delegar esse rótulo a um agente é **proibido**. O rótulo vale para o conteúdo dos arquivos protegidos que o dono viu: push sem arquivo protegido não o derruba.
- **Checklist de merge** (Jarvis e `tech-lead`): na `develop` e na `homolog`, só com todos os checks verdes (`gh pr checks`), pareceres válidos (`forge-check pr`) e, se a catraca pedir, o rótulo do dono; na `main`, nunca (`R-MAIN`).
- **Sessão de outro projeto só propõe.** Pode: criar **uma** branch própria `melhoria/<projeto>-<tema>` a partir da `develop`; abrir o PR. Não pode: commitar ou enviar em branch que não criou; resolver conflitos nem revalidar pareceres de PR alheio; mesclar; fechar ou editar PR alheio; aplicar rótulos; criar issue (dentro do Claude, só `forge sugerir --guardar "<texto>"`). Aberto o PR, avisa o usuário e **para**. O hook `conformidade` barra o resto pela raiz da sessão e falha fechado.
- A sessão de projeto usa só `~/.forge-contrib/<projeto>` e `~/.forge-contrib/<projeto>-wt/*`.
