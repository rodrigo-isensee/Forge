---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-f3-develop-no-fim
commit: 7de82a022ae4c7b51479a7fdc87646b580153e03
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (E30.6, F3 develop só no fim, #924, volta 1 por delta)

## Gatilhos
Gatilhos: controle do Forge (bin/forge-check: `commit_vale`, `trouxe_a_base`, `inicio_da_volta`), teste de controle (tests/test_forge_check_base_igual.py, tests/test_fechar_forge_check_real.py), regra (docs/regras/R-FLUXO.md), skill de processo (skills/trabalho-em-paralelo/ritmo-e-corte.md).

## Lido
`forge-check parecer delta` de `fe299c72..7de82a02`. No domínio: bin/forge-check (914-921 `trouxe_a_base`; 950 e 957-958 no `commit_vale`; 4625-4637 `inicio_da_volta` e o uso em 10892), docs/fechamento-integrador.md (2b), docs/regras/R-FLUXO.md:26, skills/trabalho-em-paralelo/ritmo-e-corte.md:20-21, tests/test_forge_check_base_igual.py (`MergeQueDescartaABase`), tests/test_fechar_forge_check_real.py:118 (S4). Relido sem mudança: `arquivos_divergentes` (bin/forge-check:736-779), por ser a peça que o A2 passa a acionar. Fora do domínio (mutantes, test_comando_pronto, test_reval_delta, test_volta_alinhada, changelog.d): não lido.

## Estado dos achados anteriores (parecer ae389935, commit fe299c72)
- A1 (bloqueante): resolvido. Citação da skill corrigida (ritmo-e-corte.md:20); suíte 3/5 verde nas duas versões no run 45938144589 em 7de82a02.
- A2 (bloqueante): resolvido. Com `base` e o head que trouxe a base depois do parecer (merge-base com a base diferente; bin/forge-check:914-921), `fora` vazio não sai mais na linha 950: vai ao `arquivos_divergentes` filtrado pelo domínio. Falha do git em `trouxe_a_base` dá True e o merge simulado ilegível dá `desatualizado: não comparei` (linha 958): falha fechada. Provas: S2 em test_forge_check_base_igual.py:200, S3 em :207, falha em :219, S4 de ponta a ponta em test_fechar_forge_check_real.py:118 (o forge-fechar real para no passo 1, sem merge).

## O que o delta muda na segurança
**Aperta:** o merge que descarta a base (`-s ours`, conflito resolvido com o lado da branch) desatualiza review e segurança; a skill, o 2b do fechamento e a R-FLUXO dizem isso. A R-FLUXO perde a exceção "base velha" (A3 do review), alinhando o texto à ferramenta.

**Neutro:** `inicio_da_volta` (R-QA da 3ª volta) troca o ponto de comparação pela árvore de `merge-tree(inicio, merge-base(origin/<base>, head))`. A ref é a da cópia de quem confere (o Jarvis), não a do autor; o `ponto` é sempre ancestral da base real, então só se desconta o que a base de fato tirou. Conflito, git que falha ou ponto na linha de primeiro pai voltam ao `inicio` (nada se afrouxa).

**Afrouxa:** nada além do já registrado na 1ª rodada (ordem do dono de 26/11 19:31, F3; rótulo `afrouxa-regra`).

## Conferência
- CI: run 45938144589 em 7de82a02: as 10 partes da suíte, bateria (passos, python 3.14, verificações longas), instalação, teto de pulados e árvore já provada verdes. `bateria`, `bateria (pareceres)` e `catraca` em fail esperando este parecer (o log de `bateria (pareceres)` cita o último parecer de segurança não aprovado) e o rótulo; não são defeito do código.
- Testes afetados, nesta cópia em 7de82a02 com a trava b: `MergeQueDescartaABase` e `DevelopSoNoFim`, 9 testes OK.
- Sonda própria (/root/.forge-contrib/wt/v0481-sec129-sonda.py, repositórios temporários): S5 `-s ours` de base que só muda tests/: review desatualiza, segurança vale (fora do domínio, coberto pelo review); S6 merge limpo e a base anda de novo sem ser trazida: os dois valem (sem falso positivo, o simulado usa o merge-base do head); S7 `-s ours` da B1 e merge normal da B2: os dois desatualizam em hooks/h; S8 merge limpo e `git revert` do commit da base no ramo: os dois desatualizam.

## Riscos aceitos e ferramentas
Riscos aceitos: a quebra semântica sem conflito depois do merge (E8 da 0.45.6) e o afrouxamento do F3 (ordem do dono de 26/11 19:31). Nenhum risco novo. Ferramentas: leitura estática, git e sonda em Python (biblioteca padrão) sobre repositórios temporários; nada instalado.
