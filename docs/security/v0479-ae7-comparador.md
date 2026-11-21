---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae7-comparador
commit: bb1bac50822cd077f979063a93430c28a1292977
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: AE7.1, `forge-check comparar` (v0478 E58.96), head bb1bac50

Revalidação do parecer aprovado no head caae27c4 (E58.59). A rodada anterior está no git e não é recopiada aqui.

Gatilhos: execução de comando (o comparador roda os hooks da base e do head), controle que analisa entrada (a medida do "só aperta") e a guarda C-2 de `tests/test_reval_delta.py` (controle do Forge).

## Delta lido
`forge-check parecer delta` deste arquivo (`caae27c4..bb1bac50`), com a develop separada por `git diff c9d69234 HEAD` e pelos commits da branch:
- `ce904e9c` (merge da develop `c9d69234`): `git show --remerge-diff` mostra só a resolução de `tests/pesos-d4.json`, com as duas chaves (`test_comando_pronto` 3.6 e `test_comparar` 3.8). O `bin/forge-check` e o `bin/forge-testes` que o delta lista no domínio vêm da develop: a parte da branch neles e no `bin/forge_comparar.py` é idêntica antes e depois do merge (hash das linhas +/- de `merge-base..caae27c4` igual ao de `c9d69234..HEAD`). `bin/forge_comparar.py` não muda em `caae27c4..HEAD`.
- `43b426e7`: teste novo `test_reescrita_do_caso_recusado_na_base_nao_conta`, citado pelo CMP60.
- `e90fbd6f`: o CMP102 ancora em `b".lsp.json", b"settings.json", b"monitors"` (uma ocorrência, `bin/forge_comparar.py:54`), alinhado à `RAIZ_FORA` atual.
- `bb1bac50`: um par novo em `CITACOES_CONHECIDAS` (`tests/test_reval_delta.py:140`) e o índice regenerado (`docs/indice-forge.md`, fora do domínio).

## Guarda C-2
O par novo é `("bin/forge_comparar.py", "README.md"): (1, "nome")`. Conferi a citação: `bin/forge_comparar.py:270` é a única linha com `README.md`, e ela só escreve o arquivo no projeto sintético de cada caso (`tempfile.mkdtemp` em `:269`, `write_text` em `:273`). Não lê o README do repositório nem o trata como texto normativo, e a linha não traz marcador de `LE_CONTEUDO`. A citação já existia em caae27c4 (mesma linha); o par só a registra.

O mecanismo da guarda não mudou: `MOTIVOS`, `LE_CONTEUDO`, `conferir_citacoes` e os testes (a) a (d) estão iguais; o diff de `tests/test_reval_delta.py` contra a develop é só essa entrada (+2 -1, com a vírgula da linha anterior).

Confirmação: só aperta. A guarda C-2 mantém os critérios e a contagem exata (1 linha, motivo `nome` conferido como escrita de arquivo sintético); o par registra uma citação já presente, sem abrir leitura de conteúdo. O resto do delta acrescenta um teste que mata o CMP60 e corrige a âncora do CMP102.

## Provas desta rodada
- `python3 -m unittest tests.test_reval_delta tests.test_comparar.DecisaoInteira.test_reescrita_do_caso_recusado_na_base_nao_conta`: 11 testes, OK.
- `bin/forge-mutante --ids CMP102,CMP60` nas specs 15 e 9 (rev bb1bac50822c): `CMP102 · morreu · bin/forge_comparar.py:54` e `CMP60 · morreu · bin/forge_comparar.py:285`.

## Estado dos achados anteriores
Sem achado aberto: A17 e A18 foram resolvidos em caae27c4, e o código deles não mudou.

## Riscos aceitos e ferramentas
- Riscos aceitos: nenhum.
- CI: sem PR aberto, não há CI no head. A suíte inteira fica para o CI do PR; aqui rodei só os testes do delta e os dois mutantes.
- Lacunas de ferramenta: gitleaks, osv-scanner, semgrep, zizmor e actionlint não estão no PATH. O delta não toca workflow nem dependência.
- Segredo: nenhum padrão de token ou chave nas linhas acrescidas.
