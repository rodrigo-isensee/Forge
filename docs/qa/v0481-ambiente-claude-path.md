---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v0481-ambiente-claude-path
commit: df4b2bf9acc9db23f376b385f50f59ccf42dc467
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: ambiente (DEVCONTAINER-CLAUDE-NO-PATH, E13.5, classe C)

Conteúdo aprovado na leitura e nos testes locais; a reprovação é só pelo CI do head (R-QA, PARECER-LE-O-CI).

## Achados
- A1 (bloqueante) .github/workflows:0 · CI do head df4b2bf9 sem verde: `bateria (verificações longas)` falhou (11s) e as 5 partes `suíte (python 3.12)` seguiam pendentes na leitura; sem `ci: verde` o parecer não aprova (PQ-3).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Só a linha que põe ~/.local/bin na frente conta no .bashrc | ClaudeNovoPrimeiroNoPath (fim do PATH, sem `:$PATH`, /usr/local/bin antes) e linha já na frente (`$HOME`, `${HOME}`, `/root`) | linha no fim, linha sem PATH, linha já correta (não duplica) | passou |
| Na sessão nova o claude novo vence o de /usr/local/bin | test_na_sessao_nova_o_claude_do_local_bin_vence_o_antigo | ordem do PATH | passou |
| postStart para se o mktemp falha | PostStartDoContainer.test_pasta_temporaria_que_falha | mktemp falho: rc 1, ERRO, nenhum git nem preparo | passou |
| Comando manual do ERRO roda o script da main | test_comando_manual_da_mensagem_de_erro | sem `/workspaces/Forge` no comando e nas chamadas | passou |
| README e avisos citam /root/.local/bin/claude | test_readme_manda_abrir..., test_avisos_mandam_abrir... | texto exato | passou |

## Cenários e resultado real
- Local: `python3 -m unittest tests.test_ambiente_recriacao tests.test_guia_varios_projetos` · 22 testes, OK.
- Vermelho (`bin/forge-testes --vermelho --modulos test_ambiente_recriacao,test_guia_varios_projetos`): base=a19718532c83, revertidos .devcontainer/devcontainer.json, README.md, scripts/preparar-estacao.sh; 6 provam por asserção (avisos, bashrc no fim do PATH, sessão nova, ERRO manual, mktemp falho, README); 16 passam na base (guardas pré-existentes, "linha já na frente" e "pasta ok": regressão, não correção).
- Mutantes: `bin/forge-mutante tests/mutantes/v0481-ambiente-claude-path.json` · rc=0, M1 a M8 `morreu` (devcontainer.json:32 x4, preparar-estacao.sh:197 x2, :487, README.md:47). Um mutante por linha de guarda mudada, conferido à mão contra o diff; `--cobertura` diz `não coberto` para json e shell por não serem Python (esperado).
- O texto do `cat` em preparar-estacao.sh:663 não tem mutante próprio; coberto por assertIn do texto.

## CI
- ci: df4b2bf9acc9db23f376b385f50f59ccf42dc467 NÃO verde (leitura de `gh pr checks`: falha em `bateria (verificações longas)`; suítes pendentes). Não gravo `ci: verde`.
