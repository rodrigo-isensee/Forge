### Adicionado
- Pre-push: varredura de segredo do delta de cada ref enviada (branch e tag) com o scripts/verificar-contribuicao.sh lido da origin/develop, antes da suíte; achado recusa o envio só com arquivo e linha. O script ganha a ponta opcional e passa a ler nome com acento, espaço ou tab e linhas escondidas por .gitattributes, também no CI (I3, versão 0.37 E8).
