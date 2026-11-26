"""Testes do núcleo do FORGE-SEMPRE-ATUAL (v047, E6.4): o que o oráculo do QA (`test_oraculo_sempre_atual`) não cobre e o que ele não
exercita sobre um `/proc` de verdade (o oráculo lê a árvore do teste; `ProcReal` cobre o `/proc` da máquina). A rodada roda
dentro do processo do teste (`Rodada.executar`) com HOME, PATH e TMPDIR de um mundo temporário (os dublês do oráculo) e com `processos_de_interesse` trocado por um dublê: assim a ocupação se prova também onde o
`/proc` é de outro namespace de pid (o sandbox do Bash), sem processo `claude` de verdade.
Rodar: python3 -m unittest tests.test_sempre_atual
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

TESTES = Path(__file__).resolve().parent
RAIZ = TESTES.parent
sys.path.insert(0, str(TESTES))
sys.path.insert(0, str(RAIZ / "bin"))
import forge_sempre_atual as fsa  # noqa: E402
from ambiente_git import remoto_sem_manutencao, sem_manutencao  # noqa: E402
from test_oraculo_sempre_atual import CLAUDE_FALSO, STUB_DA_FERRAMENTA, URL, Mundo, git_real  # noqa: E402
import test_oraculo_sempre_atual as oraculo  # noqa: E402

LIVRE = {"claude": [], "fechar": [], "duvida": False}


class Dentro(Mundo):
    """Mundo do oráculo com a rodada dentro do processo."""

    def rodar_dentro(self, projeto=None, gatilho="atalho", orcamento=60, procs=None, executar=True, origem=(True, "")):
        """`origem`: o que `tag_na_main` responde (o catálogo do mundo é fictício e o `git` falso só faz `ls-remote`); None roda a
        conferência de verdade."""
        saida = io.StringIO()
        procs = procs if procs is not None else LIVRE
        dubla_origem = mock.patch.object(fsa.Rodada, "tag_na_main", lambda self, tag: origem) if origem else contextlib.nullcontext()
        with mock.patch.dict(os.environ, self.env(), clear=True), mock.patch.object(fsa, "processos_de_interesse", lambda: procs), \
                dubla_origem, contextlib.redirect_stdout(saida), contextlib.redirect_stderr(io.StringIO()):
            rodada = fsa.Rodada(gatilho, str(projeto) if projeto else None, orcamento)
            rc = rodada.executar() if executar else 0
        self.rodada, self.saida = rodada, saida.getvalue()
        return rc

    def claude_vivo(self, pasta):
        return {"claude": [str(pasta)], "fechar": [], "duvida": False}


class Funcoes(unittest.TestCase):
    def test_maior_tag_e_numerica_e_ignora_o_que_nao_e_versao(self):
        """maior_tag: 0.10.0 > 0.9.0; rc, nome solto e tag sem v não contam"""
        saida = "\n".join(f"{'a' * 40}\trefs/tags/{t}" for t in ("v0.9.0", "v0.10.0", "v9.9.9-rc1", "latest", "vfoo", "0.99.0", "v1.0"))
        self.assertEqual(fsa.maior_tag(saida), (0, 10, 0))
        self.assertIsNone(fsa.maior_tag("lixo\n"))

    def test_resumo_tira_credencial_token_e_controle(self):
        """SEG-3 · o registro nunca guarda credencial de URL nem token de forma conhecida, e cabe em 160 caracteres"""
        texto = "fatal: https://usuario:senha@host/x e ghp_abcdefghijk123 \x1b[31m\n" + "x" * 400
        saida = fsa.resumo(texto)
        self.assertNotIn("senha", saida)
        self.assertNotIn("ghp_abcdefghijk123", saida)
        self.assertNotIn("\x1b", saida)
        self.assertNotIn("\n", saida)
        self.assertLessEqual(len(saida), 160)

    def test_ambiente_dos_filhos_e_lista_positiva(self):
        """SEG-3 · só PATH, HOME e o que a rede e a língua pedem passam; GH_TOKEN, segredo qualquer e GIT_* não, nem nome novo"""
        sujo = {"GH_TOKEN": "a", "GITHUB_TOKEN": "b", "MEU_API_KEY": "c", "DB_PASSWORD": "d", "GIT_DIR": "e", "SEGREDO_NOVO": "f",
                "PATH": "/bin", "HOME": "/h", "LC_ALL": "C", "XDG_STATE_HOME": "/s", "HTTPS_PROXY": "p"}
        with mock.patch.dict(os.environ, sujo, clear=True):
            env = fsa.ambiente_dos_filhos()
        self.assertEqual(sorted(env), ["GIT_TERMINAL_PROMPT", "HOME", "HTTPS_PROXY", "LC_ALL", "PATH", "XDG_STATE_HOME"])

    def test_dentro_nao_confunde_pasta_irma(self):
        """dentro: /a/b não contém /a/bc"""
        self.assertTrue(fsa.dentro("/tmp/a/b/c", "/tmp/a/b"))
        self.assertFalse(fsa.dentro("/tmp/a/bc", "/tmp/a/b"))


class ProcReal(unittest.TestCase):
    """A leitura de produção sobre o `/proc` da máquina, sem dublê (a guarda que os testes herméticos do oráculo não exercem)."""

    def test_proc_real_e_coerente_so_no_nosso_namespace_e_enxerga_um_claude_vivo(self):
        """RD-PROC · `/proc` do nosso namespace: coerente e o `claude` vivo é achado; de outro namespace (sandbox do Bash): dúvida"""
        try:
            nosso = os.readlink("/proc/self") == str(os.getpid())  # a verdade, lida à parte da PROC de produção
        except OSError:
            nosso = False
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / "claude").symlink_to(sys.executable)  # o `comm` de quem executa o link é o nome do link
        p = subprocess.Popen([str(tmp / "claude"), "-c", "import time; time.sleep(60)"], cwd=tmp, stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(lambda: (p.kill(), p.wait()))
        for _ in range(100):  # o `comm` só vira `claude` depois do exec
            achados = fsa.processos_de_interesse()
            if achados["duvida"] or str(tmp.resolve()) in achados["claude"]:
                break
            time.sleep(0.05)
        self.assertEqual(fsa.proc_coerente(), nosso)
        if nosso:
            self.assertEqual((achados["duvida"], str(tmp.resolve()) in achados["claude"]), (False, True))
        else:
            self.assertTrue(achados["duvida"])


class ProcFalso(unittest.TestCase):
    """`processos_de_interesse` lendo uma árvore /proc de mentira."""

    def setUp(self):
        self.proc = Path(tempfile.mkdtemp(prefix="proc-falso-"))
        self.addCleanup(shutil.rmtree, self.proc, ignore_errors=True)
        os.symlink(str(os.getpid()), self.proc / "self")
        (self.proc / str(os.getpid())).mkdir()
        (self.proc / str(os.getpid()) / "comm").write_text("python3\n")
        patcher = mock.patch.object(fsa, "PROC", str(self.proc))
        patcher.start()
        self.addCleanup(patcher.stop)

    def processo(self, pid, comm, cwd, cmdline=""):
        pasta = self.proc / str(pid)
        pasta.mkdir()
        (pasta / "comm").write_text(comm + "\n")
        (pasta / "cmdline").write_bytes(cmdline.replace(" ", "\0").encode())
        if cwd is None:
            (pasta / "cwd").mkdir()  # readlink de pasta: erro que não é "sumiu"
        else:
            os.symlink(cwd, pasta / "cwd")

    def test_coerente_le_claude_fechar_e_gh_de_merge(self):
        """S2/S6 · claude, forge-fechar e gh pr merge entram; gh de outro subcomando e outros nomes não"""
        self.processo(10, "claude", "/p/a")
        self.processo(11, "forge-fechar", "/p/b")
        self.processo(12, "gh", "/p/c", "gh pr merge 3")
        self.processo(13, "gh", "/p/d", "gh pr list")
        self.processo(14, "vim", "/p/e")
        achados = fsa.processos_de_interesse()
        self.assertEqual((achados["claude"], sorted(achados["fechar"]), achados["duvida"]), (["/p/a"], ["/p/b", "/p/c"], False))

    def test_proc_incoerente_e_duvida(self):
        """decisão do Jarvis · /proc de outro namespace (self que não é o nosso pid) conta como dúvida"""
        (self.proc / "self").unlink()
        os.symlink("999999", self.proc / "self")
        self.assertTrue(fsa.processos_de_interesse()["duvida"])

    def test_proc_sem_o_nosso_comm_e_duvida(self):
        """decisão do Jarvis · o /proc que não lê o `comm` do próprio processo é incoerente"""
        (self.proc / str(os.getpid()) / "comm").unlink()
        self.assertTrue(fsa.processos_de_interesse()["duvida"])

    def test_cwd_ilegivel_de_claude_e_duvida_e_processo_que_sumiu_nao(self):
        """decisão do Jarvis · claude cujo cwd não se lê é dúvida; o que sumiu entre a listagem e a leitura é ignorado"""
        self.processo(20, "claude", None)
        self.assertTrue(fsa.processos_de_interesse()["duvida"])
        shutil.rmtree(self.proc / "20")
        self.processo(21, "claude", "/p/a")
        shutil.rmtree(self.proc / "21" / "cwd") if (self.proc / "21" / "cwd").is_dir() else (self.proc / "21" / "cwd").unlink()
        achados = fsa.processos_de_interesse()
        self.assertFalse(achados["duvida"])
        self.assertEqual(achados["claude"], [])


class Ocupacao(Dentro):
    def projeto_a_atualizar(self):
        return self.cenario_atualiza()

    def adiado(self, p, motivo):
        self.assertEqual(self.atualizacoes(), [], "atualizou com trabalho em curso")
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.0")
        self.assertIn(f"adiado:{motivo}", self.resultados("project"))

    def test_proc_incoerente_adia_mesmo_sem_claude_visivel(self):
        """decisão do Jarvis · /proc incoerente: nada se atualiza e o registro diz adiado:duvida:proc"""
        p = self.projeto_a_atualizar()
        self.rodar_dentro(p, procs={"claude": [], "fechar": [], "duvida": True})
        self.adiado(p, "duvida:proc")

    def test_agente_vigente_com_claude_vivo_adia(self):
        """RD4/S2+S3 · claude vivo no projeto e agente vigente: adia (o oráculo faz o mesmo com processo de verdade)"""
        p = self.projeto_a_atualizar()
        self.agentes(p, 2)
        self.rodar_dentro(p, procs=self.claude_vivo(p))
        self.adiado(p, "agentes")

    def test_claude_vivo_sem_trabalho_nao_adia_e_sem_claude_o_registro_velho_tambem_nao(self):
        """RD4 · fronteira: claude vivo sem agente, trava, suíte nem integração atualiza; agentes.json sem claude vivo também"""
        p = self.projeto_a_atualizar()
        self.agentes(p, 3)
        self.rodar_dentro(p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.2")
        m = self.outro()
        q = m.cenario_atualiza()
        m.rodar_dentro(q, procs=m.claude_vivo(q))
        self.assertEqual(m.versoes()[("project", str(q))], "0.47.2")

    def test_agentes_ilegivel_com_claude_vivo_e_duvida(self):
        """RD4/seção 3 · agentes.json ilegível com claude vivo conta como ocupado"""
        p = self.projeto_a_atualizar()
        (p / ".forge" / "run").mkdir(parents=True)
        (p / ".forge" / "run" / "agentes.json").write_text("{ nao e json")
        self.rodar_dentro(p, procs=self.claude_vivo(p))
        self.adiado(p, "duvida:leitura-dos-agentes")

    def test_trava_pesado_viva_adia(self):
        """RD4/S4 · trava pesado de dono vivo com claude vivo adia; trava de dono morto não"""
        p = self.projeto_a_atualizar()
        (p / ".forge" / "run").mkdir(parents=True)
        (p / ".forge" / "run" / "pesado.json").write_text(json.dumps({"desde": time.time(), "pid": os.getpid()}))
        self.rodar_dentro(p, procs=self.claude_vivo(p))
        self.adiado(p, "pesado")
        (p / ".forge" / "run" / "pesado.json").write_text(json.dumps({"desde": time.time(), "pid": 2 ** 22 + 12345}))
        self.rodar_dentro(p, procs=self.claude_vivo(p))
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.2")

    def gancho_instalado(self, corpo):
        """O `.githooks/pre-push` da cópia instalada (`GANCHO_DA_SUITE`) trocado por um script do teste, só para o `--status`."""
        gancho = self.tmp / "instalado" / ".githooks" / "pre-push"
        gancho.parent.mkdir(parents=True, exist_ok=True)
        gancho.write_text(f'[ "$1" = "--status" ] || exit 9\necho "--status $PWD" >> "{self.tmp}/status.log"\n{corpo}\n')
        return mock.patch.object(fsa, "GANCHO_DA_SUITE", gancho)

    def test_suite_rodando_adia_e_status_ilegivel_e_duvida(self):
        """RD4/S5 · o --status da cópia instalada: rc 0 adia; rc fora de 0 e 1 e arquivo ausente são dúvida e adiam; rc 1 atualiza"""
        for corpo, motivo in (('echo rodando; exit 0', "suite"), ('exit 2', "duvida:suite"), (None, "duvida:suite")):
            with self.subTest(motivo=motivo, corpo=corpo):
                m = self.outro()
                p = m.cenario_atualiza()
                with m.gancho_instalado(corpo or "exit 1") as gancho:
                    if corpo is None:
                        gancho.unlink()
                    m.rodar_dentro(p, procs=m.claude_vivo(p))
                m.adiado(p, motivo)
        m = self.outro()
        p = m.cenario_atualiza()
        with m.gancho_instalado("exit 1"):
            m.rodar_dentro(p, procs=m.claude_vivo(p))
        self.assertEqual(m.versoes()[("project", str(p))], "0.47.2")
        self.assertEqual(len((m.tmp / "status.log").read_text().splitlines()), 1, "um --status, o da cópia instalada")

    def test_pre_push_da_pasta_do_projeto_nunca_roda(self):
        """segurança A1 (S1) · `.githooks/pre-push` gravado na pasta do projeto, com claude vivo nela: a rodada não o executa"""
        p = self.projeto_a_atualizar()
        marca = self.tmp / "MARCA"
        (p / ".githooks" / "pre-push").write_text(f'#!/bin/sh\necho "$@" > "{marca}"\nexit 0\n')
        with self.gancho_instalado("exit 1"):
            self.rodar_dentro(p, procs=self.claude_vivo(p))
        self.assertFalse(marca.exists(), "o arquivo da pasta do projeto rodou fora do sandbox")
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.2")
        self.assertNotIn(str(p), (self.tmp / "status.log").read_text(), "o --status não roda com a pasta do projeto como cwd")

    def test_integracao_em_curso_adia_sem_claude(self):
        """RD4/S6 · forge-fechar com cwd no projeto adia sozinho; em outra pasta não"""
        p = self.projeto_a_atualizar()
        self.rodar_dentro(p, procs={"claude": [], "fechar": [str(p / ".forge")], "duvida": False})
        self.adiado(p, "integracao")
        m = self.outro()
        q = m.cenario_atualiza()
        m.rodar_dentro(q, procs={"claude": [], "fechar": [str(q) + "-irmao"], "duvida": False})
        self.assertEqual(m.versoes()[("project", str(q))], "0.47.2")

    def test_usuario_cobre_a_raiz_com_claude_que_nao_tem_instalacao_propria(self):
        """RD4/seção 3 · escopo de usuário adia por agente em outra raiz; raiz com instalação de projeto não o adia"""
        outra = self.projeto("outra")
        self.instalar("0.47.0", "user")
        self.publicar("0.47.0")
        self.publicar("0.47.2")
        self.definir_ref("v0.47.0")
        self.agentes(outra, 1)
        self.rodar_dentro(procs=self.claude_vivo(outra))
        self.assertEqual(self.atualizacoes(), [])
        self.assertIn("adiado:agentes", self.resultados("user"))
        m = self.outro()
        o2 = m.projeto("outra")
        m.instalar("0.47.0", "user")
        m.instalar("0.47.0", "project", o2)
        m.publicar("0.47.0")
        m.publicar("0.47.2")
        m.definir_ref("v0.47.0")
        m.agentes(o2, 1)
        m.rodar_dentro(procs=m.claude_vivo(o2))
        self.assertEqual(m.versoes()[("user", "")], "0.47.2", "a raiz com instalação própria é do escopo de projeto dela")
        self.assertIn("adiado:agentes", m.resultados("project"))

    def test_tmux_em_duvida_adia_o_escopo_que_cobre_o_projeto(self):
        """RD4/S1 · tmux que não responde no prazo é dúvida e adia; sessão aberta adia só o escopo que cobre o projeto aberto"""
        p = self.projeto_a_atualizar()
        outro = self.projeto("outro")
        self.instalar("0.47.0", "project", outro)
        self.ctl(tmux=["jarvis-p"])
        self.rodar_dentro(p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.0")
        self.assertEqual(self.versoes()[("project", str(outro))], "0.47.2", "o escopo de outro projeto não é coberto pela sessão de p")
        m = self.outro()
        q = m.cenario_atualiza()
        with mock.patch.object(fsa.Rodada, "sessao_tmux", lambda self: None):
            m.rodar_dentro(q)
        self.assertIn("adiado:duvida:tmux", m.resultados("project"))

    def test_adiamento_conta_e_zera_quando_deixa_de_adiar(self):
        """RD4/seção 3 · o contador sobe a cada adiamento seguido, guarda a data do primeiro e some quando o escopo atualiza"""
        p = self.projeto_a_atualizar()
        self.agentes(p, 1)
        for _ in range(2):
            self.rodar_dentro(p, procs=self.claude_vivo(p))
        contagem = self.estado()["adiamentos"]["project"]
        self.assertEqual(contagem["n"], 2)
        self.assertRegex(contagem["desde"], r"^\d{4}-\d\d-\d\d$")
        (p / ".forge" / "run" / "agentes.json").unlink()
        self.rodar_dentro(p, procs=self.claude_vivo(p))
        self.assertNotIn("project", self.estado()["adiamentos"])


class Ancora(Dentro):
    def test_instalacao_so_aceita_pasta_do_cache_nao_orfa(self):
        """SEG-1 · installPath órfão, fora do cache ou inexistente não vale como âncora nem como código a executar"""
        ativo = self.instalar("0.47.1", "user")
        with mock.patch.dict(os.environ, self.env(), clear=True):
            r = fsa.Rodada("atalho")
            self.assertEqual(r.instalacao(str(ativo)), str(ativo))
            (ativo / ".orphaned_at").write_text("1\n")
            self.assertIsNone(r.instalacao(str(ativo)))
            (ativo / ".orphaned_at").unlink()
            fora = self.tmp / "fora" / "0.47.1"
            self._construir(fora, "0.47.1")
            self.assertIsNone(r.instalacao(str(fora)))
            self.assertIsNone(r.instalacao(str(self.cache / "9.9.9")))
            self.assertIsNone(r.instalacao("relativo/0.47.1"))
            link = self.cache / "0.47.2"
            os.symlink(fora, link)
            self.assertIsNone(r.instalacao(str(link)))

    def test_url_vem_da_ancora_do_usuario_e_nao_da_de_projeto(self):
        """SEG-5 · com escopo de usuário, a URL é a do plugin.json dele, mesmo que o de projeto diga outra"""
        p = self.projeto("p")
        self.instalar("0.47.0", "user")
        self.instalar("0.47.1", "project", p, repository="https://example.test/outro.git")
        self.publicar("0.47.0")
        self.publicar("0.47.2")
        self.definir_ref("v0.47.0")
        self.rodar_dentro(p)
        self.assertTrue(self.adds())
        self.assertEqual({c["args"][3].partition("#")[0] for c in self.adds()}, {URL})

    def test_estado_e_a_pasta_fixa_do_forge_forge(self):
        """SEG-4 · o estado vai para plugins/data/forge-forge/forge/sempre-atual, nunca derivado de variável de ambiente"""
        p = self.cenario_atualiza()
        with mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_DATA": str(self.tmp / "outro-lugar")}):
            self.rodar_dentro(p)
        self.assertTrue((self.estado_dir / "registro.log").is_file())
        self.assertFalse((self.tmp / "outro-lugar").exists())


class Estado(Dentro):
    def test_registro_tem_sete_colunas_e_guarda_so_as_ultimas_500(self):
        """seção 5.1 · linha TSV carimbo/gatilho/escopo/projeto/antes/depois/resultado; o arquivo fica com 500 linhas"""
        p = self.cenario_atualiza()
        self.estado_dir.mkdir(parents=True, mode=0o700)
        (self.estado_dir / "registro.log").write_text("".join(f"antigo{i}\tatalho\tuser\t-\t1\t1\tem_dia\n" for i in range(600)))
        self.rodar_dentro(p)
        linhas = (self.estado_dir / "registro.log").read_text().splitlines()
        self.assertEqual(len(linhas), 500)
        ultima = linhas[-1].split("\t")
        self.assertEqual((len(ultima), ultima[1:3], ultima[3], ultima[4:]), (7, ["atalho", "project"], str(p), ["0.47.0", "0.47.2", "atualizado"]))
        self.assertEqual((self.estado_dir / "registro.log").stat().st_mode & 0o077, 0)

    def test_estado_json_privado_e_sem_sobra_de_gravacao(self):
        """SEG-4 · estado.json 0600, gravado por troca atômica (nenhum temporário sobra)"""
        self.rodar_dentro(self.cenario_atualiza())
        self.assertEqual((self.estado_dir / "estado.json").stat().st_mode & 0o777, 0o600)
        self.assertEqual(sorted(f.name for f in self.estado_dir.iterdir() if f.name.startswith(".estado")), [])
        self.assertEqual(self.estado_dir.stat().st_mode & 0o777, 0o700)

    def test_rodada_em_andamento_barra_a_segunda(self):
        """a trava de arquivo: com outra rodada viva a segunda sai sem mudar nada e sem registrar"""
        p = self.cenario_atualiza()
        self.estado_dir.mkdir(parents=True, mode=0o700)
        import fcntl
        with open(self.estado_dir / ".trava", "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            self.assertEqual(self.rodar_dentro(p), 0)
        self.assertEqual(self.mutacoes(), [])
        self.assertFalse((self.estado_dir / "registro.log").exists())

    def test_estado_corrompido_vira_estado_vazio(self):
        """estado.json que não é JSON de objeto não derruba a rodada: segue como sem estado"""
        p = self.cenario_atualiza()
        self.estado_dir.mkdir(parents=True, mode=0o700)
        (self.estado_dir / "estado.json").write_text("[1, 2")
        self.rodar_dentro(p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.2")

    def test_sem_pasta_de_plugins_nao_faz_nada(self):
        """sem ~/.claude/plugins nada a manter: sai 0, em silêncio, e não cria a pasta"""
        shutil.rmtree(self.plug)
        self.assertEqual(self.rodar_dentro(), 0)
        self.assertFalse(self.plug.exists())
        self.assertEqual(self.saida, "")


class Alvo(Dentro):
    def test_instalada_mais_nova_que_a_publicada_nao_desce_sem_fixacao(self):
        """seção 2 · versão instalada acima da maior tag (build local) não é rebaixada pelo avanço automático"""
        p = self.projeto("p")
        self.instalar("0.48.0", "project", p)
        self.publicar("0.47.2")
        self.definir_ref("v0.47.2")
        self.rodar_dentro(p)
        self.assertEqual(self.mutacoes(), [])
        self.assertEqual(self.versoes()[("project", str(p))], "0.48.0")
        self.assertIn("adiado:instalada-mais-nova-que-a-publicada", self.resultados())

    def test_fixacao_automatica_solta_com_versao_maior_que_a_quebrada(self):
        """seção 5.3 · fixação da volta segura o alvo na boa; só uma versão maior que a quebrada a solta"""
        p = self.projeto("p")
        self.instalar("0.47.1", "project", p)
        self.publicar("0.47.1")
        self.publicar("0.47.2")
        self.definir_ref("v0.47.1")
        self.semear_estado(fixacao={"motivo": "volta-automatica", "de": "0.47.2", "para": "0.47.1", "desde": "2026-11-15"},
                           bom=self.bom("0.47.1", "project", str(p)))
        self.rodar_dentro(p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.1", "a quebrada voltou")
        self.assertEqual(self.estado()["fixacao"]["para"], "0.47.1")
        self.publicar("0.47.3")
        self.rodar_dentro(p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.3")
        self.assertNotIn("fixacao", self.estado())

    def test_fixacao_malformada_e_descartada(self):
        """seção 5.3 · fixação sem versão válida não segura o alvo: cai fora e a rodada atualiza"""
        p = self.cenario_atualiza()
        self.semear_estado(fixacao={"motivo": "dono", "para": "nao-e-versao"})
        self.rodar_dentro(p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.2")
        self.assertNotIn("fixacao", self.estado())

    def test_fixacao_do_dono_avisa_uma_vez_por_versao_nova(self):
        """seção 5.3 · fixação do dono: um aviso por versão nova, sem repetir na rodada seguinte"""
        p = self.cenario_atualiza()
        self.semear_estado(fixacao={"motivo": "dono", "de": "0.47.0", "para": "0.47.0", "desde": "2026-11-01"})
        self.rodar_dentro(p)
        aviso = self.estado()["aviso"]["texto"]
        self.assertIn("0.47.2", aviso)
        self.assertIn("fixada", aviso)
        est = self.estado()
        est["aviso"]["avisado"] = True
        self.semear_estado(**est)
        self.rodar_dentro(p)
        self.assertTrue(self.estado()["aviso"]["avisado"], "avisou de novo a mesma versão")

    def test_fixacao_gravada_pelo_dono_e_respeitada_na_abertura_seguinte(self):
        """ADR 0017 item 11 · `fixar_como_dono` grava motivo dono na versão em uso; a rodada seguinte não sobe e avisa"""
        p = self.cenario_atualiza()
        with mock.patch.dict(os.environ, self.env(), clear=True):
            self.assertEqual(fsa.fixar_como_dono("0.47.0"), (True, ""))
        fix = self.estado()["fixacao"]
        self.assertEqual((fix["motivo"], fix["de"], fix["para"]), ("dono", "0.47.0", "0.47.0"))
        self.rodar_dentro(p)
        self.assertEqual(self.mutacoes(), [], "a fixação do dono segura a atualização")
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.0")
        self.assertEqual(self.estado()["fixacao"]["motivo"], "dono")
        self.assertIn("fixada", self.estado()["aviso"]["texto"])

    def test_soltar_a_fixacao_do_dono_deixa_a_rodada_atualizar_e_poupa_a_automatica(self):
        p = self.cenario_atualiza()
        with mock.patch.dict(os.environ, self.env(), clear=True):
            fsa.fixar_como_dono("0.47.0")
            self.assertEqual(fsa.soltar_fixacao_do_dono(), (True, ""))
        self.assertNotIn("fixacao", self.estado())
        self.rodar_dentro(p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.2")
        auto = {"motivo": "volta-automatica", "de": "0.47.2", "para": "0.47.1", "desde": "2026-11-01"}
        self.semear_estado(fixacao=auto)
        with mock.patch.dict(os.environ, self.env(), clear=True):
            fsa.soltar_fixacao_do_dono()
        self.assertEqual(self.estado()["fixacao"], auto)

    def test_fixar_como_dono_recusa_versao_invalida_e_estado_inexistente(self):
        with mock.patch.dict(os.environ, self.env(), clear=True):
            self.assertFalse(fsa.fixar_como_dono("nao-e-versao")[0])
        self.assertNotIn("fixacao", self.estado())
        with mock.patch.dict(os.environ, {**self.env(), "HOME": str(self.home / "sem-claude")}, clear=True):
            (self.home / "sem-claude").mkdir()
            self.assertFalse(fsa.fixar_como_dono("0.47.0")[0])

    def test_fixacao_legada_so_com_o_log_do_forge_atualizar(self):
        """seção 5.3 · catálogo com ref, sem estado e com versoes.log em que o ref não é plugin_depois: fixação do dono; sem log, passagem"""
        p = self.cenario_atualiza()
        log = self.home / ".local" / "state" / "forge"
        log.mkdir(parents=True)
        (log / "versoes.log").write_text("2026-11-01T10:00:00\toutro\t0.44.0\t0.45.0\n")
        self.rodar_dentro(p)
        self.assertEqual(self.estado()["fixacao"]["motivo"], "dono")
        self.assertEqual(self.mutacoes(), [], "a fixação do dono segura a atualização")
        m = self.outro()
        q = m.cenario_atualiza()
        (m.home / ".local" / "state" / "forge").mkdir(parents=True)
        (m.home / ".local" / "state" / "forge" / "versoes.log").write_text("2026-11-01T10:00:00\tq\t0.46.0\t0.47.0\n")
        m.rodar_dentro(q)
        self.assertEqual(m.versoes()[("project", str(q))], "0.47.2", "o ref é um plugin_depois registrado: foi só passagem")

    def test_sem_tag_publicada_registra_e_nao_mexe(self):
        """seção 2 · catálogo sem nenhuma tag vX.Y.Z: falhou:sem-tag, nada muda"""
        p = self.cenario_atualiza()
        self.ctl(tags=[])
        self.rodar_dentro(p)
        self.assertEqual(self.mutacoes(), [])
        self.assertIn("falhou:sem-tag", self.resultados())


class OrigemDaTag(Dentro):
    """segurança A2 · a tag alvo só vale com o commit dela na `main` do remoto; senão nada muda."""

    def remoto(self):
        """Remoto local com a `main`, a tag `v0.47.2` na main e a `v9.9.9` num commit fora dela."""
        origem = self.tmp / "forge-origem.git"
        git_real("init", "-q", "--bare", "-b", "main", str(origem), cwd=self.tmp)
        remoto_sem_manutencao(origem)
        semente = self.tmp / "forge-semente"
        git_real("clone", "-q", str(origem), str(semente), cwd=self.tmp)
        (semente / "x").write_text("1\n")
        git_real("add", "-A", cwd=semente)
        git_real("commit", "-q", "-m", "versao", cwd=semente)
        git_real("tag", "-a", "-m", "v0.47.2", "v0.47.2", cwd=semente)
        git_real("switch", "-q", "-c", "melhoria/x", cwd=semente)
        git_real("commit", "-q", "--allow-empty", "-m", "fora da main", cwd=semente)
        git_real("tag", "v9.9.9", cwd=semente)
        git_real("push", "-q", "origin", "main", "melhoria/x", "--tags", cwd=semente)
        return origem

    def conferir(self, tag, url):
        """`tag_na_main` de verdade contra o remoto local (o `git_rede` só troca a URL fictícia pela do remoto local)."""
        with mock.patch.dict(os.environ, {**self.env(), "PATH": os.environ["PATH"]}, clear=True):
            rodada = fsa.Rodada("atalho")
            rodada.neutro, rodada.url = tempfile.mkdtemp(dir=self.tmp), URL
            original = fsa.Rodada.git_rede

            def git_rede(r, args):
                return original(r, ["-c", "protocol.file.allow=always", *[url if a == URL else a for a in args]])

            with mock.patch.object(fsa.Rodada, "git_rede", git_rede):
                return rodada.tag_na_main(tag)

    def test_tag_na_main_vale_e_fora_dela_nao(self):
        url = "file://" + str(self.remoto())
        self.assertEqual(self.conferir("v0.47.2", url), (True, ""))
        self.assertEqual(self.conferir("v9.9.9", url), (False, "o commit da v9.9.9 não está na main"))

    def test_busca_que_falha_ou_main_ilegivel_reprova(self):
        """falha fechada · remoto sem a tag (busca falha) e tag que não é commit (merge-base com erro) reprovam"""
        origem = self.remoto()
        ok, motivo = self.conferir("v1.0.0", "file://" + str(origem))
        self.assertFalse(ok)
        self.assertTrue(motivo.startswith("busca: "), motivo)
        arvore = git_real("rev-parse", "main^{tree}", cwd=origem)
        git_real("update-ref", "refs/tags/v3.0.0", arvore, cwd=origem)
        self.assertEqual(self.conferir("v3.0.0", "file://" + str(origem)), (False, "não deu para conferir a main"))

    def test_init_que_falha_reprova(self):
        original = fsa.Rodada.rodar

        def rodar(r, argv, cwd, cap, extra=None):
            return (128, "sem disco") if argv[1:2] == ["init"] else original(r, argv, cwd, cap, extra)

        with mock.patch.object(fsa.Rodada, "rodar", rodar):
            self.assertEqual(self.conferir("v0.47.2", "file://" + str(self.remoto())), (False, "init: sem disco"))

    def test_busca_no_prazo_esgotado_reprova(self):
        with mock.patch.object(fsa.Rodada, "git_rede", lambda r, args: (None, "prazo do passo")):
            rodada = fsa.Rodada("atalho")
            rodada.neutro, rodada.url = tempfile.mkdtemp(dir=self.tmp), URL
            self.assertEqual(rodada.tag_na_main("v0.47.2"), (False, "prazo"))

    def test_tag_fora_da_main_nada_muda(self):
        """o avanço com a origem reprovada: nenhum `add`, versão igual, registro falhou:origem-da-tag"""
        p = self.cenario_atualiza()
        self.rodar_dentro(p, origem=(False, "o commit da v0.47.2 não está na main"))
        self.assertEqual(self.adds(), [])
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.0")
        self.assertTrue(any(r.startswith("falhou:origem-da-tag") for r in self.resultados("project")), self.resultados())

    def test_volta_com_origem_reprovada_nao_mexe_no_catalogo(self):
        """seção 5.2 · a volta também confere a origem: reprovada, nenhum `add` da última boa e o registro diz volta-falhou"""
        p = self.projeto("p")
        self.instalar("0.47.1", "user")
        self.publicar("0.47.1")
        self.publicar("0.47.2", py_quebrado=True)
        self.definir_ref("v0.47.1")
        self.semear_estado(bom=self.bom("0.47.1"))
        with mock.patch.object(fsa.Rodada, "tag_na_main", lambda r, tag: (tag != "v0.47.1", "fora da main")):
            self.rodar_dentro(p, origem=None)
        self.assertEqual([c["args"][3] for c in self.adds()], [f"{URL}#v0.47.2"])
        self.assertIn("volta-falhou", self.resultados("user"))


class Catalogo(Dentro):
    def test_update_so_depois_de_o_ref_lido_ser_o_alvo(self):
        """catalogo/seção 11 · add que sai 0 sem mudar o ref (interrompido) não libera update e registra falhou:catalogo"""
        p = self.cenario_atualiza()
        self.ctl(add_sem_efeito=True)
        self.rodar_dentro(p)
        self.assertEqual(self.atualizacoes(), [])
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.0")
        self.assertTrue(any(r.startswith("falhou:catalogo") for r in self.resultados()), self.resultados())

    def test_branch_padrao_que_nao_e_main_nao_atualiza(self):
        """seção 2 · HEAD do remoto que não é refs/heads/main: nada muda e o registro diz falhou:branch-padrao"""
        p = self.cenario_atualiza()
        self.ctl(branch_padrao="develop")
        self.rodar_dentro(p)
        self.assertEqual(self.mutacoes(), [])
        self.assertTrue(any(r.startswith("falhou:branch-padrao") for r in self.resultados()), self.resultados())

    def test_update_de_projeto_roda_no_projectpath_e_o_de_usuario_em_pasta_neutra(self):
        """RD3 · cada update roda onde a CLI o entende (F5): projeto/local no projectPath, usuário em pasta neutra"""
        p, q = self.projeto("p"), self.projeto("q")
        self.instalar("0.47.0", "user")
        self.instalar("0.47.0", "project", p)
        self.instalar("0.47.0", "local", q)
        self.publicar("0.47.0")
        self.publicar("0.47.2")
        self.definir_ref("v0.47.0")
        self.rodar_dentro(p)
        onde = {c["args"][c["args"].index("--scope") + 1]: os.path.realpath(c["cwd"]) for c in self.atualizacoes()}
        self.assertEqual((onde["project"], onde["local"]), (os.path.realpath(p), os.path.realpath(q)))
        self.assertNotIn(onde["user"], (os.path.realpath(p), os.path.realpath(q), str(RAIZ)))


class Falhas(Dentro):
    def test_erro_interno_vira_registro_e_nao_vaza_traceback(self):
        """RD5 · exceção inesperada: falhou:interno no registro, rc 0 e uma linha no máximo"""
        p = self.cenario_atualiza()
        with mock.patch.object(fsa.Rodada, "ocupacao", side_effect=RuntimeError("quebrei")):
            rc = self.rodar_dentro(p)
        self.assertEqual(rc, 0)
        self.assertTrue(any(r.startswith("falhou:interno:RuntimeError") for r in self.resultados()), self.resultados())
        self.assertNotIn("Traceback", self.saida)
        self.assertLessEqual(len(self.saida.strip().splitlines()), 1)

    def test_prazo_do_passo_nao_derruba_a_rodada_e_o_geral_sim(self):
        """RD5 · passo que estoura o próprio prazo devolve rc None sem Prazo; o orçamento geral esgotado levanta Prazo"""
        with mock.patch.dict(os.environ, self.env(), clear=True):
            r = fsa.Rodada("atalho", None, 60)
            r.neutro = str(self.neutro)
            self.assertEqual(r.rodar([str(self.fbin / "claude"), "--dormir"], self.neutro, 0.3)[0], None)
            r.fim = time.monotonic() - 1
            with self.assertRaises(fsa.Prazo):
                r.rodar(["true"], self.neutro, 5)
            r.fim = time.monotonic() + 0.3
            with self.assertRaises(fsa.Prazo):
                r.rodar([str(self.fbin / "claude"), "--dormir"], self.neutro, 30)

    def test_rodar_distingue_nao_iniciou_de_prazo(self):
        """RD5 · programa que não existe devolve rc -1 (tmux ausente não é dúvida); não levanta"""
        with mock.patch.dict(os.environ, self.env(), clear=True):
            r = fsa.Rodada("atalho")
            self.assertEqual(r.rodar([str(self.tmp / "nao-existe")], self.neutro, 5)[0], -1)

    def test_lista_que_nao_e_json_registra_falhou_lista(self):
        """RD5 · `plugin list --json` com saída que não é lista: falhou:lista, sem escopo, sem update"""
        p = self.cenario_atualiza()
        self._script(self.fbin / "claude", CLAUDE_FALSO.replace('print(json.dumps(saida, indent=2))', 'print("nao e json")'))
        self.rodar_dentro(p)
        self.assertTrue(any(r.startswith("falhou:lista") for r in self.resultados()), self.resultados())
        self.assertEqual(self.atualizacoes(), [])


class Checagem(Dentro):
    def test_prazo_da_checagem_nao_volta_nem_grava_como_boa(self):
        """seção 4 · checagem sem conclusão (prazo) não é reprovação: sem volta, sem última boa nova, resultado falhou:checagem"""
        p = self.projeto("p")
        self.instalar("0.47.1", "user")
        self.publicar("0.47.1")
        self.publicar("0.47.2")
        self.definir_ref("v0.47.1")
        self.semear_estado(bom=self.bom("0.47.1"))
        original = fsa.Rodada.claude

        def claude(self, args, cwd=None, cap=60):
            return (None, "prazo do passo") if args[:2] == ["plugin", "validate"] else original(self, args, cwd, cap)

        with mock.patch.object(fsa.Rodada, "claude", claude):
            self.rodar_dentro(p)
        self.assertEqual(self.versoes()[("user", "")], "0.47.2")
        self.assertEqual(self.estado()["bom"]["user|"]["versao"], "0.47.1")
        self.assertTrue(any(r.startswith("falhou:checagem") for r in self.resultados()), self.resultados())
        self.assertNotIn("voltou", self.resultados())

    def test_adocao_sem_ultima_boa_so_confere_o_local(self):
        """seção 5.1 · sem última boa não há com o que comparar: nenhum validate nem doutor, só manifesto, compilação e shell"""
        p = self.projeto("p")
        self.instalar("0.47.1", "user")
        self.publicar("0.47.1")
        self.definir_ref("v0.47.1")
        self.rodar_dentro(p)
        self.assertEqual([c for c in self.chamadas() if c["args"][:2] == ["plugin", "validate"]], [])
        self.assertEqual(self.execs(), [])
        self.assertEqual(self.estado()["bom"]["user|"]["versao"], "0.47.1")

    def test_script_ausente_na_versao_nao_reprova(self):
        """seção 4 · versão antiga sem scripts/jarvis-forge: só erro de sintaxe reprova, arquivo ausente não"""
        p = self.projeto("p")
        ativo = self.instalar("0.45.2", "user")
        (ativo / "scripts" / "jarvis-forge").unlink()
        self.publicar("0.45.2")
        self.definir_ref("v0.45.2")
        self.rodar_dentro(p)
        self.assertEqual(self.estado()["bom"]["user|"]["versao"], "0.45.2")

    def test_fixacao_gravada_antes_de_mexer_no_catalogo(self):
        """seção 5.2 · a fixação automática vai para o disco antes do `add` da volta: se o processo morrer no meio, a abertura seguinte a vê"""
        p = self.projeto("p")
        self.instalar("0.47.1", "user")
        self.publicar("0.47.1")
        self.publicar("0.47.2", py_quebrado=True)
        self.definir_ref("v0.47.1")
        self.semear_estado(bom=self.bom("0.47.1"))
        original = fsa.Rodada.catalogo

        def catalogo(self, tag, escopos):
            if tag == "v0.47.1":
                raise KeyboardInterrupt
            return original(self, tag, escopos)

        with mock.patch.object(fsa.Rodada, "catalogo", catalogo), self.assertRaises(KeyboardInterrupt):
            self.rodar_dentro(p)
        fixacao = self.estado().get("fixacao") or {}
        self.assertEqual((fixacao.get("motivo"), fixacao.get("de"), fixacao.get("para")), ("volta-automatica", "0.47.2", "0.47.1"))

    def test_volta_so_de_quem_tem_ultima_boa(self):
        """seção 5.2 · dois escopos reprovam, só um tem última boa: esse volta; o outro registra sem-ultima-boa e fica"""
        p, q = self.projeto("p"), self.projeto("q")
        self.instalar("0.47.1", "project", p)
        self.instalar("0.47.1", "project", q)
        self.publicar("0.47.1")
        self.publicar("0.47.2", py_quebrado=True)
        self.definir_ref("v0.47.1")
        self.semear_estado(bom=self.bom("0.47.1", "project", str(p)))
        self.rodar_dentro(p)
        v = self.versoes()
        self.assertEqual(v[("project", str(p))], "0.47.1")
        self.assertIn("voltou", self.resultados("project"))
        self.assertTrue(any("sem-ultima-boa" in r for r in self.resultados("project")), self.resultados())

    def test_volta_escolhe_a_maior_ultima_boa_entre_os_reprovados(self):
        """seção 5.2 · o catálogo é um só: a volta vai para a maior última boa entre os escopos reprovados"""
        p, q = self.projeto("p"), self.projeto("q")
        self.instalar("0.47.0", "project", p)
        self.instalar("0.47.1", "project", q)
        for v in ("0.47.0", "0.47.1"):
            self.publicar(v)
        self.publicar("0.47.2", py_quebrado=True)
        self.definir_ref("v0.47.1")
        self.semear_estado(bom={**self.bom("0.47.0", "project", str(p)), **self.bom("0.47.1", "project", str(q))})
        self.rodar_dentro(p)
        self.assertEqual(self.ref(), "v0.47.1")
        self.assertEqual(self.estado()["fixacao"]["para"], "0.47.1")


class Modelo(Dentro):
    def test_escopo_de_usuario_sem_subida_nao_prepara_branch(self):
        """RD7 · plugin do usuário já em dia: abrir uma pasta qualquer não roda forge-upgrade nem toca o projeto"""
        p = self.projeto("p")
        self.instalar("0.47.1", "user")
        self.publicar("0.47.1")
        self.definir_ref("v0.47.1")
        self.semear_estado(bom=self.bom("0.47.1"))
        self.rodar_dentro(p)
        self.assertEqual(self.upgrades(), [])

    def test_escopo_de_usuario_que_subiu_prepara_a_branch(self):
        """RD7 · plugin do usuário que subiu nesta rodada, projeto com modelo atrás: prepara forge/upgrade-<v> local"""
        p = self.projeto("p")
        self.instalar("0.47.0", "user")
        self.publicar("0.47.0")
        self.publicar("0.47.2")
        self.definir_ref("v0.47.0")
        self.rodar_dentro(p)
        self.assertEqual(len(self.upgrades()), 1)

    def test_poststart_nunca_prepara_branch(self):
        """RD7 · o gatilho poststart não tem projeto aberto: nada de branch, mesmo com --projeto"""
        p = self.cenario_atualiza()
        self.rodar_dentro(p, gatilho="poststart")
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.2")
        self.assertEqual(self.upgrades(), [])

    def test_forge_upgrade_que_falha_nao_deixa_branch_pela_metade(self):
        """RD7/seção 6 · forge-upgrade que cria a branch e falha: a branch some, para a abertura seguinte tentar de novo"""
        p = self.projeto("p")
        self.instalar("0.47.0", "project", p)
        self.publicar("0.47.0")
        self.publicar("0.47.2")
        self.definir_ref("v0.47.0")
        upgrade = self.fake / "publicadas" / "0.47.2" / "bin" / "forge-upgrade"
        upgrade.write_text('#!/usr/bin/env bash\ncd "$1" && git checkout -q -b forge/upgrade-0.47.2\nexit 1\n')
        self.rodar_dentro(p)
        from test_oraculo_sempre_atual import git_real
        self.assertEqual(git_real("rev-parse", "--verify", "-q", "refs/heads/forge/upgrade-0.47.2", cwd=p, check=False), "")
        self.assertTrue(any(r.startswith("falhou:modelo") for r in self.resultados()))

    def test_fetch_que_falha_registra_falhou_modelo_e_nao_cria_branch(self):
        """RD7 · sem acesso ao remoto do projeto: falhou:modelo, nada criado, plugin atualizado do mesmo jeito"""
        p = self.cenario_atualiza()
        from test_oraculo_sempre_atual import git_real
        git_real("remote", "set-url", "origin", str(self.tmp / "nao-existe.git"), cwd=p)
        self.rodar_dentro(p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.2")
        self.assertTrue(any(r.startswith("falhou:modelo:fetch") for r in self.resultados()), self.resultados())
        self.assertEqual(self.upgrades(), [])


class ModeloComUpgradeDeVerdade(Dentro):
    """review A1 · a branch `forge/upgrade-<v>` nasce da `origin/develop`, com o `bin/forge-upgrade` de verdade na cópia instalada."""

    def preparar(self):
        p = self.projeto("p")
        self.instalar("0.47.0", "project", p)
        self.publicar("0.47.0")
        self.publicar("0.47.2")
        self.definir_ref("v0.47.0")
        publicada = self.fake / "publicadas" / "0.47.2"
        shutil.copyfile(RAIZ / "bin" / "forge-upgrade", publicada / "bin" / "forge-upgrade-real")
        (publicada / "bin" / "forge-upgrade").write_text(f'#!/bin/sh\nexec "{sys.executable}" -I "{publicada}/bin/forge-upgrade-real" "$@"\n')
        (publicada / "migrations").mkdir()
        return p

    def ramo(self, p):
        return git_real("rev-parse", "--verify", "-q", "refs/heads/forge/upgrade-0.47.2", cwd=p, check=False)

    def conferir(self, p):
        self.rodar_dentro(p)
        self.assertEqual(self.versoes()[("project", str(p))], "0.47.2")
        self.assertTrue(self.ramo(p), self.resultados())
        self.assertEqual(git_real("rev-parse", "refs/heads/forge/upgrade-0.47.2^", cwd=p), git_real("rev-parse", "origin/develop", cwd=p))
        self.assertEqual(git_real("show", "forge/upgrade-0.47.2:.forge/versao", cwd=p), "0.47.2")

    def test_clone_so_com_main_recebe_a_branch_da_origin_develop(self):
        """S1 do review · sem develop local (a worktree fica em HEAD solto): a branch nasce mesmo assim, da origin/develop"""
        p = self.preparar()
        git_real("branch", "-D", "develop", cwd=p)
        self.conferir(p)

    def test_develop_local_defasada_nao_vira_a_base(self):
        """S2 do review · develop local um commit atrás da origin/develop: a branch nasce da origin/develop"""
        p = self.preparar()
        git_real("switch", "-q", "develop", cwd=p)
        git_real("commit", "-q", "--allow-empty", "-m", "novo na develop", cwd=p)
        git_real("push", "-q", "origin", "develop", cwd=p)
        git_real("switch", "-q", "main", cwd=p)
        git_real("branch", "-f", "develop", "develop~1", cwd=p)
        self.conferir(p)
        self.assertNotEqual(git_real("rev-parse", "develop", cwd=p), git_real("rev-parse", "origin/develop", cwd=p))

    def test_hook_de_commit_do_projeto_nao_roda_no_upgrade(self):
        """segurança A3 · o forge-upgrade commita sem o core.hooksPath do projeto"""
        p = self.preparar()
        marca = self.tmp / "HOOK"
        git_real("config", "core.hooksPath", ".githooks", cwd=p)
        (p / ".githooks" / "pre-commit").write_text(f'#!/bin/sh\ntouch "{marca}"\n')
        (p / ".githooks" / "pre-commit").chmod(0o755)
        git_real("add", "-A", cwd=p)
        git_real("commit", "-q", "-m", "hook", "--no-verify", cwd=p)
        git_real("push", "-q", "origin", "HEAD:develop", cwd=p)
        marca.unlink(missing_ok=True)
        self.conferir(p)
        self.assertFalse(marca.exists(), "hook de commit do projeto rodou na abertura")


class UpgradeBase(unittest.TestCase):
    """`forge-upgrade --base`: a base dada vale em HEAD solto; o que não é commit, opção ou a main recusa com rc 2."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-upgrade-base-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.env = sem_manutencao({"HOME": str(self.tmp), "PATH": os.environ["PATH"], "LANG": "C.UTF-8", "FORGE_SEM_DOUTOR": "1",
                                   "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@exemplo.test",
                                   "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@exemplo.test"})
        self.git("init", "-q", "-b", "main")
        (self.tmp / "x").write_text("1\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "inicio")
        self.git("branch", "trabalho")
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("switch", "-q", "--detach", "HEAD")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.tmp), *args], env=self.env, capture_output=True, text=True, check=True).stdout.strip()

    def upgrade(self, *args):
        return subprocess.run([sys.executable, "-I", str(RAIZ / "bin" / "forge-upgrade"), "--ate", "0.5.0", *args, str(self.tmp)],
                              env=self.env, capture_output=True, text=True, timeout=60)

    def test_base_dada_em_head_solto_cria_a_branch_nela(self):
        r = self.upgrade("--base", "trabalho")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.git("rev-parse", "forge/upgrade-0.5.0^"), self.git("rev-parse", "trabalho"))
        self.assertIn("--base trabalho", r.stdout)

    def test_base_que_nao_e_commit_opcao_ou_main_recusa(self):
        for base, texto in (("nao-existe", "não é um commit"), ("-x", "não é um commit"), ("main", "branch de integração"),
                            ("origin/main", "branch de integração")):
            with self.subTest(base=base):
                r = self.upgrade(f"--base={base}")
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn(texto, r.stderr)
                self.assertEqual(subprocess.run(["git", "-C", str(self.tmp), "rev-parse", "--verify", "-q", "refs/heads/forge/upgrade-0.5.0"],
                                                env=self.env, capture_output=True).returncode, 1)

    def test_sem_base_em_head_solto_segue_recusando(self):
        self.git("branch", "-D", "trabalho")
        r = self.upgrade()
        self.assertEqual(r.returncode, 2)
        self.assertIn("HEAD solto", r.stderr)


class Entrada(unittest.TestCase):
    def test_dentro_do_claude_recusa_sem_rodar_nada(self):
        """D30b · main recusa com rc 2 quando chamada de dentro do Claude e não cria Rodada"""
        with mock.patch.object(fsa.fv, "dentro_do_claude", return_value=True), mock.patch.object(fsa, "Rodada") as rodada, \
                contextlib.redirect_stderr(io.StringIO()) as erro:
            self.assertEqual(fsa.main(["--gatilho", "atalho"]), 2)
        rodada.assert_not_called()
        self.assertIn("nunca de dentro do Claude", erro.getvalue())

    def test_gatilho_so_atalho_ou_poststart_e_orcamento_numerico(self):
        """interface · --gatilho obrigatório e restrito; --orcamento numérico (padrão 60)"""
        for ruim in ([], ["--gatilho", "hook"], ["--gatilho", "atalho", "--orcamento", "muito"]):
            with self.subTest(args=ruim), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as r:
                fsa.main(ruim)
            self.assertEqual(r.exception.code, 2)
        with mock.patch.object(fsa.fv, "dentro_do_claude", return_value=False), mock.patch.object(fsa, "Rodada") as rodada:
            rodada.return_value.executar.return_value = 0
            fsa.main(["--gatilho", "poststart"])
        rodada.assert_called_once_with("poststart", None, 60)

    def test_o_codigo_nao_le_variavel_que_mude_o_que_faz(self):
        """SEG-2 · só HOME, PATH e TMPDIR (e as do Claude Code na recusa): nenhuma FORGE_* nem porta dos fundos no caminho"""
        import ast
        for arq in (RAIZ / "bin" / "forge_sempre_atual.py", RAIZ / "bin" / "forge-sempre-atual"):
            for no in ast.walk(ast.parse(arq.read_text(encoding="utf-8"))):
                if isinstance(no, ast.Constant) and isinstance(no.value, str):
                    self.assertNotRegex(no.value, r"^FORGE_[A-Z_]+$", f"{arq.name}:{no.lineno}: variável FORGE_* lida em produção")


if __name__ == "__main__":
    unittest.main()


class Entradas(Mundo):
    """Entradas do FORGE-SEMPRE-ATUAL (E6.5): atalhos, trampolins e o preparo do container; o que o oráculo do QA não prende."""

    def instalar_trampolins(self):
        return subprocess.run(["bash", str(RAIZ / "scripts" / "instalar-atalho.sh")], env=self.env(), capture_output=True, text=True,
                              timeout=60)

    def trampolim(self, nome="forge", *args):
        return subprocess.run([str(self.home / ".local" / "bin" / nome), *args], env=self.env(), capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=30)

    def test_atalho_dentro_de_pasta_com_git_nao_roda_a_ferramenta_e_abre_o_claude(self):
        ativo, projeto = self.atalho_instalado()
        (ativo / ".git").mkdir()
        self.abrir_atalho(ativo, projeto, "--sem-tmux")
        self.assertEqual(self.chamadas_do_stub(), [], "um work tree (pasta com .git) nunca executa a ferramenta")
        self.assertEqual(self.eventos(), ["claude-abriu"])

    def test_reentrada_dentro_do_tmux_nao_repete_a_atualizacao(self):
        ativo, projeto = self.atalho_instalado()
        env = {**self.env(), "FORGE_ABERTURA_FEITA": "1", "TMUX": "/fake/tmux,1,0"}
        subprocess.run(["bash", str(ativo / "scripts" / "jarvis")], cwd=projeto, env=env, stdin=subprocess.DEVNULL,
                       capture_output=True, text=True, timeout=60)
        self.assertEqual(self.chamadas_do_stub(), [])
        self.assertEqual(self.eventos(), ["claude-abriu"])

    def jarvis_forge_montado(self):
        """installPath ativo com o `scripts/jarvis-forge` de verdade e o stub da ferramenta; ~/Forge e a cópia vigente clonados de uma origem local."""
        ativo = self.instalar("0.47.1", "user")
        shutil.copyfile(RAIZ / "scripts" / "jarvis-forge", ativo / "scripts" / "jarvis-forge")
        (ativo / "scripts" / "jarvis-forge").chmod(0o755)
        self._script(ativo / "bin" / "forge-sempre-atual", STUB_DA_FERRAMENTA.replace("@COMPORTAMENTO@", ""))
        origem = self.tmp / "origem.git"
        git_real("init", "-q", "--bare", "-b", "develop", str(origem), cwd=self.tmp)
        remoto_sem_manutencao(origem)  # o receive-pack local não herda GIT_CONFIG_* (ver ambiente_git.py)
        semente = self.tmp / "semente"
        git_real("clone", "-q", str(origem), str(semente), cwd=self.tmp)
        (semente / "x").write_text("1\n")
        git_real("add", "-A", cwd=semente)
        git_real("commit", "-q", "-m", "inicio", cwd=semente)
        git_real("push", "-q", "origin", "develop", cwd=semente)
        vigente, forge = self.home / ".local" / "share" / "forge" / "vigente", self.home / "Forge"
        vigente.parent.mkdir(parents=True)
        git_real("clone", "-q", str(origem), str(vigente), cwd=self.tmp)
        git_real("clone", "-q", str(origem), str(forge), cwd=self.tmp)
        return ativo, forge, {**self.env(), "XDG_DATA_HOME": str(self.home / ".local" / "share")}

    def abrir_jarvis_forge(self, ativo, forge, env):
        subprocess.run(["bash", str(ativo / "scripts" / "jarvis-forge")], cwd=forge, env=env, stdin=subprocess.DEVNULL,
                       capture_output=True, text=True, timeout=90)

    def test_jarvis_forge_roda_a_ferramenta_uma_vez_e_com_tmux_aberto_so_reanexa(self):
        ativo, forge, env = self.jarvis_forge_montado()
        for tmux_aberto, chamadas in (([], 1), (["jarvis-Forge"], 0)):
            for arq in ("ferramenta.log", "seq.log"):
                (self.fake / arq).unlink(missing_ok=True)
            self.ctl(tmux=tmux_aberto)
            self.abrir_jarvis_forge(ativo, forge, env)
            self.assertEqual(len(self.chamadas_do_stub()), chamadas, f"tmux aberto={tmux_aberto}")

    def test_jarvis_forge_dentro_de_pasta_com_git_nao_roda_a_ferramenta(self):
        ativo, forge, env = self.jarvis_forge_montado()
        (ativo / ".git").mkdir()
        self.abrir_jarvis_forge(ativo, forge, env)
        self.assertEqual(self.chamadas_do_stub(), [], "um work tree (pasta com .git) nunca executa a ferramenta")

    def test_trampolim_recusa_installpath_fora_do_cache_do_plugin(self):
        arvore = self.home / "work-tree"
        self._construir(arvore, "0.99.0", isca=True)
        self._gravar(self.plug / "installed_plugins.json", {"version": 2, "plugins": {"forge@forge": [
            {"scope": "user", "installPath": str(arvore), "version": "0.99.0"}]}})
        self.instalar_trampolins()
        r = self.trampolim("forge")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(self.execs(), [], "executou código de fora do cache do plugin")
        self.assertIn("claude plugin install forge@forge", r.stderr)

    def test_trampolim_ignora_instalacao_de_projeto_e_so_segue_a_do_usuario(self):
        p = self.projeto("p")
        self.instalar("0.47.0", "project", p)
        self.instalar_trampolins()
        r = self.trampolim("forge")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(self.execs(), [])
        ativo = self.instalar("0.47.1", "user")
        self.trampolim("forge")
        self.assertEqual([l.split()[1] for l in self.execs()], [str(ativo / "bin" / "forge")])

    def test_instalar_atalho_cria_os_tres_trampolins_e_nao_copia_o_script(self):
        self.instalar_trampolins()
        for nome in ("jarvis", "jarvis-forge", "forge"):
            texto = (self.home / ".local" / "bin" / nome).read_text(encoding="utf-8")
            self.assertIn("installed_plugins.json", texto)
            self.assertNotIn(str(RAIZ), texto)
            self.assertNotIn("sort -V", texto)

    def ativo_com_scripts(self, comportamento=""):
        ativo = self.instalar("0.47.1", "user")
        shutil.rmtree(ativo / "scripts")
        shutil.copytree(RAIZ / "scripts", ativo / "scripts")
        self._script(ativo / "bin" / "forge-sempre-atual", STUB_DA_FERRAMENTA.replace("@COMPORTAMENTO@", comportamento))
        return ativo

    def preparar(self, ativo, *args, **env):
        return subprocess.run(["bash", str(ativo / "scripts" / "preparar-estacao.sh"), "--container", *args],
                              env=self.env(FORGE_PERSISTENTE=str(self.tmp / "persistente"), **env), cwd=self.neutro,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=120)

    def test_preparo_sem_o_modo_essencial_refaz_os_atalhos_e_nao_roda_a_ferramenta(self):
        ativo = self.ativo_com_scripts()
        r = self.preparar(ativo)
        self.assertEqual(self.chamadas_do_stub(), [], r.stdout)
        self.assertTrue((self.home / ".local" / "bin" / "jarvis").is_file())

    def test_simular_nao_altera_nada_e_mostra_o_que_faria(self):
        ativo = self.ativo_com_scripts()
        r = self.preparar(ativo, "--simular", FORGE_PREPARO_ESSENCIAL="1")
        self.assertEqual(self.chamadas_do_stub(), [], r.stdout)
        self.assertIn("[simular] bash", r.stdout)
        self.assertIn("[simular] " + str(ativo / "bin" / "forge-sempre-atual") + " --gatilho poststart", r.stdout)
        self.assertFalse((self.home / ".local" / "bin" / "jarvis").exists(), "--simular não altera nada")

    def test_preparo_ignora_installpath_fora_do_cache_do_plugin(self):
        arvore = self.home / "work-tree"
        self._construir(arvore, "0.99.0", isca=True)
        shutil.copytree(RAIZ / "scripts", arvore / "scripts", dirs_exist_ok=True)
        self._script(arvore / "bin" / "forge-sempre-atual", STUB_DA_FERRAMENTA.replace("@COMPORTAMENTO@", ""))
        self._gravar(self.plug / "installed_plugins.json", {"version": 2, "plugins": {"forge@forge": [
            {"scope": "user", "installPath": str(arvore), "version": "0.99.0"}]}})
        r = self.preparar(arvore, FORGE_PREPARO_ESSENCIAL="1")
        self.assertIn("claude plugin install forge@forge", r.stdout)
        self.assertEqual(self.chamadas_do_stub(), [], "rodou a ferramenta de um installPath fora do cache")
        self.assertFalse((self.home / ".local" / "bin" / "jarvis").exists())

    def test_preparo_essencial_sem_plugin_ativo_diz_o_que_falta_e_nao_roda_nada_do_work_tree(self):
        r = subprocess.run(["bash", str(RAIZ / "scripts" / "preparar-estacao.sh"), "--container"],
                           env=self.env(FORGE_PREPARO_ESSENCIAL="1", FORGE_PERSISTENTE=str(self.tmp / "persistente")), cwd=self.neutro,
                           stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=120)
        self.assertIn("claude plugin install forge@forge", r.stdout)
        self.assertFalse((self.home / ".local" / "bin" / "jarvis").exists())
        self.assertEqual(self.chamadas_do_stub(), [])

    def test_preparo_essencial_com_ferramenta_que_falha_nao_derruba_o_poststart(self):
        ativo = self.ativo_com_scripts("sys.exit(1)")
        r = self.preparar(ativo, FORGE_PREPARO_ESSENCIAL="1")
        self.assertEqual(len(self.chamadas_do_stub()), 1)
        self.assertIn("atualização do plugin tentada no postStart", r.stdout)
        self.assertTrue((self.home / ".local" / "bin" / "jarvis").is_file())


class EmProcesso:
    """As classes do oráculo com a ferramenta (`fsa.main`) rodada dentro do processo e o `/proc` dublado livre (E1.62): no sandbox
    o `/proc` é de outro namespace e a rodada de verdade sai `adiado:duvida:proc`; aqui os mutantes da rodada se provam também
    localmente. Mesmos argumentos, ambiente (`clear=True`) e saída (`CompletedProcess`) de `Mundo.rodar`."""

    def rodar(self, projeto=None, gatilho="atalho", orcamento=None, stdin=None, env=None, timeout=90, direto=False):
        args = ["--gatilho", gatilho] + (["--projeto", str(projeto)] if projeto else [])
        args += ["--orcamento", str(orcamento)] if orcamento is not None else []
        saida, erro = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, env or self.env(), clear=True), mock.patch.object(fsa, "processos_de_interesse", lambda: LIVRE), \
                contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
            rc = fsa.main(args)
        return subprocess.CompletedProcess(args, rc, saida.getvalue(), erro.getvalue())


class EscoposDentro(EmProcesso, oraculo.Escopos):
    pass


class AncoraDentro(EmProcesso, oraculo.Ancora):
    pass


class VoltaDentro(EmProcesso, oraculo.Volta):
    pass


class CatalogoDentro(EmProcesso, oraculo.Catalogo):
    pass


class SemEnvioDentro(EmProcesso, oraculo.SemEnvio):
    pass


class ModeloDentro(EmProcesso, oraculo.Modelo):
    pass


class FalhaDentro(EmProcesso, oraculo.Falha):
    pass


class AvisosDentro(EmProcesso, oraculo.Avisos):
    pass


class RamosDaRodada(Dentro):
    """E1.62: o ramo de cada condição da rodada que o resto da suíte não distingue (o texto do registro e a raiz ocupada)."""

    def test_lista_que_falha_registra_o_erro_do_claude(self):
        p = self.cenario_atualiza()
        self.ctl(list_falha=True)
        self.rodar_dentro(p)
        self.assertIn("falhou:lista:erro interno do claude falso", self.resultados())

    def test_usuario_adia_pela_raiz_ocupada_mesmo_depois_de_uma_livre(self):
        """seção 3 · escopo do usuário: a primeira raiz com claude está livre e a segunda tem agente; adia pela segunda"""
        self.instalar("0.47.0", "user")
        self.publicar("0.47.0")
        self.publicar("0.47.2")
        self.definir_ref("v0.47.0")
        a, b = self.projeto("a"), self.projeto("b")
        self.agentes(b, 1)
        with Ocupacao.gancho_instalado(self, "exit 1"):
            self.rodar_dentro(procs={"claude": [str(a), str(b)], "fechar": [], "duvida": False})
        self.assertIn("adiado:agentes", self.resultados("user"))

    def test_sem_rede_no_head_simbolico_registra_rede(self):
        p = self.cenario_atualiza()
        self.ctl(rede=False)
        self.rodar_dentro(p)
        self.assertTrue([r for r in self.resultados("project") if r.startswith("falhou:rede:")], self.resultados())

    def test_sem_rede_na_lista_de_tags_registra_rede(self):
        p = self.cenario_atualiza()
        real = fsa.Rodada.git_rede

        def git_rede(rodada, args):
            return real(rodada, args) if "--symref" in args else (128, "fatal: tags sem rede")
        with mock.patch.object(fsa.Rodada, "git_rede", git_rede):
            self.rodar_dentro(p)
        self.assertIn("falhou:rede:fatal: tags sem rede", self.resultados("project"))

    def test_branch_padrao_errada_registra_qual_e(self):
        p = self.cenario_atualiza()
        self.ctl(branch_padrao="develop")
        self.rodar_dentro(p)
        self.assertIn("falhou:branch-padrao:refs/heads/develop", self.resultados("project"))

    def test_add_recusado_registra_add(self):
        p = self.cenario_atualiza()
        self.ctl(add_falha_para="v0.47.2")
        self.rodar_dentro(p)
        self.assertIn("falhou:add:add recusado pelo claude falso", self.resultados("project"))

    def test_update_recusado_registra_update(self):
        p = self.cenario_atualiza()
        shutil.rmtree(self.fake / "publicadas" / "0.47.2")
        self.rodar_dentro(p)
        self.assertIn("falhou:update:versao nao publicada", self.resultados("project"))

    def test_update_sem_efeito_diz_a_versao_achada(self):
        p = self.cenario_atualiza()
        with mock.patch.object(fsa.Rodada, "atualizar_escopo", lambda rodada, e: (0, "")):
            self.rodar_dentro(p)
        self.assertIn("falhou:update:esperava 0.47.2, achou 0.47.0", self.resultados("project"))

    def com_fluxo(self, fluxo):
        p = self.cenario_atualiza()
        with mock.patch.object(fsa.Rodada, "fluxo", fluxo):
            self.assertEqual(self.rodar_dentro(p), 0)

    def test_prazo_sem_escopos_registra_prazo(self):
        def fluxo(rodada):
            raise fsa.Prazo()
        self.com_fluxo(fluxo)
        self.assertIn("falhou:prazo", self.resultados())

    def test_erro_interno_sem_escopos_registra_o_erro(self):
        def fluxo(rodada):
            raise RuntimeError("quebrou")
        self.com_fluxo(fluxo)
        self.assertIn("falhou:interno:RuntimeError: quebrou", self.resultados())

    def test_linha_da_rodada_sai_no_terminal_e_a_pasta_neutra_some(self):
        neutras = []

        def fluxo(rodada):
            neutras.append(rodada.neutro)
            rodada.mensagem.append(("falhou", "rede"))
        self.com_fluxo(fluxo)
        self.assertIn("Forge: sem rede", self.saida)
        self.assertTrue(neutras and neutras[0])
        self.assertFalse(os.path.exists(neutras[0]), "a pasta neutra da rodada ficou")


def rodada_nua():
    """Uma `Rodada` fora de qualquer mundo, para os ramos que só leem os campos dela (voltar, linha, cini com dublês)."""
    with mock.patch.dict(os.environ, {"HOME": tempfile.gettempdir(), "PATH": os.defpath}, clear=True):
        rodada = fsa.Rodada("atalho", None, 60)
    rodada.estado = {"bom": {}, "adiamentos": {}}
    return rodada


def escopo(tipo="user", projeto="", versao="0.47.2"):
    return {"escopo": tipo, "projeto": projeto, "versao": versao, "install": "", "sha": "", "chave": f"{tipo}|{projeto}"}


class RamosSemMundo(unittest.TestCase):
    """E1.62: a volta, a linha do terminal e a comparação do doutor, com dublês nos métodos que saem do processo."""

    def voltar(self, rodada, reprovados, origem=True, update=(0, ""), listar=None):
        with mock.patch.object(rodada, "salvar_estado", lambda: None), \
                mock.patch.object(rodada, "origem_conferida", lambda tag, escopos: origem), \
                mock.patch.object(rodada, "catalogo", lambda tag, escopos: True), \
                mock.patch.object(rodada, "atualizar_escopo", lambda e: update), \
                mock.patch.object(rodada, "listar", lambda: listar or []):
            rodada.voltar(reprovados)

    def test_volta_com_update_recusado_registra_a_falha_do_update(self):
        rodada = rodada_nua()
        rodada.url = URL
        self.voltar(rodada, [(escopo(), {"versao": "0.47.1"}, "item")], update=(1, "recusado"))
        self.assertIn(("falhou", "update"), rodada.mensagem)
        self.assertEqual(rodada.res["user|"]["resultado"], "volta-falhou")

    def test_volta_sem_origem_guarda_o_resultado_dos_outros_escopos(self):
        rodada = rodada_nua()
        rodada.url = URL
        rodada.res = {"outro|": {"antes": "0.47.0", "depois": "0.47.0", "resultado": "em_dia"}}
        self.voltar(rodada, [(escopo(), {"versao": "0.47.1"}, "item")], origem=False)
        self.assertEqual(rodada.res["outro|"]["resultado"], "em_dia")

    def test_volta_que_falha_diz_a_pasta_so_do_escopo_de_projeto(self):
        rodada = rodada_nua()
        rodada.url = URL
        self.voltar(rodada, [(escopo(), {"versao": "0.47.1"}, "item"), (escopo("project", "/p/x"), {"versao": "0.47.1"}, "item")],
                    origem=False)
        texto = rodada.estado["aviso"]["texto"]
        self.assertIn("--scope project (na pasta /p/x)", texto)
        self.assertNotIn("--scope user (na pasta", texto)

    def test_resultado_sem_versao_registra_traco(self):
        rodada = rodada_nua()
        rodada.definir(escopo(versao=""), "pulado:projeto-ausente")
        self.assertEqual(rodada.res["user|"], {"antes": "-", "depois": "-", "resultado": "pulado:projeto-ausente"})
        rodada.definir(escopo(versao="0.47.0"), "atualizado", depois="0.47.2")
        self.assertEqual(rodada.res["user|"], {"antes": "0.47.0", "depois": "0.47.2", "resultado": "atualizado"})

    def test_linha_de_cada_mensagem(self):
        casos = [([("volta-falhou", "0.47.2", "0.47.1")], {}, "Forge: 0.47.2 falhou na checagem e a volta falhou; o Jarvis mostra o aviso"),
                 ([("falhou", "rede")], {}, "Forge: sem rede; segue na 0.47.0"),
                 ([("falhou", "add")], {}, "Forge: não atualizou (add); segue na 0.47.0"),
                 ([("atualizado", "0.47.0", "0.47.2", escopo())], {}, "Forge: 0.47.0 -> 0.47.2 (usuário)"),
                 ([("atualizado", "0.47.0", "0.47.2", escopo("project", "/p/x"))], {}, "Forge: 0.47.0 -> 0.47.2 (x)"),
                 ([], {"k": {"resultado": "adiado:agentes"}}, "Forge: atualização adiada (trabalho em curso)"),
                 ([], {"k": {"resultado": "em_dia"}}, None)]
        for mensagem, res, esperado in casos:
            with self.subTest(mensagem=mensagem, res=res):
                rodada = rodada_nua()
                rodada.escopos = [escopo(versao="0.47.0"), escopo("project", "/p/x", versao="")]
                rodada.mensagem, rodada.res = mensagem, res
                self.assertEqual(rodada.linha(), esperado)

    def test_doutor_da_comparacao_roda_no_projeto_do_escopo(self):
        tmp = Path(tempfile.mkdtemp(prefix="cini-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        for nome in ("novo", "base", "proj"):
            (tmp / nome / ".claude-plugin").mkdir(parents=True)
            (tmp / nome / ".claude-plugin" / "plugin.json").write_text("{}")
        rodada = rodada_nua()
        rodada.neutro, rodada.projeto = str(tmp), str(tmp / "aberto")
        chamadas = []

        def doutor(pasta, projeto):
            chamadas.append(projeto)
            return [], True
        e = {**escopo("project", str(tmp / "proj")), "install": str(tmp / "novo")}
        with mock.patch.object(rodada, "instalacao", lambda caminho: caminho or None), \
                mock.patch.object(rodada, "claude", lambda args, cap=60: (0, "")), \
                mock.patch.object(rodada, "rodar", lambda *a, **k: (0, "")), \
                mock.patch.object(rodada, "problemas_do_doutor", doutor):
            self.assertEqual(rodada.cini(e, {"installPath": str(tmp / "base")}), (True, ""))
        self.assertEqual(chamadas, [str(tmp / "proj")] * 2)


class ModuloComoScript(unittest.TestCase):
    def test_modulo_rodado_como_script_recusa_dentro_do_claude(self):
        """o bloco `__main__` de bin/forge_sempre_atual.py chama main(): dentro do Claude sai 2"""
        codigo = ("import os, runpy, sys; pasta = sys.argv[1]; sys.path.insert(0, pasta); "
                  "sys.argv = ['forge_sempre_atual.py', '--gatilho', 'atalho']; "
                  "runpy.run_path(os.path.join(pasta, 'forge_sempre_atual.py'), run_name='__main__')")
        r = subprocess.run([sys.executable, "-I", "-c", codigo, str(RAIZ / "bin")], capture_output=True, text=True, timeout=60,
                           env={"PATH": os.defpath, "HOME": tempfile.gettempdir(), "CLAUDECODE": "1"}, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("nunca de dentro do Claude", r.stderr)



class ProcessoDeOutraParteDaSuite(unittest.TestCase):
    """DEFEITO-TESTES-DE-PRAZO-SOB-CARGA (v0478, run 44333231292 do CI da develop): o oráculo roda a ferramenta pelo lançador
    `tests/sem_claude_ancestral.py`, e a ferramenta lia o /proc da máquina inteira. Um `forge-fechar` de outra parte da suíte,
    vivo ao mesmo tempo, adiava o escopo de usuário (`adiado:integracao`) e ele ficava na versão velha. O lançador passa a
    mostrar à ferramenta só os processos que descendem do teste."""

    def test_descende_de_segue_a_cadeia_de_pais_ate_o_teste(self):
        """descende_de: o próprio teste e os descendentes dele contam; o órfão, o init, a leitura falha e o ciclo, não"""
        import sem_claude_ancestral as lancador
        pais = {50: 40, 40: 10, 10: 1, 1: 0, 60: 1, 70: 71, 71: 70}
        ler = lambda pid: (pais.get(pid, 0), "")  # noqa: E731
        self.assertTrue(lancador.descende_de(10, 10, ler), "o próprio processo do teste")
        self.assertTrue(lancador.descende_de(50, 10, ler), "o neto do teste")
        self.assertFalse(lancador.descende_de(60, 10, ler), "o órfão, filho do init")
        self.assertFalse(lancador.descende_de(1, 10, ler), "o init")
        self.assertFalse(lancador.descende_de(99, 10, ler), "o processo cujo stat não se lê")
        self.assertFalse(lancador.descende_de(70, 10, ler), "a cadeia em ciclo termina")

    def test_lancador_troca_a_lista_de_pids_so_do_forge_sempre_atual(self):
        """o lançador entrega ao `forge-sempre-atual` só os pids que descendem do `--ate`; a outro script, a lista inteira"""
        pasta = Path(tempfile.mkdtemp(prefix="lancador-pids-"))
        self.addCleanup(shutil.rmtree, pasta, True)
        (pasta / "forge_versoes.py").write_text(
            "def _pai_e_nome(pid):\n    return {50: 40, 40: 10, 10: 1, 60: 1}.get(pid, 0), ''\n", encoding="utf-8")
        (pasta / "forge_sempre_atual.py").write_text("def pids_do_proc():\n    return ['1', '10', '40', '50', '60', '99']\n",
                                                    encoding="utf-8")
        corpo = "import json, sys\nsys.path.insert(0, %r)\nimport forge_sempre_atual\nprint(json.dumps(forge_sempre_atual.pids_do_proc()))\n"
        for nome, esperado in (("forge-sempre-atual", ["10", "40", "50"]), ("forge-outro", ["1", "10", "40", "50", "60", "99"])):
            with self.subTest(script=nome):
                (pasta / nome).write_text(corpo % str(pasta), encoding="utf-8")
                r = subprocess.run([sys.executable, "-I", str(TESTES / "sem_claude_ancestral.py"), "--ate", "10", str(pasta / nome)],
                                   capture_output=True, text=True, timeout=60, env={"PATH": os.defpath}, stdin=subprocess.DEVNULL)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(json.loads(r.stdout), esperado)

    def test_processos_de_interesse_le_os_pids_de_pids_do_proc(self):
        """a varredura só vê os pids que `pids_do_proc` entrega (o ponto que o lançador troca); sem a troca, todos do /proc"""
        teste = ProcFalso("test_coerente_le_claude_fechar_e_gh_de_merge")
        teste.setUp()
        self.addCleanup(teste.doCleanups)
        teste.processo(10, "claude", "/p/a")
        teste.processo(11, "forge-fechar", "/p/b")
        self.assertEqual(sorted(fsa.pids_do_proc()), sorted([str(os.getpid()), "10", "11"]))
        self.assertEqual(fsa.processos_de_interesse()["fechar"], ["/p/b"])
        with mock.patch.object(fsa, "pids_do_proc", lambda: [str(os.getpid()), "10"]):
            achados = fsa.processos_de_interesse()
        self.assertEqual((achados["claude"], achados["fechar"], achados["duvida"]), (["/p/a"], [], False))
