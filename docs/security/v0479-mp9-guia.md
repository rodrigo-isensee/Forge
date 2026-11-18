---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-mp9-guia
commit: 2054ef3b3ea3a7996b8e9dedbcf71fbb5782a089
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0479-mp9-guia (v0478 E24.3)

Diff lido: `0c47762a..2054ef3b` (README.md, templates/projeto/CLAUDE.md, changelog.d/v0479-mp9-guia.md, tests/test_guia_varios_projetos.py, tests/test_reval_delta.py).

## Gatilhos
Gatilhos: guarda (lista CITACOES_CONHECIDAS da reval-delta, C-2), texto que ensina escape de controle (FORGE_CARGA_LIVRE=1, R-TETO), comando que reescreve `.forge/config.json`

## Achados
- A1 (recomendado) tests/test_reval_delta.py:140 · o comentário da linha nova repete o da linha 139 (`# v047 E2.222: ...`), que não se aplica ao teste novo; apagar o segundo comentário para a lista revisada por segurança dizer só o motivo real

## Sondas

## Detalhe dos achados
- **Escape da trava de memória (README.md:47, templates/projeto/CLAUDE.md:12).** O texto bate com o código: `hooks/agentes.py:1079-1090` só aceita `FORGE_CARGA_LIVRE=1` com menos de 2 projetos no registro e recusa com registro ilegível (`ler_projetos_ativos` devolve None, `hooks/_comum.py:110`); o uso fica registrado (`registrar_escape`). O guia não amplia o escape nem ensina contorná-lo; não o apresenta como ação de agente. Sem achado.
- **Comando do `peso` (README.md:46, templates/projeto/CLAUDE.md:12).** `jq ... > .forge/config.novo && mv ...`: o `&&` impede a troca se o `jq` falhar (arquivo ausente ou JSON inválido), então não zera o config; o `.novo` que sobra num erro é inócuo. `.forge/config.json` segue sem escritor de agente (`hooks/conformidade.json:34`, `quem: []`) e o guia manda a mudança por branch e PR, do dono. Valor fora da faixa cai para 1 (`hooks/agentes.py:222-223`), o que o teste novo prende (`test_peso_do_guia_cabe_na_faixa_do_hook`). Um `peso` alto só redistribui vagas entre projetos do mesmo dono na mesma máquina: sem fronteira de confiança, sem caminho de ataque.
- **Guarda C-2 (tests/test_reval_delta.py:140).** A entrada nova `(tests/test_guia_varios_projetos.py, README.md): (1, "teste-le")` é correta: o arquivo cita `README.md` numa linha só (`tests/test_guia_varios_projetos.py:23`), é teste (o motivo `teste-le` só vale em `tests/`, conferido em `conferir_citacoes`) e a leitura só compara texto, sem decisão normativa fora do teste. A guarda não foi afrouxada: nenhuma entrada removida, contagens e `MOTIVOS` intactos. A1 é só o comentário duplicado; severidade informativa, esforço P, dono: autor da branch (doc/tech-lead).
- **Teste novo.** Carrega `hooks/agentes.py` por `spec_from_file_location` dentro do repositório; sem rede, sem escrita, sem variável de ambiente.

## Riscos aceitos e ferramentas
Sem risco aceito. Rodados localmente só o teste novo e a guarda: `python3 -m unittest tests.test_guia_varios_projetos tests.test_reval_delta.Guarda` (6 testes, OK). Suíte inteira: fica para o CI do PR. Varredura de segredos e SAST sem ferramenta no PATH (lacuna); o diff é texto e teste, sem credencial.
