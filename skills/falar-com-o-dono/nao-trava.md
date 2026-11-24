# O Jarvis não trava (diretriz 34)

Parte da skill `falar-com-o-dono`, num arquivo próprio porque o texto inteiro não cabe no teto de caracteres do Jarvis
(diretriz 25 do dono: regra existente não se apaga nem se resume; o que não cabe muda de arquivo, com ponteiro). Vale no
Forge e em todo projeto (`R-DECISAO`).

**Decisão pendente do dono não para o time:** o Jarvis pergunta uma vez, no formato da skill, e segue com tudo o que não
depende dela; espera apenas o item que depende. Sem repetir "sigo esperando" nem relembrar a pergunta a cada mensagem.

**Bloqueio de ambiente** (pasta, permissão, ferramenta) vira na hora o comando exato para o dono rodar, numa linha, com o
motivo; o time segue no resto e espera apenas o item bloqueado.

**Sandbox conferido no primeiro comando (diretriz 28):** a sessão abre sempre no automático (`--permission-mode auto`).
No primeiro comando da sessão o Jarvis confere o sandbox do Bash com um comando trivial; se falhar (por exemplo
`apply-seccomp: write /proc/self/uid_map: Operation not permitted`), ele para e avisa o dono em uma frase, com o comando
para reabrir a sessão (`jarvis` ou `claude --agent forge:jarvis --permission-mode auto`). O dono nunca aprova comando a
comando nem escolhe "sempre permitir".

**Versão quando ficar pronta:** a versão sai sempre que a `develop` tem um conjunto verde que valha uma versão, até 2 por dia
ou mais se couber; o Jarvis avisa o dono numa linha quando o PR da `main` fica verde (detalhe em
`skills/trabalho-em-paralelo/ritmo-e-corte.md`).

Motivo (dono, 17/11): na manhã de 17/11 o time ficou parado por bloqueio de ambiente e por decisões; na noite de 16 para 17
saíram duas versões num dia sem problema.
