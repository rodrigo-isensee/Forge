# Migração 0.7.0

Libera o teto de agentes adaptativo (R-TETO) nos projetos que receberam `"teto_agentes": 3` do modelo da 0.5.0. Remove de `.forge/config.json` a chave `teto_agentes` somente quando ela vale exatamente `3` (o padrão antigo do modelo); qualquer outro valor, que é uma escolha do projeto, e todas as outras chaves ficam como estão. Quem quiser manter o teto fixo em 3 depois da migração, escreva `"teto_agentes": 3` de novo (o valor 3 passa a ser respeitado como escolha). Rodar de novo não muda nada.
