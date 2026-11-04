---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/lote-l10
commit: effbe5b1b16cedb1c84698afcf4921c053692c48
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: versao-033, lote L10 (E14 VOLTA-ETAPA-NOVA, afrouxa; Q14 = A)

Escopo: só o delta `51ef12d..effbe5b` (o L09 tem parecer próprio): `bin/forge-check` (`ETAPA_ABERTA`, `etapas_novas_da_volta`, `fora_do_escopo_da_volta`, `gerar_volta`, `conferir_volta`), `tests/test_volta_por_delta.py`, `tests/mutantes/lote-l10.json`, `changelog.d/lote-l10.md`. Contra o modelo de ameaças `docs/security/ameacas/versao-033.md`, seção E14 (limite, C-1 a C-6, T-1 a T-3). Leitura estática e sonda local da função de decisão.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): a conferência da volta (R-BRIEF, `SECOES_COPIADAS`), com afrouxamento dentro do limite da Q14 = A. O PR precisa do rótulo `afrouxa-regra`, que só o dono aplica.

## Achados
- A1 (recomendado) bin/forge-check:1828 · a prova de abertura conta a partir da primeira linha do Histórico que cita o nome do brief anterior, qualquer que seja; um nome curto ou genérico abre a janela cedo. Amarrar a linha à forma da delegação ou exigir o nome na convenção `<pedido>-<destino>-<n>`.
- A2 (recomendado) bin/forge-check:2018 · a conferência lê `Cobre:`/`Etapa:` do brief da volta e o gerador os do anterior (`:1964`); passe à função a união dos dois, para a mesma decisão nos dois lados (C-5) mesmo se o cabeçalho da volta for editado.
- A3 (recomendado) bin/forge-check:1818 · `ETAPA_ABERTA` aceita qualquer texto depois de `aberta` (ex.: `aberta? não, cancelada`); ancorar o fim (`aberta\s*$` ou `aberta(\s+\(.*\))?$`) se o Jarvis não anota a linha.

## Detalhe dos achados
**Controles (C-n) por teste.** `BriefDeVolta.test_volta_acrescenta_so_a_etapa_aberta_depois_do_brief_anterior` (`tests/test_volta_por_delta.py:855-893`):
- C-1: subtestes "linha anterior editada com acréscimo no fim", "linha anterior com espaço a mais" e "acréscimo no meio" reprovam com `bloco "Fora do escopo" difere`. O código compara as linhas antigas como prefixo exato da lista nova (`fora_do_escopo_da_volta`, `:1844-1847`).
- C-2: "texto diferente do de ## Etapas" e "a mesma etapa duas vezes" reprovam; a linha nova só vale se for chave exata do dicionário montado do `## Etapas` (`:1850`).
- C-3: "aberta antes do brief anterior", "sem prova no Histórico", "brief anterior não registrado" e "prova fora da forma" (sem data, ou com prefixo `nota:`) reprovam e o gerador não propõe a linha. A prova vem só do `## Histórico` do pedido.
- C-4: "a etapa da própria volta" (`Cobre:`) e "etapa que já estava no Entregar do anterior" reprovam. O caso "já no Fora do escopo do anterior" não tem subteste próprio, mas cai no mesmo ramo (`ja`, `:1832-1836`).
- C-5: uma função só (`etapas_novas_da_volta`) decide no gerador (`:1964`) e na conferência (`:2018`); o brief gerado e preenchido passa (rc 0). Ressalva das entradas: A2.
- C-6: os cinco abusos reprovam e o acréscimo correto de E1.4b passa.

**Mudanças proibidas (T-n) pelo diff.**
- T-1: as linhas antigas seguem byte a byte (comparação de lista de strings, sem `strip`, conjunto nem ordenação); só o que vem depois do prefixo é avaliado.
- T-2: o ramo novo é só `nome == "Fora do escopo"`; `Objetivo` e `Relatório` seguem no `elif` byte a byte, e `Decisões e restrições` não foi tocado. Subtestes T-2 provam.
- T-3: a prova é só a ordem das linhas do `## Histórico` do pedido (`ETAPA_ABERTA` depois da linha com o nome do brief); nada vem do brief da volta, do executor nem de `mtime`.

**Bypass procurado.**
- **Linha forjada "etapa <id> aberta":** `docs/pedidos/` (clone e `~/.forge-contrib`) e `docs/briefs/` são escrita só do Jarvis (`hooks/conformidade.json:48-53`); executor e revisores não as gravam. Quem pode forjar é o próprio Jarvis, que é quem o limite da Q14 confia. A forma é estrita no início (data, hora, `etapa E<n>.<n>[a-z] aberta`); `- etapa ... aberta` e `- nota: ...` não valem (subteste). A cauda é livre: A3.
- **Brief anterior com nome ambíguo:** o nome é o stem do `Volta-de:` (arquivo preso pelo sha256) e casa com borda `(?<![\w-])...(?![\w-])`; a sonda confirmou que `p-dev-10` não abre a janela de `p-dev-1`. A janela começa na primeira citação do nome; com nome curto ou genérico ela abre cedo (A1). O efeito fica limitado: a etapa ainda precisa estar em `## Etapas` e fora do Entregar/Fora do escopo do anterior.
- **Linha que parece de etapa mas traz instrução:** só é aceita a linha idêntica à gerada a partir do `## Etapas` do pedido (texto passado por `sem_controle`); texto livre ou alterado reprova (`não é etapa de ## Etapas`). Para levar instrução, ela teria de estar no próprio pedido, que é do Jarvis e já vai ao executor.
- **Pedido fora das raízes:** o pedido segue lido por `caminho_do_pedido` (`:1009`), que recusa com `PedidoFora` fora de `docs/pedidos/` das raízes (E2); o delta não abre outro caminho de leitura.
- **`Cobre:` editado na volta:** a sonda trocou `Cobre: E1.3` por `E1.9`; a E1.3 continua barrada por estar no Entregar do anterior. Resta a divergência de entradas (A2).
- **Falha fechada:** sem a linha do brief no Histórico, sem `## Histórico`, com id fora do formato ou com texto vazio de etapa, a decisão é motivo, não None, e a linha acrescentada reprova.

**A1.** Evidência: `bin/forge-check:1828-1830`. Caminho: o Jarvis grava um brief com nome curto que aparece cedo no Histórico, ou anota o nome antes da delegação; uma etapa aberta antes da delegação passa por "depois". Ganho pequeno: corta do brief da volta uma etapa que existia, mas que o anterior não citava. Severidade baixa. Correção mínima: exigir na linha de início também o `.md` ou a forma `<pedido>-<destino>-<n>`, ou a última citação em vez da primeira. Esforço P. Dono: tech-lead.
**A2.** Evidência: `bin/forge-check:1924-1925,1964` contra `:2016-2018`. Caminho: o Jarvis edita o `Cobre:` do cabeçalho da volta; a etapa coberta só fica barrada se o anterior a citar no Entregar. Severidade baixa. Correção mínima: na conferência, passar `Cobre:` e `Etapa:` do anterior e da volta e barrar os dois. Esforço P. Dono: tech-lead.
**A3.** Evidência: `bin/forge-check:1818`. Caminho: anotação humana na linha de abertura que a desmente. Severidade informativa (os pedidos reais anotam a cauda de linhas do Histórico, então ancorar o fim exige combinar a forma com o Jarvis). Esforço P. Dono: tech-lead.

**Fora do delta (informativo, sem achado):** `blocos_literais` (`:1704-1715`) ignora o conteúdo de uma segunda seção com o mesmo nome. Uma volta com um segundo `## Fora do escopo` no fim escapa da comparação byte a byte. Isso já valia antes do E14, e o conferente lê o brief inteiro. Vale um item à parte do tech-lead: seção repetida no brief reprova.

## Riscos aceitos e ferramentas
Nenhum risco aceito por este parecer. O afrouxamento é o da Q14 = A, decisão do dono, e o rótulo `afrouxa-regra` fica com ele. Testes: `python3 -I -m unittest discover -s tests -p test_volta_por_delta.py` (68 testes, OK). A sonda local de `etapas_novas_da_volta` (seis casos) rodou no scratchpad, fora do repositório. `gitleaks` e `semgrep` não estão no PATH (lacuna; o delta não traz segredo nem dependência).
