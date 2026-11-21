---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae4-ordens
commit: 768ddb9017fda505bfe54164e1b962eaffecc943
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0478 (E58.73, AE4.1: `forge-check ordens` e `anotar --tipo ordem --cartao`)

Head 916ccb02 (revalidação do aprovado em 18d6d2f4: A1 e A2 da segurança), base 821db42e. Sem suíte local (a suíte inteira é o check-run `bateria` do PR); rodei só os módulos dos arquivos tocados.

## Critério → teste → resultado
Sem especificação de UX para o pedido; as obrigações são as da etapa AE4.1 (ordem sem cartão listada; `anotar --tipo ordem` exige apontador conferido; decisões intactas).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `ordens` lista `sem-cartao:` e `sem-id:` desde a data, sem contar decisão | Listagem.test_lista_sem_cartao_e_sem_id_das_ordens_desde_a_data | `--desde`, decisão com cartão forjado, ID de cartão fechado | passou |
| Linha torta vira aviso e sai do registro | Listagem.test_ordem_torta_sai_aviso_e_fica_fora | linha sem data/dois pontos | passou |
| Sem `--desde` entra a ordem antiga | Listagem.test_sem_desde_entra_a_ordem_antiga | limite inferior de data | passou |
| `decisoes` não muda | Listagem.test_decisoes_seguem_sem_as_ordens (guarda de regressão, passa na base de propósito) | n/a | passou |
| `--cartao` obrigatório só com ordem | AnotarComCartao.test_ordem_sem_cartao_e_recusada, test_cartao_so_com_ordem | ausente e fora do tipo | passou |
| Formato do apontador | test_cartao_fora_do_formato_e_recusado | formato inválido | passou |
| Cartão tem de existir e estar aberto | test_cartao_inventado_e_recusado, test_cartao_fechado_sem_entrega_e_recusado | inexistente, fechado sem entrega | passou |
| Etapa/item do pedido vale; inventada não | test_etapa_e_item_do_pedido_valem, test_etapa_inventada_e_recusada | `E5` não casa `E51.1` | passou |
| Quadro ausente ou link simbólico não confere | test_sem_quadro_so_a_etapa_vale, test_quadro_por_link_nao_confere | sem KANBAN, symlink | passou |
| Grava `· cartão: <ID>` e a listagem a conta | test_cartao_aberto_grava_a_marca_e_a_listagem_a_conta | marca no fim da linha | passou |

## Revalidação (head 916ccb02)
Delta: `bin/forge-check` (`recusa_do_apontador` abre o KANBAN.md uma vez por `_ler_regular`, só cartão do próprio pedido), testes e specs de mutantes. O A1 do parecer anterior (raiz de teste sob repositório git) está resolvido: `git init` na raiz temporária de test_ordens e test_decisoes. Novos testes: cartão de outro pedido, FIFO sem travar, quadro acima do teto. TMPDIR fora de repositório git.

- `test_ordens` 17 testes OK; `test_anotar` 18 OK; `test_decisoes` 10 OK.
- Vermelho: `vermelho: base=821db42ed97e head=916ccb02ece5 módulos=test_ordens`; contagem: não prova (passa na base)=1 (guarda de regressão de decisões); prova (asserção)=16; rc 0.
- Mutantes, uma chamada por spec, todas rc 0, 24 de 24 mortos (M22 outro pedido, M23 coluna Pedido, M24 FIFO `(erro)` sob o mutante com o controle verde, vale como morto; M6-M8 reescritos para a nova forma).
- `forge-mutante --cobertura --base 821db42e` rc 0: `base=821db42ed97e83e2108e1b88cace186eed89da6a mb=821db42ed97e83e2108e1b88cace186eed89da6a rev=916ccb02ece58f2a21179aebdf25e6e40a894d6c`; 22 linhas `coberta`, e só `não coberto: tests/pesos-d4.json` (dados, sem guarda).

## Revalidação (head b1cd22ec)
Delta de 916ccb02 a b1cd22ec no meu domínio: `bin/forge-check` (`_ler_regular` confere `S_ISREG` por `fstat` antes do `fdopen`, e pasta no lugar do quadro recusa em vez de cair com IsADirectoryError; `recusa_do_apontador` recusa quadro com U+FFFD, fora de UTF-8), `tests/test_ordens.py` (+2 testes: `test_quadro_pasta_recusa_com_rc_2`, `test_quadro_fora_de_utf8_recusa`), spec nova `v0479-ae4-ordens-4.json` e fragmento do changelog. Cada linha de guarda nova tem mutante: M25 (bin/forge-check:4847, fstat/S_ISREG) e M26 (bin/forge-check:5043, U+FFFD).

- `test_ordens` 19 testes OK; `test_anotar` 18 OK; `test_decisoes` 10 OK (forma discover, TMPDIR fora do repositório; o `/dev/shm` do sandbox só vale dentro de cada chamada, e foi criado na própria chamada).
- Mutantes, uma chamada por spec, todas rc 0, 26 de 26 mortos: spec 1 (M1-M8), spec 2 (M9-M16), spec 3 (M17-M24, M24 `(erro)` sob o mutante com o controle verde), spec 4 (M25 morreu 4847, M26 morreu 5043).
- `forge-mutante --cobertura --base 821db42e` rc 0: `base=821db42ed97e83e2108e1b88cace186eed89da6a mb=821db42ed97e83e2108e1b88cace186eed89da6a rev=b1cd22ec7933e02b3e45af9a67d8ec25afc1dda1`; 22 linhas `coberta`, e só `não coberto: tests/pesos-d4.json` (dados, sem guarda).
- Sem bug novo. Parecer mantido: aprovado.

## Revalidação (head df0cf4d9)
Delta de b1cd22ec a df0cf4d9 no meu domínio, sem a develop (`git diff c9d69234 HEAD`): `agents/jarvis.md` (item do recibo 3 caracteres menor), `tests/mutantes/est-m12-gerar.json` (M3 e M4 alinhados à linha reindentada de `bin/forge-check`), `tests/test_anotar.py` e `tests/pesos-d4.json`; o resto do delta é a develop (c9d69234).

- `test_ordens` 19 testes OK; `test_anotar` 18 OK; `test_orcamento_instrucao` 8 OK (discover, TMPDIR fora do repositório).
- `bin/forge-mutante tests/mutantes/est-m12-gerar.json`: M1-M6 morreram (M3 em `bin/forge-check:4893`).
- Mutantes das 4 specs v0479-ae4-ordens: 26 de 26 mortos (M24 `(erro)` sob o mutante com o controle verde, vale como morto); `--cobertura --base c9d69234` sem condição descoberta; só `tests/pesos-d4.json` sai `não coberto` (dado, não guarda).
- Sem vermelho novo: nenhum teste novo no delta. Sem bug novo. Parecer mantido: aprovado.

## Revalidação (head 768ddb90)
Delta de df0cf4d9 a 768ddb90 no meu domínio (`forge-check parecer delta`, sem a develop): `agents/jarvis.md` (texto encurtado, linha "Linguagem fácil"), `bin/forge-check` (`sem_controle(alvo)` nas 4 recusas de `recusa_do_apontador`; expressões compiladas no uso), `tests/test_ordens.py`, `tests/test_decisoes.py` (`sem_manutencao`) e as 4 specs de mutantes ajustadas.

- `test_ordens` 19 OK; `test_anotar` 18 OK; `test_hooks_volta_corpus` 33 OK (discover, TMPDIR fora do repositório).
- Vermelho (`--modulos test_ordens`, base a6baf239): `vermelho: base=a6baf2390934 head=768ddb9017fd módulos=test_ordens`; `contagem: não prova (passa na base)=1; prova (asserção)=18`; rc 0. Com `test_anotar` junto sai rc 2: 7 testes erram na base porque ela não conhece o argumento `cartao` (herdados, passam no HEAD); por isso o vermelho vale só para test_ordens.
- Mutantes, uma chamada por spec, `--base df0cf4d9`: 26 de 26 mortos (M1-M8, M9-M16, M17-M24 com M24 `(erro)` sob o mutante e controle verde, M25-M26), incluindo os M4-M8 e M22-M24 na nova forma `sem_controle`.
- Sem bug novo. Parecer mantido: aprovado.

## Cenários e resultado real
Vermelho antes do verde (`TMPDIR` fora de repositório git; ver A1):

```
vermelho: base=821db42ed97e head=18d6d2f4d2af módulos=test_ordens (restrito por --modulos)
revertidos à base: agents/jarvis.md, bin/forge-check, bin/forge-testes, changelog.d/v0479-ae4-ordens.md, tests/pesos-d4.json
contagem: não prova (passa na base)=1; prova (asserção)=13   (rc 0)
```

Com TMPDIR dentro de `/root/.forge-contrib/wt/` a primeira rodada deu rc 1 (2 falhas no HEAD) por causa do A1: o KANBAN real da pasta de controle venceu o do teste. Repetida com TMPDIR fora do repositório: 14 testes ok. Não é defeito do código de produção.

Mutantes (uma chamada por spec, todos rc 0, 21 de 21 mortos):

```
spec 1 (M1-M8)   morreu: M1 5062, M2 5080, M3 5098, M4 5031, M5 5032, M6 5033, M7 5036, M8 5039
spec 2 (M9-M16)  morreu: M9 5040, M10 5042, M11 7537, M12 7537, M13 7477, M14 7854, M15 7854, M16 7863
spec 3 (M17-M21) morreu: M17 7867, M18 7889, M19 7890, M20 7891, M21 10597
```

`bin/forge-mutante --cobertura --base 821db42e` (rc 0): as 19 condições Python mudadas saem `coberta · … · declarado, não provado` (provadas pela rodada acima); a única linha sem cobertura é `não coberto: tests/pesos-d4.json`, arquivo de dados (pesos), sem guarda.

Outros módulos: `test_anotar` 18 testes OK; `test_decisoes` 10 testes OK (TMPDIR fora do repositório).

Real, só leitura: `bin/forge-check ordens --pedido v0478 --raiz-pedidos /root/.forge-contrib` rc 0, 29 linhas, fecho `ordens: sem-cartao=3 sem-id=24 com-cartao=8 encerradas=0`; as ordens antigas ainda não têm a marca, como esperado. A pasta de controle ficou sem alteração (`git status` limpo).
