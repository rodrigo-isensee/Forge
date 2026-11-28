---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-cobertura-c1
commit: 67ef9dfbfc2d252ed7d82a7bd34269b5801291db
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (cobertura C1, T1 como portão da catraca), revalidação

Rodada anterior: `c4ddc61d` (aprovado, A1 a A3 recomendados; texto no git). Delta lido (`forge-check parecer delta`): `c4ddc61d..67ef9dfb`, no domínio `.github/workflows/catraca.yml`, `.github/pull_request_template.md`, `tests/catraca.py` (`violacoes_do_t1`, `com_motivo`, `forge_check`) e `tests/test_catraca.py`; fora do domínio, os dois `tests/mutantes/*.json`, `docs/engineering/praticas.md` e o fragmento do changelog. Relido do controle, além do diff: `main` de `tests/catraca.py` (raiz e head do modo `pr-texto`) e o `argparse` da catraca da base `4182a6b9` (aceita `--base` no `pr-texto`).

## Gatilhos
Gatilhos: protegido da catraca (`tests/catraca.py`), controle do Forge (portão no CI do PR, workflow `catraca.yml`).

## Conclusão
- **A1 resolvido.** O passo de regras exporta `CATRACA_DA_BASE` por `$GITHUB_ENV` (`.github/workflows/catraca.yml:45`, valor fixo do próprio script, sem dado do PR) e o passo do texto roda esse script com `--base HEAD^1` (`catraca.yml:52`). A raiz continua `.` (o checkout do merge) e o head `HEAD`, então o diff é o do PR, e o `forge-check` carregado é o ao lado do script (`tests/catraca.py:1702`), o da base. O PR não muda mais o próprio T1. A volta para `tests/catraca.py` só ocorre quando a base não tem catraca (introdução, como no passo de regras) ou quando o passo de regras já falhou antes do `echo` (job vermelho de qualquer modo). Efeito de transição: neste PR a base ainda não tem T1, então o T1 só vira portão depois do merge; é o desenho da catraca (a base julga).
- **A2 resolvido.** `com_motivo` (`tests/catraca.py:1691`) exige, numa linha que cita o arquivo, 20 caracteres além dos caminhos por arquivo citado nela; arquivo citado sem motivo próprio barra. Provado por `test_motivo_vale_por_arquivo` e pelas sondas S1 a S3. O mérito do motivo segue com o review.
- **A3 resolvido.** O comentário do modelo diz que a catraca barra e pede o caminho inteiro e o motivo por arquivo (`.github/pull_request_template.md:14`).
- O corpo do PR continua entrando só por `env:` (`catraca.yml:51`); sem injeção nova.

## Sondas
- S1 · `com_motivo` com `bin/app: só troca o texto de um aviso x` e, na linha seguinte, `bin/app2` · espera: app sim, app2 não · obtido: `[True, False]`
- S2 · `bin/app bin/app2: ` + 39 letras (40 com o `:`) · espera: os dois passam (piso 2 × 20) · obtido: `[True, True]`
- S3 · `bin/app: ` + 20 letras, `bin/app2: ` + 19 letras (20 com o `:`) · espera: os dois passam no limite · obtido: `[True, True]`

## Riscos aceitos e ferramentas
Sem risco aceito. Suíte inteira não rodada localmente (brief: sem suíte local; o CI do PR a roda); rodei `python3 -m unittest tests.test_catraca.T1NoTextoDoPr` (12 testes, OK). Ferramentas ausentes no PATH (lacuna): `gitleaks`, `zizmor`, `actionlint`, Semgrep; o workflow foi lido à mão (permissões só de leitura, checkout sem credencial persistida, sem `pull_request_target`).
