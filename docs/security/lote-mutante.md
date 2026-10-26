---
tipo: revisao-seguranca
contrato: 1
pedido: lote-mutante
branch: melhoria/lote-mutante
commit: 0fb6a2cc0128c838928220be41bc16a837c3d2a0
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-26
---
# Review de segurança: lote-mutante

Pedido LOTE-MUTANTE-REV, etapa E2.1, revalidação 2 (volta 1 do autor). Diff da entrega: `b6eb84fed86e3b5289f3950b33d43a86f34343c2...0fb6a2cc0128c838928220be41bc16a837c3d2a0`; delta desde o parecer anterior (`8aaf779`, sobre `786505960a19cb0ec3ba4ae30f454031625e75c7`): `786505960a19cb0ec3ba4ae30f454031625e75c7..0fb6a2cc0128c838928220be41bc16a837c3d2a0`, lido por `forge-check delta --parecer` (`bin/forge-mutante:38`, `:212`, `:216-217`; `tests/mutantes/lote-mutante.json`; `tests/mutantes/lote-mutante-2.json`; `tests/test_forge_mutante.py:115-127`, `:321-337`; `skills/qa-testing/SKILL.md:85`; `changelog.d/lote-mutante.md:6`). Como o gatilho é controle do Forge, reli também a guarda de executor (`bin/forge-mutante:384`), que o delta não toca mas os mutantes novos cobrem.

## Gatilhos
Controle do Forge (`R-SEGURANCA`): o `forge-mutante` produz a evidência de mutantes que o QA cola no parecer e analisa uma entrada (a spec e os ids de teste). Não é portão: nenhum hook, pre-push, CI ou `forge-check` o chama. Sem segredo, rede, workflow nem dependência nova (`unicodedata` é da biblioteca padrão).

## Achados

## Detalhe dos achados
Sem bloqueante. O parecer anterior não tinha achado no bloco; as duas recomendações dele foram revalidadas por sonda (script do commit revisado, repositório de brinquedo em `$TMPDIR`):

- **R1 (`bin/forge-mutante:217`): a recusa fora da NFKC fecha U+200C e U+200D?** Não. NFKC não altera os caracteres de formato invisíveis (categoria Cf): `tests.test_a‌b` e `tests.test_a‍b` continuam válidos (`nfkc_igual=True`). Homóglifos do mesmo formato também passam: `а` cirílico e `ο` grego. A NFKC fecha o que é compatibilidade: a ligadura `ﬁ`, o `Ａ` de largura cheia, a cedilha combinada, o `²` superescrito, o sinal de Kelvin e o de Ohm são recusados agora; `ação` composta e ASCII continuam válidos; `tests` com T cirílico já era recusado pela raiz. R1 continua **informativa e aberta**, com o mesmo caminho e a mesma conclusão de antes: a evidência continua verdadeira (o teste declarado existe, passa no controle e cai no mutante), o ganho é só confundir a leitura humana, e quem escreve a spec é o próprio autor do pedido. Correção mínima (sem mudança): recusar parte com caractere de categoria `Cf` (`unicodedata.category`) ou imprimir os ids com `ascii()`. Esforço P. Dono: tech-lead. Sem `critério mudou:`: não promovo.
- **Guardas novas saem 2 sem rodar mutante?** Sim. Spec com `testes: [1]` e com `testes: [null]` sai 2 com `spec inválida; nada foi executado.`, sem Traceback e sem nenhuma linha de mutante (`bin/forge-mutante:213`, validação antes de `principal`). Sem `tests/test_*.py`, a spec sem `executor` sai 2 com `sem leitor de veredito` sozinha, e também nas ordens `com sem` e `sem com` (`bin/forge-mutante:384`, `any`, antes de `resolver` e `principal`). Os mutantes M10 a M12 de `tests/mutantes/lote-mutante-2.json` cobrem essas duas guardas, e M11 (`any` para `all`) é morto pelo caso misto.
- **R2 (`bin/forge-mutante:304`): sem teto total nem orçamento de tempo do conjunto.** Sem mudança no delta; continua informativa e aberta, como no parecer anterior (o pedido E1 é "sem subir o teto por spec", e quem roda é o operador, na própria máquina). Esforço P. Dono: tech-lead.
- **Specs `tests/mutantes/*.json` e `skills/qa-testing/SKILL.md:85`:** são dados do pedido e documentação, sem superfície nova. A frase nova da skill descreve o fatiamento `<pedido>-<n>.json` como o código o faz: mesmo `pedido` e id único no conjunto, conferido em `bin/forge-mutante:228-233`.

Achados recorrentes (`docs/engineering/achados-recorrentes.md`, PA-7): a lista está vazia; nada a conferir nem a acrescentar.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes do lote: `python3 -m unittest tests.test_forge_mutante`, 38 testes OK no commit revisado. Sondas manuais em `$TMPDIR/security-engineer-lote-mutante/`. Ferramentas ausentes no PATH (lacuna, não instaladas): gitleaks, semgrep, osv-scanner, zizmor, actionlint; o diff não toca workflow, dependência nem segredo.
