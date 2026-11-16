---
tipo: revisao-seguranca
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-fechar-cartao
commit: ccb7613465a8be32a8fecf2070b9ad630836f364
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: melhorias-de-projeto-1311 (item 11, bin/forge-fechar)

## Gatilhos
Controle de fechamento e merge (conferência de pareceres antes do merge, `R-SEGURANCA`, `R-VERIFY`): o `forge-fechar` passa a dar ao `forge-check pr` o nome da branch local em vez do sha.

## Achados
- A1 (recomendado) bin/forge-fechar:826 · RESOLVIDO em a47ef67b: ref_check e ref_dry passam a refs/heads/$ref, e o teste test_tag_de_mesmo_nome_nao_desvia_a_conferencia cobre a tag homônima.

## Sondas

## Detalhe dos achados
**A1 (recomendado, baixa).** Evidência: `bin/forge-fechar:826` lê `sha_conferido` por `refs/heads/$ref^{commit}` (exato) e define `ref_check="$ref"` (o nome nu); `bin/forge-fechar:854` passa esse nome ao `forge-check pr --ref`, que o resolve por `rev-parse --verify --end-of-options "<nome>^{commit}"` (`bin/forge-check:1871`), com a desambiguação do git (sha completo e tag valem antes da branch). Reproduzido em repositório descartável: com a branch `melhoria/x` em C1 e uma tag `melhoria/x` em C2, `rev-parse refs/heads/melhoria/x` deu C1 e a resolução por nome deu C2; o mesmo para uma branch cujo nome é o sha40 de outro commit. Os pareceres seriam lidos de C2, e o head relido (`head_atual`) bate com `sha_conferido` (C1), então a cadeia do item não pega a troca. Caminho de ataque: quem já escreve tag ou branch no clone ou no origin (mesma permissão de empurrar a branch) planta o nome ambíguo; o ganho é só passar a conferência local. Não é bloqueante: o CI do PR reconfere o head real e o merge sai preso a `--match-head-commit`, então não há ganho de merge. Antes da mudança (sha) o caso não existia, daí o registro. Correção mínima: `ref_check="refs/heads/$ref"` no ramo com a branch local (o `branch_da_ref` já remove o prefixo `refs/heads/`) e o dry-run igual; um teste com tag homônima. Esforço P. Dono: `software-engineer` (autor do item).

**Conferido sem achado.** Injeção: `$ref` passa por `git check-ref-format --branch` (`bin/forge-fechar:111`), que rejeita `-x`, `HEAD`, `@` e controle; todo uso vai entre aspas ou `%q`; o `forge-check` usa `--end-of-options`. O sha conferido segue lido de `refs/heads/$ref` e relido depois do passo 1, no passo 2 e no merge (`--match-head-commit`); o teste `test_head_que_anda_durante_a_conferencia_ainda_para` cobre o head que anda. Sem a branch local o caminho segue pelo sha do servidor (`ref_check="$sha_conferido"`), sem nome a resolver. O dry-run não chama gh nem servidor.

## Riscos aceitos e ferramentas
Sem risco aceito. Sem PR aberto para o head: rodei `tests.test_fechar_ref_por_nome` (4 OK), `tests.test_fechar_sha_conferido` (9 OK) e `tests.test_fechar_base_andou` (30 OK) numa cópia limpa do head; a suíte inteira fica para o CI do PR. Varredura de dependências não se aplica (sem dependência nova).

## Revalidação por delta (head a47ef67b)
Delta do domínio desde 0884fae2: `bin/forge-fechar` (duas linhas: `ref_check="refs/heads/$ref"` e `ref_dry="refs/heads/$ref"`, mais comentário) e testes. Cumpre a correção mínima do A1. O `forge-check` aceita o prefixo (`removeprefix("refs/heads/")` em `bin/forge-check:1616` e `:1649`; resolução por `rev-parse ... ^{commit}` com `--end-of-options`), logo os pareceres seguem lidos da branch. Sem superfície nova: `$ref` segue validado por `git check-ref-format --branch` (`bin/forge-fechar:111`); o sha conferido e o `--match-head-commit` não mudaram; sem branch local o caminho segue pelo sha do servidor. Os mutantes M4 e M5 (`tests/mutantes/mp1311-fechar-cartao.json`) são teste, fora do domínio de segurança; não os reexecutei. Rodei `tests.test_fechar_ref_por_nome` e `tests.test_fechar` (104 testes, OK, 123 s); a suíte inteira fica para o CI do PR. Sem achado novo.

## Revalidação por delta (head ccb76134)
Delta do domínio desde a47ef67b (`forge-check parecer delta`, sem o que veio da develop): `bin/forge-testes` e `tests/test_fechar_base_andou.py`. No `bin/forge-testes`, duas entradas novas no `MAPA` (regex `bin/forge-fechar` e `templates/projeto/.forge/config.json` para a lista de módulos de teste); o mapa só escolhe quais testes rodam no envio local (`FORGE_PREPUSH_SUITE=afetados`) e a suíte inteira segue no CI do PR, então não há caminho de ataque: a mudança amplia a seleção, não a reduz. Conferi que os 34 módulos citados existem em `tests/` (nenhum nome errado que deixaria um teste de fora). No teste, a asserção passa a esperar `refs/heads/<branch>` no `forge-check pr`, o mesmo comportamento já aprovado do A1 (`bin/forge-fechar:854`, sem mudança no delta); o teste fica mais estrito. `bin/forge-fechar` e `bin/forge-check` não mudaram. Rodei `tests.test_fechar_base_andou` e `tests.test_testes_tocados` (180 testes, OK, 1 skip) no head; a suíte inteira fica para o CI do PR 539 (em execução no envio deste parecer). Sem achado novo; `R-SEGURANCA` cumprido no head ccb76134.
