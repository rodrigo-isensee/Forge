---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-fechar-1c
commit: 845b1c599976d4e5939e858c92172d09fd0c313f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0479-fechar-1c

Escopo: etapa E30.5 do pedido v0478, no head 845b1c59. Delta lido desde a rodada E30.3 (ef6b06e6, parecer ed4350e8): `git diff ef6b06e6 845b1c59` só traz pareceres (`docs/qa/`, `docs/reviews/`, `docs/security/`); código, teste e mutante são os mesmos já lidos. A análise da E30.3 (ordem e falha fechada do 1c no merge, estado entre chamadas, entrada) continua valendo e fica no git. Esta rodada responde ao pedido do dono (19/11 08:54): a mudança só aperta?

## Gatilhos
Gatilhos: controle de merge (forge-fechar, passo 2b com o 1c no merge), guarda de fluxo de branches (R-FLUXO), arquivo sensível da catraca (bin/)

## Achados

## Sondas

## Só aperta?
**Sim.** No head 845b1c59, contra a origin/develop (diff do PR, `git diff origin/develop...HEAD`, base efetiva 73842444), nada passa a ser aceito que antes era recusado. Provas, arquivo por arquivo:

- `bin/forge-fechar:842-844` (a única mudança de comportamento): uma chamada nova a `promovivel "$novo" ...` dentro de `trazer_a_base`, depois do `commit-tree` e antes de qualquer escrita de ref (`:847-852`) e do `git push origin` (`:854`). É só uma recusa a mais: `promovivel` (`:908-918`) termina em `die` (`:69`, `exit 1`) quando o promover-homolog sai diferente de 0, estoura o prazo (124) ou falta. O caminho de sucesso continua o mesmo (envio e recomeço com `--trazida`, que roda de novo o 1c no head novo, `:1273`, inalterado). `trazer_a_base` roda no shell principal (chamada direta em `:880`; `conferir_base` chamada direta em `:1299`, sem `$( )`), então a recusa encerra o script, não um subshell. Efeito colateral novo: nenhum além do que o 1c do head já fazia (busca só de `refs/remotes/origin/homolog` quando falta, `:912-913`) e um commit solto no banco local, sem ref.
- `bin/forge-fechar:916`: `${2:+ ($2)}` só muda o texto da mensagem de parada; não muda condição, código de saída nem o que se compara. Sem `eval`.
- `bin/forge-fechar:9`, `:905` (comentários) e `:1174` (texto do `--dry-run`): só texto; o `--dry-run` continua sem git remoto nem gh.
- `tests/test_fechar_base_andou.py:149-150`: a única asserção trocada. A antiga exigia o trecho `...(árvore do merge-tree), git push origin melhoria/x`; as novas exigem `...(árvore do merge-tree), roda o 1c` e `git push origin melhoria/x e recomeça a cadeia no head novo (H4)`, que é mais longo que o fim antigo. Nenhum teste removido, nenhum `skip`; três testes novos (`:271-309`), dois deles de recusa.
- `tests/mutantes/v0478-fechar-1c.json`: mutante novo (M1) que desliga a chamada; só acrescenta guarda.
- `changelog.d/v0479-fechar-1c.md` e os pareceres em `docs/`: texto, sem efeito em controle.
- Controles intocados: `tests/config.json`, `tests/catraca.py`, `hooks/`, `.github/`, `.githooks/` e `scripts/` estão fora do diff (`git diff --stat origin/develop...HEAD`: 7 arquivos). `FORGE_PROMOVER` continua só com `FORGE_FECHAR_TESTE=1`.
- Catraca local: `python3 -I tests/catraca.py --modo regras --base origin/develop --head HEAD --ramo melhoria/v0479-fechar-1c` sai 0 sem violação; o rótulo é pedido só porque `bin/` está em `SENSIVEIS` (`tests/catraca.py:50`), não por regra piorada.

Nenhum ponto aceita mais. Condição do "sim": vale para este head. A origin/develop andou (c720891e) e `git merge-tree --write-tree HEAD origin/develop` dá conflito em `bin/forge-fechar`, na linha da mensagem do 1c: a develop (bdf1b998) passou a chamar o promover-homolog por `conferir_1c <sha> [nota]` e deixou `promovivel` com um argumento só. A resolução é código novo num arquivo sensível: o head resolvido precisa de leitura por delta antes de o rótulo valer para ele. A resolução que só aperta mantém a chamada do 1c no merge antes do envio e leva o "onde" à nota do `conferir_1c` (ou o descarta), sem mudar a condição `rc_1c = 0`.

## Detalhe dos achados
Sem achado nesta rodada.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados neste head: os 3 testes `e30_1` (OK, 2,3 s) e a catraca em modo `regras` (rc 0). A suíte inteira fica no CI do PR. Lacunas do ambiente: shellcheck e gitleaks fora do PATH (não instalados, R-CUSTO).
