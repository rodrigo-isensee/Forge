---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-fila-pesada-diag
commit: 20b7e6a9b6ffe29e9ce676f8082b7f69fb162afd
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 · diagnóstico da fila pesada deixar passar mais de 2 baterias (E138.5), etapa E139.6

Escopo: `docs/devops/fila-pesada-deixa-passar.md` (40 linhas) e `changelog.d/v0480-fila-pesada-diag.md`, base `0e59c446`. Item só de texto: sem código, sem guarda nova, teto H1 não se aplica; a suíte fica no CI do PR #827.

## Conferência dos quatro furos contra `hooks/pesado.py` (no head 20b7e6a9)
1. **Mesma sessão fura a trava:** confirmado. `ocupada()` (`:187-189`) devolve falso com `mesma_sessao()` (`:368-370`, mesmo pid da sessão e mesmo `agent_id`); o PreToolUse segue para `gravar_a_vez` (`:407`), que regrava a vez do projeto, e `marcar_na_maquina` guarda uma chave por projeto (`hook.run()`), então a máquina conta 1 vaga para 2 baterias. Linhas citadas batem.
2. **Segundo plano libera na hora:** confirmado pela leitura. O ramo Post (`:397-402`) solta a trava e a vez da máquina pelo `solta()` (`:182`), e o hook não lê `run_in_background` (nenhuma ocorrência no arquivo). A nota já marca o furo como inferido, sem sonda; está honesta.
3. **Trava vence antes da bateria:** confirmado. `vez_viva()` (`:192-195`) exige `agora - desde < teto`, `TRAVA_S = 1200` (`:38`). Nuance sem efeito na conclusão: em `ocupada()` o teto é `min(expira_s(), TRAVA_S)`; em `frente_parada` é o `TRAVA_S` padrão.
4. **Comando fora do padrão:** confirmado por sonda própria (abaixo). `PESADOS_DO_FORGE` (`:47`) só traz `unittest discover`, `suite-paralela`, `pre-push --suite` e os `PELOS_ARGUMENTOS`.

O descarte do PID na fila também confere: `entrar_na_fila` (`:99`) prende a senha com `flock` e `fila_viva` (`:123`) poda a de flock livre.

Sonda do revisor (`hooks/`, `env -i`, `python3 -I`, `FORGE_MAQUINA` em `$TMPDIR`), `pesado(c, PESADOS_DO_FORGE)`: `python3 -m unittest tests.test_x` False; `python3 -m unittest -v` False; `python3 -m pytest` False; laço `for ... yes` False; `python3 -m unittest discover -s tests` True (controle).

## Checklist (leitura)
Faz o que o cartão E138.5 pede (só diagnóstico, com hipóteses do cartão cobertas e descartes explicados); correção sugerida limitada a `hooks/pesado.py` e teste, sem decidir pelo dono; fragmento de changelog presente, sem editar o `CHANGELOG.md`; nada específico de projeto (`R-NEUTRO`); um commit, mensagem em Conventional Commits.

## Parecer
Aprovado. Os quatro furos batem com o código e as linhas citadas conferem; o texto separa o que a sonda prova do que é inferido. A correção vira item de código próprio, com mutante por guarda e um teste por furo.
