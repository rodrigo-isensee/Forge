---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-limpeza-fim-item
commit: 71996730a3e485db4410e9e4a824fe4e113d4ace
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-limpeza-fim-item

Etapa E68.3 do pedido v0478. Primeira rodada, sobre `bead3e53..71996730`. Lidos: `bin/forge-copia` (modo `limpar`, `fim_do_item`, `ler`), `bin/forge-fechar` (`limpar_copias_sem_merge` e o desvio do `--limpar` sem PR MERGED), a linha nova de `skills/trabalho-em-paralelo/ritmo-e-corte.md` e os testes novos `Limpar` e `LimparSemMerge`.

## Gatilhos
Gatilhos: apagamento de arquivo no disco (cópias de trabalho), controle do fluxo de fechamento (`forge-fechar --limpar`), leitura de dado vindo do GitHub (`gh pr list`).

## Achados
- A1 (recomendado) bin/forge-copia:114 · `gh pr list --head <branch>` também lista PR de fork com o mesmo nome de branch; no repositório público, qualquer conta abre e fecha um PR assim e faz o `limpar` tratar como acabado o item sem PR próprio. Filtre `isCrossRepository == false`.
- A2 (recomendado) bin/forge-copia:151 · As checagens de limpeza (status, stash, rev-list) rodam antes da consulta de rede ao `gh`, e o `rmtree` só vem depois dela. Uma escrita na cópia nesse intervalo de segundos se perde. Chame `fim_do_item` antes das checagens, logo antes de apagar.

## Detalhe dos achados
**O que pedia a etapa: nunca apagar trabalho fora da origem nem pasta fora de `~/.forge-contrib`. Os dois se sustentam.**
- **Contenção do caminho** (`bin/forge-copia:129-134`): o destino passa por `resolve()`, que resolve `..` e link simbólico, e depois pela `commonpath` contra `raiz()`, que é o `realpath` de `~/.forge-contrib`. A própria pasta é recusada. Também é recusado o que não for a raiz do repositório (`rev-parse --show-toplevel` igual ao destino). Isso importa porque `~/.forge-contrib` é ela mesma um repositório git: uma subpasta dela, como `docs/`, não vira alvo. Sonda feita: um link simbólico em `~/.forge-contrib/wt/` apontando para um clone limpo fora da pasta saiu com rc 2 ("fica fora de"), e o clone continuou lá. Testes: `test_fora_da_pasta_ou_a_propria_pasta` e `test_pasta_que_nao_e_raiz_de_copia_fica`. O `rmtree` não segue link simbólico de dentro da cópia.
- **Trabalho fora da origem** (`bin/forge-copia:141-149`). No clone: `status --porcelain`, `stash list`, `rev-list --all --not --remotes` e nenhuma worktree ligada. É o mesmo critério do `limpar_clones` que já existia (`bin/forge-fechar:591-593`), sem o "sha mesclado", que aqui não se aplica. Na worktree: `rev-list HEAD --not --remotes`, e a saída é por `git worktree remove` sem `--force`, que recusa cópia suja ou travada. A branch local e o stash ficam no repositório. Erro de git conta como sujo (`rc or saida.strip()`). Nenhuma das duas rotas apaga branch, local ou remota.
- **Fim do item** (`bin/forge-copia:111-123`). Falha do `gh` recusa, e PR aberto recusa. Sem PR, vale só `vazio: sim`, e o `diff_vazio` dá "não verificável" para a ref igual à base. Por isso a cópia recém-criada de um item novo não é apagada.
- **forge-fechar** (`bin/forge-fechar:1300-1302`, `797-820`). Sem PR MERGED, um PR aberto para tudo, e não se chega a `mover_cartoes` nem a `limpar_entrega`, porque a função sempre termina com `exit`. As candidatas são as worktrees da branch, fora a principal, e os clones de `~/.forge-contrib/wt` com o mesmo origin. Cada uma passa pelo `forge-copia limpar`, que repete todas as guardas. Uma worktree fora da pasta liberada é recusada e fica pendente, com código 3.
- **A1.** Caminho: uma conta qualquer do GitHub abre, a partir de um fork, um PR com o nome de uma branch de trabalho em andamento que ainda não tem PR, e o fecha. O próximo `forge-copia limpar`, ou o `forge-fechar --limpar` dessa branch, apaga a cópia. O ganho é só incômodo: a cópia apagada estava limpa e com tudo na origem, e a branch continua. Severidade baixa. Correção mínima: `--json state,isCrossRepository --jq '.[] | select(.isCrossRepository | not) | .state'`. Esforço P. Dono: tech-lead, autor da E68.1.
- **A2.** Caminho: um agente ainda escreve na cópia de um item de PR fechado, por exemplo preparando a reabertura, enquanto o tech-lead roda a limpeza. A escrita feita durante a chamada de rede se perde. Severidade baixa, porque precisa de concorrência e o intervalo é curto. Correção mínima: inverter a ordem, deixando o fim do item primeiro e as checagens de limpeza logo antes do `rmtree` ou do `worktree remove`. Esforço P. Dono: tech-lead.
- **Arquivo ignorado.** `status --porcelain` não lista o que é ignorado, e o `rmtree` apaga esse conteúdo (por exemplo, um `.env` local). O comportamento já era o do `limpar_clones` e não é trabalho versionado. Fica registrado como nota, não como achado.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Rodei no head os 26 testes novos (`tests.test_forge_copia.Limpar` e `tests.test_forge_fechar.LimparSemMerge`), todos OK, e a sonda do link simbólico descrita acima. A sonda com `..` e a de arquivo ignorado foram barradas pelo hook R-REVIEW (gh simulado com HOME trocado). Valem pela leitura: o `resolve()` em `bin/forge-copia:129` e o critério do `status`. No head, não há PR nem CI. A suíte inteira fica com o CI do PR, que continua sendo o portão do merge (R-FLUXO). Faltaram no PATH: `gitleaks`, `semgrep` e `shellcheck`. O diff não toca credencial nem dependência.
