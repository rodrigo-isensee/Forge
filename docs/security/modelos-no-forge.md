---
tipo: revisao-seguranca
contrato: 1
pedido: modelos-no-forge
branch: melhoria/modelos-no-forge
commit: 29872420a29449ce52785a6448158c973236ebf6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: modelos-no-forge

Escopo: `git diff 10083383448153d36b3cf05ad8402e6075414f0b 29872420a29449ce52785a6448158c973236ebf6` (cinco arquivos: `agents/tech-lead.md`, `agents/qa-engineer.md`, `templates/projeto/docs/security/_modelo.md`, `tests/test_modelos_citados.py`, `changelog.d/modelos-no-forge.md`). Revisão estática, sem alterar a worktree além deste parecer.

## Gatilhos
- **Controles do Forge:** texto de agente (`agents/tech-lead.md:16`, `agents/qa-engineer.md:20`) e o modelo de parecer de segurança copiado para os projetos (`templates/projeto/docs/security/_modelo.md:23`).

## Veredito
**Aprovado.** Nenhum achado bloqueante.

## Achados

## Detalhe dos achados
Pontos conferidos (o foco do brief):

1. **Caminho do modelo fica dentro do repositório.** A cláusula nova em `agents/tech-lead.md:16` e `agents/qa-engineer.md:20` acrescenta só um caminho relativo (`templates/projeto/docs/<tipo>/_modelo.md`), condicionado ao repositório do próprio Forge. Não cita caminho absoluto, diretório do plugin instalado, URL nem variável de ambiente; num projeto, `templates/projeto/` não existe e vale o `docs/<tipo>/_modelo.md` local, como antes. O modelo é só referência de formato, lida pelo agente; não é executado. Não há caminho realista para um terceiro injetar um modelo: o arquivo do template é do Forge e passa pelo mesmo fluxo de branches e review.
2. **Exigência de parecer intacta.** As duas linhas só ganham o trecho entre "Modelo em" e "`forge-check docs` valida"; o frontmatter exigido pela ADR 0004, a frase de commit do parecer na branch revisada, o bloco `## Achados` e a citação de `R-REVIEW` e `R-QA` seguem iguais (o diff troca uma linha por outra que a contém inteira). Nada sai de `tests/config.json`.
3. **Formato lido por máquina inalterado.** A mudança no template de segurança é uma frase em prosa na seção "Detalhe dos achados" (`templates/projeto/docs/security/_modelo.md:23`), fora do frontmatter e do bloco `## Achados`, que são o que o `forge-check docs`, o `forge-check brief gerar --volta` e o hook de parecer leem. A frase reafirma a regra já descrita no próprio modelo (parecer aprovado deixa o bloco vazio), não a relaxa. Nenhum hook nem o `forge-check` lê o `_modelo.md` (arquivos com `_` são ignorados). Após a mudança, raiz e template são idênticos (`diff` sem saída), e o teste novo (`tests/test_modelos_citados.py:46-51`) protege essa igualdade, o que fecha a deriva entre o modelo do Forge e o que os projetos recebem.
4. **Teste novo** (`tests/test_modelos_citados.py`): só lê arquivos sob a raiz do repositório (glob fixo em `agents/` e `stacks/*/agents/`), sem rede, sem escrita, sem execução de subprocesso; o mínimo de duas citações (`:37`) evita passar vazio.

Recomendação (informativa, não bloqueia): o teste exige a cláusula só de tech-lead e qa-engineer; o `software-architect` cita um modelo sem ela, já registrado no pedido como cartão à parte (ARCH-MODELO-CITADO). Sem impacto de segurança.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, `diff` entre os dois modelos, `grep` em `hooks/` e `bin/` por leitores de `_modelo.md`. `gitleaks` não está no PATH (lacuna registrada; a entrega não toca segredo nem credencial).
