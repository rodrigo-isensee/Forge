---
tipo: revisao-seguranca
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-modelo-seguranca
commit: 4b78a54b4ebb700a9c0ac78181b24aff057385e4
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: melhorias-de-projeto-1311 (item 9, migração 0.47.1)

Head revisado 4b78a54b. Escopo: `migrations/0.47.1/migrar`, `LEIA.md` e os testes novos. Diff contra a develop, 4 arquivos.

## Gatilhos
`R-SEGURANCA`: código que escreve no sistema de arquivos de um projeto de terceiros (a migração roda pelo `forge-upgrade` em repositório clonado, que pode trazer links simbólicos versionados).

## Achados
- A1 (bloqueante) migrations/0.47.1/migrar:13 · a cópia segue link simbólico: `docs/security/_modelo.md` pendurado, ou `docs/security` como link para diretório de fora, faz a migração criar o arquivo fora do projeto.

## Sondas
- S1 · projeto com `docs/security/_modelo.md` -> link pendurado para `$F/criado_fora.md`; `migrar $P` · espera: nada escrito fora de `$P` · obtido: `criado docs/security/_modelo.md`, rc 0, arquivo de 3140 bytes criado em `$F/criado_fora.md`
- S2 · projeto com `docs/security` -> link para diretório `$F2` fora do projeto; `migrar $P2` · espera: nada escrito fora de `$P2` · obtido: `$F2/_modelo.md` criado (3140 bytes)

## Detalhe dos achados
**A1.** Evidência: `migrations/0.47.1/migrar:11-15`. `alvo.exists()` segue o link: se o link é pendurado, devolve falso, e a cópia (que também segue o link) cria o destino do link. `Path(argv[1]).resolve() / REL` resolve só a raiz do projeto, não `docs/security`, então o diretório-link passa pelo `mkdir(exist_ok=True)` e pela cópia. Caminho de ataque: quem publica um repositório (ou um colaborador) versiona o link; a vítima clona, a cópia fica limpa (exigência do `forge-upgrade`) e roda a atualização; o Forge cria no destino escolhido pelo atacante um arquivo com o conteúdo fixo do modelo. Sobrescrever arquivo existente não é possível (link para existente cai no `exists()`), e o conteúdo não é controlado pelo atacante; por isso a severidade é baixa a média (criação de arquivo fora do projeto, por exemplo em local que o usuário ou uma ferramenta lê), mas é o requisito pedido na entrega ("não segue link simbólico para fora do projeto") e foi provado.
Correção mínima: usar `os.path.lexists(alvo)` (ou `alvo.is_symlink()`) para pular quando algo já está no caminho e recusar quando `alvo.parent.resolve()` não ficar dentro de `projeto.resolve()`; criar o arquivo com abertura exclusiva (`O_CREAT|O_EXCL|O_NOFOLLOW`) em vez de copiar sobre o caminho. Acrescentar dois testes (link pendurado e diretório-link) que esperam nada fora do projeto. Esforço P. Dono: tech-lead (autor da migração).

## Conferido sem achado
- Não sobrescreve: modelo existente (arquivo comum, ou link para arquivo existente) é preservado; teste `test_atualizacao_nao_sobrescreve_o_modelo_do_projeto` passa.
- Idempotente: segunda execução sem saída e sem mudança (`test_migracao_repetida_nao_muda_nada`).
- Origem da cópia: `templates/projeto/docs/security/_modelo.md` dentro do plugin, caminho fixo, sem entrada do usuário no nome do arquivo.
- Argumento do projeto vem do `forge-upgrade`, que já o resolve; sem execução de shell, sem rede.
- Os 5 testes novos (`ModeloDeSegurancaNoProjeto`) rodados no head: 5 OK. A suíte inteira fica no CI (não há PR aberto para a branch).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sem ferramenta de varredura necessária (script curto, revisão manual e sondas locais).
