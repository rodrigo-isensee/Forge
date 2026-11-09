### Adicionado
- MAQ-I5: o `forge-check docs` recusa o parecer de QA que cita o carimbo local da suíte (`forge-suite-*.verde` ou `.dirigida` do pre-push, ou o `forge-suite-verde` da suíte paralela) numa seção de evidência ou no `## Achados`. A prova da suíte é o check-run do CI (R-QA). A seção de método que só explica que não usou o carimbo passa.
- `forge-testes --vermelho --modulos` aceita o módulo pelo nome com o pacote (`tests.test_x`), além de `test_x`; as outras grafias seguem recusadas (FORGE-TESTES-MODULOS-NOME).

### Corrigido
- As varreduras de texto de `tests/test_forge.py` (neutralidade, núcleo, anti-duplicação e IDs de regra) deixam de ler a forma compilada (`__pycache__/`, `.pyc`, `.so`), pela mesma `FORMA_COMPILADA` da catraca: um `.pyc` velho em `bin/`, `scripts/` ou `hooks/` não dá mais vermelho falso (NEUTRO-PYCACHE).
- Os testes diferenciais dos donos de heredoc em `tests/test_hooks.py` zeram os caches `lru_cache` dos hooks antes de cada lado de cada caso: a resposta guardada de outro caso não responde mais no lugar da regra (ORACULO-LIMPA-CACHE).
- O prazo estourado do `rodar` de `tests/test_hooks.py` vira `PrazoEstourado`, uma asserção: o `forge-testes --vermelho` o conta como falha na base, sem mudar a regra de prova, e o teste que espera a falha de um fixture não aceita o hook que trava (VERMELHO-TIMEOUT-FALHA, forma E5-alt).
