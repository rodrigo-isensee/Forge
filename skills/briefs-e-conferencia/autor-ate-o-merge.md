# Autor até o merge (H2)

Detalhe da skill `briefs-e-conferencia` (diretriz 25: o Jarvis e o `tech-lead` trazem o resumo e mandam ler este arquivo). Vale no Forge e em todo projeto.

## A regra (H2-AUTOR-FICA-ATE-O-MERGE)
- **O autor fica com o item até o merge:** o agente que escreveu a branch é quem a leva até a integração. Toda volta vai à mesma instância dele: achado de review, de QA e de segurança, CI vermelho do PR e conflito com a base.
- **Retomada por `SendMessage`** (to: o id do autor), com o brief de volta. A instância já tem o contexto: corrige o que o brief aponta sem reler tudo.
- **Agente novo apenas se o autor travou:** o id foi liberado como morto (lápide no registro do hook `agentes`), a sessão reiniciou e o id se perdeu, ou o registro passou do prazo (`expiracao_horas`). A instância nova recebe o mesmo brief de volta.
- **Uma volta por rodada:** os bloqueantes dos três portões (review, segurança e QA) no mesmo head viram um brief único, `forge-check brief gerar --pedido <p> --volta <brief anterior> --ref <branch> --parecer <arquivo>...`, com um `--parecer` por portão. CI vermelho ou conflito que já estejam lá entram no mesmo brief; o que chega depois é a volta seguinte. Recomendação não entra.
- Na revalidação, só é retomado quem deu o parecer com `revalida: sim` no `forge-check parecer delta <parecer>` (o que barrou ou o de domínio mudado); `revalida: não` segue valendo (META85, passo 5 do Jarvis).
- **Uma passada (H3):** antes de entregar, o autor roda a autoverificação contra os achados recorrentes que o brief de código pede (`python3 -m unittest tests.test_forge_mutante.ConferirTodas`, AR-12, e os testes de tamanho de texto); os portões rodam uma vez, juntos, no fim. O brief do portão traz no `## Ler` o `parecer delta` do parecer desatualizado ou reprovado, e o `brief gerar` avisa quando o parecer da branch está aprovado e em dia: esse portão não se dispara.

## O aviso do hook `agentes`
- Disparo de escrita numa branch cujo autor pode ser retomado recebe o aviso `R-TETO` `aviso: autor retomável (<branch>: <id>)`. O disparo segue (é aviso, não recusa): pare o agente novo e retome o autor por `SendMessage`, salvo se ele travou.
- O aviso não aparece com o autor ativo, com lápide no id ou depois do prazo.
- Versão sem o aviso: o id do autor é o que a ferramenta de agentes devolveu ao lançá-lo.

## Medida e revisão
- Medida: agentes disparados por item mesclado, levada ao dono a cada versão; partida de cerca de 12, meta de 6 (ordem do dono de 17/11).
- Revisão: se em duas versões a medida não cair, ou se a retomada deixar o item mais lento que a instância nova, o `tech-lead` traz ao dono a revisão desta regra.
