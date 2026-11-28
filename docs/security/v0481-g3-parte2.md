---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-g3-parte2
commit: 91e3d5fe4cbfae0a7e99bdb6e1e6bd6a1aebd23f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E28.8, G3 F2 partes 2 e 3, #927)

1ª rodada completa sobre `346a7860..91e3d5fe` (`bin/forge-check`, a skill `briefs-e-conferencia/conferencia-da-entrega.md`, testes, mutantes, fragmento do changelog). Ordens do dono de 26/11 16:55 e 18:54 (`## Decisões` do pedido) cobrem a saída do D2 e da bateria local e o QA lendo o CI.

Gatilhos: controle do Forge (portão da conferência da entrega e pré-voo do `forge-check pr`), leitura do GitHub pelo gh.

- ci: 91e3d5fe4cbfae0a7e99bdb6e1e6bd6a1aebd23f verde

## Achados
- A1 (recomendado) bin/forge-check:1800 · A docstring diz que o hook segue exigindo a conferência; no Forge o hook `parecer` só a vê pelo resultado gravado: sem ele, `gh pr ready`/`gh pr merge` rodam só o `cmd_pr` (hooks/parecer.py:864). Corrigir o texto: quem exige é o `pr` sem `--previo` e o `forge-fechar`.

## O que aperta, o neutro e o que afrouxa
**Aperta**
- Fecha o A1 da segurança do #923: `JOBS_DO_AGREGADOR` (`bin/forge-check:10732`) entra em `checks_ruins` por `mais` (`:1590`, `:10755`) e exige presentes e em pass, um a um, `bateria (passos)`, `bateria (verificações longas)`, `teto de pulados (python 3.12)` e `suíte (python 3.12, parte 1/5)` a `parte 5/5`; ausente ou `skipping` reprova. A janela em que um job dependente ainda não tinha check criado fecha. O `split("/", 1)` preserva o `1/5` do nome. Divergência futura com o `ci.yml` falha fechada (exigido ausente) e o teste `test_os_jobs_do_agregador_sao_os_needs_do_job_bateria_do_ci` a acusa. Testes: `test_job_do_agregador_ausente_ou_pulado_reprova` (8 jobs × ausente/pulado).
- Título do PR (PR-TITULO-DO-BRIEF) volta a ter portão na entrega, agora pela `prova_do_ci` (`:10752`), com o título lido no mesmo `gh pr view` do head; falha fechada (o regex que casa reprova). Era o pedaço que o #923 deixava sem portão.

**Neutro**
- `PQ_DO_CI` (`:9975`, `:10203`) é do tipo `pr`, que a conferência não reexecuta; a prova vem da `prova_do_ci`, que já roda no head do Forge. Nada de código da branch roda em quem confere.
- Título trocado depois da conferência: o autor pode editá-lo depois; é regra de qualidade, não de segurança, sem ganho para quem tenta.
- O resto do que o D2 conferia continua com portão: teto H1 pelo `tamanho_do_pr` do `forge-check pr`, pr-texto pela `catraca` exigida no merge, base velha pelo CI do merge.

**Afrouxa (por ordem do dono)**
- O brief de código do Forge deixa de pedir o D2 e a bateria local; o autor roda só os afetados e a prova é o CI do PR no head (a conferência a exige).
- `forge-check pr --previo`: a conferência que falta vira aviso (`:1803`). **Não abre caminho para entrar sem ela:** o `--previo` não grava o resultado que o hook lê (`:11757`; `tests/test_pr_hook_prazo.py:255`) e não imprime veredito (`:11761`); o merge passa pelo `forge-check pr` sem `--previo` no passo 1 do `forge-fechar` (`bin/forge-fechar:1879`, e `:1374` na seleção), pelos `pr_da_cli` do `brief gerar` de merge (sem `previo`) e pelo `passo_do_item`, todos exigindo a conferência (`test_o_pr_passa_o_previo_a_conferencia_com_e_sem_base`). O que se perde é só a ordem: o parecer de review e QA pode nascer antes da conferência; se ela depois reprovar, o merge fica preso.
- Resíduo, anterior a este diff (cartão, fora do delta): o hook `parecer` no Forge, sem resultado gravado, libera `gh pr ready`/`gh pr merge` do tech-lead pelos pareceres sem a conferência (`hooks/parecer.py:849-866`). Antes, o pré-voo dos revisores cobrava a conferência e servia de barreira indireta; agora a barreira é só o `forge-fechar`. Quem: o tech-lead (único com `pr_merge_integracao`) mesclando à mão fora do `forge-fechar`; ganho: entrar sem os PQ do autor conferidos, com o CI exigido pela proteção da branch e os pareceres aprovados. Severidade baixa. Correção sugerida: no clone do Forge, o `verificar` com `ATALHO` soma `fc.conferencia_do_head` ao `cmd_pr`. Dono: tech-lead.

## Detalhe dos achados
**A1** · evidência: `bin/forge-check:1800` (docstring de `conferencia_do_head`); o caminho do hook em `hooks/parecer.py:849-866` chama só `fc.cmd_pr`, que não lê a conferência (ela só entra pelo `pr_da_cli`, `bin/forge-check:1659`, `:1677`). Caminho de ataque: quem confia no texto deixa de rodar o `forge-fechar` achando que o hook segura o merge. Severidade: baixa. Correção mínima: o texto diz que o merge exige a conferência pelo `forge-check pr` sem `--previo` e pelo `forge-fechar`, e o hook só pelo resultado gravado; ou o hook passa a exigi-la (o cartão acima). Esforço: P. Dono: tech-lead (autor do E28.6).

## Riscos aceitos e ferramentas
Nenhum risco aceito. CI do #927 no head 91e3d5fe (run 45920800632): todos em pass ou skipping, instalação e verificações longas (e2e) inclusas, fora `bateria (pareceres)` e `bateria`, vermelhos por construção (esperam os pareceres), e a `catraca` em pass. Rodados aqui: `tests.test_forge_pronto` e `tests.test_pre_envio_brief.QaLeOCiSemEsperarAConferencia`, 43 OK. Ferramentas: o varredor de segredos não está no PATH (lacuna; diff sem credencial, lido à mão); sem SAST de workflow, que esta entrega não toca.
