### Alterado
- Hooks conformidade e parecer: o código de saída `$?` deixa de ser construção não modelada; passa entre aspas duplas sempre e, fora de aspas, só sem `IFS` no texto da chamada; todo outro `$`, crase, chaves e `case` seguem recusados, e o papel só de leitura segue recusando `echo $?` (ADR 0011, emenda H1-1; afrouxa, rótulo afrouxa-regra; PN7-DOLAR-INTERROG, P-N7).
