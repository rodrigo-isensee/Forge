---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-a2-concessao
commit: 4c325c557ee7cf5544a28488eb06346ae9bfbc1f
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0478 · PV-A2 (concessão `item:` presa ao commit), etapa E57.62

Escopo: `d4f0b10a..4c325c55` (`bin/forge_autorizacao.py`, `tests/test_autorizacao.py`, mutantes M1 a M28, fragmento do changelog). Referência: ADR 0018, Emenda PR-VERDE E1 (aceita pelo dono em 2026-11-20 13:51) e as linhas PV-A2 do modelo de ameaças da emenda (Alvo, Ato, Commit).

## Gatilhos
Gatilhos: controle de autorização do dono (ADR 0018), afrouxamento de regra (rótulo `afrouxa-regra`), execução de `git` por subprocesso.

## Só aperta ou afrouxa?
- **Muda um estado que antes era sempre recusado:** na base, `item:<CARTAO>` caía em `Alvos fora da forma` e saía `adulterada` (e `ler` saía 1). No head, `bin/forge_autorizacao.py:24` aceita a forma e a concessão pode sair `ativa`. É exatamente o que a E1 da emenda prevê, e a emenda tem o aceite do dono; não é afrouxamento novo que precise de outra decisão.
- **Nenhuma regra fica mais frouxa no head:** o estado `ativa` não libera nada hoje. Conferi quem lê: o único consumidor de `concessoes()` é `cmd_ler` (`bin/forge_autorizacao.py:238`), que só mostra e diz "só leitura, nada barra"; `hooks/` e `.githooks/` não leem `.forge/autorizacoes/`; `bin/forge_quarentena.py:89` confere só a forma `A-<n>`, não o estado; nenhum script usa o código de saída de `autorizacao ler`. O rótulo e a catraca seguem pelos itens 9 e 10, sem mudança.
- **Os alvos `pr:` e `versao:` não mudam:** `do_item` (`:134`) e `fora_do_revisado` (`:218`) só rodam com `Alvos` começando por `item:`; o mutante M28 prova que a conferência do head não vaza para esses alvos.
- **Ressalva:** a partir do PV-A3, o `declarar` passa a confiar no `ativa` deste leitor (E2: "lê a concessão ativa do registro local"). Por isso os defeitos A1 e A2 abaixo, que hoje não abrem nada, viram brecha no PV-A3. Eles bloqueiam aqui porque contradizem as linhas PV-A2 do modelo de ameaças.

## Achados
- A1 (bloqueante) bin/forge_autorizacao.py:176 · `git diff --name-only` sem `--no-renames`: depois do Commit revisado, `git mv` de um arquivo de código para `docs/qa/` aparece só com o nome novo, a conferência "depois dele só pareceres" passa e a concessão fica ativa com o arquivo de código removido do Ramo (S1).
- A2 (bloqueante) bin/forge_autorizacao.py:29 · a RESSALVA não tem `antes`, `depois`, `sem` nem `menos`, que o item 5 da ADR 0018 lista e a E1 aplica ao item: ("com ressalva nasce pendente"); "pode aplicar o rótulo no item PV-A2 depois do CI" sai ativa (S2).
- A3 (recomendado) bin/forge_autorizacao.py:146 · o termo do ato é buscado como trecho na frase inteira, alvo incluído: com cartão `ROTULO-1`, "o item ROTULO-1 está pronto" sai ativa sem nenhum termo de ato. Procure o termo na frase sem o trecho do alvo e como palavra inteira.
- A4 (recomendado) bin/forge_autorizacao.py:181 · aqui se exige "todo parecer presente aprova", não "os pareceres exigidos" da E1: um único parecer de review aprovado já dá ativa (S4). Registre o limite na docstring e no changelog, ou faça o PV-A3 conferir as classes exigidas antes de confiar no ativa.

## Sondas
- S1 · no repositório do teste `ItemPresoAoCommit`: `git mv codigo.txt docs/qa/codigo.txt; git commit -m mv`, depois `concessoes()` com a concessão padrão · espera: ('inativa', 'Commit não é o head: o Ramo muda depois dele') · obtido: ('ativa', '')
- S2 · corpo "pode aplicar o rótulo no item PV-A2 depois do CI" (o mesmo com "sem o teste" e "antes do merge"), Estado-inicial ativa · espera: ('adulterada', '... ressalva na mensagem') · obtido: ('ativa', '')

## Detalhe dos achados
**A1.** Evidência: `bin/forge_autorizacao.py:176`. Com `diff.renames` ativo por padrão (git 2.43 no ambiente) e a config do usuário valendo, `--name-only` só lista o destino de uma renomeação. Caminho de ataque: depois do parecer, um agente com escrita na branch move `bin/<guarda>` ou `tests/<teste>` para `docs/reviews/` (o papel dele escreve ali) e envia. O `ler` continua dizendo que o Commit é o head, e no PV-A3 o `declarar` grava o arquivo de autorização de um Commit que já não descreve o Ramo. A catraca (E4 c) seria a última barreira no CI. Severidade: média (hoje nenhum consumidor; vira alta no PV-A3). Correção mínima: `git(raiz, "diff", "--no-renames", "--name-only", commit, ponta)` (de preferência também `-c diff.renames=false`, para não depender da config), e um caso no teste `test_commit_que_nao_e_o_head...` com `git mv` de código para `docs/qa/`. Esforço P. Dono: autor da branch (`software-engineer`), teste com o `qa-engineer`.

**A2.** Evidência: `bin/forge_autorizacao.py:29` comparada com a ADR 0018, item 5 ("As marcas de negação e condição (`nao`, `nunca`, `ainda`, `antes`, `depois`, `so se`, `se`, `exceto`, `menos`, `sem`)"), e com a E1 ("Mensagem com ressalva nasce pendente, como no item 5"). Caminho de ataque: uma concessão gravada `ativa` a partir de "pode aplicar o rótulo no item X depois do CI" passa no leitor; a condição do dono se perde e, no PV-A3, o `declarar` a usa. Severidade: média. Correção mínima: a RESSALVA cobre a lista inteira do item 5 mais as que já estão no código, ou seja `nao`, `nunca`, `jamais`, `ainda`, `antes`, `depois`, `so se`, `se`, `caso`, `exceto`, `salvo`, `desde que`, `a menos`, `menos`, `sem`, e o teste `test_alvo_sem_marcador...` ganha um caso por marca. Fica registrado que a regra do item 5 é o vocabulário positivo (lista negativa em trava é o AR-3); o leitor é defesa em profundidade, e o vocabulário positivo vem no `gravar`. Esforço P. Dono: o mesmo.

**A3.** Proporcional: o nome do cartão vem do time, não de terceiro, e é raro ter um termo do ato dentro dele. Correção: tirar o trecho casado por `marcado` da frase antes de procurar `rotulo`/`afrouxa`, e procurar o termo como palavra inteira (`\b`). Esforço P.

**A4.** A E1 manda o `gravar` recusar Commit "sem pareceres aprovados" exigidos; no leitor, a regra é "todo parecer da branch presente aprova, e há ao menos um". Isso aperta quando há parecer reprovado ou de `riscos-aceitos`, mas não confere a classe (review, QA e, com gatilho, segurança). Recomendação: escrever o limite e garantir a classe no PV-A3 ou no `gravar`. Esforço P.

**Conferido sem achado:** `git` sem as variáveis `GIT_*` herdadas e falhando fechado (`:156-163`, teste `test_git_herdado...`); `Commit` só sha40 minúsculo e `Ramo` sem `-` no início nem `..` (`:25-26`), o que impede injetar opção no `rev-parse` e no `merge-base`; `git grep -F` com o nome exato conferido de novo no frontmatter (`:179-180`); parecer sem frontmatter não conta; a ref do `origin` vale antes da local; `pendente-confirmacao` sem marcador continua pendente (a E1 manda nascer pendente). A pasta `.forge/autorizacoes/` não tem barreira de caminho no hook contra agente: isso vem de antes, é do G1.2 e da E3, e não muda aqui.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodei a classe nova com as sondas, herdando `ItemPresoAoCommit` (11 testes, OK), contra o módulo do head. A suíte inteira não rodou localmente (o brief manda sem suíte local) e não achei o CI do head: `gh` não respondeu no ambiente. `gitleaks` e o SAST da stack não estão no PATH (lacuna); o diff não traz credencial nem dado pessoal.
