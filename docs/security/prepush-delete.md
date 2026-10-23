---
tipo: revisao-seguranca
contrato: 1
pedido: PREPUSH-DELETE
branch: melhoria/prepush-delete
commit: 4d4eadf67ce3691992806b6cc39577428d57a584
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: PREPUSH-DELETE

## Gatilhos
Controle do Forge (`R-SEGURANCA`): `.githooks/pre-push` (R-VERIFY, R-FLUXO). Revisão estática do diff `origin/develop...4d4eadf`.

## Achados

## Detalhe dos achados
Conferido no código (`.githooks/pre-push:105-147`) e nos testes novos (`tests/test_pre_push_trava.py`):
- Só o push de remoção pula a suíte: `n_envios` conta as refs com `local_sha` com algum dígito diferente de zero; o atalho exige `n_refs > 0` e `n_envios == 0`, fora do `--suite`. Uma ref que envia código, mesmo ao lado de remoções e em qualquer ordem, faz `n_envios >= 1` e segue o caminho de sempre.
- Remoção de `main`, `homolog` e `develop` continua recusada: a recusa por `remote_ref` está dentro do `while`, que lê todas as refs antes do atalho (que fica depois do laço); a recusa sai com `exit 1`, inclusive para remoção e para remoção misturada a branch comum. Os testes cobrem os três nomes e o caso com `develop` junto.
- Push misto e push com código: sem mudança. A checagem de fast-forward (R-VERIFY) continua antes e só vale para `local_sha` não zerado; o atalho não a afrouxa. Sem entrada vazia, o caminho `n_refs=0` é o anterior.
- Caminho de ataque: quem controla o stdin do hook já controla a máquina local; o atalho não dá ganho a quem apaga ref (não leva objeto novo). A defesa de fundo (CI e proteção de branch no remoto) não muda.
- Observação informativa (sem ação): remoção de tag (`refs/tags/*`) também pula a suíte, como o texto da mensagem diz; antes ela já não era barrada, só atrasada.
- shellcheck: `shellcheck -x .githooks/pre-push` sem avisos (rodado na worktree do commit revisado).

## Riscos aceitos e ferramentas
Sem riscos aceitos. Ferramentas: shellcheck (presente no PATH). A suíte completa não foi rodada por este parecer (é do QA e do CI); a leitura dos testes novos foi estática. O rótulo `afrouxa-regra` no PR é do dono, pois o pre-push deixa de rodar a suíte em um caso.
