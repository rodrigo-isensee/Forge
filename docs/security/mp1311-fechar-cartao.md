---
tipo: revisao-seguranca
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-fechar-cartao
commit: 0884fae230d784f90d6cb0108dfa414ee91707e0
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: melhorias-de-projeto-1311 (item 11, bin/forge-fechar)

## Gatilhos
Controle de fechamento e merge (conferência de pareceres antes do merge, `R-SEGURANCA`, `R-VERIFY`): o `forge-fechar` passa a dar ao `forge-check pr` o nome da branch local em vez do sha.

## Achados
- A1 (recomendado) bin/forge-fechar:854 · nome sem prefixo resolve pelo git na ordem sha, tag, branch: tag de mesmo nome da branch faz o forge-check ler outro commit que o sha conferido; passe refs/heads/$ref (aceito por branch_da_ref); o CI e o merge preso ao sha cobrem.

## Sondas

## Detalhe dos achados
**A1 (recomendado, baixa).** Evidência: `bin/forge-fechar:826` lê `sha_conferido` por `refs/heads/$ref^{commit}` (exato) e define `ref_check="$ref"` (o nome nu); `bin/forge-fechar:854` passa esse nome ao `forge-check pr --ref`, que o resolve por `rev-parse --verify --end-of-options "<nome>^{commit}"` (`bin/forge-check:1871`), com a desambiguação do git (sha completo e tag valem antes da branch). Reproduzido em repositório descartável: com a branch `melhoria/x` em C1 e uma tag `melhoria/x` em C2, `rev-parse refs/heads/melhoria/x` deu C1 e a resolução por nome deu C2; o mesmo para uma branch cujo nome é o sha40 de outro commit. Os pareceres seriam lidos de C2, e o head relido (`head_atual`) bate com `sha_conferido` (C1), então a cadeia do item não pega a troca. Caminho de ataque: quem já escreve tag ou branch no clone ou no origin (mesma permissão de empurrar a branch) planta o nome ambíguo; o ganho é só passar a conferência local. Não é bloqueante: o CI do PR reconfere o head real e o merge sai preso a `--match-head-commit`, então não há ganho de merge. Antes da mudança (sha) o caso não existia, daí o registro. Correção mínima: `ref_check="refs/heads/$ref"` no ramo com a branch local (o `branch_da_ref` já remove o prefixo `refs/heads/`) e o dry-run igual; um teste com tag homônima. Esforço P. Dono: `software-engineer` (autor do item).

**Conferido sem achado.** Injeção: `$ref` passa por `git check-ref-format --branch` (`bin/forge-fechar:111`), que rejeita `-x`, `HEAD`, `@` e controle; todo uso vai entre aspas ou `%q`; o `forge-check` usa `--end-of-options`. O sha conferido segue lido de `refs/heads/$ref` e relido depois do passo 1, no passo 2 e no merge (`--match-head-commit`); o teste `test_head_que_anda_durante_a_conferencia_ainda_para` cobre o head que anda. Sem a branch local o caminho segue pelo sha do servidor (`ref_check="$sha_conferido"`), sem nome a resolver. O dry-run não chama gh nem servidor.

## Riscos aceitos e ferramentas
Sem risco aceito. Sem PR aberto para o head: rodei `tests.test_fechar_ref_por_nome` (4 OK), `tests.test_fechar_sha_conferido` (9 OK) e `tests.test_fechar_base_andou` (30 OK) numa cópia limpa do head; a suíte inteira fica para o CI do PR. Varredura de dependências não se aplica (sem dependência nova).
