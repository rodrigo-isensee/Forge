---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae4-ordens
commit: 18d6d2f4d2afd939cf66ca5f22bc3c7a2a87c8f6
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0478 (E58.73, AE4.1: `forge-check ordens` e `anotar --tipo ordem --cartao`)

Head 18d6d2f4, base 821db42e. Sem suíte local (a suíte inteira é o check-run `bateria` do PR); rodei só os módulos dos arquivos tocados.

## Achados
- A1 (recomendado) tests/test_ordens.py:48 · `Base.setUp` cria a raiz em `tempfile.mkdtemp`; com TMPDIR dentro de um repositório git (o `~/.forge-contrib` é um), `raiz_principal` aponta para ele e o KANBAN real vence: 2 falhas. Fixar a raiz do teste fora disso (mesmo vício em test_decisoes).

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
