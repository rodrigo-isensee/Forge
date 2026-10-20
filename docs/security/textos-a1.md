---
tipo: revisao-seguranca
contrato: 1
pedido: textos-a1
branch: melhoria/textos-a1
commit: b9a8d7548e429dc7abebd4c61c5c16895484a001
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: textos-a1

## Gatilhos
Controles do Forge: a regra `R-FLUXO` (controle do Forge) e `tests/test_hooks.py` (teste do hook `conformidade`). Revisão estática do diff `0f480c8..b9a8d75` (5 arquivos de conteúdo, 26 acréscimos, 1 linha trocada); suíte não rodada, por ordem do brief.

## Achados

## Detalhe dos achados
Sem achado. Conferido:
- `R-FLUXO`, linha 16 da fonte: a única linha trocada só ganhou o parêntese "a trava lê a `develop` do remoto, depois de `git fetch`, e não a cópia local"; o resto da linha é idêntico. Aperta a trava (evita comparar com base local velha) e não remove nem afrouxa item protegido: os 20 padrões de `invariantes` de `R-FLUXO` e `skills/ci-cd/SKILL.md` em `tests/config.json` continuam presentes (conferidos por regex).
- tests/test_hooks.py:844-849: os 4 casos novos do papel aq (maiúsculas no caminho, maiúsculas na raiz do clone, clone como link para fora do home, `.git` aninhado em `propostas/`) esperam código 2 (bloqueio) e mensagem de recusa; só acrescentam casos, sem alterar o hook nem os casos existentes. Fecham a recomendação do parecer `docs/security/fc-aq-hook.md`. O review do tech-lead mostrou os casos falhando sob mutação do hook.
- skills/qa-testing/SKILL.md e skills/ci-cd/SKILL.md (seção "Simulação de merge"): usa só `git fetch origin <base>`, `git merge --no-ff refs/remotes/origin/<base>` em cópia descartável e `git rev-parse`; não há `--force`, `--no-verify`, credencial, token nem serviço pago (busca nos acréscimos: 0 ocorrências). Respeita `R-VERIFY` e `R-CUSTO`. O fetch usa a rede só para o remoto do próprio projeto.
- changelog.d/textos-a1.md: só texto.

Recomendação não bloqueante (informativa): o roteiro não diz de onde clonar a cópia descartável (cartão ROTEIRO-CLONE-ORIGEM, já aberto pelo QA); ao fechá-lo, mande clonar do remoto, não de um clone local sem `origin/<base>`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sem ferramenta de varredura necessária (só texto e teste); gitleaks e demais não rodados por não haver código executável novo nem segredo no diff.
