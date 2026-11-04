### Corrigido
- Hook `conformidade`: o corpo da crase sai como o bash o lê (tira a barra de `\\`, `` \` `` e `\$`), além da leitura antiga; a crase aninhada em três níveis, que passava com rc 0 (`gh repo delete` e o rótulo `afrouxa-regra` no fundo), chega ao teto de profundidade e recusa (SEGMENTO-CRASE-HOOK).
