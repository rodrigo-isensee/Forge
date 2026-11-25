---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-docs-ok
commit: 9fa5f83278cfea50921a8fbd156766067450d354
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E14.21, #892, classe C)

Gatilhos: controle do Forge (saída do `forge-check docs`, portão dos pareceres), texto do brief dos portões (cópia do revisor).

## Conferência
Diff lido inteiro (`220ba3fa..9fa5f83`, 7 arquivos). Veredito por mudança: só aperta ou neutro.

- **`bin/forge-check:11239-11240` (neutro):** `docs: ok` sai só com `a.cmd == "docs" and not violacoes`, depois de imprimir as violações; o rc segue `1 if violacoes else 0` (`:11247`), intocado. Toda reprovação do `docs` (frontmatter, achados, sondas, pedido, diff ilegível com `--base`, `:11234` via `cmd_docs`) chega como item de `violacoes`, então nunca imprime o ok; a guarda de versão (`:11055-11057`) e uma exceção saem antes do print. Nada que barra hoje deixa de barrar.
- **Chamadores que leem a saída:** nenhum. Procurei `forge-check ... docs` e `"docs"` em listas de argv em `.githooks/` (pre-push, commit-msg), `templates/projeto/.githooks/`, `.github/workflows/ci.yml` e o do modelo, `hooks/` (o `conformidade.json:117` só lista o comando como permitido ao papel), `bin/forge-fechar` (só roda `pr`), `bin/forge_pronto.py`, a catraca e `scripts/`: nenhum decide por saída vazia; todos os usos são por rc ou por humano. Os testes que comparavam stdout vazio foram atualizados; os demais que chamam `docs` só usam stderr, `assertIn` ou a igualdade script×rápido (`tests/test_forge.py:3857`), que não muda.
- **`bin/forge-check:9731-9734` (aperta):** com etapa em `ETAPAS_DE_PARECER` (review, seguranca, qa), o brief manda criar o clone com `--revisao` (head remoto da branch, sem cair na base); o caminho passa pelo mesmo `valor_de_shell_seguro` de antes e a `branch` entra como já entrava no ramo antigo. Etapa de código mantém o texto antigo (teste `test_brief_de_parecer_cria_o_clone_de_revisao`, com o negativo da etapa `codigo`).
- **`skills/checagem-do-brief/por-tema.md:5` (aperta):** só texto, a mesma regra.

Testes rodados no `9fa5f83` (os do diff e os que tiram dúvida): `tests.test_volta_por_delta`, `tests.test_parecer_fora_do_delta`, `tests.test_forge_copia.BriefSugereACopia`, `tests.test_forge.DocsPareceresPedidoECaminho` (166 OK) e `tests.test_forge -k test_docs -k test_qa_medio` (7 OK). A suíte inteira é do CI do #892 (em andamento neste parecer; o merge depende dele verde).

Observação fora do meu domínio (estilo, ao `tech-lead`): `bin/forge-check:11241` perdeu o espaço em `gravar =not`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, grep dos chamadores e os testes acima. O clone deste parecer nasceu com o `forge-copia --revisao` da própria branch: o `forge-copia` do plugin instalado (0.47.15) ainda recusa `--revisao` (falha fechada, rc 2, sem criar cópia), o que vale até a release levar esta mudança.
