---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0480-bench-versao
commit: d2bdd9ab9e68015620a02188909ecf5453ff5b50
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 E3.2 (PR #870, BENCH-VERSAO, bench real)

## Escopo lido
Diff `a27eab7e..d2bdd9ab`: `tests/bancada/versao.py` (369 linhas, novo), `tests/test_bancada_versao.py` (17 testes), `tests/bancada/romanos/{pedido,resposta}.md`, `tests/config.json` (+1 hash em `termos_proibidos_hash`), `tests/mutantes/v0480-bench-versao.json` (M1-M8), `docs/bench-versao.md`, `changelog.d/v0480-bench-versao.md`. Teto H1: tudo em `tests/` e texto, fora da contagem. Primeiro parecer da branch.

## Conferência
- Nunca no CI: o roteiro não é descoberto pelo `unittest` (não casa `test*.py`); nenhum workflow, hook nem `bin/forge-testes` o cita; os testes usam `claude` e `gh` falsos à frente do `PATH` e o remoto é um bare local. A guarda recusa com `CI` e `GITHUB_ACTIONS` (saída 2, testado com valor vazio e `1`).
- Chave de API paga: só `ANTHROPIC_API_KEY` é recusada; outras credenciais pagas passam (A2, sonda S2-S4), e o `claude` filho herda o ambiente inteiro (`versao.py:187`).
- O agente não o executa: não há mecanismo. Numa sessão de agente (`CLAUDECODE` definida, como nesta) a guarda passa e o `--executar` seguiria para a rodada (A1, S1). Nada foi executado com `--executar` neste review.
- Sessão sempre `--permission-mode auto`, nunca bypass (testado); testes escondidos fora do repositório, congelados por sha256, marca vigiada pelo hash; avaliação por `python3 -I` com ambiente mínimo. Correto.
- CI do head `d2bdd9ab` (run 45484693745): vermelho, 7 jobs `fail` (A3-A6).
- Teste novo rodado localmente: `python3 -m unittest tests.test_bancada_versao`, 17 OK; no CI, `test_tokens_das_transcricoes_somam_subagentes_sem_repetir` falhou (A3).
- `forge-check pr v0480-bench-versao`: classe C (`tests/config.json`); faltam review, QA e segurança e a conferência de entrega do head.

## Achados
- A1 (bloqueante) tests/bancada/versao.py:347 · "Só o dono roda" sem mecanismo: na sessão de agente (CLAUDECODE definida) a guarda passa e --executar gastaria a cota do dono. Recuse também com CLAUDECODE (e CLAUDE_CODE_ENTRYPOINT), com teste do ramo e mutante.
- A2 (bloqueante) tests/bancada/versao.py:42 · R-CUSTO: ANTHROPIC_AUTH_TOKEN, CLAUDE_CODE_USE_BEDROCK e CLAUDE_CODE_USE_VERTEX passam (S2-S4) e o claude filho herda o ambiente (linha 187). Recuse-as e passe ao Popen um env sem credenciais pagas; teste por variável.
- A3 (bloqueante) tests/test_bancada_versao.py:283 · Teste instável: monta a pasta trocando só "/" e espaço, mas o nome do tempfile pode ter "_" (o roteiro troca todo não alfanumérico); falhou no CI. Use a mesma regra do roteiro ou um cwd fixo sem "_".
- A4 (bloqueante) tests/pesos-d4.json:23 · CI vermelho: test_forge.PesosDaSuite recusa o módulo novo test_bancada_versao sem peso; meça com scripts/suite-paralela.py --medir e grave o peso.
- A5 (bloqueante) tests/test_bancada_versao.py:78 · CI vermelho: test_ambiente_git recusa git sem env= do ponto único (linha 78) e o bare sem remoto_sem_manutencao no setUp (linha 104). Use ambiente_git como os outros módulos.
- A6 (bloqueante) tests/bancada/romanos/pedido.md:10 · CI vermelho: test_reval_delta acusa citação nova de caminho de TEXTO (README.md) fora da lista conhecida; reescreva sem o caminho ou atualize CITACOES_CONHECIDAS com o parecer de segurança.
- A7 (bloqueante) tests/mutantes/v0480-bench-versao.json:1 · Guardas sem mutante: limite de tokens (versao.py:179), prazo (181), sha alterado (80), marca fora do config (86), tag inexistente (88), trava (281) e claude fora do PATH (362). Um por linha; passou de 8, abra o -2.json.
- A8 (recomendado) tests/bancada/versao.py:201 · terminate sem kill de reserva: claude que ignora SIGTERM prende o proc.wait() e o leitor.join() (205) além das 4 h; espere com timeout e mande kill.

## Sondas
- S1 · principal(["--tag","v0.0.0-inexistente","--repo","a/b","--bench",tmp], {"PATH":...,"CLAUDECODE":"1"}) · espera: rc=2 (recusa) · obtido: rc=1 (passou da guarda de ambiente)
- S2 · a mesma chamada com ANTHROPIC_AUTH_TOKEN=x · espera: rc=2 (recusa) · obtido: rc=1 (passou da guarda de ambiente)
- S3 · a mesma chamada com CLAUDE_CODE_USE_BEDROCK=1 · espera: rc=2 (recusa) · obtido: rc=1 (passou da guarda de ambiente)
- S4 · a mesma chamada com CLAUDE_CODE_USE_VERTEX=1 · espera: rc=2 (recusa) · obtido: rc=1 (passou da guarda de ambiente)

## Parecer
Reprovado. O desenho segue o E175.1 e a decisão do dono (limites, auto sem bypass, testes escondidos congelados, carga e fonte de cada medida), mas as duas garantias pedidas não estão de pé: o agente pode rodar a rodada (A1) e há credenciais pagas que a guarda não vê (A2). O CI do head está vermelho (A3-A6) e faltam mutantes de guardas (A7). A8 vira cartão depois do merge. Na volta, a revalidação lê só o delta.
