---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-validar-yaml-workflow
commit: 418faf58fdeccad239d75eeeaf22b41c9340db1e
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v048, validador de YAML dos workflows (E13.6), 2ª rodada (delta)

Gatilhos: CI/CD (validador dos workflows de `.github/`, que vai entrar no envio)

Delta lido (`forge-check parecer delta`): `d7a8c8f9..418faf58`. No domínio, só `scripts/validar-yaml-workflow.py` (regex de comentário, `lstat`/`S_ISREG`, teto de 1 MiB, rc 2 sem arquivos). Fora do domínio e lidos para conferir as sondas: os 6 testes novos, as duas specs de mutantes e a linha do índice. A 1ª rodada fica no git (`c088e268`).

## Estado dos achados anteriores
- A1 resolvido: `scripts/validar-yaml-workflow.py:43` (`\s#.*$` e `rstrip`). S1 refeita: 0,0002 s, 0,0002 s e 0,0005 s para N = 10000, 20000 e 40000, e 0,005 s para 400000. Teste: `test_linha_longa_de_espacos_e_linear`.
- A2 resolvido para link e arquivo especial dentro da pasta: `:72-79`. S2 refeita: rc 2, "não é arquivo regular". S3 refeita: rc 2, sem ecoar o conteúdo de fora. Teto: um arquivo de 1 MiB + 1 byte sai rc 2. Testes: `test_link_para_arquivo_especial_sai_2`, `test_link_para_fora_nao_ecoa_o_conteudo`, `test_arquivo_acima_de_1_mib_sai_2`. A variante com a pasta como link fica no A5.
- A3 resolvido: `:66-68`. Sem `.github/` e com a pasta vazia, os dois saem rc 2 com a mensagem no stderr. Teste: `test_sem_workflow_nenhum_sai_2`.

Corpus legítimo: os workflows do repositório, os do modelo de projeto e o `dependabot.yml` saem rc 0. Os 19 testes do arquivo passam neste head.

## Achados
- A4 (bloqueante) scripts/validar-yaml-workflow.py:39 · explorável: S4. O laço dos itens `- ` copia o resto da linha a cada volta, e o custo fica quadrático: uma linha de `- ` repetidos de 1 MiB (abaixo do teto) leva cerca de 46 s. É a mesma família do A1 (custo linear pedido), em código anterior ao delta
- A5 (recomendado) scripts/validar-yaml-workflow.py:64 · com `.github/workflows` versionada como link para uma pasta de fora, o glob entra nela, o `lstat` vê arquivos regulares e o conteúdo de fora vai para a saída (S5). Recusar a pasta quando ela ou `.github` forem links, com rc 2

## Sondas
- S4 · `validar("- "*n + "a: b\n")` com n = 64000, 128000, 256000 · espera: tempo linear, como em S1 (0,005 s para 400 mil caracteres) · obtido: 0,74 s, 2,98 s, 11,5 s (quadrático; cerca de 46 s em 1 MiB); com a correção do A4: 0,12 s em 1 MiB

## Detalhe dos achados
**A4.** Evidência: `scripts/validar-yaml-workflow.py:39-42`. Cada volta faz `resto[1:].lstrip()` duas vezes, e cada uma copia o resto da linha. Essas linhas não mudaram desde `d7a8c8f9`, então o achado é novo e fora do delta. Eu o deixei passar na 1ª rodada. Ele bloqueia pelo G1.2, porque a sonda S4 prova que é explorável e o requisito de custo linear era o mesmo do A1. Caminho de ataque: igual ao do A1. Quando o validador entrar no envio, uma linha de `- ` repetidos num workflow, mesclada por um PR, prende o envio de todos os contribuidores e o job do CI por até cerca de 46 s por linha. Severidade baixa (só negação de serviço do fluxo, e a linha teria de passar pelo review).

Correção mínima: andar por índice, sem copiar.
```python
        i = 0
        while resto.startswith("- ", i):
            itens = True
            j = i + 1
            while j < len(resto) and resto[j].isspace():
                j += 1
            col, i = col + j - i, j
        resto = resto[i:]
```
Conferi numa cópia que os 19 testes continuam verdes e que o corpus sai rc 0. Ela dá o mesmo resultado do head em 200 mil entradas aleatórias (alfabeto com `- `, tabulação, espaço inseparável, `:`, `#` e `|`). S4 cai para 0,12 s em 1 MiB. Teste a acrescentar: a mesma linha de S4 dentro de um orçamento de tempo, como em `test_linha_longa_de_espacos_e_linear`. Esforço P. Dono: `devops-engineer`.

**A5.** Evidência: `scripts/validar-yaml-workflow.py:64-65` (o glob segue a pasta) e `:72` (o `lstat` só olha o último componente). Repro: numa árvore temporária, `.github/workflows` como link para uma pasta de fora com `x.yml` (`segredo: token: XYZ-pasta-fora`). Sem argumento, a saída foi rc 1 e `x.yml:1: valor simples com ... token: XYZ-pasta-fora` no stdout (S5). Caminho de ataque: o git versiona esse link. Um PR que troque a pasta pelo link faz o envio e o CI ecoarem trechos de `*.yml` de fora do repositório. Severidade baixa: o PR apaga os workflows reais, o que é muito visível no review, e no CI do PR o autor já controla o código. Por isso não bloqueia. Pela regra da segurança, ele volta e é corrigido antes do merge.

Correção mínima: no ramo sem argumento, se `pasta.is_symlink()` ou `pasta.parent.is_symlink()`, imprimir no stderr e retornar 2. Teste: a pasta como link sai rc 2 sem ecoar o conteúdo. Esforço P. Dono: `devops-engineer`.

Fora destes achados: entre o `lstat` e o `open` (`:72-75`) há uma janela de troca do arquivo. Ela só serve a quem já escreve na árvore local e não dá caminho de ataque, por isso não vira achado.

Suíte: não afirmo CI verde. No momento da leitura, o CI do PR para `418faf58` tinha a suíte (5 partes) pendente e a `bateria (pareceres)` vermelha, que espera os pareceres. Rodei só os 19 testes do arquivo, as sondas S1 a S5, o corpus e a equivalência da correção do A4.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, sondas locais em árvore temporária, cronometragem de `validar()` e comparação aleatória da correção proposta com o head. O teste com FIFO ficou de fora porque o hook de conformidade barra `mkfifo` em caminho com `.git`. O `lstat` com `S_ISREG` já recusa FIFO, como mostra S2 com um dispositivo. Faltaram no PATH, como na 1ª rodada: o varredor de segredos, o SAST, os linters de workflow e o auditor de dependências. Nenhum deles mudaria o parecer: não há dependência nova nem workflow alterado.
