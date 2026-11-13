---
tipo: revisao-seguranca
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-modelo-seguranca
commit: c734a22a012c8564c2c65e354e3401aa5394ae39
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: melhorias-de-projeto-1311 (item 9, migração 0.47.1), revalidação por delta

Head revisado c734a22a; parecer anterior em 4b78a54b (reprovado, A1). Delta lido por `forge-check parecer delta`: só `migrations/0.47.1/migrar` está no domínio; o spec de mutantes e `tests/test_forge.py` ficam fora dele (rodei os testes novos mesmo assim).

## Gatilhos
`R-SEGURANCA`: código que escreve no sistema de arquivos de um projeto de terceiros (migração rodada pelo `forge-upgrade`).

## Achados

## Resolução do A1 anterior
Corrigido em `migrations/0.47.1/migrar:23-31`; nenhum achado novo, bloqueante ou recomendado.

## Sondas de revalidação (reproduzidas no head)
- link pendurado no modelo: recusado, rc 1, nada criado fora do projeto.
- `docs/security` como link para diretório de fora: recusado, rc 1, diretório de fora vazio.
- `docs` como link: recusado, rc 1, nada criado.
- modelo como link para arquivo existente: recusado, rc 1, arquivo de destino intacto.
- projeto sem modelo: criado (3140 bytes), segunda execução rc 0 sem mudança.
- Testes `ModeloDeSegurancaNoProjeto` (7, com os 2 novos de link): OK. A suíte inteira fica no CI (sem PR aberto).

## Desvios relatados pelo autor
- Recusar com saída 1 (em vez de pular em silêncio) também o link para arquivo existente: aceito. Falha fechada; o `forge-upgrade` (`bin/forge-upgrade:167-169`) para e manda resolver à mão na branch da atualização, sem escrever nada. Não sobrescreve nada.
- Abertura exclusiva `O_CREAT|O_EXCL|O_NOFOLLOW` com escrita de bytes lidos do template, no lugar de `shutil.copy`: aceito; cobre o último componente contra corrida. A janela entre a checagem de `docs`/`docs/security` e o `mkdir` exigiria um atacante local concorrente na máquina da vítima, sem caminho realista; não é achado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sem ferramenta de varredura necessária (script curto, revisão manual e sondas locais).
