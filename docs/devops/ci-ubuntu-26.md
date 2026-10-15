---
tipo: revisao-devops
contrato: 1
pedido: ci-ubuntu-26
branch: melhoria/ci-ubuntu-26
commit: 77a4028ba046ccf58774565adffbe73c3e505b6d
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-15
---
# Review de devops: ci-ubuntu-26

## Parecer
Aprovado: fixar `ubuntu-24.04` agora e migrar para a 26.04 em janela controlada.

**O que muda e quando.** Fonte: issue actions/runner-images#14748 ("`ubuntu-latest` label will use Ubuntu 26.04 in November 2026", aberta em 2026-09-17, consultada em 2026-10-15 por rede) e README do repositório `actions/runner-images` (a tabela hoje ainda mapeia `ubuntu-latest` para 24.04; `ubuntu-26.04` já existe como rótulo). A migração é gradual, em semanas, a partir de 19/10/2026, com término previsto em 19/11/2026. Nesse período o mesmo workflow pode cair ora na 24.04, ora na 26.04: o CI ficaria imprevisível. O README documenta que fixar a versão no `runs-on` evita a migração.

**Diferenças que importam aqui** (READMEs das imagens Ubuntu2404 e Ubuntu2604, versões de 2026-10):
| Item | 24.04 | 26.04 | Passo do CI afetado |
|---|---|---|---|
| Python do sistema | 3.12.3 | 3.14.4 | `python3` sem `setup-python` em ci.yml (versao, fluxo, segredos, pareceres), catraca.yml e release.yml; só o job `testes` fixa 3.12 |
| shellcheck | 0.9.0 | 0.11.0 | job `shell`: regras novas podem gerar achados que a 0.9 não vê |
| Runtime JS (node) | 22.23.3 | 24.21.0 | jobs `plugin` e `instalacao` usam `setup-node` 24: sem efeito |
| jq / git | 1.7 / 2.55.0 | 1.8.1 / 2.55.0 | scripts de shell que usem jq: risco baixo |
| apt | n/a | n/a | nenhum workflow roda `apt`; actionlint e zizmor vêm de binário com sha256 fixo; sem risco |

**O que quebraria (hipótese, não medido).** Não rodei a suíte em Python 3.14 nem na 26.04 (sem acesso a runner; o Python local é 3.10). Os pontos prováveis são os scripts `python3` e `tests/catraca.py` nos jobs sem `setup-python`, e achados novos do shellcheck 0.11. Isso só se confirma rodando num runner `ubuntu-26.04`.

**Mudança feita.** `runs-on: ubuntu-latest` para `ubuntu-24.04` em ci.yml (9 jobs), catraca.yml (2) e release.yml (1). Mesmo número de jobs, sem matriz, sem runner maior.

**Janela de migração (recomendada, outro cartão).** Antes de 19/11/2026: (1) numa branch `melhoria/*`, trocar para `ubuntu-26.04` e ver o CI; (2) corrigir o que quebrar (fixar Python com `setup-python` nos jobs que dependem dele, tratar achados do shellcheck); (3) mesclar. A 24.04 tem suporte do GitHub por mais tempo, mas confira o aviso de descontinuação antes de adiar demais.

**Achado.** Nenhum bloqueante. Recomendado: fixar `setup-python` também nos jobs sem ele, na migração.

**Fora do alcance.** O runner privado (cota de cobrança do diagnóstico `ci-minutos`) é problema separado: esta mudança não o resolve nem agrava.

**Ferramentas.** `actionlint` e `shellcheck` não estão no PATH deste ambiente: lacuna registrada; o job `workflows` do CI roda actionlint e zizmor. A mudança é só troca de rótulo. Parecer de segurança (`R-SEGURANCA`, gatilho `.github/`) é do `security-engineer`, ainda pendente.

## Revalidação (HEAD 77a4028, após merge da develop 3f4a21e)
Aprovado, mantido. Conferido por `git diff origin/develop -- .github CHANGELOG.md`: o diff em `.github/` são só 4 linhas `runs-on: ubuntu-latest` para `ubuntu-24.04` (catraca.yml 1, ci.yml 2 com `rapida` e `bateria`, release.yml 1); o `CHANGELOG.md` está fora do diff e o fragmento `changelog.d/ci-ubuntu-26.md` entrou. `grep ubuntu-latest .github` não retorna nada: nenhum job novo do #138 ficou no rótulo móvel. Os 9 jobs do parecer anterior viraram 2 em ci.yml (consolidação do #138), mesmo critério.

`rapida` e `bateria` na 24.04 sem perda: ambos fixam `setup-python` 3.12 (SHA fixado) antes de `python3 -m unittest discover`; o shellcheck da `bateria` é o do runner (0.9.0 na 24.04), o mesmo que a develop já usava com `ubuntu-latest` (hoje 24.04), então nenhum achado novo. Resta um passo da `bateria` que usa `python3` do sistema antes do `setup-python` (testes de pareceres): 3.12.3 na 24.04, sem mudança. A recomendação de fixar o Python também nesse passo vale para a migração à 26.04.

Registro: `tests.test_ci_local` falha na develop (026231f e 3f4a21e), não nesta branch; correção em `melhoria/ci-local-jobs-consolidados`. Não é motivo de reprova do #136. `actionlint` e `shellcheck` seguem fora do PATH (lacuna); o CI roda ambos. Push (escopo `workflow`), rótulo `afrouxa-regra` e merge: do dono.

## Custo e rollback
Custo: zero adicional (`R-CUSTO`): mesmos jobs, mesmo tipo de runner. Em repositório privado a 24.04 e a 26.04 consomem minutos na mesma taxa. Rollback: reverter o commit (volta ao `ubuntu-latest`). Mudança em `.github/` exige o rótulo `afrouxa-regra` do dono no PR, e o envio exige o escopo `workflow`, que o bot não tem: o dono executa o push.
