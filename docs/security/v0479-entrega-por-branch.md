---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-por-branch
commit: f4689e1254bf579f5110b4f58c677fac1b9f05e3
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 E79.3, ENTREGA-POR-BRANCH (K-345)

Escopo: `adc52def..f4689e12`, 1 commit; código só em `bin/forge-check` (`isencoes_do_diff` e `cmd_entrega_conferir`), mais 2 testes, 4 mutantes e o fragmento do changelog.

## Gatilhos
Gatilhos: controle do Forge (`bin/forge-check`: portão de isenção de QA e escritor único da linha `entrega conferida` no Histórico).

## A mudança só aperta?
Sim, nas duas partes. Nenhum caso antes recusado passa a ser aceito:
- `isencoes_do_diff` (`bin/forge-check:1044`): o predicado novo exige a catraca carregada e usa `motivo_de_controle`, que já inclui o `MD_DE_CONTROLE` (`bin/forge-check:1087`); o conjunto isento é subconjunto do anterior. Catraca que não carrega devolve `set()` (falha fechada). Teste novo `test_k345_md_em_caminho_de_controle_da_classe_nao_isenta` rodado aqui: `OK`.
- `cmd_entrega_conferir` (`bin/forge-check:10080-10083`): só acrescenta uma linha de reprovação; não remove condição nenhuma. Teste novo `test_k345_ponta_local_diferente_da_enviada_nao_grava` rodado aqui: `OK`.

O aperto da gravação, porém, é incompleto: a ausência da `origin/<branch>` é tratada como consentimento (A1).

## Achados
- A1 (bloqueante) bin/forge-check:10081 · sem a ref origin/<branch> (branch nunca enviada, ou ref de rastreio apagada) a condição é falsa e a entrega grava a ponta só local, contra o que o changelog.d/v0479-entrega-por-branch.md:2 afirma ("só grava a ponta enviada"); provas S1 e S2.
- A2 (recomendado) bin/forge-check:10080 · a ponta "enviada" é lida da ref de rastreio local, que um update-ref local iguala ao head sem envio (S3 grava); conferir contra o remoto (ls-remote) ou registrar o limite no comentário.

## Sondas
- S1 · selado, entregar, sem push, `forge-check entrega --pedido` gravando (sonda sobre a classe Entrega dos testes) · espera: rc 1 e nada gravado · obtido: rc 0 e a ponta local gravada
- S2 · push, commit só local, `git update-ref -d refs/remotes/origin/melhoria/x`, conferir gravando · espera: rc 1 e nada gravado · obtido: rc 0 e o commit só local gravado
- S3 · push, commit só local, `git update-ref refs/remotes/origin/melhoria/x <local>`, conferir gravando · espera: rc 1 · obtido: rc 0 e o commit só local gravado

## Detalhe dos achados
**A1.** Evidência: `bin/forge-check:10081` (`if gravar and remoto and remoto != head`). Caminho: o autor (ou o Jarvis) confere a entrega antes do primeiro envio, ou com a ref de rastreio ausente (`fetch --prune` depois de a branch remota sumir, outro nome de remoto); a linha `entrega conferida <sha>` vai ao Histórico apontando um commit que ninguém mais vê, e o portão seguinte (review, QA, segurança no "mesmo head") ancora num sha que não existe no remoto. É o mesmo defeito do K-345 que este item corrige, só por outra entrada. Severidade: baixa (integridade do registro do processo, ator local, sem dado nem segredo), bloqueante por ser defeito provado contra o requisito declarado do item. Correção mínima: recusar também quando `remoto` é `None` com `gravar` (mensagem "a branch não foi enviada; envie antes de gravar ou confira com --sem-gravar"), e ajustar os testes que hoje gravam sem envio (`test_cumpriu_grava_uma_vez` e os da classe `Entrega` que chamam `conferir()` sem `push`) para enviar antes; um mutante para a nova condição. Esforço: P. Dono: tech-lead (autor do E79.1).

**A2.** Evidência: `bin/forge-check:10080` lê `refs/remotes/origin/{branch}`, que é estado local. Caminho: só deliberado (um agente forja a ref com `update-ref`); proporcionalidade: recomendação, não vulnerabilidade. Correção mínima: comparar com `git ls-remote origin refs/heads/<branch>` (rede local ao remoto já usado pelo push) ou, se a rede for indesejada aqui, dizer no comentário que a garantia é contra o esquecimento, não contra forja. Esforço: P. Dono: tech-lead. Volta e é corrigido antes do merge (`R-REVIEW`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte: não rodada aqui (brief: sem suíte local); a do autor está em `/root/.forge-contrib/wt/e791-saida/resumo.log`, citada no review E79.2; o CI do PR não foi consultável desta sessão (sem acesso ao `gh`), lacuna registrada. Rodados: os 2 testes novos (`OK`) e as sondas S1 a S3 (classe `Entrega` de `tests/test_selo_e_entrega.py`, em pasta temporária). Sem segredo no diff (leitura manual).
