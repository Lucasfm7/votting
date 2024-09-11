from flet import *
import flet
from validate_docbr import CPF, CNPJ
from backend.search_cpf import buscar_pessoa_por_cpf
from backend.send_message import send_sms
import asyncio
import os
import random  # Para gerar o código aleatório de validação


# Página Base
class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.page.bgcolor = "#F2F2F2"
        self.page.margin = 0
        self.page.padding = 0
        self.loading_indicator = ProgressBar(visible=False, width=self.page.width, color=colors.RED, border_radius=20, height=10)

    def build_shared_content(self, controls):
        # Imagem que ocupa o topo da tela, utilizando toda a largura
        imagem_topo = Image(
            src="header.jpeg",  # Imagem de placeholder para o topo
            width=self.page.width,
            height=150,
            fit=ImageFit.COVER
        )

        # Logo principal
        logo_principal = Image(
            src="logo.png",  # Imagem principal
            width=150,
            height=150,
        )

        # Logo secundária
        logo_secundaria = Image(
            src="realizacao_aciac.jpeg",  # Logo de parceria 1
            width=250,
            height=100
        )

        # Imagem do rodapé que ocupa toda a largura
        imagem_rodape = Image(
            src="footer.jpeg",  # Imagem de placeholder para o rodapé
            width=self.page.width,
            height=100,
            fit=ImageFit.COVER,
        )

        # Coluna principal com o conteúdo, logo principal e logo secundária
        return Column(
            controls=[
                imagem_topo,  # Imagem no topo
                Container(expand=True),
                Container(
                    content=logo_principal,  # O logo principal
                    alignment=alignment.center,  # Alinha o logo ao centro
                    margin=0,  # Adiciona um espaçamento entre o logo e o conteúdo abaixo
                    padding=0,
                ),
                Container(expand=True),
                *controls,  # Adiciona os controles, como TextField e botões
                Container(expand=True),
                Container(
                    content=logo_secundaria,  # Logo secundária abaixo do botão
                    alignment=alignment.center,
                    margin=0,  # Adiciona um espaçamento entre o logo e o conteúdo abaixo
                    padding=0
                ),
                Container(expand=True),
                imagem_rodape  # Imagem no rodapé
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            expand=True,
        )


# Página de Validação de CPF/CNPJ
class CPFValidatorPage(BasePage):
    def __init__(self, page: Page, navigate):
        super().__init__(page)
        self.navigate = navigate
        self.input_field = None
        self.output_text = None
        self.name = None
        self.company = None

    def build(self):
        titulo = Text(value="Digite seu CPF ou CNPJ", text_align=TextAlign.LEFT, size=14, color=colors.GREY_500)
        self.input_field = TextField(
            width=300, text_align=TextAlign.LEFT,
            border_color=colors.GREY_300, focused_border_color=colors.RED,
            border_width=1, focused_border_width=2,
            autofocus=True,
            on_submit=lambda e: self.verificar_cpf(None)
        )
        self.output_text = Text("", color=colors.RED)

        botao_avancar = CupertinoButton(
            text="Avançar", color=colors.WHITE, bgcolor=colors.RED, on_click=self.verificar_cpf, width=300
        )

        container = Container(
            content=self.build_shared_content([
                Column(
                    controls=[titulo, self.input_field],
                    spacing=5,
                ),
                self.output_text, botao_avancar
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
        # Simulação da busca de pessoa por CPF (use a função real em produção)
        resultado = buscar_pessoa_por_cpf(cpf)  # Supondo que esta função retorna um dicionário
        if resultado:
            self.name = resultado['nome']
            self.company = resultado['empresa']
            self.loading_indicator.visible = False
            # Passa os valores de name e company para a próxima página
            self.navigate('nome_sobrenome_telefone', self.name, self.company)
        else:
            self.loading_indicator.visible = False
            self.output_text.value = "CPF não encontrado ou erro na requisição."
        self.page.update()

# Página de Nome, Sobrenome e Telefone
class NomeSobrenomeTelefonePage(BasePage):
    def __init__(self, page: Page, navigate, name=None, company=None):
        super().__init__(page)
        self.navigate = navigate
        self.name = name  # Recebe o nome da pessoa
        self.company = company  # Recebe o nome da empresa

    def build(self):
        # Texto "Bem-vindo(a)"
        titulo_bemvindo = Text(value="Bem-vindo(a)", text_align=TextAlign.CENTER, size=14, color=colors.GREY_500)
        
        # Verifica se `company` ou `name` foram passados e os exibe em uma linha separada
        if self.company:
            titulo_nome = Text(value=f"{self.company}", text_align=TextAlign.CENTER, size=14, color=colors.GREY_500)
        elif self.name:
            titulo_nome = Text(value=f"{self.name}", text_align=TextAlign.CENTER, size=14, color=colors.GREY_500)
        else:
            titulo_nome = Text(value="", text_align=TextAlign.CENTER, size=14, color=colors.GREY_500)

        nome_titulo = Text(value="Nome", text_align=TextAlign.LEFT, size=14, color=colors.GREY_500)
        nome_field = TextField(width=300, border_color=colors.GREY_300, focused_border_color=colors.RED, autofocus=True)

        sobrenome_titulo = Text(value="Sobrenome", text_align=TextAlign.LEFT, size=14, color=colors.GREY_500)
        sobrenome_field = TextField(width=300, border_color=colors.GREY_300, focused_border_color=colors.RED)

        telefone_titulo = Text(value="DDD + Telefone (que receberá SMS)", text_align=TextAlign.LEFT, size=14, color=colors.GREY_500)
        telefone_field = TextField(prefix_text="+55 ", width=300, border_color=colors.GREY_300, focused_border_color=colors.RED)

        botao_enviar = CupertinoButton(
            text="Enviar", color=colors.WHITE, bgcolor=colors.RED, on_click=lambda e: self.enviar_telefone(f"+55{telefone_field.value}"), width=300
        )

        container = Container(
            content=self.build_shared_content([
                Column(controls=[titulo_bemvindo, titulo_nome, nome_titulo, nome_field, sobrenome_titulo, sobrenome_field, telefone_titulo, telefone_field], spacing=5),
                botao_enviar
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

        # Apenas imprime o código gerado em vez de enviar SMS
        codigo_enviado = random.randint(100000, 999999)
        print(f"Código de validação gerado: {codigo_enviado}")

        self.loading_indicator.visible = False

        if codigo_enviado:
            self.navigate('verificacao_codigo', codigo_enviado)
        else:
            self.mostrar_mensagem_temporaria("Erro ao gerar o código. Tente novamente.")

    def mostrar_mensagem_temporaria(self, mensagem):
        snack_bar = SnackBar(Text(mensagem))
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()


# Página de Verificação de Código com Caixinhas Separadas
class VerificacaoCodigoPage(BasePage):
    def __init__(self, page: Page, codigo_enviado, navigate):
        super().__init__(page)
        self.codigo_enviado = codigo_enviado
        self.navigate = navigate
        self.input_fields = []

    def build(self):
        # Função que verifica o código quando os 6 dígitos são inseridos
        def verificar_codigo(e):
            codigo_inserido = ''.join([field.value for field in self.input_fields])
            self.loading_indicator.visible = True
            self.page.update()

            if codigo_inserido == str(self.codigo_enviado):
                self.loading_indicator.visible = False
                self.navigate('selecao_candidato')
            else:
                self.loading_indicator.visible = False
                self.mostrar_mensagem_temporaria("Código incorreto. Tente novamente.")

        # Função para mudar o foco para o próximo campo
        def on_digit_entered(e, index):
            if len(self.input_fields[index].value) == 1 and index < 5:
                self.input_fields[index + 1].focus()
            elif index == 5:
                verificar_codigo(None)

        # Criação das caixinhas
        row = Row(spacing=10, alignment=MainAxisAlignment.CENTER)
        for i in range(6):
            field = TextField(
                width=41, height=60, text_align=TextAlign.CENTER,
                on_change=lambda e, idx=i: on_digit_entered(e, idx),
                border_color=colors.GREY_300, focused_border_color=colors.RED
            )
            self.input_fields.append(field)
            row.controls.append(field)

        botao_verificar = CupertinoButton(
            text="Verificar Código", color=colors.WHITE, bgcolor=colors.RED,
            on_click=verificar_codigo, width=300
        )

        container = Container(
            content=self.build_shared_content([row, botao_verificar]),
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

    def mostrar_mensagem_temporaria(self, mensagem):
        snack_bar = SnackBar(Text(mensagem))
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()

# Página de Seleção de Candidatos (Votação)
class SelecaoCandidatoPage(BasePage):
    def __init__(self, page: Page, navigate):
        super().__init__(page)
        self.navigate = navigate
        self.selected_candidate = None
        self.candidatos = [f"Candidato {i+1}" for i in range(15)]
        self.column_count = 1

    def build(self):
        # Configura o redimensionamento dinâmico da página
        self.page.on_resized = self.on_resized
        self.display_candidates()

    def on_resized(self, e):
        # Obter a largura atual da janela
        page_width = self.page.window_width

        # Definir o número de colunas com base na largura da janela
        if page_width < 300:
            self.column_count = 1
        elif page_width < 500:
            self.column_count = 2
        elif page_width < 700:
            self.column_count = 3
        elif page_width < 900:
            self.column_count = 4
        else:
            self.column_count = 5
        
        # Atualiza a exibição com o número de colunas calculado
        self.display_candidates()

    def display_candidates(self):
        # Limpa a página para redesenhar os elementos
        self.page.clean()

        # Container que centraliza os candidatos
        grid = Column(alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, spacing=20)

        row = Row(alignment=MainAxisAlignment.CENTER, spacing=10)
        for i, candidato in enumerate(self.candidatos):
            row.controls.append(self.create_candidate_image(candidato))
            if (i + 1) % self.column_count == 0:
                grid.controls.append(row)
                row = Row(alignment=MainAxisAlignment.CENTER, spacing=10)

        # Adicionar a última linha, se houver candidatos restantes
        if row.controls:
            grid.controls.append(row)

        # Adiciona o layout à página com rolagem automática e centralização
        self.page.add(
            Column(
                controls=[
                    grid,
                    CupertinoButton(text="Confirmar Voto", color=colors.WHITE, bgcolor=colors.GREEN, on_click=self.confirmar_voto, width=300)
                ],
                alignment=MainAxisAlignment.CENTER,
                expand=True,
                scroll=ScrollMode.AUTO  # Permitir rolagem
            )
        )

    def create_candidate_image(self, candidato):
        nome_candidato = candidato if candidato else "Candidato Desconhecido"
        return Container(
            content=Image(src=f"https://placehold.co/100x200?text={nome_candidato}&grayscale", width=100, height=200),
            alignment=alignment.center,
            width=100,
            height=200,
            border_radius=border_radius.all(10),
            border=border.all(2, colors.GREY_400),
            on_click=lambda e: self.selecionar_candidato(nome_candidato)
        )

    def selecionar_candidato(self, candidato):
        self.selected_candidate = candidato
        print(f"Candidato selecionado: {self.selected_candidate}")

    def confirmar_voto(self, e):
        if self.selected_candidate:
            dialog = AlertDialog(
                title=Text("Confirmação de Voto"),
                content=Text(f"Você votou em {self.selected_candidate}. Confirma o voto?"),
                actions=[TextButton("Cancelar", on_click=self.cancelar_confirmacao), TextButton("Confirmar", on_click=self.finalizar_voto)],
                actions_alignment=MainAxisAlignment.END,
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
        else:
            self.mostrar_mensagem_temporaria("Selecione um candidato antes de confirmar o voto.")

    def cancelar_confirmacao(self, e):
        self.page.overlay.clear()
        self.page.update()

    def finalizar_voto(self, e):
        self.page.overlay.clear()
        dialog = AlertDialog(
            title=Text("Voto Confirmado"),
            content=Text(f"Voto em {self.selected_candidate} confirmado! Obrigado por votar."),
            actions=[TextButton("Fechar", on_click=lambda e: self.page.clean())],
            actions_alignment=MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
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
            self.current_page = NomeSobrenomeTelefonePage(self.page, self.navigate, *args)  # Passa nome e empresa
        elif page_name == 'verificacao_codigo':
            self.current_page = VerificacaoCodigoPage(self.page, args[0], self.navigate)
        elif page_name == 'selecao_candidato':
            self.current_page = SelecaoCandidatoPage(self.page, self.navigate)

        self.current_page.build()

if __name__ == "__main__":
    def main(page: Page):
        app = MyApp(page)

    flet.app(target=main, view=flet.WEB_BROWSER, port=int(os.getenv("PORT", 8000)))
