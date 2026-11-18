---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-merge-checks
commit: 9f497b0f140a450c578dae79e5ec00d88d3ff31c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474 E3.71 (merge só com os checks do head verdes, E3.45)

Diff lido: `3d8ad440..9f497b0f`, em `bin/forge-check` (`checks_do_head`, `checks_exigidos`, `gh_json`, chamada em `pr_da_cli`), `bin/forge-fechar` (`exigidos`, `ler_exigidos_do_destino`, `exigidos_ok`, `msg_exigido`, passo 4 do seco) e testes e mutantes.

Conclusão: nada fica mais frouxo. Os exigidos fixos ficam: `bin/forge-fechar:85` (`readonly`, intocado) copiados para `exigidos` em `:87`, que só ganha itens (`:539`); `bin/forge-check:1439` com os mesmos três pares (o teste `test_os_pares_do_forge_sao_os_do_forge_fechar` os prende). Leitura do ruleset ou da proteção que falha não acrescenta nem tira nada: no forge-fechar a saída só entra com saída 0 do `gh api` (`:536-537`) e no forge-check a forma inesperada cai no `except` (`:1463-1470`). Checks ilegíveis reprovam (`:1486-1487`). O curinga `*/<contexto>` só amplia o casamento por nome do lado dos exigidos e todo check casado tem de estar em `pass` (um `pass` falso de outro workflow com o mesmo nome não tapa o vermelho do verdadeiro). Só leitura: `gh api` sem `-X` nem `-f` (GET), `gh pr view` e `gh pr checks`, sem custo (`R-CUSTO`), com teto de 10 s e `stdin` fechado. O destino passa por `[A-Za-z0-9._/-]{1,200}` antes da URL (`:1456`), vem do `baseRefName` do PR, e no forge-fechar é o `alvo` fixo (develop ou homolog). Nomes de check vindos do GitHub saem por `sem_controle` (sonda S5). O mutante M1 de `tests/mutantes/i4-checks-exigidos.json` acompanha a condição nova e continua apagando o par workflow/nome inteiro.

Gatilhos: controle do Forge (portão de merge), integração com o GitHub, `bin/` do fluxo de branches (`R-MAIN`).

## Achados
- A1 (recomendado) bin/forge-check:1478 · gh pr view que falha (rede, gh ausente, saída ilegível) vira "sem PR" e o portão novo não confere; distinguir "no pull requests found" do erro e reprovar no erro. Não é mais frouxo que a base: o merge também precisa do gh e o ruleset do GitHub confere.
- A2 (recomendado) bin/forge-check:1484 · num projeto sem ruleset nem proteção legível, logo depois do push ("no checks reported", lista vazia) o pr aprova; o Forge reprova pelos pares fixos. Opcional: com o PR aberto e zero checks, avisar no stderr.
- A3 (recomendado) bin/forge-check:1478 · até 4 chamadas ao gh de 10 s cada no caminho do gh pr merge, cujo prazo do hook é 8 s (hooks/_comum.py PRAZO_DO_MERGE_S); vencido, recusa (falha fechada): risco de disponibilidade, não de segurança.

## Sondas

## Detalhe dos achados
Sondas executadas (não provam bloqueante, ficam aqui em prosa): carregando `bin/forge-check` e trocando `gh_json` por respostas fixas, com o PR aberto no head, `checks_do_head`: S1 `pr view` sem resposta → `[]` (A1); S2 `pr checks` com "no checks reported" e sem ruleset, no Forge → reprova com os três pares ausentes; S3 ruleset `{"message":"Not Found"}` → nada acrescentado, os pares continuam; S4 `isDraft` ausente → não confere (o comparador `is not False` não aprova por engano, só não confere); S5 nome com ESC → sai sem o caractere de controle.

- A1: severidade baixa. Caminho: falha transitória do gh no `forge-check pr` com o `gh pr merge` em seguida funcionando; o servidor ainda exige os checks do ruleset. Correção mínima: em `gh_json`, devolver o código de saída; em `checks_do_head`, reprovar quando a saída não é 0 e o stderr não é o de PR inexistente. Esforço P. Dono: autor da branch (tech-lead).
- A2: severidade baixa (informativa no Forge). Caminho: agente que mescla num projeto sem ruleset no instante entre o push e o registro dos checks. Correção: aviso no stderr; reprovar mudaria o comportamento dos projetos sem CI, decisão do dono. Esforço P. Dono: tech-lead.
- A3: informativa. Correção: um teto total para as chamadas do `checks_do_head` abaixo do prazo do hook. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes rodados aqui: `tests.test_forge_check_pr`, `tests.test_forge_fechar`, `tests.test_fechar_checks_exigidos` (39 testes, OK). CI: a branch ainda não tem PR nem execução de CI (`gh run list` vazio); a suíte inteira fica para o CI do PR, que o passo 4 do forge-fechar exige verde antes do merge. Ferramentas ausentes no PATH (lacuna): gitleaks, zizmor, actionlint, semgrep, shellcheck; nenhum workflow mudou.
