---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0480-bench-versao
commit: 011c4c1e6d6eb550932e0d880b7a89244bb72190
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (E3.8, PR #870, bench de versões com agentes), volta por delta

Delta lido: `git diff d2bdd9ab..011c4c1e` (volta única E3.5: `d60eb059`, `011c4c1e`); de código, `tests/bancada/versao.py`, `tests/test_bancada_versao.py`, `docs/bench-versao.md`, `tests/bancada/romanos/pedido.md`, mutantes e `tests/pesos-d4.json`. `forge-check parecer delta`: nenhum arquivo do domínio dele mudou (o roteiro conta como teste); relido o delta inteiro mesmo assim, por ser o objeto dos bloqueantes. Já lido na rodada anterior (no git, `c4e65e3a`): o resto do roteiro, a doc e os testes do PR.

**Só aperta ou neutro:** só aperta e, no resto, neutro. Aperta: `AMBIENTE_PROIBIDO` com 8 nomes (`tests/bancada/versao.py:45`), recusa do `--executar` em sessão de agente (`CLAUDECODE`, `CLAUDE_CODE_ENTRYPOINT`), o filho sem essas variáveis (`ambiente_da_sessao`), `apiKeySource` diferente de `none` (ou ausente) encerra com `api-paga`, `repo_descartavel` (público, vazio, da conta do gh), `--remoto-url` só pasta local, negação de `<bench>/escondidos` à sessão, sha256 reconferido numa cópia privada, SIGKILL após SIGTERM. Neutro: critério 5 do `pedido.md` reescrito (os escondidos são os mesmos, sha256 em `CONGELADOS` inalterado), mutantes, pesos, `leitor.join` com prazo. Nenhuma regra, invariante, hook, workflow ou permissão do Forge muda.

## Gatilhos
Gatilhos: custo (`R-CUSTO`, sessão real com a assinatura), execução de agente em modo auto na máquina do dono, credenciais do dono (git e gh) e remoto público, integridade da avaliação (testes escondidos).

## Achados
- A4 (recomendado) tests/bancada/versao.py:292 · Segue aberto (dono): a nota vem da última linha `resultado:` de um processo que importa o código entregue; entrega que imprime essa linha no encerramento fixa a própria nota.
- A5 (recomendado) docs/bench-versao.md:19 · Segue aberto (usuário): `~/.forge-bench` fora do denyRead das configurações protegidas do clone do Forge e do usuário; as sessões do time leem os escondidos.
- A6 (recomendado) tests/bancada/versao.py:235 · Segue aberto (autor): a sessão herda a credencial gh do dono, que alcança todos os repositórios dele; a doc não pede token fino só do descartável como GH_TOKEN da rodada.
- A7 (recomendado) tests/bancada/versao.py:45 · Provedor pago posto no bloco `env` das configurações do usuário ou gerenciadas (Bedrock, Vertex, gateway) não passa pelo os.environ e pode chegar com apiKeySource `none`; recusar também quando esses nomes estão nesses `env`.
- A8 (recomendado) tests/bancada/versao.py:168 · Só `<bench>/escondidos` é negado: as rodadas anteriores em `<bench>/rodadas` (projeto e `avaliado` de outras versões) ficam legíveis pela sessão; negar as pastas irmãs já existentes evita copiar a entrega de outra versão.

## Sondas

## Detalhe dos achados
**Estado dos achados anteriores**
- **A1 (bloqueante): resolvido.** `tests/bancada/versao.py:45` (a lista inteira pedida), `:227-229` (o filho não herda nenhuma), `:187-191` e `:242-243` (`apiKeySource` diferente de `none`, inclusive ausente, encerra com `api-paga` e mata sem esperar o intervalo); o laço de `rodada` sai no `limite`, sem nova volta. Sonda local (arquivo de sonda gravado pelo Write, sem `--executar`, HOME temporário): as 6 variáveis pagas dão rc=2; `ler_evento` com `none` deixa `limite` vazio, com `user`, `apiKeyHelper` e sem o campo dá `api-paga`; `ambiente_da_sessao` tira `ANTHROPIC_AUTH_TOKEN` e `CLAUDECODE`. Falha segura: se a assinatura vier com outro valor, a rodada para cedo, sem cobrança. Resíduo em A7.
- **A2 (bloqueante): resolvido.** (a) `:280-288`: copia os dois `CONGELADOS` para `tempfile.TemporaryDirectory` (0700), confere o sha256 da cópia e roda a cópia; não há janela entre conferir e rodar. Sonda: escondido reescrito para imprimir `resultado: 2/2` dá `escondido alterado` (na rodada anterior, S2 dava 2/2). (b) `:160-175`: `<bench>/escondidos` resolvido entra em `sandbox.filesystem.denyRead` e `denyWrite` e em `Read`/`Edit`/`Write(//<abs>/**)` no `permissions.deny` do projeto (sintaxe de caminho absoluto correta; a sonda conferiu o JSON gerado).
  **Negar só `<bench>/escondidos` basta?** Para o requisito do A2, sim: os testes e a marca só existem em `<bench>/escondidos/<versão>/`; `avaliado`, `rodada.json` e `sessao.jsonl` das rodadas não contêm o texto dos escondidos (a avaliação só grava `resultado: n/m`), e a cópia da avaliação fica em pasta temporária fora do bench, apagada ao fim. Negar o bench inteiro negaria o próprio projeto. A escrita, mesmo se a negação falhar (por exemplo, a sessão editando o `settings.json` do próprio projeto), é pega pelo sha256. O que sobra é a leitura de outras rodadas (A8): contaminação entre versões, não vazamento dos escondidos.
- **A3 (recomendado): resolvido.** `repo_descartavel` (`:126-138`) exige `PUBLIC`, `isEmpty` verdadeiro e dono igual ao login do gh, chamado só com `--executar` (`:426`); `--remoto-url` só pasta local (`:82-83`).
- **A4, A5, A6:** abertos, sem mudança no delta; donos e correção mínima como na rodada anterior (`c4e65e3a`).

**A7** · caminho: o dono tem Bedrock, Vertex, Foundry ou gateway configurados no bloco `env` de `~/.claude/settings.json` ou das configurações gerenciadas; a sessão filha os aplica, o `os.environ` do roteiro não os vê e o `apiKeySource` pode vir `none` (o provedor não usa chave da API) · severidade baixa (custo; exige configuração deliberada) · correção mínima: antes do `--executar`, ler o `env` de `~/.claude/settings.json`, `~/.claude/settings.local.json` e `/etc/claude-code/managed-settings.json` e recusar se trouxer algum nome de `AMBIENTE_PROIBIDO` (`CI`, `GITHUB_ACTIONS`, `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, `CLAUDE_CODE_USE_BEDROCK`, `CLAUDE_CODE_USE_VERTEX`, `CLAUDE_CODE_USE_FOUNDRY`) ou a chave `apiKeyHelper`; teste com HOME temporário · esforço P · dono: autor do PR.

**A8** · caminho: a sessão medida, em modo auto, lista `../..` e acha `<bench>/rodadas/<outra-tag>/avaliado` com uma entrega que já passou; copiá-la infla a nota da versão medida · severidade baixa (integridade da medida; sem dado pessoal) · correção mínima: em `so_a_tag`, acrescentar a `denyRead` e ao `permissions.deny` cada pasta já existente em `<bench>/rodadas` que não seja a da rodada · esforço P · dono: autor do PR.

Suíte: CI do head `011c4c1e` (run 45503525036) com as 10 partes da suíte em 3.12 e 3.14 verdes; falha só a `bateria (pareceres)`, que espera os pareceres desta volta. `tests.test_bancada_versao` local: 26 testes OK.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff e sondas locais que chamam as funções do roteiro com HOME temporário; nenhuma chamada ao modelo, nenhum `--executar`, nenhuma pasta do bench do dono criada; leitura do CI do PR pelo gh.
