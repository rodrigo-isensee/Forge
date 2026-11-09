---
id: R-BRIEF
titulo: Brief selado pela ferramenta antes da delegação
verificada_por: `forge-check brief selar` (selo sha256) e hook `agentes` (só delega brief selado com o hash citado no prompt)
---
# R-BRIEF: Brief selado pela ferramenta antes da delegação

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: o Jarvis e quem mantém o Forge.

Revisar em: 2027-01-07
Medida: 759 de 2.313 briefs (33%) reprovados pelo conferente agente, 26% sem mérito (estudo 0.43.1)

- Toda delegação a um agente que escreve ou roda Bash leva um brief gravado em `docs/briefs/<pedido>-<destino>-<n>.md` e **selado** **antes** de chegar ao agente: `forge-check brief selar --arquivo <brief> --pedido <pedido>` grava o selo (sha256) só se todas as checagens passam; o hook `agentes` recusa a delegação sem selo ou com hash diferente do citado no prompt. Brief editado pede selo novo.
- **O gerador parte do pedido e do desenho, nunca de outro brief:** `forge-check brief gerar --pedido <p> --destino forge:<nome> --branch <b>` calcula base, `Desde:`, etapa e estado do PR; ninguém os digita. O brief de volta sai dele com `--volta`.
- **Brief curto:** até cerca de 8.000 caracteres. As decisões do dono vão **por referência** (pedido, hash do bloco e ids da etapa), nunca copiadas; o agente lê o pedido e, se o brief divergir, para e relata.
- Um brief delega uma só etapa de `## Etapas` e a cita no "Entregar" como `(E<n>.<m>)`. As outras etapas do pedido vão ao "Fora do escopo" com o trecho literal e **sem** a marca "Retira do escopo original", que só existe no corte real (`R-DECISAO`). Etapa que não aparece nem no "Entregar" nem no "Fora do escopo" reprova no selo.
- O selo confere também: corte de escopo marcado, "Pronto quando" com `PQ-n` e tipo de prova (`R-PROVA`), etapa de outro papel, contradição com o `## Fora do escopo` do pedido e regra citada só com o que o arquivo delas diz.
- O `forge:conferente` é **opcional**, só para dúvida de conteúdo; a forma é da ferramenta.
