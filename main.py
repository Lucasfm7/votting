from flet import *
import flet
from validate_docbr import CPF, CNPJ
from backend.search_cpf import buscar_pessoa_por_cpf
from backend.send_message import send_sms
import asyncio


# Página Base
class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.loading_indicator = ProgressBar(visible=False, width=self.page.width, color=colors.RED, border_radius=20, height=10)

    def build_shared_content(self, controls):
        # Logo principal no topo
        logo_principal = Image(
            src="Logo_Destaques.png",  # Imagem principal
            width=200,
            height=200
        )

        # Logos de parceria no canto inferior direito
        logo_parceria_1 = Image(
            src="Logo_ACIAC.png",  # Logo de parceria 1
            width=75,
            height=75
        )

        # Coluna principal com conteúdo e logos de parceria
        return Column(
            controls=[
                Container(
                    content=logo_principal,  # O logo principal deve estar dentro de um Container ou diretamente
                    alignment=alignment.center,  # Alinha o logo ao centro
                    margin=margin.only(bottom=20),  # Adiciona um espaçamento entre o logo e o conteúdo abaixo
                ),
                *controls,  # Adiciona os outros controles abaixo do logo
                Container(
                    content=Row(
                        controls=[logo_parceria_1],
                        alignment=MainAxisAlignment.END,
                        spacing=10
                    ),
                    alignment=alignment.bottom_right,  # Alinha o logo de parceria na parte inferior direita
                    expand=True  # Faz com que o container preencha o espaço disponível
                ),
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True,
        )

# Página de Validação de CPF/CNPJ
class CPFValidatorPage(BasePage):
    def __init__(self, page: Page, navigate):
        super().__init__(page)
        self.navigate = navigate
        self.input_field = None
        self.output_text = None

    def build(self):
        titulo = Text(value="Digite seu CPF ou CNPJ", text_align=TextAlign.CENTER, size=20)
        self.input_field = TextField(
            label="", width=300, text_align=TextAlign.LEFT,
            border_color=colors.GREY_300, focused_border_color=colors.RED,
            border_width=1, focused_border_width=2,
            autofocus=True,  # Foco automático ao iniciar a página
            on_submit=self.verificar_cpf  # Acionar o botão ao pressionar Enter
        )
        self.output_text = Text("", color=colors.RED)

        botao_avancar = CupertinoButton(
            text="Avançar", color=colors.WHITE, bgcolor=colors.RED, on_click=self.verificar_cpf, width=300
        )

        container = Container(
            content=self.build_shared_content([
                titulo, self.input_field, self.output_text, botao_avancar
            ]),
            alignment=alignment.center, expand=True,
            opacity=0.0, animate_opacity=1000
        )

        self.page.add(
            Column(
                controls=[self.loading_indicator, container],
                alignment=MainAxisAlignment.START, expand=True
            )
        )

        container.opacity = 1.0
        container.update()

    def verificar_cpf(self, e):
        cpf = self.input_field.value.strip()
        self.loading_indicator.visible = True
        self.page.update()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.processar_verificacao(cpf))

    async def processar_verificacao(self, cpf):
        resultado = buscar_pessoa_por_cpf(cpf)
        self.loading_indicator.visible = False

        if resultado:
            self.navigate('nome_sobrenome_telefone')
        else:
            self.output_text.value = "CPF não encontrado ou erro na requisição."
        self.page.update()

# Página de Nome, Sobrenome e Telefone
class NomeSobrenomeTelefonePage(BasePage):
    def __init__(self, page: Page, navigate):
        super().__init__(page)
        self.navigate = navigate

    def build(self):
        nome_field = TextField(label="Nome", width=300, border_color=colors.GREY_300, focused_border_color=colors.RED, autofocus=True)
        sobrenome_field = TextField(label="Sobrenome", width=300, border_color=colors.GREY_300, focused_border_color=colors.RED)
        telefone_field = TextField(label="Telefone (DDI DDD Número)", width=300, border_color=colors.GREY_300, focused_border_color=colors.RED)

        botao_enviar = CupertinoButton(
            text="Enviar", color=colors.WHITE, bgcolor=colors.RED, on_click=lambda e: self.enviar_telefone(telefone_field.value), width=300
        )

        container = Container(
            content=self.build_shared_content([
                nome_field, sobrenome_field, telefone_field, botao_enviar
            ]),
            alignment=alignment.center, expand=True,
            opacity=0.0, animate_opacity=1000
        )

        self.page.add(
            Column(
                controls=[self.loading_indicator, container],
                alignment=MainAxisAlignment.START, expand=True
            )
        )

        container.opacity = 1.0
        container.update()

    def enviar_telefone(self, telefone):
        self.loading_indicator.visible = True
        self.page.update()

        codigo_enviado = send_sms(telefone)

        self.loading_indicator.visible = False

        if codigo_enviado:
            self.navigate('verificacao_codigo', codigo_enviado)
        else:
            self.mostrar_mensagem_temporaria("Erro ao enviar o SMS. Tente novamente.")

    def mostrar_mensagem_temporaria(self, mensagem):
        snack_bar = SnackBar(Text(mensagem))
        self.page.overlay.append(snack_bar)  # Use overlay para adicionar o SnackBar
        snack_bar.open = True
        self.page.update()

# Página de Verificação de Código
class VerificacaoCodigoPage(BasePage):
    def __init__(self, page: Page, codigo_enviado, navigate):
        super().__init__(page)
        self.codigo_enviado = codigo_enviado
        self.navigate = navigate

    def build(self):
        codigo_field = TextField(label="Digite o código recebido", width=300, border_color=colors.GREY_300, focused_border_color=colors.RED, autofocus=True)

        botao_verificar = CupertinoButton(
            text="Verificar Código", color=colors.WHITE, bgcolor=colors.RED, 
            on_click=lambda e: self.verificar_codigo(codigo_field.value), width=300
        )

        container = Container(
            content=self.build_shared_content([codigo_field, botao_verificar]),
            alignment=alignment.center, expand=True,
            opacity=0.0, animate_opacity=1000
        )

        self.page.add(
            Column(
                controls=[self.loading_indicator, container],
                alignment=MainAxisAlignment.START, expand=True
            )
        )

        container.opacity = 1.0
        container.update()

    def verificar_codigo(self, codigo_inserido):
        self.loading_indicator.visible = True
        self.page.update()

        if codigo_inserido.strip() == str(self.codigo_enviado):
            self.loading_indicator.visible = False
            self.navigate('selecao_candidato')  # Certifica-se que navega para a próxima página
        else:
            self.loading_indicator.visible = False
            self.mostrar_mensagem_temporaria("Código incorreto. Tente novamente.")

# Página de Seleção de Candidatos (Votação)
class SelecaoCandidatoPage(BasePage):
    def __init__(self, page: Page, navigate):
        super().__init__(page)
        self.navigate = navigate
        self.selected_candidate = None

    def build(self):
        # 15 candidatos; caso o nome não esteja disponível, usamos um padrão "Candidato X"
        candidatos = [f"Candidato {i+1}" for i in range(15)]  # Lista de candidatos

        # Função para criar o efeito de zoom, borda arredondada e cor ao passar o mouse sobre a imagem
        def create_candidate_image(candidato):
            # Verificando se o nome do candidato existe, senão atribuímos um nome fictício
            nome_candidato = candidato if candidato else "Candidato Desconhecido"
            
            # Gerando uma imagem fictícia de exemplo
            image = Image(
                src=f"https://placehold.co/150x150?text={nome_candidato}&grayscale",  # Usando imagens de exemplo em preto e branco
                width=200,
                height=200,
                fit=ImageFit.COVER,
                scale=1.0,  # Inicia com a escala normal
                animate_scale=500  # Animação de zoom
            )

            # Quando o mouse entra, remove o efeito de grayscale e aumenta o zoom
            def on_mouse_enter(e):
                image.src = f"https://placehold.co/150x150?text={nome_candidato}"  # Remove o grayscale
                image.scale = 1.2  # Aumenta o zoom
                image.update()

            # Quando o mouse sai, volta ao estado preto e branco e remove o zoom
            def on_mouse_exit(e):
                image.src = f"https://placehold.co/150x150?text={nome_candidato}&grayscale"  # Aplica o grayscale novamente
                image.scale = 1.0  # Volta ao zoom normal
                image.update()

            # Adicionando eventos de mouse
            image.on_hover = on_mouse_enter
            image.on_hover_exit = on_mouse_exit

            # Container com borda arredondada
            return Container(
                content=image,
                alignment=alignment.center,
                width=200,
                height=200,
                padding=10,
                border_radius=border_radius.all(10),  # Borda arredondada
                border=border.all(2, colors.GREY_400),  # Borda cinza clara
                on_click=lambda e: self.selecionar_candidato(nome_candidato)  # Seleciona o candidato ao clicar
            )

        # Criar a grid de 5 colunas e 3 linhas
        rows = []
        for i in range(0, len(candidatos), 5):  # Agrupa 5 candidatos por linha
            row = Row(
                controls=[create_candidate_image(c) for c in candidatos[i:i + 5]],
                alignment=MainAxisAlignment.CENTER,
                spacing=10
            )
            rows.append(row)

        botao_confirmar_voto = CupertinoButton(
            text="Confirmar Voto", color=colors.WHITE, bgcolor=colors.GREEN, on_click=self.confirmar_voto, width=300
        )

        container = Container(
            content=self.build_shared_content([*rows, botao_confirmar_voto]),  # Adiciona todas as linhas à página
            alignment=alignment.center,
            expand=True,
            opacity=0.0,  # Começa com opacidade 0 para o efeito de fade-in
            animate_opacity=1000  # Anima a opacidade ao longo de 1000ms
        )

        self.page.add(
            Column(
                controls=[self.loading_indicator, container],
                alignment=MainAxisAlignment.START,
                expand=True
            )
        )

        container.opacity = 1.0
        container.update()

    def selecionar_candidato(self, candidato):
        self.selected_candidate = candidato
        print(f"Candidato selecionado: {self.selected_candidate}")
        
    def confirmar_voto(self, e):
        if self.selected_candidate:
            dialog = AlertDialog(
                title=Text("Confirmação de Voto"),
                content=Text(f"Você votou em {self.selected_candidate}. Confirma o voto?"),
                actions=[
                    TextButton("Cancelar", on_click=self.cancelar_confirmacao),
                    TextButton("Confirmar", on_click=self.finalizar_voto)
                ],
                actions_alignment=MainAxisAlignment.END,
            )
            
            # Usando Page.overlay.append() em vez de self.page.dialog
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
        else:
            self.mostrar_mensagem_temporaria("Selecione um candidato antes de confirmar o voto.")

    def cancelar_confirmacao(self, e):
        self.page.overlay.clear()  # Remove o diálogo do overlay
        self.page.update()

    def finalizar_voto(self, e):
        self.page.overlay.clear()  # Remove o diálogo do overlay
        self.page.clean()
        self.page.add(Text(f"Voto em {self.selected_candidate} confirmado! Obrigado por votar.", size=24, color=colors.GREEN))
        self.page.update()


# Página Principal de Controle (MyApp)
class MyApp:
    def __init__(self, page: Page):
        self.page = page
        self.page.title = "Validação de CPF/CNPJ"
        self.page.theme_mode = ThemeMode.LIGHT
        self.page.padding = 10

        self.current_page = None

        self.navigate('cpf_validator')  # Inicia na página de CPF/CNPJ

    def navigate(self, page_name, *args):
        self.page.clean()
        if page_name == 'cpf_validator':
            self.current_page = CPFValidatorPage(self.page, self.navigate)
        elif page_name == 'nome_sobrenome_telefone':
            self.current_page = NomeSobrenomeTelefonePage(self.page, self.navigate)
        elif page_name == 'verificacao_codigo':
            self.current_page = VerificacaoCodigoPage(self.page, args[0], self.navigate)
        elif page_name == 'selecao_candidato':
            self.current_page = SelecaoCandidatoPage(self.page, self.navigate)

        self.current_page.build()

def main(page: Page):
    app = MyApp(page)

flet.app(target=main, view=flet.WEB_BROWSER)