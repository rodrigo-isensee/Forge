---
tipo: revisao-seguranca
contrato: 1
pedido: v0479-aviso-versao-parada
branch: melhoria/v0479-aviso-versao-parada
commit: 1d47aa8ec5d32e91308dd65d5793279634024106
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-aviso-versao-parada

Etapa E69.4 do pedido v0478. Diff `bead3e53..1d47aa8e`: `hooks/doutor.py`, `bin/forge_versoes.py`, `README.md`, fragmento do changelog, desenho em `docs/propostas/`, testes e mutantes.

## Gatilhos
Gatilhos: hook de controle do Forge (`hooks/doutor.py`), leitura de estado fora do projeto (`~/.claude/plugins`), escrita em `.forge/run/`.

Confirmação: só aperta. O diff acrescenta um aviso novo no Stop e não remove nem enfraquece nenhuma guarda: a extração de `pasta_do_sempre_atual` (`hooks/doutor.py:186`) mantém as mesmas recusas (pasta ausente, link, não pasta, outro dono) e `avisos_do_sempre_atual` continua saindo com `[]` nelas (`hooks/doutor.py:276`); os mutantes A4 e A5 de `tests/mutantes/v047-sempre-atual-4.json` só trocam `return []` por `return None` no trecho de origem e seguem presos aos mesmos testes; `tests/test_doutor.py` só ganha linhas (212 a mais, nenhuma removida); quatro arquivos de mutantes novos.

## Achados

## Sondas

## Detalhe dos achados
Sem achado bloqueante nem recomendado. O que foi conferido:

- **R-CUSTO, rede e token:** nenhuma chamada nova de rede, subprocesso ou API no diff de `hooks/doutor.py` e `bin/forge_versoes.py` (sem `subprocess`, `urlopen`, `ls-remote` novo). A versão da `main` vem do cache `versao-nova` já gravado pela consulta diária existente; sem rede, usa a última guardada com a data (`hooks/doutor.py:263`).
- **Nenhum agente atualiza o plugin:** o aviso só monta uma frase com o comando que a pessoa roda (`bin/forge_versoes.py:167`); não há escrita em `~/.claude/plugins` nem chamada de atualização. `versao_instalada` só lê `installed_plugins.json` por `_ler_limitado` (sem seguir link, arquivo regular, teto de 1 MiB; `bin/forge_versoes.py:184`) e conta só o escopo do usuário ou o do próprio projeto.
- **Injeção na mensagem ao usuário:** tudo que entra no `systemMessage` é normalizado: causa de um conjunto fixo, versões reconstruídas de inteiros (`versao_de`), contagem de adiamentos só `int`, etapa da falha presa a `[a-z0-9-]{1,32}` (`hooks/doutor.py:211`), data presa a `AAAA-MM-DD` (`hooks/doutor.py:263`). Testes: `test_falha_sem_etapa_ou_com_etapa_estranha_nao_vai_ao_texto`, `test_data_guardada_fora_da_forma_nao_vai_ao_texto`, `test_instalada_fora_da_forma_nao_quebra`.
- **Escrita em `.forge/run/`:** a medida abre `versao-parada.log` com `O_NOFOLLOW|O_APPEND` (`hooks/doutor.py:224`), e o estado vai por `gravar_json` (temporário `O_EXCL|O_NOFOLLOW` e `os.replace`); link plantado faz `OSError`, que `principal` registra sem comer os outros avisos (`hooks/doutor.py:383`).
- **Leitura do estado da ferramenta:** só pela pasta própria validada; `registro.log` e `estado.json` por `_ler_limitado` com teto. Teste: `test_pasta_da_ferramenta_que_e_link_nao_e_lida`.
- **Supressão:** limiar constante, sem variável de ambiente que o desligue (`hooks/doutor.py:41`); estado próprio fora da forma recomeça a contagem (`test_estado_proprio_fora_da_forma_recomeca_a_contagem`), ou seja, adulterar o estado atrasa o aviso em no máximo 2 dias, sem caminho de ataque com ganho.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte: a inteira roda no CI; nesta branch ainda não há execução de CI nem PR (`gh run list --branch` vazio), e o merge depende do CI verde. Rodei só o módulo que tira a dúvida, `python3 -m unittest tests.test_doutor`: 128 testes, OK. Ferramentas: leitura estática do diff; `gitleaks` não foi necessário (o diff não traz credencial nem configuração).
