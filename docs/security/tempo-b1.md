---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/tempo-b1
commit: b250b178dab0a1200945ac6bf8c120da1270a55b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: versao-033 (E6 TEMPO-B1, L07)

Base `2c4cbf46b1e9f7f166e6504e27f13013ead1751f`, head revisado `b250b178dab0a1200945ac6bf8c120da1270a55b`. Diff de 9 arquivos: `hooks/agentes.py` (2 linhas, só texto das mensagens de bloqueio), `bin/forge-check` (a mensagem ao conferente sai sem o bloco do texto), `agents/conferente.md`, `skills/briefs-e-conferencia/SKILL.md`, `docs/hooks.md`, fragmento do changelog e três testes.

## Gatilhos
`R-SEGURANCA`: controle do Forge (`hooks/agentes.py`, portão `R-BRIEF` da mensagem ao `forge:conferente`) e o texto do conferente que decide o veredito do brief.

## Achados
- A1 (recomendado) agents/conferente.md:43 · sem `Brief-sha256:` a mensagem curta fica só com `aviso:`; sem a cópia do texto nada liga a mensagem ao arquivo: a falta da linha deveria reprovar (o hook já a exige)
- A2 (recomendado) agents/conferente.md:16 · o texto dos dois blocos ainda separa por `BRIEF>>>`; na forma curta a junção de `modo: brief` e `modo: entrega` cai no hook (duas `Arquivo:` no cabeçalho), recusa fechada, mas o texto ficou antigo (AR-9)
- A3 (recomendado) hooks/agentes.py:254 · na forma curta o cabeçalho vai até o fim da mensagem e linhas livres além dos campos conhecidos passam; vale avaliar uma lista fechada de campos na forma curta

## Detalhe dos achados
**R-BRIEF contra a mensagem curta (o pedido do brief).** A lógica de decisão do hook não mudou: o diff em `hooks/agentes.py` troca só o texto de `bloquear` em `hooks/agentes.py:278` e `:282`; `mensagem_sem_forma` (`:213`), `hash_do_brief_diverge` (`:249`) e `ler_brief` (`:232`) são idênticos à base. Prova diferencial: os testes novos de `tests/test_agentes_hash_brief.py` (forma curta aceita nos dois modos; recusada com hash errado, arquivo ausente, fora de `docs/briefs/` e sem `modo:`) passam também com o `hooks/agentes.py` da base 2c4cbf4 (21 testes, rc=0). Logo nenhuma mensagem recusada na base passa a ser liberada: a forma curta já era aceita pela base, e o único conjunto aceito é o de antes. Falha fechada na leitura, por leitura do código: arquivo ausente (`os.lstat` levanta `OSError`, `dados=None`, bloqueia); link (o `realpath` resolve e o destino tem de estar sob `docs/briefs/` da raiz da sessão ou de `~/.forge-contrib`; link para fora recusa); caminho fora de `docs/briefs/` (recusa em `:237`); FIFO e dispositivo (`S_ISREG` antes e depois do `open`); mais de 256 KiB (recusa); hash ausente, com outra caixa ou diferente (`VALOR_DO_HASH` só minúsculo, comparação exata); `modo:` ausente (`mensagem_sem_forma`). Duas `Arquivo:` ou duas `Brief-sha256:` no cabeçalho recusam.

**O que o conferente perde lendo só do disco.** A comparação texto da mensagem contra arquivo era redundante com o hash conferido pelo hook e pelo conferente (`forge-check brief` imprime o hash do arquivo que ele lê): com a forma curta não há cópia que possa divergir, e o conferente confere exatamente os bytes que leu. A única checagem que some é o caso sem `Brief-sha256:`, hoje só aviso (A1): com a cópia, o texto ainda prendia a mensagem ao conteúdo; sem ela, não. O hook barra essa mensagem onde está ativo, por isso é recomendação. A troca do arquivo entre a conferência e a delegação continua coberta pelo `Brief-sha256:` da entrega.

- A1 · evidência `agents/conferente.md:43` · caminho: sessão sem o hook (ou hook desligado) manda a mensagem sem hash, o conferente aprova o que estiver no disco no momento da leitura · severidade baixa · correção mínima: na forma sem o bloco, a falta de `Brief-sha256:` é `forma:` e reprova · esforço P · dono `tech-lead`.
- A2 · evidência `agents/conferente.md:16` · sem caminho de ataque (a junção é recusada pelo hook) · informativa · correção mínima: dizer que na forma curta cada bloco vai em mensagem própria · esforço P · dono `tech-lead`.
- A3 · evidência `hooks/agentes.py:254` · caminho: quem monta a mensagem acrescenta texto livre depois do cabeçalho; já era possível na base, antes do `<<<BRIEF` · severidade baixa (o autor da mensagem é o Jarvis, e o conferente trata `modo:` fora do lugar como `forma: instrução ao conferente`) · correção mínima: decidir no backlog se a forma curta aceita só os campos que o `forge-check brief mensagem` imprime · esforço P · dono `tech-lead`.

PA-7 conferido: AR-5 (python sem `-I`) não se aplica, o diff não cria caminho que execute Python; AR-9 virou A2; os demais não tocam o diff.

## Riscos aceitos e ferramentas
Sem risco aceito. Testes dos arquivos tocados (D-5): `python3 -m unittest tests.test_mensagem_conferente tests.test_agentes_hash_brief tests.test_forge`, 517 testes, rc=0. Prova diferencial com o hook da base em `$TMPDIR/security-engineer-tempo-b1/dif`. Ferramentas ausentes no PATH (lacuna, não instaladas): `gitleaks`, `semgrep`, `osv-scanner`; o diff não traz segredo nem dependência, por leitura.
