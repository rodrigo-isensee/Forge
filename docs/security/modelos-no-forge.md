---
tipo: revisao-seguranca
contrato: 1
pedido: modelos-no-forge
branch: melhoria/modelos-no-forge
commit: d7052be4d5b18552f527023029af762bb2cb58cf
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: modelos-no-forge (volta 2)

Escopo: a entrega inteira, `git diff 10083383448153d36b3cf05ad8402e6075414f0b d7052be4d5b18552f527023029af762bb2cb58cf`; a volta 1 foi revisada em `29872420a29449ce52785a6448158c973236ebf6` (aprovada). Volta por delta (`forge-check delta --parecer` sobre o parecer anterior): o delta de código toca só `bin/forge-testes:45-46` e `tests/test_modelos_citados.py:47-48`, além do parecer de review em `docs/reviews/`. Revisão estática, sondas numa cópia em `$TMPDIR` (`git archive` do commit revisado).

## Gatilhos
- **Controles do Forge:** texto de agente (`agents/tech-lead.md:16`, `agents/qa-engineer.md:20`), o modelo de parecer de segurança copiado para os projetos (`templates/projeto/docs/security/_modelo.md:23`) e, nesta volta, o mapa do modo dirigido do `bin/forge-testes`.

## Veredito
**Aprovado.** Nenhum achado bloqueante.

## Achados

## Detalhe dos achados
Volta 2 (o delta, pelo A1 do review anterior):

1. **Mapa do `bin/forge-testes` (`bin/forge-testes:45-46`).** A tupla `CONTEUDO` ganha `test_modelos_citados`; nada é retirado do mapa. O efeito é só alargar o conjunto dirigido para `agents/`, `skills/`, `docs/`, `stacks/` e, via `PUBLICADO`, `templates/`. O script é ferramenta de iteração, não portão (o pre-push e o CI rodam a suíte inteira, e `test_testes_tocados` vigia que nenhum portão o chame); mesmo assim, a mudança reduz a chance de verde local enganoso e não abre caminho para pular teste. Mudar o script cai em `ALTERA_O_MAPA` (suíte completa).
2. **Literais de volta (`tests/test_modelos_citados.py:47-48`).** O teste de igualdade entre o modelo da raiz e o do template passa a citar os dois caminhos como literais `RAIZ / "..."`, o que o põe de volta sob a conferência `MapaCobreOQueOsTestesLeem`; isso fecha o contorno de checagem apontado no review (R-CONFORMIDADE). O teste segue só lendo arquivos sob a raiz, sem rede, escrita nem subprocesso.
3. **Sondas na cópia:** `tests.test_modelos_citados` 3 OK; `MapaCobreOQueOsTestesLeem` OK.

Volta 1 (sem mudança desde `29872420`, reconferida pelo diff da entrega inteira): a cláusula nos agentes só acrescenta um caminho relativo dentro do repositório do Forge, sem caminho absoluto, URL nem variável de ambiente; a exigência de parecer (ADR 0004, R-REVIEW, R-QA) fica intacta; a frase nova no modelo do template está em prosa, fora do frontmatter e do bloco `## Achados`, e raiz e template seguem idênticos.

Recomendação (informativa, não bloqueia): ARCH-MODELO-CITADO (`agents/software-architect.md:20`) continua como cartão à parte; sem impacto de segurança.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, `forge-check delta`, execução local dos testes afetados numa cópia. `gitleaks` não está no PATH (lacuna registrada; a entrega não toca segredo nem credencial).
