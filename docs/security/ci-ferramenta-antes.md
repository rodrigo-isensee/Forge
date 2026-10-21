---
tipo: revisao-seguranca
contrato: 1
pedido: ci-ferramenta-antes
branch: melhoria/ci-ferramenta-antes
commit: 07bfbe856be86649836f0bdce50cb83874a6e2c5
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: ci-ferramenta-antes

Intervalo revisado: `10c838f..07bfbe8` (19cb145 teste vermelho; a2080cd `.github/workflows/ci.yml`; 07bfbe8 fragmento `changelog.d/ci-ferramenta-antes.md`), e o `.github/workflows/ci.yml` inteiro no HEAD.

## Gatilhos
- Controles do Forge e CI (`R-SEGURANCA`): `.github/workflows/ci.yml`, job `bateria`, e o teste que o protege em `tests/test_ci_local.py`.

## Achados

## Detalhe dos achados
Verificações feitas, sem achado bloqueante:

1. **Nada muda em permissão, gatilho nem credencial.** `permissions:` do workflow (`ci.yml:14-15`) e do job (`ci.yml:42-44`) iguais; `on:` sem `pull_request_target` (`ci.yml:7-12`); checkout com `persist-credentials: false` (`ci.yml:54`); o `GH_TOKEN` continua só no passo do gate (`ci.yml:58`). O passo do Claude Code não recebe token nem segredo no `env`.
2. **Instalação da ferramenta.** Mesma versão fixa (`@anthropic-ai/claude-code@2.1.296`) e o mesmo `--allow-scripts` restrito ao pacote (`ci.yml:94`), herdados da #251; a mudança só põe a nova tentativa e o `claude --version` (`ci.yml:95-96`). A segunda tentativa baixa o mesmo pacote fixo e o npm confere a integridade do mesmo jeito: repetir não afrouxa a conferência. Com o shell padrão do runner (`bash -e`), a falha da segunda tentativa ou do `claude --version` derruba o passo; não há `continue-on-error` no arquivo (o teste novo o proíbe, `tests/test_ci_local.py:146`).
3. **Os passos movidos continuam obrigatórios.** Testes, shellcheck, download com checksum de actionlint e zizmor, actionlint, zizmor e o e2e (`ci.yml:154-183`) mantêm o mesmo `if: !cancelled() && pesada == 'true'` e o mesmo conteúdo, só mudaram de lugar; com `!cancelled()`, rodam mesmo que uma checagem barata falhe, e qualquer falha reprova o job. As versões e os SHA-256 das ferramentas (`ci.yml:46-49`) não mudaram.
4. **Ordem frente à catraca.** O passo de pareceres (`ci.yml:138-153`) continua rodando o `tests/catraca.py` da base numa worktree própria. Antes, a suíte do PR (código arbitrário do autor) rodava antes dele; agora roda depois, o que reduz a janela em que código do PR poderia mexer no `$RUNNER_TEMP` antes da catraca. Os passos de código do PR que já o precediam (`bin/forge-changelog`, `scripts/verificar-contribuicao.sh`) seguem como estavam.

Recomendações (informativas, não bloqueantes; sem caminho de ataque):

- R1. `ci.yml:95`: a segunda tentativa roda em qualquer falha do `npm install`, não só de rede, e a mensagem diz "(rede)". Não há ganho para um atacante (o pacote é fixo e a integridade é conferida nas duas vezes), por isso não é achado de segurança; a fidelidade ao texto da decisão do dono (nova tentativa só por falha de rede) é questão de review e do parecer de devops. Correção mínima, se o dono quiser o texto literal: repetir só quando o log do npm trouxer erro de rede (`ECONNRESET`, `ETIMEDOUT`, `EAI_AGAIN`, `ENOTFOUND`, `fetch failed`), ou ajustar a mensagem. Esforço P. Dono: `devops-engineer`.
- R2. A mudança de ordem de shellcheck, actionlint, zizmor e do e2e (aviso do conferente) não reduz controle: os passos rodam iguais e reprovam o job do mesmo modo. Só o tempo até o vermelho dessas checagens fica maior; quem decide se a ordem cabe no pedido é o review.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática do diff e do workflow inteiro; `python3 -m unittest tests.test_ci_local` passou (50 testes). `actionlint`, `zizmor`, `gitleaks` e `shellcheck` não estão no PATH local (lacuna registrada); o próprio job `bateria` roda actionlint e zizmor em versão fixa sobre este workflow.
