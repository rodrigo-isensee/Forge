---
tipo: review
contrato: 1
pedido: dv-5
branch: melhoria/dv-5
commit: 90014ae265c00c8129b9af1d1d465f4e828bd03f
parecer: aprovado
revisor: forge:tech-lead (outra instância)
data: 2026-10-20
---
# Review da DV-5: trava de release no `forge-check sobreposicao --ref`

Escopo: `git diff 87dbbad..90014ae` (bin/forge-check, docs/regras/R-FLUXO.md, tests/config.json, tests/test_sobreposicao_quadro.py, changelog.d/dv-5.md).

## O que conferi
- E1: `release_em_curso` só roda com `--ref` e no subcomando `sobreposicao` (`executar`); com a versão da origin/develop maior que a da origin/homolog (comparação por tupla de inteiros, não por texto) e a branch diferente de `melhoria/release-<versão da develop>`, devolve rc 1 e a mensagem com o motivo e o que fazer. Sem `--ref`, ou sem release em curso (versões iguais ou develop menor), a saída e o rc 0 são os de antes; versão ausente ou ilegível vira aviso e rc 0 (não bloqueia sem prova). Confere.
- E2: a frase entrou uma vez só, na "Fila de integração" de R-FLUXO, que é o texto único da regra; nenhum outro arquivo de agente, skill ou doc repete a frase (só o fragmento do changelog a descreve e cita R-FLUXO pelo ID). Sem duplicação de regra.
- E3: 8 testes em `TravaDeRelease` cobrem branch de fora barrada, branch da release passando (com e sem o prefixo `origin/`), release de outra versão barrada, sem release em curso, comparação numérica (0.9.0 contra 0.10.0), sem `--ref` e versão ausente ou ilegível. Testes sem rede (refs remotas criadas com `update-ref`) e determinísticos.
- E4: fragmento changelog.d/dv-5.md no formato; sem custo (R-CUSTO), sem termo de projeto (R-NEUTRO).
- Invariantes: tests/config.json só ganhou um trecho (a frase nova da R-FLUXO); nenhum saiu (o diff não tem linha removida no arquivo).
- Saída das ferramentas (rodadas por mim sobre 90014ae, sem suíte concorrente pelo pgrep do R-TETO): `python3 -m unittest tests.test_sobreposicao_quadro tests.test_forge.AntiDuplicacao tests.test_forge.Neutralidade` 27 OK; `python3 -m unittest tests.test_forge` (inclui RegrasInviolaveis) 279 OK. Suíte completa e validar-plugin: cito a prova do autor (941 OK; validar-plugin OK), sem refazer.
- Segurança: parecer próprio do security-engineer (E1.3), não refeito aqui.

## Achados

## Detalhe dos achados
- Recomendado (bin/forge-check:1130): o nome da branch só tira os prefixos `refs/heads/` e `origin/`; `--ref refs/remotes/origin/melhoria/release-<versão>` seria barrado. O erro cai do lado seguro (falso positivo, não falso negativo); tirar também `refs/remotes/origin/` é ajuste de uma linha numa próxima volta.
- Recomendado (bin/forge-check:1123): a trava lê as refs locais origin/develop e origin/homolog; com elas desatualizadas o resultado pode errar nos dois sentidos. O autor já registrou o risco; vale a frase de `git fetch` antes, no doc do integrador, ou o `forge-fechar` chamar a trava depois do seu `git ls-remote` (fora do escopo deste pedido).
