### Corrigido
- tests: o teste das checagens baratas do pre-push prova que o hook não espera a trava pelo estado dela (o flock de fora ainda segura quando o hook volta), sem teto fixo de 15 s que reprovava com a máquina carregada (v047 E2.303)
