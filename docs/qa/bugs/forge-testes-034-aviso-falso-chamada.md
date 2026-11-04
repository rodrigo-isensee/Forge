# forge-testes-034-aviso-falso-chamada - aviso de MAPA dispara em teste que só passa "bin/x" como argumento
- Severidade: baixa
- Responsável sugerido: autor do bin/forge-testes (agente de desenvolvimento do Forge)
- Ambiente: melhoria/forge-testes-034 @ 1d7a02fa45244ba44dbcb2863c2029f350798c8e

## Passos para reproduzir
1. `bin/forge-testes --listar tests/test_testes_tocados.py bin/forge-testes`
2. Ou, em qualquer diff: `bin/forge-testes --listar --base b45e40aff4868a42620910e905dcda953c90d37e`

## Resultado esperado
Sem aviso: o módulo só cita `bin/forge-changelog` e `bin/forge-sugerir` como dado de teste (`self.plano("bin/forge-sugerir", ...)`, tupla `("bin/forge-changelog", ...)`), não lê o arquivo.

## Resultado obtido
Dois avisos em stderr: "lê bin/forge-changelog, mas o MAPA não leva a test_testes_tocados" (idem forge-sugerir). A forma `(` + aspas de LEITURA_DE_BIN casa qualquer chamada ou tupla com o caminho. Só ruído (o plano não muda; o teste da suíte passa), mas o autor da própria ferramenta o recebe.

## Evidência
Linhas 116 e 247 de tests/test_testes_tocados.py; regex em bin/forge-testes (LEITURA_DE_BIN). Saída idêntica à da develop, exceto essas duas linhas.
