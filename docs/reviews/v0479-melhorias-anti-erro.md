---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-melhorias-anti-erro
commit: 57beff2a66ab13048540f90dcdffdc689e359aad
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0479-melhorias-anti-erro

Code review do desenho das AE1 e AE3 a AE8 (v0478 E54.9) no head 57beff2a, base develop 5ccac0bf. O diff é só texto: `docs/propostas/v0479-melhorias-anti-erro.md` (244 linhas) e o fragmento `changelog.d/v0479-melhorias-anti-erro.md`. Classe T; sem código, sem guarda, sem mutante.

## Achados
- A1 (bloqueante) docs/propostas/v0479-melhorias-anti-erro.md:144 · O AE3.1 manda o commit automático rodar com `core.hooksPath` vazio. Isso troca o caminho dos hooks, o que `R-VERIFY` proíbe (`hooks/conformidade.py:2563` barra o mesmo). Fora do sandbox o relógio nem passa pelo hook. Troque por recusa quando a pasta de controle tiver hook ativo.
- A2 (recomendado) docs/propostas/v0479-melhorias-anti-erro.md:145 · O AE3.2 e o D3 (linha 196) dão push ao relógio, e a linha 11 diz que só se lê o GitHub. A condição do dono no D7 (20/11 13:51) é: só lê o GitHub e só grava na pasta de controle. Registre a condição e diga quem faz o push.

## Parecer
Reprovado pelo A1. O desenho está bem fundamentado. A seção 1 traz medida com fonte. A seção 2 explica por que o existente não basta, com evidência (conferi `bin/forge-check:7771`: é o `linhas_de_decisao` dentro do `cmd_decisoes`, só DECISÃO). O corte respeita o teto de 150 linhas (H1) e uma trilha por arquivo (diretriz 33). A seção 7 tem critério de reversão observável por risco, e a seção 5 traz oráculos por classe (PAR-P2). Neutro (`R-NEUTRO`): a pasta de controle está definida para o Forge e para o projeto. Sem custo (`R-CUSTO`): a opção (c) do D7 foi recusada pelo custo.

A1: o caso de abuso "`.git/hooks` da pasta de controle" é real, mas a defesa escolhida contorna um controle (`R-VERIFY`, `R-CONFORMIDADE`). Isso piora porque o relógio roda fora do sandbox (D7), onde o hook `conformidade` não vê o comando. Uma defesa que aperta em vez de contornar: o `controle salvar` confere `core.hooksPath` e `.git/hooks` antes do commit e recusa, com `nao-verificavel`, se houver hook ativo que não seja da fábrica. A correção é de uma célula da tabela e não muda nenhuma decisão do dono.

A2 não bloqueia. As decisões do dono chegam ao brief por referência (`R-BRIEF`), mas quem implementar o AE3.2 lendo só o desenho vai achar push no relógio. Isso esbarra na condição do D7.

Suíte: não rodada (brief: sem suíte local; texto só). Sem PR, sem CI para citar.
