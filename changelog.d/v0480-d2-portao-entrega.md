### Adicionado
- D2 do estudo determinístico (portão de entrega do autor): patch `patches/d2-portao-entrega.patch` para o dono aplicar no `.githooks/pre-push`, com as checagens baratas do índice do Forge, do teto H1 e do texto do PR aberto (o passo pr-texto da catraca), sem teste local no envio; provado em `tests/test_pre_push_d2.py` numa cópia temporária do hook (E173.2)
