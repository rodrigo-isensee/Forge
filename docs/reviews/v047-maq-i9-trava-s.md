---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-maq-i9-trava-s
commit: 07319ed9b506d894403898f7efde8e3ce08090bb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v047 (E2.679, MAQ-I9 fatia 2, TRAVA_S 1200)

## Achados
- A2 (recomendado) tests/test_pesado_fila.py:92 · `tempfile.mkdtemp` sem `addCleanup(shutil.rmtree, ...)` deixa uma pasta por teste no TMPDIR; mesmo padrão das classes já existentes no arquivo, então fica para um ajuste do arquivo inteiro

## Sondas
- S1 · tests.test_pesado_fila.TravaDeVinteMinutos.test_pid_vivo_ha_mais_de_10_min_segue_ocupado_e_vai_para_a_fila (trava de outra sessão, PID vivo, há 700 s) · espera: docs/hooks.md:14 diz que libera (mais de 10 min) · obtido: rc 2, "há 11 min", "posição 1 de 1" (segue ocupada)

## Escopo lido
Diff 73a0ab81...8bff4e7d (7 arquivos; código e teste: hooks/pesado.py 4+/2-, tests/test_pesado_fila.py 39+/1-, tests/test_forge_pesado.py 1+/1-, abaixo do teto M14). Regras "leitura" do `docs/engineering/praticas.md` que alcançam hooks/ e tests/. A frase de `docs/security/processo-pronto-develop-instancias.md` é do parecer da segurança (`R-SEGURANCA`), que a assume; não revisada aqui.

## Verificações
- Constante única: `bin/forge-pesado:102` e `hooks/agentes.py:329` importam `pesado.TRAVA_S`; nada mais copia o 600 em código. `hooks/pesado.py:114` segue com `min(hook.expira_s(), TRAVA_S)`, então `expiracao_horas` menor ainda limita (teste `test_expiracao_menor_limita_os_20_min`).
- Afrouxa-regra: a trava prende outras sessões por até 20 min com PID vivo; PID morto solta na hora (sem mudança). O destaque `afrouxa-regra` no PR é exigido pela E2.665; o PR ainda não existe (o brief pede sem PR).
- Testes novos rodados (4, OK, 2,6 s): `TravaDeVinteMinutos` (3) e `ForgePesado.test_trava_vencida_fica_livre`. Subprocesso com `ambiente_limpo()` e o filho com `-I`.
- Mutantes (`bin/forge-mutante tests/mutantes/v047-maq-i9-trava-s.json`, rev 8bff4e7dbb0a): M1 (1200→600) morreu, M2 (1200→1400) morreu. A única guarda mudada é a constante da linha 33; um mutante por direção.
- Fixture renomeado (`sem-post-expira-em-20-min.json`, `desde` agora-1300) coerente com o novo prazo.
- Suíte completa: fica no CI do PR; não rodada aqui.

## Revalidação (delta)
Achado A1 (bloqueante, resolvido em 07319ed9), registrado aqui na forma original: docs/hooks.md:14 · a referência do hook ainda diz que a trava vale "há menos de 10 minutos"; o mesmo em :72 ("a trava de tarefa pesada, em 10 minutos") e :122-123; com TRAVA_S = 1200 isso é falso. Doc afetada na mesma entrega (Definição de pronto, R-REVIEW); trocar por 20 minutos (1.200 s)
`forge-check parecer delta` lido: o delta de código e teste é só `docs/hooks.md` (4+/4-, linhas 14, 72, 122, 123), que agora diz 20 minutos (1.200 s); o resto do intervalo são os pareceres de QA e segurança. O único "10 min" que sobra em `docs/hooks.md` é o retry do hook `doutor` (linha 16), alheio à trava. A1 resolvido; A2 segue recomendado, fora do bloqueio.

## Parecer
Aprovado no head 07319ed9: código, testes e mutantes já estavam corretos e a doc de referência agora bate com TRAVA_S = 1200.
