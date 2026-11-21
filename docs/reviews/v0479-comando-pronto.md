---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-comando-pronto
commit: 34b6bf7bf5732b299a39d22c59dbf86950536286
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0479-comando-pronto (v0478 E66.3)

Code review de COMANDO-PRONTO-NO-TEXTO (E66.1) no head 34b6bf7b; escopo lido: `git diff bead3e53..34b6bf7b` (9 arquivos, 145+/13-, 2 commits).

## Parecer
Aprovado.

- Pedido (E66, `R-BRIEF`): as citações de `forge-check anotar`, `brief mensagem` e `forge-fechar` nas três skills saem com as opções obrigatórias do `--help`; `fluxo-do-pedido` troca a citação incompleta de `brief selar` pela remissão ao passo 3 da skill. Os cortes de texto (descrição de `fluxo-do-pedido`, "(agente, CI, merge, memória)", "nesta skill") não tiram regra com ID nem frase protegida: busca dos trechos removidos em `tests/` sem resultado.
- `tests/test_comando_pronto.py`: a fonte é o `--help` de cada ferramenta, em subprocesso com ambiente limpo e `-I` (regra do papel); `--help` que falha cai em achado, não em verde. Os ramos de falha têm teste de comportamento (`test_ramos_de_falha`), há mínimo de arquivos (5) e de citações (20) (checklist 11), e exceção sem uso reprova.
- Sondas no head (cópia restaurada depois): tirar `--ref` do `forge-fechar` em `ritmo-e-corte.md:22` → "falta --ref"; somar `--inventada` em `fluxo-do-pedido/SKILL.md:13` → "opção --inventada não existe no --help"; `forge-check mensagem` em `briefs-e-conferencia/SKILL.md:16` → "sem subcomando". Os três reprovam o teste.
- `bin/forge-testes:153,246`: só a tupla `FORGE_CHECK` e uma linha do mapa; nenhuma guarda mudada, sem mutante a declarar. Peso em `tests/pesos-d4.json` presente (PR-VERDE C1). H1: 2 linhas de código fora testes e documentação.
- Rodado no head: `test_comando_pronto` (3 testes OK) e `test_anotar` (18 OK, o único teste existente alterado). `forge-testes --listar --base bead3e53`: "suíte completa (bin/forge-testes altera o mapa ou a configuração)"; a suíte inteira fica no CI do PR, obrigatório para o merge (`R-REVIEW`); não rerrodada aqui (brief: sem suíte local).
- Segurança: parecer aprovado no mesmo head (`docs/security/v0479-comando-pronto.md`, 7f0633a4), citado sem refazer.

## Achados
- A1 (recomendado) tests/test_comando_pronto.py:24 · a exceção SEM_OBRIGATORIAS deixa `forge-check escape registrar` (skills/trabalho-em-paralelo/SKILL.md:20) sem as opções obrigatórias, contra o objetivo do item; abrir cartão para caber o comando completo (ou remeter a um detalhe da skill) e tirar a exceção.
- A2 (recomendado) tests/test_comando_pronto.py:82 · `citacoes` usa `FERRAMENTA.search` e confere só o primeiro comando de cada trecho entre crases; um segundo comando no mesmo trecho passa sem conferência. Trocar por `finditer` com o resto cortado até o próximo comando.
