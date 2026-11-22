### Corrigido
- hooks/conformidade.py: a troca de branch na linha (git switch, git checkout) só vale certa quando o operador garante que ela rodou; com ';', '||' ou '|' a branch de antes segue candidata e a de integração decide (S22: 'false && git switch -c x; git push' na main é recusado)
- hooks/conformidade.py: o resto com barra depois de $(…), crase ou variável ("$d/.", "$(echo .git)/.", "$@"/c) recusa como o literal quando o valor calculado cai no .git ou o texto que o produz o cita (A20)
