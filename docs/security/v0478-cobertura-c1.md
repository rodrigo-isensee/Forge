---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-cobertura-c1
commit: c4ddc61daa61bd4341aded9ff3eb983893be3959
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (cobertura C1, T1 como portão da catraca)

Diff lido: `4182a6b9...c4ddc61d` (`tests/catraca.py`, `tests/test_catraca.py`, os dois `tests/mutantes/v0478-cobertura-c1*.json`, `docs/engineering/praticas.md`, o fragmento do changelog) e, fora do diff, o que o controle usa: `.github/workflows/catraca.yml`, `.github/pull_request_template.md`, `bin/forge-check` (`codigo_sem_teste`, `classe_para_o_t1`, `classe_das_mudancas`, `teste_mudou_de_verdade`).

## Gatilhos
Gatilhos: protegido da catraca (`tests/catraca.py`), controle do Forge (portão novo no CI do PR).

## Conclusão
A exceção `## Sem teste` não vira atalho mecânico:
- **Arquivo por prefixo:** `citado` (`tests/catraca.py:1657`) exige o caminho inteiro, com fronteira dos dois lados. Sondas locais: `bin/`, `bin/*`, `./bin/app`, `bin/apps`, `bin/app.py`, `BIN/APP` e `x/bin/app` não citam `bin/app`; `` `bin/app` ``, `(bin/app)`, `bin/app:`, `bin/app.` e o fim de linha com `\r` (corpo vindo da interface web) citam. Comentário HTML não cita (`secao` o remove, `tests/catraca.py:1639`).
- **Motivo genérico:** o piso é mecânico (20 caracteres além dos caminhos, que são retirados do texto antes da contagem, `tests/catraca.py:1678`); repetir os caminhos não enche o motivo. O mérito do motivo é leitura, declarado em `docs/engineering/praticas.md:15`, com a métrica de reversão no changelog (mais de 2 PRs por versão com a exceção). Ver A2.
- **Texto controlado pelo autor:** é o desenho da exceção (o autor escreve a justificativa; o review a lê). O corpo entra só por `env:` (sem injeção no shell, `.github/workflows/catraca.yml:49`), o workflow roda de novo no evento `edited` (`catraca.yml:8`), e a edição posterior só pode tirar a citação (fica vermelho) ou trocar o texto sem mudar o código revisado. Sem caminho de ataque que ganhe código sem teste além do que o review já vê.
- **Falha fechada:** classe ilegível vale N (`bin/forge-check:1289`), git que falha dá C (`bin/forge-check:1118`), e o diff dos testes ilegível levanta `ErroDeGit` (`tests/catraca.py:1675`); provado por `test_diff_dos_testes_ilegivel_barra` e `test_classe_t_isenta_e_n_barra`.
- **Script do autor:** o passo `pr-texto` roda a catraca e o `forge-check` do head (A1). Os dois estão em `PROTEGIDOS` (`tests/catraca.py:47-48`), e o passo de regras, que roda a versão da base no mesmo job, barra a mudança neles sem o rótulo do dono. Enfraquecer o T1 no próprio PR exige, portanto, a decisão do dono.

Isenção pela classe T (até poucas linhas fora dos caminhos de controle) é a regra do T1 desde a 0.43.3, não novidade deste diff.

## Achados
- A1 (recomendado) .github/workflows/catraca.yml:50 · O passo pr-texto, agora portão do T1, roda tests/catraca.py e bin/forge-check do head; com o rótulo do dono no PR, o código do autor decide o próprio T1. Correção: rodar o "$script" da base (o worktree do passo anterior) também aqui, e renomear o passo.
- A2 (recomendado) tests/catraca.py:1678 · O motivo conta uma vez para a seção inteira: um texto genérico de 20 caracteres cobre N arquivos. Mérito fica com a leitura; manter a métrica de reversão e, se a exceção virar rotina, exigir motivo por arquivo citado.
- A3 (recomendado) .github/pull_request_template.md:14 · O comentário do modelo ainda diz que o `## Sem teste` é só lido no review; com o T1 como portão, deve dizer que a catraca barra e que cada arquivo vai citado pelo caminho inteiro, com o motivo.

## Sondas

## Detalhe dos achados
- **A1** · severidade baixa · caminho: autor (agente) muda `violacoes_do_t1` para devolver vazio num PR que já tem o rótulo `afrouxa-regra` por outro motivo; o passo de regras passa pelo rótulo e o `pr-texto` roda o código alterado. Exige o dono rotular e não ler a mudança da catraca. Correção mínima: no passo "Seções...", `python3 "$script" --modo pr-texto` com o `script` da base (o worktree `$RUNNER_TEMP/base` persiste no job; exportar o caminho por `$GITHUB_ENV`). Esforço P. Dono: `devops-engineer` escreve, o dono do Forge envia (escopo `workflow`).
- **A2** · severidade baixa · sem ataque além do que o review já cobre; só reduz o atrito da exceção. Esforço P. Dono: `tech-lead`.
- **A3** · severidade informativa (usabilidade do controle). Esforço P. Dono: autor da branch.

## Riscos aceitos e ferramentas
Sem risco aceito. Suíte inteira não rodada localmente (brief: sem suíte local; o CI do PR a roda); rodei `python3 -m unittest tests.test_catraca.T1NoTextoDoPr` (10 testes, OK) e as sondas de `citado` e `secao` acima. Ferramentas ausentes no PATH (lacuna): `gitleaks`, `zizmor`, `actionlint`, Semgrep; o diff não traz segredo nem mudança de workflow (lido à mão).
