---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.12
branch: melhoria/v0479-release-04712
commit: 61cda6b8e4a79f0f236803e0faa758e3a1ab335d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: release 0.47.12 (versão inteira)

Escopo: `git diff v0.47.11..61cda6b8` (`v0.47.11` = `2fae3f93`), 21 merges de primeiro pai até o corte `09491a3b` e a marca `61cda6b8` (E59.1). Cada item entrou com os próprios pareceres; aqui se confere a junção e a marca.

Gatilhos: hooks (`agentes`, `conformidade`, `_comum`, `_json_raso`, `doutor`, `pesado`), execução de comando (`bin/forge-check`, `bin/forge-testes`, `bin/forge_onde.py`, `bin/forge-placar`), sandbox do modelo de projeto, regra afrouxada (`R-FLUXO`, A3), release usada por todos os projetos.

## Detalhe dos achados
Sem achados. Junção conferida:
- Pareceres de segurança da versão: os 17 em `docs/security/` acrescidos desde `v0.47.11` estão `aprovado` (`v0479-ae1-onde`, `-ae8-ruleset`, `-agentes-caiu-em-finito`, `-bp1-relogio-hook`, `-bp2-i2-regra`, `-bp3-s2-container`, `-bp3-s3-registro`, `-corpus-custo`, `-doc-a3-fora-de-pareceres`, `-forge-check-ci-verde`, `-json-profundo`, `-meta85-forge-check`, `-pv-a1-adr`, `-pv-b1-registros`, `-recomendado-restos`, `-sai-quarentena-s1`, `-sandbox-controle`).
- Revisado × mesclado (squash): para cada um, o patch de `merge-base(commit, 09491a3b)..commit:` contra `<squash>^..<squash>`, fora de `docs/{qa,reviews,security,devops}`, `tests/mutantes/`, `CHANGELOG.md` e `changelog.d/`. Iguais (`git patch-id --stable` ou árvore igual): ae1-onde, ae8-ruleset, agentes-caiu-em-finito, bp2-i2-regra (mesmas linhas, só deslocamento de contexto), bp3-s2-container, bp3-s3-registro, corpus-custo, doc-a3, forge-check-ci-verde, meta85-forge-check, pv-a1-adr, recomendado-restos, sai-quarentena-s1. Diferem só fora do código de produção: `v0479-sandbox-controle` (`169d5783`: peso `test_sandbox_controle: 1.7` em `tests/pesos-d4.json`), `v0479-json-profundo` (`89a4e02b`: uma linha do `_json_raso.py` em `docs/indice-forge.md`), `v0479-pv-b1-registros` (`6cc55807`: `remoto_sem_manutencao(remoto)` em três testes de `tests/test_testes_tocados.py`, que grava a config sem manutenção no repositório nu temporário do teste, sem herdar `GIT_*`). Nenhum muda hook, `bin/`, workflow nem regra; sem caminho de ataque.
- Marca `61cda6b8`: só `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.12 (iguais ao `CHANGELOG.md` `[0.47.12] - 2026-11-20`), `[Não publicado]` vazio, os 21 fragmentos apagados (`changelog.d/` só com o `README.md`; as 52 linhas removidas estão todas no `[0.47.12]`) e a linha do placar em `docs/engineering/placar-mutacao.md`. Nada além disso.
- Segredo: 0 ocorrências de token, chave privada ou credencial nas linhas acrescidas de `v0.47.11..61cda6b8` (ghp_, github_pat_, AKIA, chave privada, xox, sk-). Neutralidade: o `[0.47.12]` cita só ferramentas, hooks, testes e IDs do pedido.

## Riscos aceitos e ferramentas
Nenhum risco aceito nem pendente de aceite. A suíte inteira é do CI do PR; a promoção exige o CI verde. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint não estão no PATH; a versão não toca workflow nem dependência.
