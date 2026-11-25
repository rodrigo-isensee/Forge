---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-ae2-quadro-anda
commit: f45bf805616768db672757c4896fd112fee05534
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (AE2, #875, E10.11)

Escopo: revalidação por delta, `8087e23d..f45bf805` (voltas E10.9 e E10.10). Delta lido: `forge-check parecer delta` com o que veio da `develop` fora; do domínio, só os commits da branch: `bin/forge-fechar` (`coluna_do_cartao`), `tests/test_fechar_move_cartao.py`, `tests/test_sobreposicao_quadro.py`, `skills/kanban-scrum/SKILL.md` e `movimento.md`, as specs `est-m12-*` e `v0481-ae2-quadro-anda{,-2,-4,-5}.json`, o fragmento do changelog e a resolução do conflito em `docs/fechamento-integrador.md` (merge `0fc65e4d`, as duas redações juntas, sem perda). Nenhuma linha de `bin/forge-check` mudou nos commits da branch.

## Achados
- A1 (bloqueante) tests/mutantes/v0481-ae2-quadro-anda-5.json:6 · AE33 e AE34 já existem em -4.json (as guardas do forge-fechar, E10.9); com as duas specs juntas o forge-mutante recusa: "id de mutante repetido entre as specs", rc 2, nada roda (S1). Renumere os de -5.json para AE35 a AE41.
- A2 (recomendado) bin/forge-fechar:952 · coluna_do_cartao exclui o cabeçalho mas não o separador: `Cartão: ---` (forma aceita) acha a linha `|---|...|` e o cartão `---` nasce em Pronto pelo movimento, que já exclui o separador. O filtro não é igual ao celulas_de_cartao (por leitura).

## Sondas
- S1 · sh /root/.forge-contrib/wt/_tl-v0481-ae2-sonda-s1.sh (forge-mutante -5.json -4.json --ids AE35) · espera: rc 0, AE35 morre · obtido: "spec inválida; nada foi executado. id de mutante repetido entre as specs: AE33, AE34", rc=2

## Parecer
**Reprovado** pelo A1, um defeito novo do delta: o conjunto de mutantes declarados do pedido deixa de rodar numa chamada só. A correção é só renumerar os sete ids de `-5.json` (e o fragmento do changelog que cita "AE33 a AE39").

Correções conferidas no head:
- **A1 anterior (recomendado, E10.6):** `coluna_do_cartao` lê só linha de 7 células e fora do cabeçalho; `Cartão: ID` e a linha de 6 colunas só avisam (teste novo). Resolvido para o cabeçalho; o separador ficou (A2 acima, mesma classe, recomendado).
- **E10.10:** os casos de borda saem do `SKILL.md` para `skills/kanban-scrum/movimento.md` com o mesmo conteúdo; o resumo aponta para ele. AE12 realinhado ao trecho atual; AE33 a AE39 (-5) cobrem as condições que a `--cobertura` apontava. O teste da trava confere o caminho e a causa no aviso, sem `[Errno n]`.
- **EST-M12:** trechos de M4, M7, M8, M9, M14 e M18 realinhados a uma ocorrência só, mesma troca de sentido.

Ferramentas: `forge-mutante --conferir --base 8087e23d`: "o trecho de cada spec do diff está no lugar". Rodei `-5.json` (AE33 a AE39 morreram), `-4.json --ids AE33,AE34` (morreram, `bin/forge-fechar:952`) e `-2.json --ids AE12` (morreu). Testes do item no head: `test_fechar_move_cartao` e `test_sobreposicao_quadro`, 97 OK. Sem `shellcheck` nesta máquina; o CI decide. Tamanho (H1): o delta da branch soma cerca de 8 linhas de código. Commits em Conventional Commits, em português.

CI do head: suítes 3.12 e 3.14 (partes 1 a 5), passos, verificações longas, instalação e teto de pulados verdes. Vermelhos só os que esperam: `catraca` pede o rótulo `afrouxa-regra` (mudança em `bin/forge-check`, ADR 0008, lida no log); `bateria (pareceres)` e `bateria` leem o parecer de QA ainda reprovado.
- ci: f45bf805616768db672757c4896fd112fee05534 verde
