### Adicionado
- forge-mutante --conferir --base SHA: em segundos e sem rodar teste, confere que o trecho `de` de cada mutante das specs do diff aparece uma vez no arquivo e que a `linha_base` de cada isenta abre a condição na base (a linha que envelhece depois de um merge da develop; v047 E1.140)

### Corrigido
- forge-mutante: o .forge/run/testes.log que não se grava vira aviso em vez de derrubar a rodada, e o controle vermelho diz quando o teste declarado não está no commit da rev (v047 E1.140)
