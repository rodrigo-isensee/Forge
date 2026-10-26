### Alterado
- pre-push: o envio de branch roda só os testes afetados pelo `bin/forge-testes` (módulo de teste mudado, filtro, mapa ou hook no diff e qualquer dúvida seguem para a suíte inteira, a única que anota a árvore verde); os bloqueios de conteúdo ficam e a bateria completa segue no CI do PR.
- pre-push: o envio dirigido vale só para `refs/heads/melhoria/*` (outra branch roda a suíte inteira) e o Python do plano e da execução roda com `-I`, para um módulo plantado em `bin/` não decidir o plano.
