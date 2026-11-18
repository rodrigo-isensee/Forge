---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-mp8-maquina
commit: 528cc26744ae2331c46006c638c9670b49928a77
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0479-mp8-maquina (MP8, v0478 E23.6, revalidação)

Volta por delta. Lido: `forge-check parecer delta docs/security/v0479-mp8-maquina.md`, intervalo `6ebd057c..528cc267`. No domínio, só `bin/forge-status` (`versao_do_projeto`) e `bin/forge_dono.py` (`TETO_DO_ARQUIVO`, `_ler_com_teto`, `cmd_abertas`). Fora do domínio: `changelog.d/`, `tests/test_maquina.py`, `tests/test_forge_dono.py` e mutantes. O resto do MP8 já foi lido na rodada anterior (no git, commit `6ebd057c`). Suíte: não rodada aqui (roda só no CI). Refiz só as sondas S1 e S2, num diretório temporário.

Gatilhos: controle do Forge (registro da máquina, MP2), leitura de arquivo de outro projeto (entrada não confiável)

## Achados anteriores
- A1 (recomendado), resolvido: `bin/forge-status:82` pula `.forge/versao` e `.claude-plugin/plugin.json` quando a pasta-mãe é link. S1 refeita: com `.forge -> alvo/` e `alvo/versao` contendo `segredo 9.8.7 aqui`, sai `?` (antes saía `9.8.7`). Com `.claude-plugin` em link, sai `?`. Com `.forge/versao` regular contendo `1.2.3`, sai `1.2.3`.
- A2 (recomendado), resolvido: `bin/forge_dono.py:577` lê no máximo `TETO_DO_ARQUIVO + 1` bytes (8 MB) de cada pedido e do `KANBAN.md`. Acima disso levanta `OSError`, que `cmd_abertas` já trata como ilegível. A borda está testada em `tests/test_maquina.py:423-428`. S2 refeita em processo isolado: com `docs/pedidos/g.md` de 47.400.067 bytes, `pendentes` levou 0,070 s, com pico de 24.204 KB (antes 1,08 s e 121.076 KB), e deu o aviso `g.md ilegível (OSError)`. Um pedido de exatamente 8.000.000 bytes com uma pergunta conta `1` (0,029 s, 31.840 KB).

## Detalhe
A checagem de A1 olha só a pasta-mãe imediata. Nos dois caminhos, ela é o único componente intermediário dentro do projeto; a própria `pasta` vem do registro, que só os hooks gravam. O `arq.open` de `_ler_com_teto` segue link, mas `cmd_abertas` já pula antes o arquivo com `arq.is_symlink()` e a pasta em link. FIFO não chega por git.

Observação de exatidão, não de segurança: um pedido acima do teto conta como `0` no `--maquina`, e não como `?`, porque o arquivo ilegível sai da lista (comportamento que já vale para qualquer arquivo ilegível). Pedido com mais de 8 MB não é caso realista.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática e sondas locais com a biblioteca padrão; nenhuma varredura externa. O delta não traz dependência nem workflow novos.
