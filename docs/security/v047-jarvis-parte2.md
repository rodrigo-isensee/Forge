---
tipo: revisao-seguranca
contrato: 1
pedido: v047-jarvis-parte2
branch: melhoria/v047-jarvis-parte2
commit: 1c3e34f2d04e2a6250615182a225c65d2ac201ad
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v047-jarvis-parte2 (E4.2, diretrizes 2, 11 e 16)

## Gatilhos
Regra de processo em `docs/regras/README.md` e em duas skills (`R-WIP`, `R-FLUXO`, `R-REVIEW`): nenhum código de produção, hook, workflow, segredo nem permissão tocados. Revisão por segurança do que a edição poderia afrouxar.

## Achados
- A1 (recomendado) docs/regras/README.md:10 · âncoras das 5 regras de R-LIMITES.md removidas dos links: a navegação cai no topo do arquivo, sem perda de regra; opcional restaurar o link do R-MAIN.

## Sondas

## Detalhe dos achados
- A1: informativa, esforço P, dono tech-lead. Os 5 links apontam para `R-LIMITES.md` (existe); o texto de cada regra segue em `R-LIMITES.md`, só a âncora saiu.
- Conferido sem achado: as regras cortadas (validade e medida, `R-WIP` 1 cartão por agente, gargalo, teto, limites de coluna, `origem:` nunca validação do usuário) estão todas no texto novo; o corte de "AV5", da exceção `anti_duplicacao.excecoes` e de "(pedido do usuário)" é só referência. "Portão sem retorno em 53 min: confira que parou e relance" mantém a conferência antes de relançar. A integração na `develop` segue exigindo pareceres da classe aprovados e CI verde, agora por PR próprio. "Vaga livre não espera a versão" vale só para começar (desenho, plano de teste, ameaças, item sem arquivo em comum): o merge continua pelo fluxo, sem pular portão; "parado não se abandona" não cria atalho de aprovação.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados no head: `RegrasInviolaveis`, `RegrasComId`, `TextosDoAgenteEDaRegra`, `DiretrizesDoDonoNaRWip`, `AntiDuplicacao` (13 testes, OK); todos os links relativos de `docs/regras/README.md` resolvem; 10 recusas `(R-WIP)` em `bin/forge-check`, como a medida diz. Suíte inteira não rodada local (carga da máquina, diretriz 15); fica ao CI do PR, ainda não aberto. Sem ferramentas de varredura necessárias (só texto).
