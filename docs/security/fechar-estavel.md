---
tipo: revisao-seguranca
contrato: 1
pedido: fechar-estavel
branch: melhoria/fechar-estavel
commit: 6a1f2b3fee83ca24ea8ba1e24da2ea2f7e97ef0d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: fechar-estavel

Escopo: `git diff ef71b3c08913cf119396559c23fa9b0478e4607a 6a1f2b3fee83ca24ea8ba1e24da2ea2f7e97ef0d` (`bin/forge-fechar`, `.github/pull_request_template.md`, `docs/fechamento-integrador.md`, `tests/test_fechar.py`, `changelog.d/fechar-estavel.md`). Revisão estática, mais uma sonda local com o `gh` falso dos testes, numa cópia em `$TMPDIR`.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): o `bin/forge-fechar` guarda o fechamento (pareceres, checks, rótulo, merge preso ao head). Também `.github/` (modelo de PR).

## Achados

## Detalhe dos achados
Conferências pedidas no brief:

1. **A repetição não cobre operação que muda o PR ou a branch.** `ler()` (`bin/forge-fechar:62`) só envolve leituras: `pr list` (`:151`), `pr view` de rótulos, título e corpo, base, rascunho e estado (`:199-200`, `:211`, `:223`, `:228`). `repetir()` (`:72`) só aparece no `git push origin --delete` da limpeza (`:233`). No passo 4, a nova contagem `falhas` (`:170-187`) só repete a leitura `pr checks` e para (falha fechada) depois de 3 erros seguidos. O push de código (fora do script), `pr create` (`:162`), `pr ready` (`:219`) e `pr merge` (`:222`) rodam uma vez só. Quando o merge dá erro, o script só lê o estado e para se não estiver `MERGED` (`:223-224`). Conforme.
2. **Reconhecer PR já MERGED não pula checagem para um head diferente.** O passo 1 (`forge-check pr`, pareceres) roda sempre antes. No passo 3, o atalho do PR `MERGED` exige base igual ao alvo e `headRefOid` igual ao head remoto conferido no passo 2 (`:153`). O teste `test_pr_mesclado_com_outro_head_nao_impede_o_pr_novo` prova que outro head segue o fluxo inteiro. O atalho `merge-base --is-ancestor` (`:147`) só se aplica quando o head já está na base, e aí não há conteúdo novo a mesclar. Nos dois atalhos, o script não mescla nada: nenhum conteúdo entra na `develop` sem a Catraca e os checks. Conforme. A ressalva de robustez está em R1, abaixo.
3. **O item do rótulo no modelo não libera nada por si.** O item fica desmarcado (`.github/pull_request_template.md:19`, o mesmo texto do corpo gerado). O passo 5 só *para* quando o item está marcado e o rótulo falta. A liberação da Catraca depende só do evento `labeled` do dono, posterior ao último push (`tests/catraca.py:430-445`), e não lê esse item. O texto do PR não libera nenhum controle. Conforme.
4. **Sem rede paga (`R-CUSTO`).** O script só acrescenta `sleep` e repetição de chamadas `gh` e `git` já existentes. Os testes usam `gh` e `git` falsos em repositório temporário. Conforme.

Recomendações (não bloqueantes):

- **R1 (baixa) `bin/forge-fechar:211`, `:223`, `:228`:** no passo 6, o reconhecimento de `MERGED` lê `gh pr view <branch>` sem prender o número do PR do passo 3 nem o `headRefOid`. A sonda local confirma: se a leitura resolver para outro PR já `MERGED` da mesma branch, com outro head, o script sai com sucesso ("o merge não se repete"), sem mesclar, e apaga a branch remota e a local. Caminho realista: quase nenhum. O `gh` prefere o PR aberto e, sem aberto, o mais recente, que é o próprio PR do passo 3. Seria preciso um terceiro fechar o PR durante a espera *e* haver um PR `MERGED` mais novo na mesma branch. Ninguém ganha acesso, e nenhum conteúdo entra sem checks. O efeito seria um sucesso falso e a perda da referência da branch, que se recupera por `refs/pull/<n>/head`. Correção mínima: guardar o número do PR no passo 3 e, no passo 6, ler `gh pr view <número> --json state,headRefOid`, aceitando `MERGED` só com `headRefOid` igual a `$remoto_sha`, a mesma regra do passo 3 (`:153`). Esforço P. Dono: tech-lead, numa próxima melhoria. Não bloqueia: a guarda principal (merge preso ao head) está intacta.
- **R2 (informativa) `bin/forge-fechar:233`:** o `push --delete` não tem *lease*. Um push feito por outro agente entre as tentativas seria apagado. Isso já acontecia antes; a repetição só alonga a janela em até 2 × `FORGE_FECHAR_PAUSA` (6 s no padrão). Nada a fazer agora: `--force-with-lease` cairia na `R-VERIFY`.
- **R3 (informativa) `bin/forge-fechar:147`:** o atalho usa a ref local `origin/develop` sem `fetch`. Uma ref velha só causa falso negativo: o script segue o fluxo normal, o que é seguro.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, `python3 -m unittest tests.test_fechar` (47 OK) e uma sonda local com o `gh` falso (cenário de R1). Ausentes do PATH, e não instaladas: `shellcheck`, `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner`. O `shellcheck` e a validação do plugin rodam no CI. A mudança não traz segredo, dependência nem workflow.
