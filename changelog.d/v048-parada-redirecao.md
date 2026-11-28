### Corrigido
- Vigia: a redireção de descritor para /dev/null (2>/dev/null, >/dev/null, &>/dev/null) deixa de contar como escrita e como alvo no aviso de contorno do hook de parada; a escrita no alvo barrado com ela no fim segue acusada (HOOK-PARADA-CONTA-REDIRECAO).
