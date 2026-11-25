---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: 4ab16b74a90aa0d9214d1a6c32764dfac9e7fe89
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E7.47, #888, revalidação por delta, 3ª volta)

Gatilhos: hook de bloqueio (`hooks/_comum.py`: `executar`, `prazo_vencido`, `registrar_sob_vigia`), R-REVIEW, R-CONFORMIDADE.

## Resumo
- Delta lido: `forge-check parecer delta` de `1d6692f5` a `4ab16b74`, sem o que veio da develop. No domínio: `hooks/_comum.py:2879-2992`, `hooks/conformidade.py:1800-1804`, a fixture renomeada (100%, sem mudança), `tests/test_hooks.py`, `tests/test_hooks_volta_corpus.py` e `tests/test_hooks_volta_propriedades.py`. Fora do domínio, lidos também: o changelog e as specs `v0481-prazo-forge-2.json` (M22), `v0481-prazo-forge-3.json`, `lote-unico-032-l31.json` e `v0478-bp1-relogio.json`. O merge `5f99d144` só resolveu conflito em `docs/hooks-fixtures.md` (`git show --remerge-diff`). A rodada E7.39 fica no git.
- **O que aperta:**
  - o prazo do vigia passa a contar da partida do processo (`idade_do_processo`, `/proc/self/stat` campo 22 contra `CLOCK_BOOTTIME`, `:2879`, `:2969`), e não de depois do Python e dos imports. O vigia arma o que resta (`:2978`) e o prazo longo rearma do mesmo `inicio`;
  - a sessão e o registro depois do prazo vencido cabem no que resta do teto prazo + 0,5 + 0,5 (`prazo_da_etapa`, `:2892`). Sem tempo, a sessão não é lida e a linha recusa (`:2927`), e o registro não roda (`:2902`). Isso fecha o A6 (o A1 do review, o hook morto aos 10 s sob carga com o merge liberando pelo FIFO).
- **O que é neutro:**
  - a docstring de `especial_no_git` agora registra as formas livres na sessão do Forge. Isso fecha o A3;
  - a idade que falha (sem `/proc`, ilegível, sem `CLOCK_BOOTTIME`, `argv[0]` de outro script) dá 0, o comportamento de antes. O `UnicodeDecodeError` é `ValueError` e também cai aí. A idade é medida pelo kernel, e o agente não a controla;
  - o teste de parede passa do FIFO no `commondir` para o FIFO no `HEAD`. Desde o #886, o `commondir` recusa logo sem esperar. O `HEAD` mantém a prova da espera, então o teste não ficou mais fraco. A asserção segue `returncode 2` e `R-REVIEW: o hook não decidiu em 7.5 s`;
  - o `LANCADOR_MEDIDO` (`test_hooks_volta_propriedades.py:37`) troca `idade_do_processo` só no teste que mede a parede de dentro do lançador. A partida real sob atraso tem prova própria (`test_hooks.py:4189`, `sleep 3` antes do `exec` do `parecer.py` de produção).
- **O que afrouxa:** só na margem. Com o prazo contado mais cedo, mais linhas chegam ao prazo vencido sob carga. Onde o prazo vencido libera por desenho, isso vale para a linha sem marcador crítico na sessão não vigiada (VIGIA-AGENTES-PESADO, `agentes` e `pesado`), que agora pode ser liberada até uma "partida" antes. Essa linha antes seria decidida por inteiro. A linha com ação crítica continua recusando. Não há caminho de ataque que libere crítica: o efeito limita a guarda de recurso, não a trava de comandos. Vai como cartão, não como achado.
- **Achados anteriores:**
  - **A6 resolvido.** Prova: os 61 testes rodados, entre eles `test_partida_lenta_recusa_o_merge_antes_do_corte` na parede real com carga de 42 a 50 em 12 núcleos, e os mutantes M14-M22 mortos.
  - **A3 resolvido** (`hooks/conformidade.py:1802-1804`).
  - **A7 resolvido.** A develop foi trazida, e o CI rodou em `4ab16b74`.
- **CI** (run 45692259103, `pull_request`, no head exato): verdes as 10 partes da suíte (3.12 e 3.14), `bateria (passos)`, `bateria (verificações longas)`, `instalação`, `teto de pulados` e `árvore já provada na develop`. `bateria (pareceres)` falhou porque falta o parecer de review aprovado em `docs/reviews/v0481-prazo-forge.md`, e o agregador `bateria` falhou por consequência. A `catraca` (run 45695828717) falhou, pelo log, por três motivos:
  1. R-CONFORMIDADE: a mudança em `hooks/_comum.py` e `hooks/conformidade.py` espera o parecer ou o rótulo;
  2. "confira no parecer": o valor esperado trocado em `test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo`, de 4,0 para 3,5, que só segue a fixture da 2ª volta. É neutro;
  3. R-QA: a guarda apagada `critico is None and evento != "PreToolUse"` (`hooks/_comum.py:2875` da base) está sem mutante declarado numa spec do diff. Ela vem de `a4d12870` (E7.23), fora deste delta, e foi reescrita na forma equivalente `recusa = evento != "PostToolUse" and (...)`, que tem mutantes (`v0480-vigia-agentes-pesado` M1, `v0481-prazo-forge` M2). O parecer não a libera: pede uma isenção com motivo na spec ou o rótulo. Vai como cartão.
- Rodados aqui:
  - `python3 -m unittest tests.test_hooks.SondaS1ComRelogioFalso tests.test_hooks.PrazoVencidoNaSessaoDoForge tests.test_hooks_volta_corpus tests.test_hooks_volta_propriedades`: 61 testes, OK, em 817 s sob carga;
  - `bin/forge-mutante tests/mutantes/v0481-prazo-forge-3.json` (M14-M21) e `--ids M22`: todos morreram;
  - `bin/forge-mutante --cobertura --base origin/develop` confirma o item 3 da catraca.

## Parecer
- ci: 4ab16b74a90aa0d9214d1a6c32764dfac9e7fe89 verde

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Ferramentas:
- `forge-check parecer delta`, `git diff`, `git show --remerge-diff` e `bin/forge-mutante` (mutantes e `--cobertura`);
- `gh pr view`, `gh run list`, `gh run view --log-failed`;
- unittest dos módulos tocados.

Nada externo. Varredor de segredos, SAST e auditor de dependências: o delta não traz dependência nem segredo.
