---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-d2-portao-entrega
commit: 5cac29190646ed60b36cfe8f704b948bc920ee69
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E173.24, PR #864, volta por delta)

Delta lido: `forge-check parecer delta` em `d64a506b..5cac2919` (E173.16). No domínio: `patches/d2-portao-entrega.patch` e `tests/test_pre_push_d2.py`; fora: o fragmento do changelog e `tests/mutantes/*.json`. Já lido e sem mudança: o resto do patch e a conclusão da rodada em `d64a506b` (no git). Achados anteriores: nenhum.

Gatilhos: hook de envio (portão local do pre-push, controle do Forge), chamada ao `gh` com corpo de PR vindo da rede

## Achados
- A1 (recomendado) patches/d2-portao-entrega.patch:50 · O comentário diz que a fronteira do `d2_so_avisa` é a do `so_parecer`, mas o filtro (`:59`) é mais largo: aceita docs/security/aceites/, docs/security/ameacas/, `_*` e apagar. Sem caminho de ataque (D2 não confere esses arquivos); alinhe o filtro às exclusões do so_parecer ou corrija o texto.

## Detalhe dos achados
Conclusão por escrito: em relação ao hook em vigor, o patch **só aperta** (o hook vivo não tem o PORTAO-D2); em relação à rodada anterior, o delta troca `falhas=1` por `d2_so_avisa || falhas=1` só nos dois blocos D2 (`:76`, `:88`), e o "só avisa" **não abre caminho para enviar outra coisa sem as checagens**:

- **Só o D2 é afrouxado.** Nenhuma outra checagem do hook passa a consultar o `d2_so_avisa`; neutralidade, não fast-forward (R-VERIFY, `.githooks/pre-push:144`), changelog e as demais barram igual.
- **Todo ref é conferido.** O laço percorre todos os `envios` (`:55`), não só o do HEAD: um envio de duas refs, uma só de parecer e outra com código, barra. Remoção de ref não entra em `envios` (`.githooks/pre-push:142`) e não tem o que o D2 confira.
- **Falha fechada.** Ref nova (remoto zero), sha remoto desconhecido ou `git diff` com erro dão delta vazio; a linha vazia casa o `grep -v` e barra (`:57-59`; `test_ref_nova_ou_sha_remoto_desconhecido_barra`). Nome com caractere de controle sai entre aspas pelo git e também barra. O delta é sobre ancestral provado (o hook já recusa o não fast-forward), então o que vai é só o diff de árvore lido.
- **O que o D2 deixa de barrar já está no remoto.** Índice, teto e corpo do PR medem a branch (código já enviado e revisado); um delta só em `docs/{reviews,qa,security,devops}/` não muda `bin/`, `hooks/` nem `scripts/` (`scripts/indice-forge.py:21`) nem o corpo do PR. O CI do PR segue o portão que vale.
- **A1, fronteira.** Sonda local: um envio só de `docs/security/aceites/x.md`, `docs/security/ameacas/x.md` ou `docs/qa/_modelo.md` sobre o PR com teto estourado sai 0 com o aviso. Não é caminho de ataque: o D2 nunca conferiu esses arquivos, que continuam sob o hook `conformidade`, o `forge-check docs` e o CI; é só divergência entre o comentário e o filtro.
- **Testes dos arquivos tocados:** `python3 -m unittest tests.test_pre_push_d2` no head 5cac2919: 22 testes, OK (28,1 s); `git apply --check` do patch: aplica limpo. Suíte inteira: só no CI do PR #864 (não conferível daqui: o `gh` não tem credencial no sandbox).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do delta, `git apply --check`, testes do arquivo tocado e uma sonda local (subclasse do `SoParecer` em arquivo do scratchpad, entradas `docs/security/aceites/x.md`, `docs/security/ameacas/x.md`, `docs/qa/_modelo.md`; obtido: saída 0 com o aviso nas três). Lacuna: analisador de shell e varredores de segredo e de workflow fora do PATH (o CI roda o analisador de shell).
