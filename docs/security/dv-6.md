---
tipo: revisao-seguranca
contrato: 1
pedido: dv-6
branch: melhoria/dv-6
commit: e316b0b1665442f203bde8489531ca125594836f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-19
---
# Review de segurança: dv-6

## Gatilhos
Controle do CI (`forge-changelog conferir`, `R-SEGURANCA`). Revisão estática do diff e9c81e0..e316b0b; sem varredura de ferramenta (nada a escanear: Python sem dependência nova).

## Achados

## Detalhe dos achados
Sem achado bloqueante nem recomendado. Conferido:
- Só o ramo de fechamento ganhou exceção: `bin/forge-changelog:150-155` exige `not outras and not novos and apagados`; o PR de release continua tratado antes (`:146`), e qualquer outra combinação cai no caminho antigo.
- Fragmento apagado sem a linha no CHANGELOG reprova: `conferir_fechamento` (`:129-137`) sai com erro citando a linha; o fragmento é lido da base (`git show base:p`), então o PR não pode alterá-lo antes de apagar; fragmento ilegível ou vazio também sai com erro (`ler_fragmento`).
- Nenhum arquivo de comportamento passa sem fragmento: `outras` filtra de `mudou` (agents, skills, templates, bin, scripts, docs, .claude-plugin, hooks) só os prefixos `docs/reviews|qa|security|devops/`, que são documentação; `docs/regras/` e demais docs continuam contando. Renomear fragmento para dentro de caminho da fábrica aparece como mudança em `mudou` (`--no-renames`). Nome com espaço não é reconhecido como fragmento e cai no caminho que exige fragmento (falha fechada).
- Testes: `python3 -m unittest tests.test_changelog`, 29 OK (inclui fechamento, linha faltando, fechamento com outra mudança, fechamento com parecer).

Observação (informativa, sem caminho de ataque realista, não bloqueia): a conferência da linha é por substring no CHANGELOG.md inteiro (`:134`), não restrita à seção da versão em fechamento; um fragmento apagado cuja linha já exista em versão antiga passa. O pior efeito é perder uma entrada de changelog, que o revisor humano vê no diff; nenhum efeito sobre o comportamento da fábrica. Endurecer, se desejado, para linha inteira na seção da versão corrente.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: só leitura do diff e a suíte do changelog; sem gitleaks/zizmor (nada de segredo nem workflow no diff; ci.yml não foi alterado).
