---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v0481-ambiente-claude-path
commit: df4b2bf9acc9db23f376b385f50f59ccf42dc467
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v0481-ambiente-claude-path (PR #965, E13.9)

1ª rodada completa no head df4b2bf9 contra a develop a1971853 (7 arquivos: `.devcontainer/devcontainer.json`, `README.md`, `scripts/preparar-estacao.sh`, fragmento do changelog, mutantes e dois testes). O conteúdo de segurança está correto; o parecer só reprova porque o CI do Revisar-sha está vermelho por um defeito que este diff introduz (A1), e o portão não aprova com CI vermelho.

## Gatilhos
Gatilhos: script de preparo da estação executado como root (scripts/preparar-estacao.sh), configuração do container com código baixado e executado no início (postStartCommand do .devcontainer).

## Achados
- A1 (bloqueante) scripts/preparar-estacao.sh:197 · o novo grep com \$HOME entre aspas simples dispara SC2016 e derruba o job "bateria (verificações longas)" do CI no df4b2bf9 (a base a1971853 passa); correção: `# shellcheck disable=SC2016` na linha de cima, como já há na 198

## Sondas
- S1 · shellcheck scripts/preparar-estacao.sh (no df4b2bf9) · espera: rc=0, sem aviso · obtido: SC2016 (info) na linha 197, rc=1; a mesma linha no job 141043709196 do CI termina em exit code 1

## Detalhe dos achados
**A1.** Evidência: `scripts/preparar-estacao.sh:197`; job "bateria (verificações longas)" do run 46166032218 (head df4b2bf9) falha com SC2016 nessa linha e `exit code 1`; `shellcheck` sobre o arquivo da base a1971853 passa. Caminho de ataque: nenhum (não é vulnerabilidade); é defeito provado que mantém o CI vermelho, e o portão de segurança só aprova com o CI do Revisar-sha verde. Severidade: informativa (segurança), bloqueante pelo portão. Correção mínima: `# shellcheck disable=SC2016 # o $HOME do padrão é literal` logo acima da linha 197 (o `$` ali é texto do padrão, não expansão). Esforço: P. Dono: devops-engineer (autor do E13.5).

**O que foi conferido e está correto (sem achado):**
- PATH (pedido do brief): o padrão novo da linha 197 aceita só `export PATH=` seguido de `$HOME`, `${HOME}` ou `/root` com `/.local/bin:` no início. O conjunto aceito é subconjunto estrito do antigo (`export PATH=.*\.local/bin`): toda linha que o novo aceita o antigo já aceitava, e linhas com outra pasta antes (`/tmp:$HOME/.local/bin:...`, `/home/x/.local/bin:`, `.local/binx`) deixam de contar e ganham a linha da frente. A única linha que o script escreve continua `export PATH="$HOME/.local/bin:$PATH"` (linha 199). Nenhuma pasta gravável nova entra antes das do sistema além de `~/.local/bin`, que já entrava. Uma linha preexistente do usuário como `export PATH="$HOME/.local/bin:/tmp:$PATH"` continua aceita, como já era; o script não a cria.
- postStart (`.devcontainer/devcontainer.json:32`): `d=$(mktemp -d) &&` fecha a falha antiga (sem pasta, o clone ia para `/r` como root); com mktemp falhando, nada clona nem roda e a saída é ERRO com exit 1 (provado por `PostStartDoContainer.test_pasta_temporaria_que_falha_para_com_erro_e_nada_roda` e pelo mutante M1). O `rm -rf "$d"` com `d` vazio vira `rm -rf ""`, inofensivo.
- Comando manual da mensagem de ERRO: as duas URLs do postStart são a mesma literal fixa do GitHub, sem variável do ambiente nem `${...}` (conferido no JSON decodificado: 2 ocorrências, 0 expansões); `credential.helper=` vazio; `--branch main --single-branch`. O texto está entre aspas simples no `echo`, então `$(mktemp -d)` e `"$d/r"` saem literais, sem execução no postStart; não há apóstrofo no texto que feche a aspa. Não aponta mais para `/workspaces/Forge` (cópia gravável pelo agente), o que fecha o caminho "agente edita o script da cópia de trabalho e o dono o roda como root". Provado por `test_comando_manual_da_mensagem_de_erro_parte_da_main_e_nao_da_copia_de_trabalho` e pelo mutante M3. A confiança na main (sem fixar commit) é a mesma do postStart, já aceita: a main só muda pelo PR mesclado pelo usuário (R-MAIN).
- README:47 e avisos (`scripts/preparar-estacao.sh:487`, `:663`): o caminho absoluto `/root/.local/bin/claude` evita abrir o `claude` antigo de `/usr/local/bin`, que quebra a proteção dos comandos; nenhuma credencial, nenhum segredo.
- Testes novos: usam `git` e `mktemp` falsos num PATH temporário e HOME em pasta temporária; nenhum toca rede, o HOME real ou o `.bashrc` real.

Testes rodados localmente no df4b2bf9: `python3 -m unittest tests.test_ambiente_recriacao tests.test_guia_varios_projetos` → 22 testes, OK. A suíte inteira fica no CI: no momento da leitura, as cinco partes da suíte estavam pendentes e "bateria (verificações longas)" vermelha (A1); este parecer não afirma CI verde.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: shellcheck (presente). Lacunas: gitleaks, zizmor e actionlint ausentes no PATH (não instalados, R-CUSTO); varredura de segredos feita por leitura do diff (sem segredo, sem token; o comentário do devcontainer mantém o GH_TOKEN fora do container). Nenhum workflow mudou.
