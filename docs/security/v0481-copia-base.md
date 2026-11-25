---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-copia-base
commit: 1571a36f79ed939ceca9979c969ef65136faa926
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (E13.5, #879, forge-copia clone: base e branch remota)

Lido: `d49accf8..1571a36f` inteiro (`bin/forge-copia`, `tests/test_forge_copia.py`, `tests/mutantes/v0481-copia-base.json`, `changelog.d/v0481-copia-base.md`). Primeira rodada de segurança da branch; sem parecer anterior.

Gatilhos: controle do Forge (criação de cópia de trabalho na pasta liberada do sandbox; ref de onde a branch de trabalho nasce; apagamento de pasta).

## Conferência
- **Nenhum caminho deixa a cópia na branch padrão nem sobre ref errada.** Depois do clone (`bin/forge-copia:307`), só há dois desfechos: a branch nova criada com `switch --no-track -c` a partir de um ponto que existe como commit (`bin/forge-copia:126`, `:130-139`, `:310`), ou a cópia apagada e saída 1 (`:311-313`). Antes, a falha do `switch` deixava o clone na branch padrão com saída 1; agora ele some. O ponto de partida é, nesta ordem: `refs/remotes/origin/<branch>` (a branch já publicada, nome já validado por `check-ref-format --branch`, `:284`), a base como dada, `origin/<base>`. Na cópia recém-clonada, a única branch local é a padrão, igual à remota dela, então a base como dada e `origin/<base>` não divergem; a branch remota que existe parte do head dela, o que evita divergência e envio recusado. Sem upstream (`--no-track`), provado por teste e pela S2.
- **Apagamento (`:311`).** `real` é o caminho resolvido, dentro da pasta liberada, não link e livre (inexistente ou pasta vazia, `ocupado`, `:81`), e o clone acabou de nascer nele: o que se apaga é o que o comando criou (no pior caso, mais a pasta vazia que já estava ali). O apagamento não segue link simbólico do conteúdo clonado (S1: o link versionado para fora é removido e o alvo fica intacto).
- **Só aperta ou neutro, por escrito: só aperta.** Todas as recusas de hoje continuam antes do clone e intactas (opção com `-`, nome de branch, papel, destino fora ou ocupado, disco, `.gitignore` do projeto, `--origem` faltando); falha do clone segue saindo 1 sem procurar base (teste `test_clone_que_falha_sai_1_antes_de_procurar_a_base`); base inexistente segue saindo 1, agora sem deixar a cópia. A base continua sendo qualquer revisão aceita antes pelo `switch` (nada novo aceito além de `origin/<base>`, que só existe como ref de rastreio do clone). O modo `worktree` e o `limpar` não mudaram. A troca no teste `Disco` (mock de `ponto_de_partida`) só substitui o que o clone falso não tem.
- **Observação fora do delta (sem achado):** `--branch main`, `develop` ou `homolog` não é recusado pelo script, antes e depois; o envio a essas branches segue barrado pelo `pre-push` (`R-MAIN`), e no clone cuja padrão é a própria branch o `switch` falha e a cópia é apagada.
- Testes: `python3 -m unittest tests.test_forge_copia` → 81 testes, OK. Suíte inteira: só no CI do PR #879, no mesmo head `1571a36f` (em andamento ao escrever; o merge depende dela verde).

## Sondas
- S1 · clone com `--base nada` de origem que versiona link simbólico para pasta fora com sentinela · espera: rc 1, cópia apagada, sentinela intacta · obtido: rc=1 existe=nao sentinela=vivo
- S2 · clone `--branch melhoria/y` que já existe na origem, sem `--base` · espera: rc 0, HEAD igual ao head remoto, sem upstream · obtido: rc=0 head_ok=sim upstream=nenhum

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, testes do arquivo tocado e as duas sondas acima, em pasta temporária com origem local (nada externo). Varredor de segredos, SAST e auditor de dependências: o delta não traz dependência nem segredo.
