---
id: R-BRIEF
titulo: Brief conferido antes da delegação
verificada_por: conferente (modo brief) e revisão (transcrições, ADR 0007); o hook `brief` (selo pelo hash) ainda não existe
---
# R-BRIEF: Brief conferido antes da delegação

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: o Jarvis e quem mantém o Forge. Revisão: 2026-10-14.

- Todo prompt de delegação do Jarvis passa pelo `forge:conferente` no modo `brief` **antes** de chegar ao agente de destino. Isentos: o próprio conferente e os agentes só de leitura, sem escrita nem Bash.
- O brief é gravado em disco, em `docs/briefs/<pedido>-<destino>-<n>.md`, antes da conferência. Vai ao conferente com o caminho e a cópia literal, exatamente como será enviado; o conferente confere que a cópia é igual ao arquivo. O conferente lê do disco o pedido (`docs/pedidos/<id>.md`) e as decisões registradas, sem depender da paráfrase do Jarvis.
- Ele confere: fidelidade (cada item do "Entregar" vem do pedido ou de uma decisão registrada); decisões do dono e ADRs citadas presentes, sem contradição; corte de escopo marcado (`R-DECISAO`); forma ("Pronto quando" com `PQ-n` e tipo de prova, `R-PROVA`); e a etapa do fluxo, quando o brief manda abrir PR ou mesclar.
- A forma e o corte saem de `forge-check brief <arquivo> --pedido <pedido>` (determinístico; o conferente copia as linhas). `forge-check brief gerar --pedido <pedido>` monta os blocos fixos do brief (decisões do pedido copiadas literalmente, etapas de outro papel, marca de corte, formato das provas), e o Jarvis completa o resto.
- Passada única: o conferente lista **todos os achados** de uma vez. O Jarvis corrige o conjunto e confere o resultado sozinho antes de reenviar (sem limite de rodadas); a rodada seguinte apenas confirma as correções. O agente só recebe o texto aprovado, sem edição depois da conferência.
- Autoconferência do Jarvis antes de cada envio, em cinco pontos: as linhas `DECISÃO DO DONO` do pedido entram no brief sem alteração; todo item de escopo e toda etapa aparece no "Entregar" (citação `(E<n>)`) ou no "Fora do escopo" (etapa de outro papel, sem a marca; corte real, com a marca completa); todo `PQ-n` leva tipo de prova e, sendo `cmd`, o `espera:` do vocabulário de `R-PROVA`; hashes de commit, de base e de brief completos (40 e 64 caracteres); regras citadas só com o que o arquivo delas diz, copiando o trecho.
