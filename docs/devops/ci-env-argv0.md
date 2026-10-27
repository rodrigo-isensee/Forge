---
tipo: revisao-devops
contrato: 1
pedido: CI-ENV-ARGV0
branch: melhoria/ci-env-argv0
commit: 3f2bdf1d113b27f8063279c82867e62442e4d037
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-27
---
# Review de devops: CI-ENV-ARGV0

## Parecer
Aprovado. Um passo novo em cada job de bateria (`bateria` e `bateria (python 3.14)`), antes de "Testes do Forge": instala `rust-coreutils` (uutils, apt do runner ubuntu-24.04, sem fonte paga nem ação de terceiros), liga `/usr/lib/cargo/bin/coreutils/env` como `env` numa pasta no começo do `PATH` (`$GITHUB_PATH`) e confere, com `shutil.which("env")` (o mesmo que `envs_da_maquina`), que o `env` achado é esse, que aceita `-a x true` e que roda `env X=1 printf`. Qualquer falha encerra o job (`set -euo pipefail`, sem `continue-on-error`). Na `bateria` o passo segue o mesmo `if` da suíte (gate de commit só de parecer).
- Ferramentas: `shellcheck` no corpo do passo (limpo); `actionlint` e `zizmor` ausentes do PATH (lacuna; o CI da bateria roda os dois neste mesmo arquivo); YAML lido por `yaml.safe_load`.
- Prova local do passo (conferência pega a falta): sem a instalação e o `ln`, `o env do PATH é /usr/bin/env, não o do uutils`, rc=1; com um `env` que recusa `-a`, `o env ... não aceita -a`, rc=1; com a instalação, `env (uutils coreutils) 0.8.0`, rc=0.
- Sem entrada não confiável em `run:`; sem segredo; `permissions:` inalteradas.
- recomendado: fixar a versão do pacote (`rust-coreutils=<versão>`) se a mudança de versão do apt do runner virar ruído; não vale agora, o runner é fixado em ubuntu-24.04 e a conferência pega regressão.

## Risco
- A versão do `rust-coreutils` no noble pode não ter `-a`: a conferência falha o job (falha fechado) e o passo seguinte seria subir a versão ou outra fonte do apt; não foi possível provar no runner daqui (sem rede ao apt do runner), a primeira execução do PR é a prova.
- Substituir o `env` do `PATH` vale para a suíte inteira (é o objetivo); os scripts com `#!/usr/bin/env` seguem o `/usr/bin/env` absoluto, que não muda.
- Rede: `apt-get update` e `install` dependem do espelho do runner; falha de rede reprova o job (sem nova tentativa, como pedido: falha fechado).

## Custo e rollback
- Tempo estimado do passo: 15 a 30 s por job (update + um pacote de ~12 MB), dois jobs em paralelo, ~0,5 a 1 min de runner por execução do PR, dentro da franquia gratuita (`R-CUSTO`); o timeout de 15 min não muda e a suíte não fica mais lenta com o `env` do uutils (estimativa, medir no primeiro `gh run list`).
- Sem recurso novo nem serviço pago. Rollback: reverter o commit (remove os dois passos); nada persiste no runner.
