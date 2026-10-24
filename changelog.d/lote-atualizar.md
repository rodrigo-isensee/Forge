### Corrigido
- **forge atualizar:** se algo falha depois do commit que resolve o conflito de `.forge/versao`, a mesclagem é desfeita de verdade (antes a mensagem dizia que desfez, mas a branch ficava com o merge); o teste de publicar também deixa de copiar `__pycache__`.
