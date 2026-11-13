---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-jarvis-parte2
commit: 65cf916b96d6bfa7e0acb7472bfe21b2c7b91551
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v047-jarvis-parte2 (E4.2, diretrizes 2, 11 e 16)

## Gatilhos
Regra de processo em `docs/regras/README.md` e em duas skills (`R-WIP`, `R-FLUXO`, `R-REVIEW`): nenhum código de produção, hook, workflow, segredo nem permissão tocados. Revisão por segurança do que a edição poderia afrouxar.

## Achados
- A2 (bloqueante) tests/test_forge.py:626 · o enxugamento da E3.15 reescreveu a linha Integração contínua (D2) de skills/trabalho-em-paralelo/SKILL.md:16 e o teste da diretriz 16 ainda exige a frase antiga: DiretrizesDoDonoNaRWip falha no head (CI vermelho); ver S1.
- A1 (recomendado) docs/regras/README.md:10 · âncoras das 5 regras de R-LIMITES.md removidas dos links: a navegação cai no topo do arquivo, sem perda de regra; opcional restaurar o link do R-MAIN.

## Sondas
- S1 · `python3 -I -m unittest tests.test_forge.DiretrizesDoDonoNaRWip.test_as_skills_do_passo_citam_o_id` · espera: OK · obtido: FAIL, AssertionError: frase `entra na develop por PR próprio, com CI verde, sem junção de frentes (R-FLUXO)` não encontrada (tests/test_forge.py:626)

## Detalhe dos achados
- A1: informativa, esforço P, dono tech-lead. Os 5 links apontam para `R-LIMITES.md` (existe); o texto de cada regra segue em `R-LIMITES.md`, só a âncora saiu.
- Conferido sem achado: as regras cortadas (validade e medida, `R-WIP` 1 cartão por agente, gargalo, teto, limites de coluna, `origem:` nunca validação do usuário) estão todas no texto novo; o corte de "AV5", da exceção `anti_duplicacao.excecoes` e de "(pedido do usuário)" é só referência. "Portão sem retorno em 53 min: confira que parou e relance" mantém a conferência antes de relançar. A integração na `develop` segue exigindo pareceres da classe aprovados e CI verde, agora por PR próprio. "Vaga livre não espera a versão" vale só para começar (desenho, plano de teste, ameaças, item sem arquivo em comum): o merge continua pelo fluxo, sem pular portão; "parado não se abandona" não cria atalho de aprovação.

## Revalidação (delta 1c3e34f2..65cf916b, E3.20)
Lido só `forge-check parecer delta`: skills/kanban-scrum/SKILL.md e skills/trabalho-em-paralelo/SKILL.md (tests/test_reval_delta.py é só lista, fora do domínio). Nenhuma regra afrouxou: o PR passou a abrir com pareceres aprovados no head (mais estrito), o corte de "serializam", "gargalo" e dos relógios D-4 é só redação, o acréscimo de triagem é adição. Sem achado de segurança novo; a reprovação é só por A2.
- A2: defeito provado, esforço P, dono tech-lead (teste) ou autor da skill. Correção mínima: alinhar a asserção de tests/test_forge.py:626 à frase nova da skill, isto é, exigir `entra na `develop` por PR próprio, sem juntar frentes (`R-FLUXO`)` (ou a frase inteira "o PR abre com os pareceres da classe aprovados no head e a entrega conferida; com CI verde, entra na `develop` por PR próprio, sem juntar frentes (`R-FLUXO`)"), mantendo a exigência de PR próprio e do ID `R-FLUXO`, sem remover a asserção. Rodar `DiretrizesDoDonoNaRWip`.
- Os outros 12 testes do conjunto afetado (`RegrasInviolaveis`, `RegrasComId`, `TextosDoAgenteEDaRegra`, `AntiDuplicacao` e o resto de `DiretrizesDoDonoNaRWip`) passam. Suíte inteira não rodada (carga, diretriz 15); sem PR aberto.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados no head: `RegrasInviolaveis`, `RegrasComId`, `TextosDoAgenteEDaRegra`, `DiretrizesDoDonoNaRWip`, `AntiDuplicacao` (13 testes, OK); todos os links relativos de `docs/regras/README.md` resolvem; 10 recusas `(R-WIP)` em `bin/forge-check`, como a medida diz. Suíte inteira não rodada local (carga da máquina, diretriz 15); fica ao CI do PR, ainda não aberto. Sem ferramentas de varredura necessárias (só texto).
