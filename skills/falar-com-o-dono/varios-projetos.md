# Vários projetos na mesma máquina (diretriz 35)

Parte da skill `falar-com-o-dono`, num arquivo próprio porque o texto inteiro não cabe no teto de caracteres do Jarvis
(diretriz 25 do dono: o que não cabe muda de arquivo, com ponteiro). Vale no Forge e em todo projeto (`R-DECISAO`).

**Quando vale:** com mais de um projeto ativo na máquina. O sinal é o arquivo `~/.forge/maquina/projetos-ativos.json`
(`{"projetos": ["<nome>", ...]}`), que o registro da máquina (MP2) vai preencher; sem ele, ilegível ou com um nome só,
conta um projeto só e **nada muda**. O nome do projeto é o da pasta do projeto.

**Projeto no começo (MP1):** com mais de um projeto ativo, todo recibo, toda pergunta e a mensagem da manhã começam por
`Projeto: <nome>`, na primeira linha.

**Confirmar o projeto (MP1):** se a mensagem do dono cita outro projeto (nome, pasta, PR de outro repositório) ou é
ambígua, a resposta é só a pergunta "isto é para o projeto <X>?"; nada é registrado (`forge-check anotar`, cartão,
disparo) até a resposta.

**Telegram (MP7):** toda resposta pelo Telegram (`reply`) começa por `[<projeto>]`: um bot só serve a todos os projetos
(decisão do dono, 17/11). Com mais de um projeto ativo, mensagem do dono sem o nome do projeto recebe "para qual
projeto?" e não vira ação. A allowlist não muda.

**Exceção do dono (17/11):** a sessão de desenvolvimento do próprio Forge (o repositório do Forge) não confirma o
projeto nem põe prefixo (`Projeto:` ou `[<projeto>]`), porque só toca o Forge; ela continua contando no registro e no
teto da máquina (MP2 a MP5).

**Medida:** o hook `meta`, no fim de cada rodada, só mede (nunca bloqueia) e grava em `.forge/run/mensagens.jsonl`
`projetos_ativos`, `sem_projeto` (a mensagem não começa por `Projeto:`), `cita_outro_projeto` (a última fala do dono
cita outro projeto ativo) e `sem_pergunta_do_projeto` (citou e a resposta não traz "isto é para o projeto"); só
contagens, nunca o nome nem o texto. Meta: zero decisões respondidas no projeto errado.
