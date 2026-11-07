### Adicionado
- Testes da volta única com QA em paralelo: review, QA e segurança reprovados na mesma ref voltam num brief só, com todo bloqueante de cada parecer, e o QA aprovado num head anterior ao código novo sai desatualizado no `forge-check pr` (E4 EST-M6, versao-040).

### Mudado
- `R-REVIEW` passa a "Code review em toda entrega": o review corre em paralelo ao QA e à segurança, no mesmo head, e nenhuma das duas colunas é pulada; `R-SEGURANCA`, o passo 6 do Jarvis, os agentes e as skills seguem o mesmo texto. O QA continua obrigatório em toda entrega; as reprovações da mesma rodada voltam ao autor num brief único, e na rodada paralela o QA commita só o parecer (teste que achar necessário vira achado para o autor). Em `tests/config.json`, dois invariantes trocados pelas frases novas, sem afrouxar (decisão do dono 7b; E4 EST-M6, versao-040).
