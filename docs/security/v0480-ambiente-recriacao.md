---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-ambiente-recriacao
commit: 93a2123cdbef523aaa7da20aaaf2a7455895d475
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0480-ambiente-recriacao (E119.6, revalidação da volta única)

Delta lido (`forge-check parecer delta`): `09457540..93a2123c`, no domínio só `scripts/preparar-estacao.sh` e `templates/projeto/.devcontainer/preparar-ambiente.sh`; fora do domínio (não relidos): o fragmento do changelog, a spec de mutantes e `tests/test_ambiente_recriacao.py`. A rodada anterior (parecer no `09457540`) fica no git e não é recopiada.

## Gatilhos
Gatilhos: comando como root fora do sandbox no postStart, download e execução de código de terceiro, alteração do PATH do shell de root, modelo de projeto.

## Sondas

## Detalhe dos achados

**Achados anteriores.**
- A1 (recomendado): **fechado.** As duas chamadas do instalador têm `--proto '=https' --proto-redir '=https' --connect-timeout 20 --max-time 120` (`scripts/preparar-estacao.sh:210`, `templates/projeto/.devcontainer/preparar-ambiente.sh:97`). O `timeout 300` continua cobrindo o `bash`, e o `-f` com o `&&` impede executar download falho.
- A2 (recomendado): **fechado.** A falta agora dá o comando em dois passos, baixar para `instalar-claude.sh` e depois `bash` (`scripts/preparar-estacao.sh:205` e `:214`, `templates/projeto/.devcontainer/preparar-ambiente.sh:101` e `:105`): download cortado não executa nada.

**Conferido no delta, sem achado.** O teste do PATH passou a exigir `^[[:space:]]*export PATH=.*\.local/bin` (`scripts/preparar-estacao.sh:195`, `templates/projeto/.devcontainer/preparar-ambiente.sh:107`): linha comentada ou menção solta não conta mais como feito. A linha gravada é a mesma da rodada anterior, e `~/.bashrc` e `~/.local/bin` seguem fora da escrita do sandbox, então o risco não muda. Nenhum segredo no delta.

**Cartões (fora do delta, não bloqueiam esta entrega; dono `devops-engineer`).**
- C1: `scripts/preparar-estacao.sh:534` instala o nvm com `curl -fsSL ... | bash` (versão fixa por tag, sem limite de tempo). Mesma correção de A1 e A2: baixar para arquivo com `--proto '=https' --proto-redir '=https' --connect-timeout 20 --max-time 120` e só então `bash`; o texto do `[simular]` (`:532`) acompanha. Severidade baixa: a origem é https e a máquina é a do dono; o ganho é contra download cortado e rede presa.
- C2: `scripts/preparar-estacao.sh:569` (modo `--ferramentas`/estação) ainda faz `curl -fsSL https://claude.ai/install.sh | bash`. Alinhar com o caminho do container (`:210-211`): download para `mktemp -d` com os mesmos limites, `bash` com `timeout 300` e stdin de `/dev/null`; o `[simular]` (`:567`) acompanha. Severidade baixa, mesma razão de C1.

## Riscos aceitos e ferramentas
Nenhum risco aceito pelo dono; o aceite do instalador sem soma fixa (rodada anterior) continua valendo sem mudança. Rodados: `bash -n` nos dois scripts e `python3 -m unittest tests.test_ambiente_recriacao tests.test_ambiente_hook` (19, OK). Suíte inteira não rodada (brief: sem suíte local); sem PR nem CI para citar, o CI verde do PR segue condição do merge (`R-SEGURANCA`, `R-REVIEW`). Faltaram shellcheck, gitleaks, zizmor e actionlint (fora do PATH; nada instalado).
