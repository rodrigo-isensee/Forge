---
tipo: review
contrato: 1
pedido: F4-ATUALIZAR
branch: melhoria/f4-atualizar
commit: 671c6251eade090150d8c12c562804e1f79b4780
parecer: aprovado
revisor: forge:tech-lead (outra instância)
data: 2026-10-23
---
# Review da F4: `forge atualizar` nasce da `develop` atual e oferece ao dono o conflito em `.forge/versao`

Escopo: `git diff origin/develop...671c625` (base `7423c44`): `bin/forge-atualizar`, `tests/test_atualizar.py`, `README.md`, `changelog.d/f4-atualizar.md`. Dois commits: `2d6a5ba` (testes) e `671c625` (correção), em Conventional Commits em português, um por mudança coerente.

## O que conferi (lendo como quem roda o upgrade num projeto)
- **Branch nasce da `develop` atual:** `forge-upgrade` cria `forge/upgrade-<v>` a partir da `develop` local (`bin/forge-upgrade:61,76`); `adiantar_develop_local` a leva até `origin/develop` antes disso, só quando é avanço (`merge-base --is-ancestor`): `merge --ff-only` se a pessoa está na `develop`, senão `update-ref` com valor antigo (atômico, não perde commit). Nunca força. Confere com o pedido.
- **`develop` local divergiu do remoto:** `adiantar_develop_local` não mexe (nada se perde); a branch nasce da `develop` local e `integrar_develop` traz a `origin/develop` depois, por merge. Resultado certo, mas silencioso (A3).
- **Sem terminal (CI, pipe):** `main` sai com 2 antes de qualquer passo (`fv.tem_terminal`, linha 125) e recusa dentro do Claude (linha 121); a pergunta do conflito nunca roda sem terminal. Se a entrada acabar no meio, `fv.confirmar` trata EOF como "não" e a mesclagem é desfeita. Seguro.
- **Conflito em `.forge/versao`:** só quando a lista de não mesclados é exatamente `[".forge/versao"]`; com "s" do dono no terminal, `checkout --ours` + `add` + `commit --no-edit`; commit que falha (hook) ou "n" desfaz com `merge --abort`. `.forge/versao` continua sendo só do dono, pelo terminal (`R-CONFORMIDADE`); o parecer de segurança cobre o controle.
- **Outro conflito (sozinho ou junto com `.forge/versao`):** desfaz a mesclagem inteira (`merge --abort`), lista os arquivos e oferece voltar. A branch fica como estava; nada é resolvido pelo comando. Confere.
- **Sem remoto ou sem rede:** `buscar_develop` falha e o fluxo segue como antes. Nada é enviado (só `fetch`).
- **Testes:** `python3 -m unittest tests.test_atualizar` com `HOME=$TMPDIR/tech-lead-f4`: `Ran 64 tests in 55.884s OK`. Os 6 novos (`AtualizarComDevelopQueAvancou`, linhas 360 a 427) cobrem: local atrasada, avanço no meio sem conflito, conflito em `.forge/versao` aceito e recusado, conflito em outro arquivo (com `develop` local à frente do remoto) e sem remoto. O `claude` falso empurra o commit durante a troca do plugin: imita bem o "avançou no meio". Lacunas em A4.
- **Documentação:** `README.md:77` e a docstring do comando batem com o código (ordem: adianta a `develop` antes do ponto de retorno; integra depois do `forge-upgrade`; pergunta só no conflito de `.forge/versao`). Fragmento `changelog.d/f4-atualizar.md` no formato. Sem custo (`R-CUSTO`), sem termo de projeto (`R-NEUTRO`), sem `--force` (`R-VERIFY`).
- Regras "ferramenta": o Forge não tem `docs/engineering/praticas.md`; a bateria (suíte completa, shellcheck, validação do plugin) roda no pre-push e no CI, sem saída a citar aqui além da suíte do módulo acima.

## Achados
- A1 (recomendado) bin/forge-atualizar:67 · a mensagem "avancei a cópia local" sai mesmo se o `merge --ff-only` ou o `update-ref` falharem (código de saída ignorado); checar o retorno e só anunciar o avanço quando ele aconteceu.
- A2 (recomendado) bin/forge-atualizar:82 · a pergunta não mostra qual versão a `develop` trazia em `.forge/versao`; o dono descarta sem ver. Mostrar as duas (`git show :3:.forge/versao`) e avisar se a da develop for maior que a nova.
- A3 (recomendado) bin/forge-atualizar:61 · `develop` local divergente (ou à frente) do remoto é pulada em silêncio; uma linha avisando que a branch nasce da develop local, com commits ainda não enviados, evita surpresa no PR.
- A4 (recomendado) tests/test_atualizar.py:360 · sem teste para a pessoa parada na `develop` atrasada (caminho `merge --ff-only`) nem asserção de que a `develop` local divergente fica intacta; acrescentar os dois.
- A5 (recomendado) bin/forge-atualizar:193 · com a `develop` já adiantada (linha 170), a falha da simulação diz "Não mudei nada no projeto"; ajustar o texto ou adiantar a develop só depois da simulação.

## Parecer
Aprovado. A correção faz o que a F4 pede, nem mais nem menos: a branch do upgrade nasce da `develop` atual por avanço simples, o conflito só em `.forge/versao` é decidido pelo dono no terminal e qualquer outro conflito é desfeito por inteiro, sem forçar nem enviar nada. Os cinco achados são recomendados (mensagens fiéis ao que aconteceu e dois testes de borda) e podem ir num pedido seguinte; nenhum bloqueia o QA.
