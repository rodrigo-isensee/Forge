---
tipo: review
contrato: 1
pedido: v047-ambiente-sobrevive
branch: melhoria/v047-ambiente-sobrevive
commit: 680725756d94129c230f52c6401d697463f6e88d
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047-ambiente-sobrevive

Code review da classe C (E2.89) no head 68072575, AMBIENTE-SOBREVIVE-RECRIACAO (E2.54). Parecer completo: não havia parecer anterior.

## Achados
- A1 (bloqueante) scripts/preparar-estacao.sh:9 · Requisito da ORDEM DO DONO 15/11 16:46 não cumprido: o Jarvis, ao abrir, confere o ambiente e dá o comando na 1ª mensagem. O --verificar existe, mas nada o chama (agents/jarvis.md e o SessionStart de hooks/hooks.json sem mudança). Ligue-o ao abrir, com teste.
- A2 (bloqueante) .devcontainer/devcontainer.json:23 · R-SEGURANCA (B2 da 0.43.1): refs/remotes/origin/main é gravável pelo Bash do agente no sandbox (S1); forjar o ref faz o início seguinte rodar como root, fora do sandbox, qualquer script. Leia do remoto: git fetch origin main e git show FETCH_HEAD:. Idem no modelo :17.
- A3 (recomendado) scripts/preparar-estacao.sh:272 · Guardas novas em shell (container_hooks, verificar_container, preparar-ambiente.sh) sem tests/mutantes/v047-ambiente-sobrevive.json; a --cobertura sai `não coberto` para os 4 arquivos. Na volta, um mutante por linha de guarda com o teste do ramo de falha.
- A4 (recomendado) tests/test_forge.py:1954 · 354 linhas de código e teste (M14, teto 150): o corpo do PR precisa de `teto: excedido, 354 linhas, <motivo>`, ou separe o modelo de projeto do devcontainer do Forge.

## Sondas
- S1 · test -w /workspaces/Forge/.git/refs/remotes/origin (Bash do agente, sandbox ativo) · espera: não gravável · obtido: gravável

## Parecer
Reprovado por A1 e A2.

A1: o cartão tem duas partes pedidas pelo dono; a segunda (o Jarvis confere ao abrir e dá o comando exato) ficou só como ferramenta. O comentário da linha 9 e o fragmento do changelog afirmam que o Jarvis a abre, e nada no diff faz isso. Sugestão: o `doutor.py` do SessionStart (ou a seção de abertura do Jarvis) roda `preparar-estacao.sh --verificar` no repositório do Forge e `preparar-ambiente.sh --verificar` no projeto, e repassa as linhas `falta:`; teste de comportamento com ambiente faltando.

A2 complementa o A1 do parecer de devops (E2.92, janela até a release em que a origin/main não tem `FORGE_PREPARO_ESSENCIAL`), sem refazê-lo: mesmo com a marca na main, o ref local `refs/remotes/origin/main` não é "código mesclado pelo dono", é um arquivo em `.git/refs` (ou `packed-refs`) que o sandbox deixa gravar. A sonda S1 só testou a permissão; o ref não foi alterado. O teste `test_devcontainer_prepara_sozinho_sem_rodar_o_work_tree` confere o texto `refs/remotes/origin/main:` e por isso não pega o desvio. Sugestão: o próprio comando busca do remoto (`git -C ... fetch -q origin main && git -C ... show FETCH_HEAD:<script>`; a URL vem do `.git/config`, protegido) e o teste passa a exigir a leitura pelo `FETCH_HEAD`. A severidade final de segurança fica com o parecer do security-engineer (E2.90).

Conferido sem achado: idempotência e "nunca apaga dados" nos dois scripts; `core.hooksPath` de outra ferramenta preservado; `--verificar` não altera nada (teste com o registro de chamadas); `--simular` respeitado em `container_hooks` (usa `fazer`); falha do preparo não derruba o container (`; true`); sem segredo gravado (GH_TOKEN só por `localEnv`; o escopo do token é o A2 de devops); `_projeto_ambiente` usa `ambiente_limpo()`; R-NEUTRO e R-CUSTO sem violação. PA-7 (achados-recorrentes): AR-1 e AR-2 conferidos no A3; os demais AR não alcançam o diff (sem Python novo fora de teste, sem hook).

Ferramentas, citadas sem refazer o que é do autor: `bin/forge-mutante --cobertura --base cb45a962` rc=0, com os 4 arquivos `não coberto` (shell e JSON não se analisam); `shellcheck` nos dois scripts rc=0; `tests.test_forge.PrepararEstacao` 19 testes OK neste head. Suíte completa fica com o CI do PR.
