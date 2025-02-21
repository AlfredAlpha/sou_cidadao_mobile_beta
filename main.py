import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
from plyer import filechooser, camera
from pathlib import Path

# Cores da bandeira de Cabreúva/SP (verde, branco, azul)
CORES = {
    "verde": "#006400",  # Verde escuro ajustado para a bandeira
    "branco": "#FFFFFF",
    "azul": "#000080"    # Azul escuro ajustado para a bandeira
}

# Vereadores pré-definidos (exemplo)
VEREADORES = [
    {"nome": "João Silva", "email": "joao.silva@cabreuva.sp.gov.br"},
    {"nome": "Maria Oliveira", "email": "maria.oliveira@cabreuva.sp.gov.br"}
]

# Configurações de e-mail (substitua pelos valores reais)
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = "seu_email@gmail.com"
EMAIL_PASSWORD = "sua_senha_app"  # Use uma senha de aplicativo se for Gmail

# Configuração inicial da janela
Window.clearcolor = (1, 1, 1, 1)  # Fundo branco

class TelaApresentacao(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        layout.add_widget(Label(text="Sou Cidadão", font_size=40, color=CORES["azul"]))
        layout.add_widget(Label(text="Envie suas solicitações aos vereadores de Cabreúva", 
                              font_size=20, color=CORES["verde"]))
        layout.add_widget(Button(text="Iniciar", on_press=self.ir_para_selecao, 
                               size_hint=(1, 0.2), background_color=CORES["azul"],
                               background_normal=""))
        self.add_widget(layout)

    def ir_para_selecao(self, instance):
        self.manager.current = "selecao_vereador"

class TelaSelecaoVereador(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        layout.add_widget(Label(text="Selecione o Vereador", font_size=30, color=CORES["azul"]))
        for vereador in VEREADORES:
            btn = Button(text=vereador["nome"], on_press=self.selecionar_vereador, 
                        size_hint=(1, 0.2), background_color=CORES["verde"],
                        background_normal="")
            btn.vereador = vereador
            layout.add_widget(btn)
        self.add_widget(layout)

    def selecionar_vereador(self, instance):
        self.manager.vereador_selecionado = instance.vereador
        self.manager.current = "preencher_dados"

class TelaPreencherDados(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.layout.add_widget(Label(text="Preencha os Dados", font_size=30, color=CORES["azul"]))
        self.nome = TextInput(hint_text="Nome", size_hint=(1, 0.2))
        self.telefone = TextInput(hint_text="Telefone", size_hint=(1, 0.2))
        self.descricao = TextInput(hint_text="Descrição", multiline=True, size_hint=(1, 0.4))
        self.layout.add_widget(self.nome)
        self.layout.add_widget(self.telefone)
        self.layout.add_widget(self.descricao)
        self.layout.add_widget(Button(text="Próximo", on_press=self.ir_para_foto, 
                                    size_hint=(1, 0.2), background_color=CORES["azul"],
                                    background_normal=""))
        self.add_widget(self.layout)

    def ir_para_foto(self, instance):
        if not self.nome.text or not self.telefone.text or not self.descricao.text:
            self.mostrar_erro("Preencha todos os campos obrigatórios!")
        else:
            self.manager.dados_usuario = {
                "nome": self.nome.text,
                "telefone": self.telefone.text,
                "descricao": self.descricao.text
            }
            self.manager.current = "adicionar_foto"

    def mostrar_erro(self, mensagem):
        popup = Popup(title="Aviso", size_hint=(0.8, 0.4))
        popup.content = Label(text=mensagem)
        popup.open()

class TelaAdicionarFoto(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.layout.add_widget(Label(text="Adicionar Foto (Opcional)", font_size=30, color=CORES["azul"]))
        self.foto_path = None
        self.foto_status = Label(text="Nenhuma foto selecionada", font_size=20, color=CORES["verde"])
        self.layout.add_widget(self.foto_status)
        self.layout.add_widget(Button(text="Tirar Foto", on_press=self.tirar_foto, 
                                    size_hint=(1, 0.2), background_color=CORES["verde"],
                                    background_normal=""))
        self.layout.add_widget(Button(text="Escolher da Galeria", on_press=self.escolher_foto, 
                                    size_hint=(1, 0.2), background_color=CORES["verde"],
                                    background_normal=""))
        self.layout.add_widget(Button(text="Próximo", on_press=self.ir_para_confirmacao, 
                                    size_hint=(1, 0.2), background_color=CORES["azul"],
                                    background_normal=""))
        self.add_widget(self.layout)

    def tirar_foto(self, instance):
        try:
            camera.take_picture(filename="foto_solicitacao.jpg", on_complete=self.carregar_foto)
        except Exception as e:
            self.mostrar_erro(f"Erro ao tirar foto: {str(e)}")

    def escolher_foto(self, instance):
        try:
            filechooser.open_file(on_selection=self.carregar_foto)
        except Exception as e:
            self.mostrar_erro(f"Erro ao escolher foto: {str(e)}")

    def carregar_foto(self, caminho):
        if isinstance(caminho, list):
            caminho = caminho[0]
        self.foto_path = caminho
        self.foto_status.text = "Foto carregada com sucesso!"

    def mostrar_erro(self, mensagem):
        popup = Popup(title="Aviso", size_hint=(0.8, 0.4))
        popup.content = Label(text=mensagem)
        popup.open()

    def ir_para_confirmacao(self, instance):
        self.manager.foto_path = self.foto_path
        self.manager.current = "confirmacao"

class TelaConfirmacao(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.layout.add_widget(Label(text="Confirme os Dados", font_size=30, color=CORES["azul"]))
        self.dados_label = Label(text="", font_size=20, color=CORES["verde"])
        self.layout.add_widget(self.dados_label)
        self.layout.add_widget(Button(text="Enviar", on_press=self.enviar_email, 
                                    size_hint=(1, 0.2), background_color=CORES["azul"],
                                    background_normal=""))
        self.layout.add_widget(Button(text="Voltar ao Início", on_press=self.voltar_inicio, 
                                    size_hint=(1, 0.2), background_color=CORES["verde"],
                                    background_normal=""))
        self.add_widget(self.layout)

    def on_pre_enter(self, *args):
        dados = self.manager.dados_usuario
        vereador = self.manager.vereador_selecionado
        self.dados_label.text = (f"Nome: {dados['nome']}\n"
                                f"Telefone: {dados['telefone']}\n"
                                f"Descrição: {dados['descricao']}\n"
                                f"Vereador: {vereador['nome']}")

    def enviar_email(self, instance):
        try:
            msg = MIMEMultipart()
            msg["From"] = EMAIL_USER
            msg["To"] = self.manager.vereador_selecionado["email"]
            msg["Subject"] = "Solicitação do Cidadão - Sou Cidadão"
            corpo = (f"Nome: {self.manager.dados_usuario['nome']}\n"
                    f"Telefone: {self.manager.dados_usuario['telefone']}\n"
                    f"Descrição: {self.manager.dados_usuario['descricao']}")
            msg.attach(MIMEText(corpo, "plain"))

            if self.manager.foto_path:
                with open(self.manager.foto_path, "rb") as f:
                    img = MIMEImage(f.read())
                    msg.attach(img)

            with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
                server.starttls()
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                server.send_message(msg)

            self.mostrar_mensagem("Solicitação enviada com sucesso!")
            self.manager.current = "apresentacao"
        except Exception as e:
            self.mostrar_mensagem(f"Erro ao enviar solicitação: {str(e)}")

    def voltar_inicio(self, instance):
        self.manager.current = "apresentacao"

    def mostrar_mensagem(self, mensagem):
        popup = Popup(title="Aviso", size_hint=(0.8, 0.4))
        popup.content = Label(text=mensagem)
        popup.open()

class SouCidadaoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TelaApresentacao(name="apresentacao"))
        sm.add_widget(TelaSelecaoVereador(name="selecao_vereador"))
        sm.add_widget(TelaPreencherDados(name="preencher_dados"))
        sm.add_widget(TelaAdicionarFoto(name="adicionar_foto"))
        sm.add_widget(TelaConfirmacao(name="confirmacao"))
        return sm

if __name__ == "__main__":
    SouCidadaoApp().run()