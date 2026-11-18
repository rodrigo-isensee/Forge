---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0476-revisar-sha-delta
commit: e4191c1b4546d4c12962aed79d7652faba1a44cb
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474 (E3.76, branch melhoria/v0476-revisar-sha-delta)

Escopo: diff 3d8ad440..e4191c1b em `bin/forge-check` (controle do Forge), `bin/forge-testes`, testes e mutantes novos. Pergunta do portão: algum controle ficou mais frouxo? Resposta: não.

## Gatilhos
Gatilhos: controle do Forge (forge-check: Revisar-sha, parecer delta, recusa do brief gerar)

## Achados
- A1 (recomendado) bin/forge-check:2384 · ref_publicada confia no origin/<branch> local sem fetch: com a branch remota apagada e recriada (sem prune), o Revisar-sha aponta código antigo; falha fechada (o portão acusa desatualizado), mas o brief sai errado. Avisar quando o remoto não é ancestral da local.
- A2 (recomendado) bin/forge-check:3258 · documento_sem_parecer separa por startswith(b"---"): .md de docs/devops/ que só começa com "---" (régua) segue fora do delta; usar ler_frontmatter e exigir tipo em DOMINIO_DO_PARECER. Não é regressão: antes todo docs/devops/ ficava fora.

## Sondas

## Detalhe dos achados
**Mudança 1, `sha_a_revisar` pelo head remoto** (`bin/forge-check:2384-2397`). O `ref` só vira `refs/remotes/origin/<ref>` quando essa ref resolve para commit (`sha_do_commit`, `rev-parse --verify --end-of-options`, `bin/forge-check:2013-2018`) e segue para `rev-list` depois de `--end-of-options`: nenhum `ref` vira opção do git. `HEAD` e ref vazia nunca viram `origin/HEAD` (teste `tests/test_revisar_sha.py:32`). Chamadores: `:937` (dica de texto com sha; `origin/<sha40>` não existe), `:3208` (parecer novo), `:8723` e `:9036` (Revisar-sha do brief). O Revisar-sha é só o alvo do parecer; a validade do parecer continua conferida contra o head entregue pelo portão de desatualização (`bin/forge-check:920-929`), que não mudou. Caso local à frente do remoto (commits não enviados): o Revisar-sha fica no remoto, o parecer cobre um commit anterior e o portão o acusa `desatualizado` ao chegar o código novo: falha fechada. Caminho de ataque: quem empurra na branch remota já controla o código que o PR mescla; revisar o que está publicado é o comportamento correto. A1 é de usabilidade (brief errado), não de bypass; baixa; esforço P; dono `forge:tech-lead` (autor do forge-check).

**Mudança 2, `parecer delta` com documento sem frontmatter** (`bin/forge-check:3252-3258`, `:3314`). Só devolve ao delta arquivos que antes saíam todos (`LIVRES` inclui `docs/devops/`); o delta fica maior, nunca menor. Apagado (sem blob) volta ao delta (`bool(cod)`), também mais estrito. `git cat-file blob <sha>:<nome>`: o argumento começa pelo sha, não vira opção. Nomes impressos seguem por `nome_seguro`. A2 é melhoria de precisão; informativa; esforço P; dono `forge:tech-lead`. Os `.md` sem frontmatter de `docs/security/` (modelo de ameaças, postura) seguem fora do delta, como antes (teste `tests/test_parecer_delta.py:43`); fica registrado, sem achado, porque essa pasta só o papel de segurança escreve (hook conformidade).

**Mudança 3, recusa do PR mesclado** (`bin/forge-check:8525-8528`). Só o texto mudou; a recusa continua (`rc 1`, `tests/test_revisar_sha.py:39`). Base e branch passam por `caminho_impresso` (`sem_controle`): sem injeção de linha de veredito. A orientação não sugere `--force`, `--no-verify` nem recriar a branch apagada (`R-VERIFY`).

**Suíte:** sem PR nesta etapa (brief: sem PR), logo sem CI no head; rodei os testes novos (`tests/test_parecer_delta.py` e `tests/test_revisar_sha.py`: 8 testes, OK); o lote vizinho (volta_por_delta, aq5_parecer_novo, estado_da_branch, reval_delta, selo_e_entrega) passou de 600 s no ambiente e foi cortado, sem resultado. A suíte inteira fica para o CI do PR, que o `tech-lead` cita no merge.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura estática do diff, testes locais da biblioteca padrão; `gitleaks`, `zizmor` e `semgrep` ausentes do PATH (lacuna; o diff não toca workflow, dependência nem segredo).
