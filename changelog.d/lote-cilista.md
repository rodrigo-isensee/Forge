### Alterado
- Teste de ordem do CI (tests/test_ci_local.py): a bateria passa a conferir uma lista fechada do que pode rodar antes do actionlint e do zizmor (checkout e setups fixados por SHA, gate, download com checksum, passo exclusivo do commit só de parecer); qualquer outro passo antes do lint reprova (CI-LINT-LISTA-ABERTA).
