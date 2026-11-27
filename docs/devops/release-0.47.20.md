---
tipo: revisao-devops
contrato: 1
pedido: release-0.47.20
branch: melhoria/v0481-release-0-47-20-pareceres
commit: 779356dcee5f1c840e328dc6efbd3fa9275e8d77
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-27
---
# Review de devops: release 0.47.20 (PR #935, main..779356dc)

## Achados
- A1 (recomendado) CHANGELOG.md:1 · o corpo do PR #935 da main não lista as regras afrouxadas (#909, #918, #920, #928, #929, #931, #932 e agora #936) nem traz a saída de `tests/catraca.py --modo rotulados`; o tech-lead edita o corpo antes do merge do dono (R-FLUXO).
- A2 (recomendado) .github/workflows/ci.yml:1 · `actionlint` e `zizmor` ausentes nesta estação; não rodei os dois sobre `ci.yml`, `diario.yml` e `obsoletas.yml` (só `shellcheck` existe). Quem instala é o preparar-estacao.
- A3 (recomendado) CHANGELOG.md:1 · a tabela do PR #935 (linhas até #934) não cita o #936 (afrouxa: rótulo e marca no título; encolhe o #930, sai a guarda de grafia do Bash) nem o #937 (rótulo só por arquivo protegido, nenhuma regra afrouxa); acrescente as duas linhas.

## Detalhes
- ci: 779356dcee5f1c840e328dc6efbd3fa9275e8d77 verde

Revalidação por delta (H3), `8855671d..779356dc`: o parecer anterior cobria o head 1e301536. Entraram o #936, o #937 e o anexo dos fragmentos (#939). O delta não toca `.github/`, `Dockerfile*`, `compose*` nem IaC: o código é `bin/forge_pareceres.py` e `hooks/conformidade.py`, mais testes, mutantes, docs e CHANGELOG. Sem mudança de pipeline, o checklist do parecer anterior segue valendo (permissões, SHAs, `concurrency`, `R-MAIN`, `R-CUSTO`, `R-VERIFY`).

Regras afrouxadas, conferência pedida no brief:
- #936: rótulo `afrouxa-regra` no GitHub e marca `[afrouxa-regra]` no título; afrouxa pela catraca (sai a guarda de grafia do Bash na raiz do Forge e os casos de oráculo dela; ficam Write/Edit e o caminho literal). Precisa de linha na tabela do PR da main (A3).
- #937: rótulo `afrouxa-regra` presente, exigido só porque `bin/forge_pareceres.py` é arquivo protegido (ADR 0008); o corpo do PR declara que nenhuma regra afrouxa (conta aceita mais estreita, registro é exigência nova). Entra na tabela como "rótulo por arquivo protegido, sem afrouxar".
- #918 segue como no parecer anterior (sem o rótulo, declarado na tabela do PR).

Prova de CI: o PR #939 (head 779356dc) tem todas as checagens concluídas e verdes (`bateria`, `bateria (pareceres)`, `catraca`, `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, as 5 partes da suíte 3.12, `instalação (python 3.14)`, `teto de pulados`, `árvore já provada na develop`), e o push na `develop` do mesmo sha rodou o CI com sucesso. Jobs de push e cobertura aparecem `skipping` no PR, como previsto. Esta branch de pareceres não tem PR, então não há `gh pr checks` próprio; a prova é a do mesmo sha.
