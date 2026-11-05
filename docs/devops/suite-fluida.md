---
tipo: revisao-devops
contrato: 1
pedido: suite-fluida
branch: melhoria/suite-fluida
commit: 389c585e627559e0e9371bfc7cab04659f83b15f
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-05
---
# Review de devops: suite-fluida

## Parecer
Aprovado. Revisão estática de `b45e40a...389c585` e da volta `27c5981..389c585`. A branch não toca `.github/`, `Dockerfile*`, `compose*` nem IaC; o parecer cobre o efeito da suíte fluida sobre o CI e o pre-push. Ferramentas: `shellcheck` presente (nenhum `.sh` mudou); `actionlint` ausente do PATH (lacuna, sem workflow alterado). A suíte inteira é do QA (`R-TETO`); não rodei.

## Achados
- A1 (recomendado) `scripts/suite-paralela.py:174`, `:252-266` · no runner gratuito de 2 a 4 núcleos, `base = min(4, nproc)` e `cabe <= nproc` dão 2 processos com nproc 2, 3 a 4 com nproc 3 ou 4. O teto antigo era 4, então com nproc 4 o comportamento é o de hoje. Nenhuma regressão esperada; sugestão: no checkpoint da release, comparar `gh run list` da bateria com a anterior (limite de +20%). Não devolve.
- A2 (recomendado) `scripts/suite-paralela.py:585` · o resumo do passo (`GITHUB_STEP_SUMMARY`) segue gravado depois do veredito, e erro nele vira `resumo indisponível` sem mudar o rc. Sugestão: conferir no primeiro run do PR que o resumo aparece. Não devolve.

## Verificações pedidas
- Jobs de CI: `.github/workflows/ci.yml:36`, `:58` e `:238` chamam `python3 scripts/suite-paralela.py` sem argumento e sem ramo especial; `ci.yml` não mudou no diff. Sem `FORGE_SUITE_PROCS`, o CI roda em modo fluido.
- `timeout-minutes`: 20 (push na develop), 25 e 25; inalterados e suficientes: a fila nunca passa de min(nproc, módulos) e o piso é min(2, nproc), então o pior caso é a suíte com 2 processos, como num runner de 2 núcleos.
- Workers que sobem e descem (E2): descer é não lançar o próximo módulo; o processo em andamento termina. A medida é só leitura de `/proc/stat` e `/proc/<pid>/stat`. No runner (VM dedicada) quase não há carga alheia, então fica no teto de nproc. No pre-push local, a suíte cede a máquina a outras tarefas (piso de 2 processos com carga alta ou memória baixa) e a trava de uma suíte por vez segue intacta, fora do caminho fluido.
- `FORGE_SUITE_PROCS`: corrigido na volta (`:188-190`, faixa 1 a nproc, falha fechada), em linha com o R-TETO e o parecer de segurança.
- Pre-push: `.githooks/pre-push:278-279` continua chamando o script com `FORGE_SUITE_TRAVA`; o hook não mudou. O `bin/forge-testes` só ganhou o mapa de `hooks/agentes.py` para `test_suite_paralela`.
- Textos (E3): `README.md` e `docs/hooks.md` descrevem processos que sobem e descem e batem com o script; não resta "até 4 processos" (`grep`). Os "1 a 4" que sobram são do `forge-mutante`, outro controle.
- Teto de agentes (E4): não roda no CI; é só texto no R-TETO.
- Fluxo (E5): este é o parecer de devops do fluxo normal; o PR precisa do rótulo `afrouxa-regra` do dono (aviso ao `tech-lead`).

## Custo e rollback
Custo zero (`R-CUSTO`): só biblioteca padrão, sem rede, serviço nem runner maior; os minutos de CI não sobem (mesmos jobs; no máximo menos paralelismo em runner de 2 núcleos). Rollback: `git revert` do merge na `develop` devolve o teto fixo de 4 e os textos antigos; sem migração, estado nem artefato.
