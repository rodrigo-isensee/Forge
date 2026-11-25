---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: 0048e0c4160e62e66f5a166b068911e58c9ce848
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (E6.16, #878, G2.1 `forge-check parecer publicar`)

Uma passada sobre o diff `30dde218..0048e0c4` (12 arquivos), contra a ADR 0019 e o modelo `docs/security/ameacas/g2-parecer-status.md` (na `develop`, #876). Veredito: o corte é neutro para os portões de hoje, com uma exceção provada: o `publicar` abre um caminho de escrita no Forge a partir de sessão de projeto que o `R-CONTRIB` barra hoje para o `gh` (A1).

## Achados
- A1 (bloqueante) bin/forge-check:3781 · `forge-check parecer publicar` grava comentário e status pelo `gh` de dentro do processo, que o hook não vê: na sessão de projeto, com alvo no Forge (`GH_REPO` ou cópia do Forge), passa onde `gh pr comment` barra por R-CONTRIB (S1 e S2). Afrouxa barreira de hoje (M18.1 cortado).
- A2 (recomendado) tests/test_forge_pareceres.py:296 · falta `test_c15_aceite_de_outro_commit` (M14.1, modelo seção 3, item G2.1): aceite do dono com `commit:` diferente do parecer deve recusar; o código confere (bin/forge-check:3762), falta a prova e o mutante que a desliga.

## Sondas
- S1 · fixture do hook `conformidade`, sessão de projeto, `GH_REPO=rodrigo-isensee/Forge gh pr comment 1 --body x` · espera: código 2, R-CONTRIB · obtido: código 2, `R-CONTRIB: gh pr comment: a sessão de projeto não cria branch, não commita, não envia nem abre PR no Forge`
- S2 · mesma fixture, `GH_REPO=rodrigo-isensee/Forge forge-check parecer publicar .forge/pareceres/v1/review.md` · espera: código 2, R-CONTRIB · obtido: código 0, stderr vazio

## Gatilhos
Gatilhos: controles-do-forge, autorizacao, ci-cd.

## Detalhe dos achados
As sondas rodam o hook pela máquina de `tests/test_hooks.py` (`Fixture.montar` e `rodar`) num repositório temporário; nada chama o GitHub nem grava status ou comentário.

**A1 (média; bloqueante pela R-CONTRIB e pelo critério do brief "nada que barra hoje deixa de barrar").**
- Evidência: o hook só confere o alvo do `gh` digitado (`hooks/conformidade.py:3415`, `gh_contrib`, chamado em `:3751`); o `publicar` chama o `gh` por `subprocess` (`bin/forge_pareceres.py:37`), com `{owner}/{repo}` resolvido pelo `GH_REPO` ou pela pasta, e posta comentário e status (`bin/forge_pareceres.py:84-93`). O `forge-check` está no PATH em toda sessão com o plugin.
- Caminho: agente de sessão de projeto guiado por texto injetado (ator 2 do modelo), com um parecer válido e autoria do papel na própria cópia e o `commit:` igual ao head de um PR aberto do Forge (obtido por `fetch`, ou rodando numa cópia do Forge), roda `GH_REPO=<forge> forge-check parecer publicar ...`. Ganha: comentário e status `parecer-*` e `pareceres` num PR do Forge, o que a diretriz 36 proíbe à sessão de projeto. Hoje nenhum leitor usa esses statuses; o efeito fica no `R-CONTRIB` e no ruído, e vira entrada do G2.2.
- Correção mínima (dono: o autor do G2.1; `hooks/conformidade.py` é `PROTEGIDOS`): na sessão de projeto (`not self.sessao_forge`), o hook trata `forge-check parecer publicar` como `gh pr comment`: barra por R-CONTRIB quando o alvo é o Forge pela mesma regra do `gh_contrib` (`alvo_do_forge(pasta, repo_env)`, com a pasta de `--raiz`/`-C`/cwd e o `GH_REPO` da linha). Mais simples e coerente com a D5 do desenho (G2 vale para o Forge nesta versão, para os projetos na seguinte): barrar `forge-check parecer publicar` em toda sessão de projeto até a migração. Fixtures: S2 vira `contrib-publicar-no-forge-bloqueia`; corpus de legítimos: o mesmo comando na sessão do Forge libera.

**A2.** Recomendado: o comportamento está certo; falta o caso que o modelo atribui ao G2.1 e a troca no `forge-mutante` que o mata.

## O corte, mitigação por mitigação
Entregues, com teste (`tests/test_forge_pareceres.py`, 29 testes verdes aqui, `gh` falso no PATH): M1.3 (`test_nenhum_workflow_usa_secrets`), M2.1 na escrita (`test_c3_tipo_ou_veredito_fora_da_lista`), M3.1 e M13.1 no agregado (`test_agregado_pending_com_exigido_invalido`), M5.3 (`test_c20_corpo_devolvido_difere_do_local`, `test_crlf_devolvido_vale`), M7.1 com sha256 de 64 hex (`test_c9_sha256_inteiro_e_teto_de_140`; a forma mais longa cabe em 140), M9.1 sem a folga do `pr` (`test_c11_sem_autoria_jsonl_recusa`, `test_c11_papel_autor_publica`, `test_texto_mudado_depois_da_autoria`), M9.2 só a parte do `conformidade.json` (`test_caminho_por_papel_em_forge_pareceres`), M14.1 (A2), M19.1 na escrita (`--paginate --slurp`, `test_c17_gh_com_erro_ou_ausente`).

Cortados: M1.4, M4.1, M4.2, M9.2 (parte do hook `autoria`), M9.3, M10.1 (o "M10.2" do PR é a segunda metade de M10.1, a extração conferida pelo `ls-remote`; o modelo não tem M10.2) e M18.1. São neutros hoje porque:
- nenhum leitor de status existe neste head: `forge-check pr`, o hook `parecer`, o `forge-fechar` e o job `bateria (pareceres)` leem só os arquivos;
- os checks exigidos (`bateria`, `catraca`) têm a fonte fixada em GitHub Actions (`docs/protecao-de-branch.md:22-24`) e `CHECKS_EXIGIDOS` casa workflow e nome (`bin/forge-fechar:116`); status de token não os satisfaz;
- na sessão do Forge, o mesmo token já grava status e comentário pelo `gh api` sem trava (M4.2 é futuro); o `publicar` não dá capacidade nova ali;
- o M4.1 do G2.2 invalida na leitura todo status sem registro de publicação, inclusive os gravados por este item: a falha fechada vale para trás.
Condição, a registrar no PR e no cartão do G2.2: a primeira leitura de status (G2.2) não entra sem M1.4, M4.1, M4.2, M9.2 (hook), M9.3, M10.1 e M18.1. No mesmo item, filtrar `isCrossRepository` no `pr_aberto` (`bin/forge_pareceres.py:48`; PR de fork com a mesma branch e o mesmo sha).

Só aperta, por escrito: `PROTEGIDOS` ganha `bin/forge_pareceres.py` (`tests/catraca.py:49`); `hooks/conformidade.json:79-82` só acrescenta regras de caminho por papel; o subcomando novo fica fora da lista `so_leitura` (sonda local: `conferente` recebe código 2). Efeito colateral que aperta: o agregado `pending` e o `failure` de `reprovado` aparecem no `gh pr checks` e o `checks_ruins` (`bin/forge-check:1547`) os conta como não verdes; um PR em que um portão publica e outro não fica sem merge até todos publicarem (operação, ao `tech-lead`).

D3 b) do dono: sem permissão, o `gh` sai com código diferente de zero e o `publicar` recusa (`bin/forge_pareceres.py:39-43`, `test_c17_gh_com_erro_ou_ausente`). Com permissão de comentar e sem a de status, o comentário fica e o status não se grava: falha fechada no que vale.

## Suíte e CI
CI do head 0048e0c4 (#878) em andamento na leitura: `catraca` e `bateria (pareceres)` em falha esperada (rótulo do dono e parecer ausente), partes da suíte pendentes. Rodei só `tests.test_forge_pareceres` e as sondas.

## Riscos aceitos e ferramentas
Nenhum risco aceito. `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` ausentes do PATH: lacuna registrada, nada instalado (`R-CUSTO`). Revisão estática; nenhuma chamada de escrita à API.
