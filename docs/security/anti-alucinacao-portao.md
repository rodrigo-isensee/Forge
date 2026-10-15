---
tipo: revisao-seguranca
contrato: 1
pedido: anti-alucinacao-portao
branch: melhoria/anti-alucinacao-portao
commit: c365315
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-15
---
# Review de segurança: anti-alucinacao-portao (fatia 3)

Escopo: `git diff origin/melhoria/anti-alucinacao-regras..c365315` em `hooks/_comum.py`, `hooks/parecer.py`, `tests/catraca.py`, `agents/tech-lead.md` e `docs/hooks.md`. Referências: o parecer de autor `docs/reviews/anti-alucinacao-portao.md`, a seção 9, a linha "| 3 |" da seção 11 e a seção 14 da proposta anti-alucinação, com as decisões do dono (P1 = B, P2 = A, P3 = A, §14 = B). Os pontos do modelo de ameaça são a raiz do clone, o `--draft` e o `gh pr ready`.

**Veredito: aprovado.** A fatia só acrescenta guarda: nenhuma sonda achou um caminho que passasse no hook anterior e que agora fique mais frouxo. Os projetos continuam com o mesmo comportamento. Ficam dois cartões de severidade baixa (A1 e A2), que não bloqueiam, e dois pontos informativos.

## Gatilhos
Mudança em mecanismo de controle (o portão `R-REVIEW`/`R-QA` do hook `parecer`), na falha fechada (ADR 0009, seção 7) e na catraca do CI (`tests/catraca.py`, modo `pareceres`). Não há segredo, rede nem dependência nova.

## Modelo de ameaça (resumo)
- **Ativo:** a integridade da `develop`, da `homolog` e da `main` do Forge, usadas por todos os projetos. Um merge sem parecer válido é o vetor do #120.
- **Ator:** um agente na sessão do Forge (cópia principal ou worktree), que alucina ou tenta contornar um bloqueio. Ataque externo fica fora: o hook roda local e lê só o disco e o git.
- **Fronteiras:**
  - o texto do comando Bash, que o hook lê (categoria [B] de `docs/hooks.md`: barra em regra, sem garantir);
  - o disco do clone (`.claude-plugin/plugin.json`, `.forge/`);
  - o GitHub. Num repositório privado sem ruleset, a única guarda do GitHub é que ele não mescla PR em rascunho.
- **STRIDE:**
  - Tampering: forjar o manifesto ou o `.forge/` para mudar a raiz;
  - Elevation: desligar o hook;
  - Denial: bloqueio falso, inclusive pela falha fechada;
  - Repudiation: sem log do erro interno.

## Sondas
Feitas num diretório descartável em `$TMPDIR`, com os hooks tirados de `git archive origin/melhoria/anti-alucinacao-portao` (c365315), `HOME` isolado e repositórios git de teste. Para comparar, rodei a mesma bateria com `git archive origin/melhoria/anti-alucinacao-regras` (354ad7d, o hook anterior). O rc é a saída do hook: 2 bloqueia, 0 libera.

| # | Cenário | rc (antes → agora) | Leitura |
|---|---|---|---|
| S1 | Clone (manifesto, sem `.forge/versao`), review reprovado: `gh pr create` sem `--draft` | 0 → **2** | PQ-1 confirmado |
| S1 | Mesmo clone: `gh pr merge feature/x` | 0 → **2** | PQ-1 confirmado |
| S1 | `gh pr create --draft` / `--draft=false` / `--title -d` | 0 / **2** / **2** | `bandeira` não se engana com `=false` nem com `-d` usado como valor |
| S1 | `gh pr ready feature/x`, `gh pr ready` (branch atual) | **2**, **2** | portão do rascunho |
| S1 | `gh pr ready 123`, `gh pr ready <URL>` | **2**, **2** | `R-CONTRIB`, sem branch |
| S1 | `gh pr ready --undo feature/x` | 0 | volta para rascunho: correto |
| S1 | `gh api graphql` com `markPullRequestReadyForReview` | 0 | ver A2 |
| S2 | Clone sem parecer: `gh pr ready` / `gh pr merge` / `gh pr create` / `gh pr create -d` | 2 / 2 / 2 / 0 | PQ-2 confirmado |
| S3 | Clone com review e QA aprovados: `gh pr ready` / `gh pr create` | 0 / 0 | sem bloqueio falso |
| S4 | **Manifesto forjado** em pasta alheia (sem `.forge/versao`), reprovado: create / merge / ready | 0/0/0 → **2/2/2** | só ganha guarda |
| S4 | Pasta alheia sem manifesto: create / merge | 0/0 → 0/0 | igual a antes |
| S5 | Projeto (`.forge/versao`) com manifesto forjado: `create --draft` / `ready` | 2/0 → 2/0 | o projeto vem antes do manifesto; nada muda |
| S6 | **Worktree fora de `~/.forge-contrib/wt/`**: create sem `--draft` / ready / create `--draft` | 2 / 2 / 0 | a raiz não depende de `em_contrib`: guarda também fora de `wt/` |
| S6 | Worktree em `~/.forge-contrib/wt/`: `gh pr ready` sem parecer | 2 | confirmado |
| S7 | **Clone com `.forge/config.json` e `hooks_desligados: ["parecer"]`**: create / ready | **2 / 2** | `hooks_desligados` não vale no clone |
| S7b | Clone **convertido em projeto** (`.forge/versao` e `hooks_desligados`): create / merge | 0 / 0 | ver A1 |
| E1, E2 | **Erro interno** (forge-check que lança exceção), no clone: `gh pr ready`, `gh pr merge` | **2**, **2** | falha fechada; o erro foi para `.forge/run/erros.log` da cópia |
| E3 | JSON inválido, sessão (`CLAUDE_PROJECT_DIR`) no clone, pasta corrente alheia, `gh pr ready` | **2** | falha fechada pela raiz da sessão |
| E3b / E3c | JSON inválido sem sessão / sessão no clone sem marcador crítico | 0 / 0 | seletiva, como manda a ADR 0009 |
| E6 | Erro interno com `FORGE_GUARDA_ABERTA=1` | 0 | saída de emergência do dono, que o agente não tem como acionar |
| S8 | **Projeto comum**: `create --draft` sem parecer / `ready` sem parecer / `merge` sem parecer / `create` com `hooks_desligados` | 2/0/2/0 → 2/0/2/0 | **nenhum projeto muda de comportamento** |

Também passaram, na cópia da branch: `tests.test_hooks.Hooks.test_fixtures`, `test_raiz_de_estado_no_clone_do_forge` e `tests.test_catraca` ("Ran 129 tests ... OK"). Isso inclui as fixtures de projeto de antes.

`tests/catraca.py:614-620`: o laço agora junta as violações de todos os pedidos e só aprova com `pedidos and not achados`. Sem pedido, a função continua reprovando. Fecha o furo da seção 9, item 4, sem abrir caminho novo.

## Achados

### A1. Converter o clone em projeto religa o `hooks_desligados` (baixa)
- **Evidência:**
  - `hooks/_comum.py:44` e `hooks/_comum.py:480-490`: `Hook.projeto` tenta primeiro `raiz_do_projeto`, e o `hooks_desligados` vale sempre que existe `.forge/versao`.
  - `hooks/conformidade.py:1192-1193`: numa sessão com raiz no clone, o `conformidade` só age dentro de um projeto e não protege o `.forge/` do próprio clone. A frase de `docs/hooks.md` sobre o `.forge/` do clone, na seção "No clone do Forge", já diz isso.
- **Sondas:**
  - S7b: com `.forge/versao` e `.forge/config.json` contendo `hooks_desligados: ["parecer"]` no clone, `gh pr create` e `gh pr merge` saem com rc 0;
  - C1 e C2: o `conformidade`, numa sessão com raiz no clone e `agent_type` `forge:tech-lead`, deixa gravar os dois arquivos (rc 0).
- **Caminho de ataque:** um agente na sessão do Forge é barrado pelo `parecer`, grava os dois arquivos na cópia de trabalho (ficam fora do git) e mescla na `develop` sem parecer válido. São dois atos deliberados, que violam `R-CONFORMIDADE`.
- **Por que baixa:** é da mesma classe dos desvios já registrados como [B] em `docs/hooks.md`, como um script gravado e executado depois. Não é regressão: antes desta fatia o hook nem agia no clone. A barreira de servidor continua sendo o job `pareceres` do CI.
- **Correção mínima (P):** em `Hook.projeto(..., clone_do_forge=True)`, ignorar `hooks_desligados` também quando a cópia tem o manifesto do Forge (`tem_manifesto_do_forge`), mesmo com `.forge/versao`. O manifesto continua servindo só para acrescentar guarda. Acrescentar uma fixture "clone com `.forge/versao` e `hooks_desligados` barra".
- **Dono:** `tech-lead`, numa fatia seguinte ou num ajuste a esta. Não bloqueia.

### A2. `gh api graphql` com `markPullRequestReadyForReview` passa no clone (baixa, cartão)
- **Evidência:**
  - `hooks/parecer.py:309` (`merge_por_api`) só olha `pulls/<n>/merge`;
  - `hooks/conformidade.py:903-919` (`graphql_perigoso`) reconhece a mutação, mas `hooks/conformidade.py:952` só barra quando a sessão não é do clone.
  - A limitação já está registrada em `docs/hooks.md:91`.
- **Sondas:** S1, `parecer` rc 0; C3, `conformidade` com sessão no clone, rc 0.
- **Caminho de ataque:**
  1. Um agente barrado no `gh pr ready` tira o PR do rascunho pela API GraphQL.
  2. O agente continua sem conseguir mesclar: `gh pr merge` e `gh api .../merge` barram (S1, rc 2).
  3. Mas o PR passa a parecer pronto, e o dono pode mesclá-lo pela interface, que é o vetor do #120.
- **Classificação:** baixa. Exige um contorno deliberado. Com §14 = B, o dono aceitou que tirar o rascunho pela interface não é trava. O caminho do agente pela API não estava coberto por essa decisão, mas o dano depende ainda de um segundo ato do dono. **Vira cartão e não bloqueia.**
- **Correção mínima (P):** no clone do Forge, o `parecer` trata `gh api graphql` mutante com `markPullRequestReadyForReview` como `gh pr ready` sem branch, porque o ID do PR é global, e barra com `R-CONTRIB`. A leitura do texto inline, de `-F query=@arq` e de `--input` pode reaproveitar `graphql_perigoso`, que já falha fechado no que não consegue ler. Depois, atualizar a linha de `docs/hooks.md:91`. Fixture: graphql ready no clone barra; `convertPullRequestToDraft` passa.
- **Dono:** `tech-lead`.

### A3. Erro interno no clone antes de achar a raiz não é registrado (informativa)
- **Evidência:** `hooks/_comum.py:576`: `registrar_erro` usa `raiz_do_projeto` em vez de `raiz_de_estado`.
- **Efeito:** em E3, com JSON inválido e a pasta corrente no clone, o hook bloqueia, mas não grava o erro no `.forge/run/erros.log` que a mensagem manda consultar. Em E1 e E2 o log foi gravado, porque a raiz já estava definida. Não há perda de guarda, só de rastreabilidade (Repudiation).
- **Correção (P):** usar `raiz_de_estado` em `registrar_erro`, já que as fatias 4 e 5 reutilizam essa raiz.
- **Dono:** `tech-lead`.

### A4. A falha fechada pela sessão no clone pode bloquear fora dele (informativa)
- **Evidência:** `hooks/_comum.py:109`.
- **Efeito:** com a sessão no `~/Forge` e um erro interno, um comando com marcador crítico (`api`, `merge`, `pull`, `pr create|merge|ready`) é barrado em qualquer pasta (E3).
- **Por que aceitável:** é falso bloqueio só quando há erro interno. Há saída do dono (`FORGE_GUARDA_ABERTA=1`, E6) e o motivo vai para o `erros.log`. É coerente com a ADR 0009, seção 7. Sem ação.

## Riscos aceitos e ferramentas
- **Riscos aceitos:** nenhum novo neste parecer. O PR que sai do rascunho pela interface do GitHub já foi aceito pelo dono na decisão §14 = B (proposta anti-alucinação, seção 14 e risco R7). O A2 cobre só o caminho do agente e vira cartão.
- **Não verificado:**
  - comportamento real do GitHub (sem rede nem PR de teste). Que PR em rascunho não é mesclável e que o `PATCH` REST não muda `draft` vem da documentação do GitHub, não de sonda;
  - `gh pr create --draft --web`, porque o agente não opera o navegador.
- **Ferramentas:** só leitura do código, sondas locais em Python e git, e os testes do repositório. `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner` e `bandit` não estão no PATH: é uma lacuna, sem impacto aqui, porque o diff não toca workflow, dependência nem segredo.
