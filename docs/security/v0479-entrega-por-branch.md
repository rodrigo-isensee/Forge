---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-por-branch
commit: f39a94ed266957ef62be4bc1061c2581da54a7db
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 E79.6, ENTREGA-POR-BRANCH (K-345), revalidação

Volta por delta (`R-REVIEW`): a rodada anterior (reprovada em `f4689e12`) fica no git. Lido só `forge-check parecer delta`, intervalo `f4689e12..f39a94ed`; no domínio, só `bin/forge-check`. Fora do domínio e não relidos: `changelog.d/`, `tests/mutantes/`, `tests/test_selo_e_entrega.py` (usado só para rodar as sondas).

## Gatilhos
Gatilhos: controle do Forge (`bin/forge-check`: escritor único da linha `entrega conferida` no Histórico).

## Delta lido
- `bin/forge-check:10091-10093` (`cmd_entrega_conferir`): a ponta passa a vir de `remoto_da_branch` (`bin/forge-check:7552`, `git ls-remote origin refs/heads/<branch>`, só a linha do nome exato, sha validado por `SHA40`); grava só com `lido` e `remoto == head`.
- `bin/forge-check:10020` (`recusa_da_gravacao`): mensagem por caso (sem resposta do remoto, branch ausente no remoto, ponta diferente); o nome passa por `nome_seguro`.
- `bin/forge-check:1605` e `:1619`: só o texto do aviso de isenção de QA; nenhuma condição muda.

## A mudança só aperta?
Sim. Antes recusava com `remoto` (ref de rastreio) presente e diferente do head; agora recusa sempre que o `ls-remote` não responde (falha fechada, o `git()` tem limite de tempo e o `TimeoutExpired` vira não lido), que a branch não existe no remoto, ou que a ponta remota difere do head. O único caso antes recusado e agora aceito é a ref de rastreio velha com o remoto já igual ao head (envio por outra cópia sem `fetch`): a ponta está de fato no `origin`, que é o requisito; não é afrouxamento. `--sem-gravar` segue conferindo sem gravar.

Limite residual, sem caminho de ataque proporcional: quem troca o URL do `origin` na própria cópia controla o que o `ls-remote` responde; é forja deliberada do ator local, fora do K-345 (o esquecimento do envio).

## Achados da rodada anterior
- A1 (rodada f4689e12, bloqueante): corrigido em `bin/forge-check:10092`; S1 e S2 agora recusam; testes `test_k345_branch_nunca_enviada_nao_grava` e `test_k345_ref_de_rastreio_apagada_ou_forjada_nao_grava`.
- A2 (rodada f4689e12, recomendado): corrigido em `bin/forge-check:10091` (ls-remote); S3 agora recusa; testes `test_k345_ref_de_rastreio_apagada_ou_forjada_nao_grava` e `test_k345_origin_sem_resposta_nao_grava`.

## Sondas
- S1 · selado, entregar, sem push, `forge-check entrega --pedido exemplo --branch melhoria/x --etapa codigo` gravando · espera: rc 1 e nada gravado · obtido: rc 1, `head: a "origin/melhoria/x" não existe no remoto (git ls-remote)`, nada gravado
- S2 · push, commit só local, `git update-ref -d refs/remotes/origin/melhoria/x`, conferir gravando · espera: rc 1 e nada gravado · obtido: rc 1, `head: o local <local> não é a "origin/melhoria/x" <enviado>`, nada gravado
- S3 · push, commit só local, `git update-ref refs/remotes/origin/melhoria/x <local>`, conferir gravando · espera: rc 1 · obtido: rc 1, mesma recusa, nada gravado
- S4 · legítimo: push do head, conferir gravando · espera: rc 0 e uma linha gravada · obtido: rc 0, 1 linha

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte: não rodada aqui (brief: sem suíte local); o CI do PR não foi consultável desta sessão (sem `gh`), lacuna registrada. Rodados: as sondas S1 a S4 (subclasse da `Entrega` de `tests/test_selo_e_entrega.py`, em pasta temporária, 20 testes `OK`) e os 4 testes `test_k345_*` da classe `Entrega` (`OK`). Sem segredo no delta (leitura manual).
