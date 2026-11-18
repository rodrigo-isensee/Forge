---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-mp8-maquina
commit: 6ebd057c42e72eafe3b1033c3685799e9fef951e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0479-mp8-maquina (MP8, v0478 E23.3)

Escopo lido: `git diff 0c47762a..6ebd057c` (`bin/forge-status`, `docs/hooks.md`, `changelog.d/`, `tests/test_maquina.py`, mutantes) e os leitores que o diff chama: `hooks/_maquina.py:63` (`ler_regular`) e `bin/forge_dono.py:576` (`cmd_abertas`). Suíte: não rodada aqui (só no CI); rodadas só as sondas abaixo, num diretório temporário.

## Gatilhos
Gatilhos: controle do Forge (registro da máquina, MP2), leitura de arquivo de outro projeto (entrada não confiável)

## Achados
- A1 (recomendado) bin/forge-status:82 · `ler_regular` usa O_NOFOLLOW só no último componente: `.forge` (ou `.claude-plugin`) versionado como link leva a leitura para fora do projeto; sai só o primeiro X.Y.Z do arquivo (sonda S1). Recusar pasta intermediária em link.
- A2 (recomendado) bin/forge-status:94 · `pendentes` lê `docs/pedidos/*.md` e `KANBAN.md` do outro projeto sem teto de tamanho (`read_text` em `forge_dono.py:589`), ao contrário dos 4 KB da versão; 47 MB custaram 1 s e 121 MB de memória (S2). Teto por arquivo, como `TETO_DE_BYTES`.

## Sondas

## Detalhe dos achados
**Isolamento entre projetos.** A proposta (multi-projeto, seção Segurança) diz que nenhum projeto lê arquivo de outro pelo registro; o próprio MP8 (escopo `confirmado`) pede a versão e as decisões de cada projeto, o que exige ler. A entrega reduz ao mínimo: da outra pasta só sai o primeiro `X.Y.Z` (`bin/forge-status:35`, `:87`) e a contagem de linhas `aberta:` (`:95`); nenhum texto de pergunta, nome de pedido nem conteúdo atravessa. O consumidor é a mesma conta de usuário que já pode ler as duas pastas, então não há fronteira de privilégio cruzada; o que um agente do projeto A passa a ver pelo `--maquina` é versão e número, sem valor de ataque. Leio como cumprido em espírito; a docstring (`bin/forge-status:12`) registra a exceção ("Do outro projeto só se leem a versão e a contagem; nada vai à rede"). Sem rede, sem gravação, sem `git` na outra pasta.

**Saída.** Cada linha passa por `sem_controle` (C0, DEL, C1) e corte em 300 caracteres (`bin/forge-status:112-114`); `projeto` e `pasta` vêm do registro que só os hooks gravam (pasta 0700). Coberto por `tests/test_maquina.py:392` e `:402` (link na `.forge/versao` e na `docs`).

**A1.** Evidência: `hooks/_maquina.py:65` abre com `O_NOFOLLOW`, que só vale para o último componente; `bin/forge-status:80-82` monta `pasta/.forge/versao` e `pasta/.claude-plugin/plugin.json`. O git versiona link simbólico, então um repositório clonado pode trazer `.forge -> <qualquer pasta>`. Caminho: repositório de terceiro aberto numa sessão do Forge entra no registro; o dono (ou agente de outro projeto) roda `--maquina`; lê-se até 4 KB de um arquivo arbitrário legível pelo usuário e o primeiro `X.Y.Z` dele aparece como "Forge X.Y.Z". Ganho do atacante: praticamente nenhum (número de três partes, mostrado ao próprio usuário). Severidade baixa. Correção mínima: em `versao_do_projeto`, pular quando `(Path(pasta) / nome).parent.is_symlink()`, como `cmd_abertas` faz com `docs` (`forge_dono.py:583`); teste com `.forge` em link. Esforço P. Dono: tech-lead (autor do E23.1). Observação de exatidão, não de segurança: o fallback `.claude-plugin/plugin.json` vale em qualquer projeto que seja plugin, não só no clone do Forge como diz a docstring (`:78`).

**A2.** Evidência: `bin/forge_dono.py:589` (`arq.read_text`) e `:595` (KANBAN), chamados por `bin/forge-status:94` para cada projeto do registro. Caminho: repositório com um `.md` enorme em `docs/pedidos/` deixa o `--maquina` lento e pesado para o dono; FIFO não chega por git. Severidade baixa (disponibilidade local, sem trava de controle: o `--maquina` só mostra). Correção mínima: ler com teto (por exemplo `ler_regular(arq, TETO_DE_BYTES)` e tratar acima do teto como ilegível, `?`). Esforço P. Dono: tech-lead.

Provas das sondas (ambas sobre recomendação, por isso fora de `## Sondas`, que só leva prova de bloqueante): S1, projeto temporário com `.forge -> alvo/` e `alvo/versao` contendo `segredo 9.8.7 aqui`: `versao_do_projeto` devolveu `9.8.7`. S2, `docs/pedidos/g.md` de 47.400.000 bytes: `pendentes` em 1,08 s, pico de 121.076 KB.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática e sondas locais com a biblioteca padrão; nenhuma varredura externa. Sem novas dependências nem workflow no diff, então sem varredura de cadeia de suprimentos nesta entrega.
