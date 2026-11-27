---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-ci-uma-vez
commit: e8368a4cdd98951a1a3b96d18eb539e648d299ca
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E32.5, F6, #929)

1ª rodada completa sobre `6edd59d2..e8368a4c` (merge-base com a develop): `.github/workflows/ci.yml`, `.github/workflows/diario.yml` (novo), `scripts/arvore-testada.py` (`--do-pr`), testes, mutantes, `docs/protecao-de-branch.md`, fragmento. Decisão do dono de 26/11 19:37 (no `## Decisões` do pedido) cobre o desenho: suíte uma vez no PR, 3.14 só instalação e fumaça, longas e mutantes no diário, a develop não repete o que passou no PR.

Gatilhos: CI e workflows, permissões do token, controle do Forge (prova da árvore que pula a suíte na develop e, por transitividade, na promoção).

## Achados
- A1 (bloqueante) scripts/arvore-testada.py:163 · a prova do PR aceita qualquer check `bateria` do github-actions no head, sem ligar ao run do ci.yml nem à base em que rodou: PR do mesmo head contra outra branch (base editada depois, `edited` não dispara o CI) ou check criado pela API vira prova e pula a suíte até a main.

## Sondas
- S1 · prova_do_pr com API falsa: check `bateria` success do run do PR #77 contra a base melhoria/x (base.sha fora do head) · espera: (False, ...) · obtido: (True, 'árvore 1111111 igual à do head 3333333 do PR #77, com a bateria verde'), sem ler actions/runs

## Detalhe dos achados
**A1.** Evidência: `scripts/arvore-testada.py:163-166` lê `commits/<head>/check-runs` e aceita o mais recente com `name == "bateria"` e `app.slug == "github-actions"`; nada consulta `actions/runs` nem a base do run. O CI do PR dispara só em `opened, synchronize, reopened` (`.github/workflows/ci.yml:22`). Com a prova aceita, `rapida-partes-doze` pula todos os passos (`ci.yml:95` a `:173`) e o job "checagem rápida (push na develop)" fica verde sem suíte; é esse job que `provar` (SP4, C-3) lê na promoção develop → homolog → main, então a suíte não roda em nenhum degrau.

Caminho de ataque (quem tem push numa branch, inclusive um agente com o token do bot, sem escopo `workflow`): cria a branch X com `scripts/suite-partes.py` (ou um teste) neutralizado, abre o PR do head H (que já contém a develop) contra X; o CI roda `merge(X, H)` e o `bateria` de H fica verde; edita a base do PR para `develop` (sem novo CI). O `bateria` exigido pelo ruleset já está verde em H (isso já era assim antes do F6); o que o F6 tira é a segunda barreira: antes o push na develop rodava a suíte, o "checagem rápida" ficava vermelho e a promoção não achava prova. Segunda via, para quem tem escopo `workflow`: um workflow com `checks: write` cria um check `bateria` success em qualquer sha (o check do GITHUB_TOKEN sai com o app github-actions). Ganho: código que quebra a suíte (inclusive teste de controle de segurança) chega à main sem nenhuma execução da suíte; o diário 3.14 abre uma issue, mas não é portão. Severidade: alta (integridade do portão do CI, ator interno ou agente comprometido).

Correção mínima (dono `devops-engineer`, esforço P), no padrão do `prova_valida` (C-3): em `prova_do_pr`, trocar a leitura do check pela execução do workflow: `actions/runs?head_sha=<head>&event=pull_request`, filtrar `path == .github/workflows/ci.yml`, `head_repository.full_name == repo`, `status == completed` e `pull_requests[]` com `number` igual ao do PR e `base.ref == develop`; exigir `compare/<base.sha do run>...<head>` em `ahead` ou `identical` (assim `merge(base, H)` tem a árvore de H); ler `actions/runs/<id>/jobs` e exigir um único job `bateria` em `success` na tentativa mais recente do run mais recente. O `actions: read` de `ci.yml:43` passa a ser usado. Teste de abuso (qa-engineer) em `tests/test_arvore_testada.py`, `ProvaDoPr`: (1) run do PR com `base.ref` diferente de develop ou `base.sha` fora do head → False; (2) check `bateria` sem run do ci.yml (criado pela API) → False; (3) run de `workflow_dispatch` ou de outro `path` com job `bateria` → False; (4) tentativa mais recente vermelha com anterior verde → False.

## O que aperta, o neutro e o que afrouxa
**Aperta**
- Nada no portão do PR; o `diario.yml` acrescenta uma execução diária na develop (suíte 3.14, e2e 3.12, fatia de mutantes) com issue automática, que não existia como sinal fora do PR.

**Neutro**
- PR de fork: `head.repo.full_name == repo` (`scripts/arvore-testada.py:156`) e o teste "head de fork" recusam.
- Head trocado: exige `merge_commit_sha == sha` do push, árvore do head igual à do commit e o check no `head_sha` do head; squash e merge normal dão a mesma árvore com o head descendente da develop anterior (`compare ... ahead|identical`, `:161`); rebase merge diverge e cai na suíte inteira (falha fechada).
- Check de mesmo nome de outro app: `app.slug` recusa. Check de mesmo nome por outro workflow na árvore do head: o workflow entra no diff revisado e na develop (mesma raiz de confiança de editar o `ci.yml`).
- Falha fechada no envio: erro de rede ou HTTP sai 1 sem detalhe (teste `test_erro_da_api_sai_1_sem_detalhe`, verde aqui); job `arvore-envio` vermelho pula as partes e o agregador `rapida` (com `always()`) reprova; cancelamento por `concurrency` deixa o commit sem prova da develop.
- Permissões e entradas: `arvore-envio` só leitura (`contents`, `actions`, `checks`, `pull-requests`), token só no passo da prova, `persist-credentials: false`, entradas por `env:`, código executado é o da develop já mesclada. `diario.yml`: `contents: read` no topo, `issues: write` só no job `cartao` (`diario.yml:130`), que não faz checkout nem roda código do repositório; título fixo, corpo de `needs.*.result` e do contexto do run por `env:`; `ref: develop` fixo; ações fixadas por SHA. O `$linha` sem aspas em `diario.yml:118` vem de nomes de arquivo de `tests/mutantes/` da develop (revisados), sem entrada externa.
- `workflow_dispatch` do diário a partir de outra branch roda o arquivo daquela branch; editar workflow já exige o escopo `workflow`, sem ganho novo.

**Afrouxa** (decidido pelo dono em 26/11 19:37; o `tech-lead` confere o rótulo `afrouxa-regra`, ADR 0003)
- A suíte no 3.14, o e2e no 3.12 e os mutantes saem do portão do PR e viram sinal diário sem bloqueio.
- O push na develop deixa de rodar a suíte quando o PR a provou; o "checagem rápida (push na develop)" passa a significar "provado no PR" e a promoção herda essa prova. É aqui que o A1 pesa.

## Riscos aceitos e ferramentas
Nenhum risco aceito. CI do head: `gh pr checks 929` traz só `catraca`; o run de push do `ci.yml` no e8368a4c (45924102244) falhou por arquivo de workflow inválido (o A1 do parecer de devops), então não há `bateria` no head e o parecer não poderia aprovar de qualquer forma. Rodei `tests.test_arvore_testada` (27 testes, OK) e a sonda S1, com API falsa, sem rede. Ferramentas ausentes nesta estação: `gitleaks`, `actionlint`, `zizmor`, `osv-scanner`, `semgrep` (lacuna; o CI roda `actionlint` e `zizmor`).
