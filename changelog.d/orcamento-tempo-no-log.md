### Alterado
- O teste do orçamento de heredocs (`test_muitos_heredocs_recusam_dentro_do_orcamento`) escreve no stderr, passe ou falhe, uma linha `ORCAMENTO-TEMPO teste=… medido=…s limite=…s medida=cpu|parede forma=…` com o pior tempo medido e o limite, para o log do CI medir os testes de tempo instáveis (ORCAMENTO-TEMPO-NO-LOG).
