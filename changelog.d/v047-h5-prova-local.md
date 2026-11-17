### Alterado
- `forge-mutante SPEC --base SHA` roda, de cada mutante do diff, só os testes dos módulos que `forge-testes --listar` aponta para os caminhos do diff (linha `testes fora dos módulos do diff`); sem plano dirigido ou sem teste do mutante nesses módulos, os testes declarados rodam inteiros, como antes (H5-PROVA-LOCAL-POR-TESTES-TOCADOS).
