---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-copia-mensagem
commit: 7bdd25d54a37943b23faf6d3dcd3fc558544eebc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E14.5, #889, forge-copia: mensagem certa e clone de revisão)

Lido: `8833d0f6..7bdd25d5` inteiro (`bin/forge-copia`, `tests/test_forge_copia.py`, `tests/mutantes/v0481-copia-mensagem.json`, `tests/mutantes/v0481-copia-base.json`, `changelog.d/v0481-copia-mensagem.md`). Primeira rodada de segurança da branch; sem parecer anterior. O clone desta revisão (`~/.forge-contrib/wt/v0481-copia-mensagem-sec`) foi criado pelo próprio `forge-copia clone --revisao` da branch: nasceu em `7bdd25d5`, na `melhoria/v0481-copia-mensagem`, sem upstream (`git config --get branch.<branch>.remote` sai 1).

Gatilhos: controle do Forge (criação de cópia de trabalho na pasta liberada do sandbox; ref de onde a branch nasce; apagamento de pasta).

## Conferência
- **Nenhum caminho deixa clone na main ou sobre ref errada.** Com `--revisao`, `ponto_de_partida` (`bin/forge-copia:138-150`) só devolve `refs/remotes/origin/<branch>` ou `None` (`:145`); a base nunca é consultada. `None` ou `switch` que falha levam ao apagamento e à saída 1 (`:331-335`), como no COPIA-BASE já aprovado. O nome passa antes por `check-ref-format --branch` (`:306`), então expressões de revisão (`HEAD`, `develop~0`) são recusadas com 2 antes do clone (S6, S7). `--branch develop` ou `main` igual à padrão do clone: o `switch -c` falha e a cópia some (S3, S4). `--branch main` pedido de propósito numa origem cuja padrão é outra cria a cópia na `main` remota (S5): o mesmo de antes sem `--revisao` (a branch remota já vinha primeiro), e o envio segue barrado pelo `pre-push` (`R-MAIN`); sem achado.
- **`worktree --revisao` sai 2** antes de qualquer escrita (`:301-302`, S8, teste `test_worktree_de_revisao_e_recusada`). `limpar` retorna antes e ignora a opção (neutro).
- **Mensagem (`:133-158`, `:334`).** `candidatas` não gera mais `origin/origin/<base>`: tenta menos refs, nunca mais (só aperta). A mensagem só leva a branch, a base e a ref já validadas, à saída de erro; sem segredo nem caminho novo.
- **Só aperta ou neutro, por escrito: só aperta.** `--revisao` é opção nova e opcional; sem ela, o único efeito é não tentar `origin/origin/<base>` (que só existiria como ref de rastreio exótica). Todas as recusas de hoje seguem antes do clone e intactas com `--revisao` (destino fora, `..`, link, a própria pasta, ocupado com conteúdo preservado, nome com `-`, nome inválido: S9-S11, S14-S16). A troca no mutante `v0481-copia-base.json` M2 é equivalente à anterior (base sem `origin/` só como dada).
- Mesmas sondas rodadas na base `8833d0f6`: `--revisao` era recusado pelo analisador de argumentos (2), e S12/S13 citavam `origin/origin/nada`; agora citam só as refs tentadas.
- Testes: `python3 -m unittest tests.test_forge_copia` → 85 testes, OK. Suíte inteira: só no CI do PR #889, no mesmo head `7bdd25d5` (em andamento ao escrever; `bateria (pareceres)` vermelha por faltarem os pareceres; o merge depende de tudo verde).

Sondas executadas (nenhuma prova bloqueante; script `sonda_v0481_copia.py` no rascunho da sessão, origem local em pasta temporária, `python3 -I`), formato `entrada → obtido`:
S1 `--revisao` branch ausente → rc 1, cópia apagada, msg só `origin/melhoria/nao`; S2 branch presente com `--base origin/nada` → rc 0 no head remoto; S3 `--branch develop` → rc 1 apagada; S4 `--branch main` (padrão main) → rc 1 apagada; S5 `--branch main` (padrão develop) → rc 0 em `main`; S6 `HEAD` → rc 2; S7 `develop~0` → rc 2; S8 worktree → rc 2; S9 fora → 2; S10 ocupado → 2, conteúdo intacto; S11 `-x` → 2; S12 sem `--revisao`, base `nada` → rc 1, `origin/melhoria/nao, nada, origin/nada`; S13 base `origin/nada` → rc 1, sem `origin/origin/`; S14 a própria pasta → 2; S15 link → 2; S16 `..` → 2.

## Sondas

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, testes locais e sondas em origem descartável; nenhuma varredura externa.
