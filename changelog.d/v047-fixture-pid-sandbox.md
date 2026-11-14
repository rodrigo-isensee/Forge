### Corrigido
- As 4 fixtures agentes/* de pid e sessão (tests/test_hooks.py) saem puladas com motivo quando o namespace de pid do pai não é legível (sandbox dos subagentes), para a prova de pré-envio da diretriz 23 poder passar; onde é legível seguem valendo e o hook não muda (E1.90, v047, 0.47.1).
