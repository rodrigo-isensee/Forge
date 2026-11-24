---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0480-bench-versao
commit: d2bdd9ab9e68015620a02188909ecf5453ff5b50
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (E3.4, PR #870, bench de versões com agentes)

Escopo: `a27eab7e..d2bdd9ab` (8 arquivos: `tests/bancada/versao.py`, `tests/test_bancada_versao.py`, `tests/bancada/romanos/*`, `tests/config.json`, `tests/mutantes/v0480-bench-versao.json`, `docs/bench-versao.md`, fragmento do changelog). Primeira rodada; sem parecer anterior na branch.

**Só aperta ou neutro:** só aperta e, no resto, neutro. `tests/config.json:103` só acrescenta um hash a `termos_proibidos_hash` (aperta `Neutralidade`); nenhuma regra, invariante, hook, workflow ou permissão do Forge muda; o roteiro é novo, fora do CI e só age com `--executar`.

## Gatilhos
Gatilhos: custo (`R-CUSTO`, sessão real com a assinatura), execução de agente em modo auto na máquina do dono, credenciais do dono (git e gh) e remoto público, integridade da avaliação (testes escondidos).

## Achados
- A1 (bloqueante) tests/bancada/versao.py:42 · A recusa de API paga só olha ANTHROPIC_API_KEY: ANTHROPIC_AUTH_TOKEN, ANTHROPIC_BASE_URL e CLAUDE_CODE_USE_BEDROCK/VERTEX/FOUNDRY passam (S1) e chegam à sessão (o filho herda o ambiente em :187); uma rodada de ~28 M tokens processados vira cobrança.
- A2 (bloqueante) tests/bancada/versao.py:231 · O teste escondido roda sem reconferir o sha256: a sessão medida (mesmo HOME, sandbox do projeto sem a pasta do bench no denyRead) pode ler e trocar o avaliador; S2 deu 2/2 sem PR e sem marca. Exigência "fora do alcance" não cumprida.
- A3 (recomendado) tests/bancada/versao.py:74 · --repo só passa por regex: não confere que o repositório é público, da conta do gh logada e vazio pela API; ls-remote de URL inacessível volta vazio e conta como vazio; --remoto-url pode divergir de --repo (o PR é lido de outro repositório).
- A4 (recomendado) tests/bancada/versao.py:233 · A nota sai da última linha `resultado:` da saída de um processo que importa o código do agente; código entregue que imprime essa linha no fim (atexit) fixa a própria nota. O protocolo é público no roteiro.
- A5 (recomendado) docs/bench-versao.md:15 · Os testes escondidos ficam fora do repositório, não fora do alcance do time: as sessões do Forge leem o HOME inteiro (sem a pasta do bench no denyRead); só a marca detecta cópia literal, não a leitura que orienta o ajuste.
- A6 (recomendado) tests/bancada/versao.py:187 · A sessão herda a credencial gh do dono, que alcança todos os repositórios dele; a rodada só precisa do descartável.

## Sondas
- S1 · sonda_bench.py (harness falso do PR), env ANTHROPIC_AUTH_TOKEN=1 (e CLAUDE_CODE_USE_BEDROCK=1, CLAUDE_CODE_USE_VERTEX=1, ANTHROPIC_BASE_URL=1), sem --executar · espera: rc=2 recusado · obtido: rc=0, não recusado, nas quatro
- S2 · sonda_bench.py: claude falso que reescreve o test_escondido.py congelado para imprimir `resultado: 2/2` e sai sem PR, com --executar · espera: avaliação recusa o escondido alterado · obtido: rc=0, pr=None, resultado=2/2, marca=None

## Detalhe dos achados
**A1** · evidência `tests/bancada/versao.py:42` (lista), `:347` (conferência), `:187` (o filho herda `os.environ`) · caminho: o dono roda `--executar` numa máquina com `ANTHROPIC_AUTH_TOKEN`, provedor de nuvem ou gateway configurados (ou `apiKeyHelper` nas configurações); a sessão de horas é cobrada por token em vez da assinatura · severidade média (custo real, `R-CUSTO`; o texto do roteiro e da doc promete "sem API paga") · correção mínima: `AMBIENTE_PROIBIDO` com a lista inteira: `CI`, `GITHUB_ACTIONS`, `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, `CLAUDE_CODE_USE_BEDROCK`, `CLAUDE_CODE_USE_VERTEX`, `CLAUDE_CODE_USE_FOUNDRY`; e, em `ler_evento`, se o evento `system/init` trouxer `apiKeySource` diferente de `none`, encerrar a sessão com `limite` = `api-paga` (cobre o `apiKeyHelper`); teste com cada nome e com o init falso · esforço P · dono: autor do PR (developer do E175.3).

**A2** · evidência `tests/bancada/versao.py:76-81` (sha256 só no início), `:231` (roda o arquivo como está ao fim), `:139-144` (`so_a_tag` não acrescenta proteção), `templates/projeto/.claude/settings.json:32-37` (denyRead com 4 caminhos) · caminho: o agente medido, em modo auto e com o HOME do dono, lê `~/.forge-bench/escondidos/` (o sandbox só restringe leitura nos 4 caminhos) e o troca por Edit/Write ou o lê para ajustar a entrega; a nota sobe sem entrega (S2). A marca só pega o que aparece no projeto ou no log da sessão principal · severidade média (integridade da medida que decide versões; sem dado pessoal) · correção mínima: (a) `avaliar` reconfere o sha256 dos `CONGELADOS` imediatamente antes de rodar, copia os dois arquivos para uma pasta temporária privada e roda de lá; divergência grava `resultado: escondido alterado`; (b) `so_a_tag` acrescenta a pasta `--bench` resolvida a `sandbox.filesystem.denyRead` e `denyWrite`, e `Read(<bench>/**)`, `Edit(<bench>/**)`, `Write(<bench>/**)` a `permissions.deny`; testes: S2 como caso de abuso e a leitura das configurações do projeto · esforço P · dono: autor do PR.

**A3** · caminho: engano do dono (repositório privado ou de organização, ou URL errada) leva o projeto, o CI do modelo e o PR a um repositório que não é o descartável público; em privado, o CI do modelo consome minutos pagos · severidade baixa · correção mínima: `gh repo view <repo> --json visibility,isEmpty,owner` exigindo `PUBLIC`, `isEmpty` verdadeiro e `owner.login` igual a `gh api user --jq .login`; `--remoto-url` aceito só como caminho local (testes) · esforço P · dono: autor do PR.

**A4** · caminho: entrega que aprende o protocolo (está no roteiro, que vai na árvore das tags seguintes) e imprime a linha no encerramento · severidade baixa · correção mínima: no teste escondido (fora do repositório, do dono), rodar o código do projeto em processo filho e a nota no pai; no roteiro, nada além de ler a nota de um arquivo criado pelo pai · esforço P · dono: o dono (testes escondidos).

**A5** · correção mínima: o dono acrescenta `~/.forge-bench` ao `sandbox.filesystem.denyRead` das configurações protegidas do clone do Forge e do usuário (arquivo que nenhum agente escreve) · esforço P · dono: o usuário, levado pelo Jarvis.

**A6** · correção mínima: a doc pede um token de granularidade fina só para o repositório descartável, exportado como `GH_TOKEN` na rodada, e o roteiro o repassa ao filho · esforço P · dono: autor do PR.

Pontos do brief conferidos sem achado além dos acima: nunca bypass (`tests/bancada/versao.py:104` fixa `--permission-mode auto`; o diff não tem `bypass`, `dangerously` nem `skip-permissions` fora de texto e teste); recusa no CI (`CI`/`GITHUB_ACTIONS` recusam mesmo vazias, teste `test_recusa_com_ci_github_actions_ou_chave_da_api`); os testes do PR usam `claude` e `gh` falsos à frente do PATH e HOME temporário (`tests/test_bancada_versao.py:115-116`), sem rede nem modelo; nada toca projetos do dono pelo roteiro (cria o projeto em pasta nova, recusa remoto não vazio, `:119`); a sessão é contida pelos hooks da árvore da tag (`R-CONTRIB` impede escrita em `~/.forge-contrib` a partir do projeto). Suíte: o CI do head `d2bdd9ab` está vermelho (run 45484693745: `test_ambiente_git`, `test_reval_delta`, `PesosDaSuite` e `test_tokens_das_transcricoes...` na 3.12), falhas estruturais, fora deste domínio; o teste do PR passou localmente (17 testes).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff e duas sondas locais com o harness falso do próprio PR; nenhuma chamada ao modelo nem a sistema externo além da leitura do CI do PR.
