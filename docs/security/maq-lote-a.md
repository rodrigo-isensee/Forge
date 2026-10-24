---
tipo: revisao-seguranca
contrato: 1
pedido: maq-lote-a
branch: melhoria/maq-lote-a
commit: 8e8acf0a457d7b1a3810fcaa6cbad873b99751e1
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-24
---
# Review de segurança: maq-lote-a

## Gatilhos
`controles do Forge` (R-SEGURANCA): `agents/tech-lead.md` (papel que guarda o push e os portões), `tests/pesos-d4.json` (entrada de `scripts/suite-paralela.py`) e `tests/test_forge.py`. Sem segredo, dado pessoal, dependência nova, workflow nem hook alterados (`git diff --stat` não toca `hooks/`, `.githooks/`, `.github/`, `scripts/`, `bin/`).

## Achados

## Detalhe dos achados
Sem achado. Conferido:
- Push em segundo plano (`agents/tech-lead.md:21`): só muda como o tech-lead espera o `git push`; o push segue passando pelo `.githooks/pre-push` inteiro (fila, trava, bloqueio de não fast-forward, suíte completa). Nada de `--no-verify`, `--force` nem desvio de `R-VERIFY`/`R-MAIN`. A frase de worktree parada até a notificação protege a prova do pre-push (árvore igual no início e no fim).
- V2 dirigida (`agents/tech-lead.md:22`): é verificador do autor; o texto diz que a suíte completa roda uma vez, no push. Não substitui o pre-push nem o CI do PR, nem os portões review, segurança, QA e conferência.
- Pesos (`tests/pesos-d4.json`): 64 chaves, todas identificadores de módulo existentes em `tests/test*.py` (nenhum faltando, nenhum órfão), valores numéricos não negativos. `scripts/suite-paralela.py:86-95` usa o peso só em `repartir` (ordem LPT e carga); a lista de módulos vem do glob, então o peso não inclui nem exclui teste. Sem entrada que vire caminho ou comando.
- Teste novo (`tests/test_forge.py:4862-4890`): só leitura de arquivos do repositório; não afrouxa invariante.
- Recomendação já registrada no review (limite de 20% sem peso) não é de segurança.
- PA-7 (`docs/engineering/achados-recorrentes.md`): sem item registrado; nada a conferir.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática manual do diff; gitleaks, osv-scanner, zizmor e semgrep não foram rodados (diff sem workflow, dependência nem segredo; ferramenta de varredura fica ao CI).
