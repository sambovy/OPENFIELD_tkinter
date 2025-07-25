import flet as ft
import time
import asyncio
import matplotlib.pyplot as plt
import base64
import io


class OpenFieldApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Teste de Campo Aberto - Marcação de Áreas"
        self.page.window.width = 1400
        self.page.window.height = 700
        self.page.theme_mode = ft.ThemeMode.LIGHT
        
        # Variáveis do teste
        self.test_running = False
        self.start_time = None
        self.remaining_time = 0
        self.animal_id = ""
        self.test_duration = 300
        
        # Variáveis para armazenar o tempo acumulado em cada área
        self.corner_time = 0.0
        self.lateral_time = 0.0
        self.center_time = 0.0
        
        # Variáveis para controlar se um botão de área está atualmente pressionado
        self.corner_button_pressed = False
        self.lateral_button_pressed = False
        self.center_button_pressed = False
        
        # Variáveis para registrar o tempo de início da pressão do botão
        self.corner_press_time = None
        self.lateral_press_time = None
        self.center_press_time = None
        
        # Dados do teste para relatório
        self.test_data = {}
        
        # Controles da interface
        self.animal_id_field = None
        self.duration_field = None
        self.timer_text = None
        self.start_button = None
        self.stop_button = None
        self.corner_button = None
        self.lateral_button = None
        self.center_button = None
        self.corner_time_text = None
        self.lateral_time_text = None
        self.center_time_text = None
        self.report_text = None
        self.chart_container = None
        
        self.create_ui()
        
        # Inicia o timer
        self.page.run_task(self.timer_loop)
    
    def create_ui(self):
        # Campos de configuração
        self.animal_id_field = ft.TextField(
            label="ID do Animal",
            width=300,
            value=""
        )
        
        self.duration_field = ft.TextField(
            label="Duração do Teste (segundos)",
            width=300,
            value="300",
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        config_section = ft.Container(
            content=ft.Column([
                ft.Text("Configurações do Teste", style=ft.TextThemeStyle.HEADLINE_SMALL),
                self.animal_id_field,
                self.duration_field,
            ]),
            padding=20,
            border=ft.border.all(1, "#9E9E9E"),
            border_radius=8,
            margin=ft.margin.only(bottom=20)
        )
        
        # Timer e controles
        self.timer_text = ft.Text(
            "Tempo Restante: 00:00",
            style=ft.TextThemeStyle.HEADLINE_MEDIUM,
            text_align=ft.TextAlign.CENTER
        )
        
        self.start_button = ft.ElevatedButton(
            "Iniciar Teste",
            on_click=self.start_test,
            bgcolor="#4CAF50",
            color="#FFFFFF",
            width=150,
            height=50
        )
        
        self.stop_button = ft.ElevatedButton(
            "Parar Teste",
            on_click=self.stop_test,
            bgcolor="#F44336",
            color="#FFFFFF",
            width=150,
            height=50,
            disabled=True
        )
        
        control_section = ft.Container(
            content=ft.Column([
                ft.Text("Controle do Teste", style=ft.TextThemeStyle.HEADLINE_SMALL),
                self.timer_text,
                ft.Row([
                    self.start_button,
                    self.stop_button
                ], alignment=ft.MainAxisAlignment.CENTER),
            ]),
            padding=20,
            border=ft.border.all(1, "#9E9E9E"),
            border_radius=8,
            margin=ft.margin.only(bottom=20)
        )
        
        # Botões de área
        self.corner_button = ft.Container(
            content=ft.Text("Canto", color="#FFFFFF", size=16, weight=ft.FontWeight.BOLD),
            bgcolor="#F44336",
            padding=20,
            border_radius=8,
            alignment=ft.alignment.center,
            width=200,
            height=80,
            on_click=lambda e: self.toggle_area_button("corner"),
            disabled=True
        )
        
        self.lateral_button = ft.Container(
            content=ft.Text("Lateral", color="#000000", size=16, weight=ft.FontWeight.BOLD),
            bgcolor="#2196F3",
            padding=20,
            border_radius=8,
            alignment=ft.alignment.center,
            width=200,
            height=80,
            on_click=lambda e: self.toggle_area_button("lateral"),
            disabled=True
        )
        
        self.center_button = ft.Container(
            content=ft.Text("Centro", color="#FFFFFF", size=16, weight=ft.FontWeight.BOLD),
            bgcolor="#4CAF50",
            padding=20,
            border_radius=8,
            alignment=ft.alignment.center,
            width=200,
            height=80,
            on_click=lambda e: self.toggle_area_button("center"),
            disabled=True
        )
        
        # Labels de tempo
        self.corner_time_text = ft.Text("Tempo no Canto: 0.00 s")
        self.lateral_time_text = ft.Text("Tempo na Lateral: 0.00 s")
        self.center_time_text = ft.Text("Tempo no Centro: 0.00 s")
        
        area_section = ft.Container(
            content=ft.Column([
                ft.Text("Marcação de Áreas (Clique para alternar)", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Row([
                    self.corner_button,
                    self.lateral_button
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([
                    self.center_button
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                self.corner_time_text,
                self.lateral_time_text,
                self.center_time_text,
            ]),
            padding=20,
            border=ft.border.all(1, "#9E9E9E"),
            border_radius=8,
            expand=True
        )
        
        # Coluna esquerda
        left_column = ft.Column([
            config_section,
            control_section,
            area_section
        ], expand=True)
        
        # Relatório
        self.report_text = ft.Text(
            "Nenhum relatório gerado ainda.",
            selectable=True,
            expand=True
        )
        
        report_section = ft.Container(
            content=ft.Column([
                ft.Text("Relatório do Teste", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Container(
                    content=self.report_text,
                    padding=10,
                    border=ft.border.all(1, "#E0E0E0"),
                    border_radius=4,
                    height=200,
                    bgcolor="#FAFAFA"
                ),
                ft.Row([
                    ft.ElevatedButton(
                        "Gerar/Atualizar Relatório",
                        on_click=self.generate_report,
                        icon=ft.icons.ASSESSMENT
                    ),
                    ft.ElevatedButton(
                        "Exportar Relatório",
                        on_click=self.export_report,
                        icon=ft.icons.DOWNLOAD
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER),
            ]),
            padding=20,
            border=ft.border.all(1, "#9E9E9E"),
            border_radius=8,
            margin=ft.margin.only(bottom=20)
        )
        
        # Container para o gráfico
        self.chart_container = ft.Container(
            content=ft.Text("Gráfico será exibido após gerar o relatório.", text_align=ft.TextAlign.CENTER),
            padding=20,
            border=ft.border.all(1, "#9E9E9E"),
            border_radius=8,
            expand=True,
            alignment=ft.alignment.center
        )
        
        chart_section = ft.Container(
            content=ft.Column([
                ft.Text("Distribuição de Tempo por Área", style=ft.TextThemeStyle.HEADLINE_SMALL),
                self.chart_container
            ]),
            padding=20,
            border=ft.border.all(1, "#9E9E9E"),
            border_radius=8,
            expand=True
        )
        
        # Coluna direita
        right_column = ft.Column([
            report_section,
            chart_section
        ], expand=True)
        
        # Layout principal
        main_row = ft.Row([
            ft.Container(content=left_column, expand=1, padding=10),
            ft.Container(content=right_column, expand=1, padding=10)
        ], expand=True)
        
        self.page.add(main_row)
    
    def start_test(self, e):
        # Validações
        if not self.animal_id_field.value.strip():
            self.show_snack_bar("Por favor, insira o ID do Animal.", "#F44336")
            return
        
        try:
            duration = int(self.duration_field.value)
            if duration <= 0:
                raise ValueError
        except ValueError:
            self.show_snack_bar("Por favor, insira uma duração válida (número inteiro positivo).", "#F44336")
            return
        
        # Inicia o teste
        self.test_running = True
        self.start_time = time.time()
        self.remaining_time = duration
        self.animal_id = self.animal_id_field.value.strip()
        self.test_duration = duration
        
        # Reset das variáveis
        self.corner_time = 0.0
        self.lateral_time = 0.0
        self.center_time = 0.0
        self.corner_button_pressed = False
        self.lateral_button_pressed = False
        self.center_button_pressed = False
        self.corner_press_time = None
        self.lateral_press_time = None
        self.center_press_time = None
        self.test_data = {}
        
        # Atualiza interface
        self.start_button.disabled = True
        self.stop_button.disabled = False
        self.corner_button.disabled = False
        self.lateral_button.disabled = False
        self.center_button.disabled = False
        
        self.update_area_time_labels()
        self.page.update()
    
    def stop_test(self, e=None, manual_stop=True):
        if not self.test_running:
            return
        
        self.test_running = False
        
        # Finaliza qualquer botão pressionado
        if self.corner_button_pressed:
            self.release_area_button("corner")
        if self.lateral_button_pressed:
            self.release_area_button("lateral")
        if self.center_button_pressed:
            self.release_area_button("center")
        
        # Atualiza interface
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.corner_button.disabled = True
        self.lateral_button.disabled = True
        self.center_button.disabled = True
        
        self.update_area_time_labels()
        self.generate_report(None)
        
        if manual_stop:
            self.show_snack_bar(f"Teste para {self.animal_id} finalizado!", "#4CAF50")
        
        self.page.update()
    
    def toggle_area_button(self, area):
        if not self.test_running:
            return
        
        # Se o botão já está pressionado, libera
        if (area == "corner" and self.corner_button_pressed) or \
           (area == "lateral" and self.lateral_button_pressed) or \
           (area == "center" and self.center_button_pressed):
            self.release_area_button(area)
        else:
            # Libera qualquer outro botão pressionado
            if self.corner_button_pressed:
                self.release_area_button("corner")
            if self.lateral_button_pressed:
                self.release_area_button("lateral")
            if self.center_button_pressed:
                self.release_area_button("center")
            
            # Pressiona o novo botão
            self.press_area_button(area)
    
    def press_area_button(self, area):
        current_time = time.time()
        
        if area == "corner":
            self.corner_button_pressed = True
            self.corner_press_time = current_time
            self.highlight_button(self.corner_button, True, "#F44336")
        elif area == "lateral":
            self.lateral_button_pressed = True
            self.lateral_press_time = current_time
            self.highlight_button(self.lateral_button, True, "#2196F3")
        elif area == "center":
            self.center_button_pressed = True
            self.center_press_time = current_time
            self.highlight_button(self.center_button, True, "#4CAF50")
        
        self.page.update()
    
    def release_area_button(self, area):
        current_time = time.time()
        
        if area == "corner" and self.corner_button_pressed:
            elapsed = current_time - self.corner_press_time
            self.corner_time += elapsed
            self.corner_button_pressed = False
            self.corner_press_time = None
            self.highlight_button(self.corner_button, False, "#F44336")
        elif area == "lateral" and self.lateral_button_pressed:
            elapsed = current_time - self.lateral_press_time
            self.lateral_time += elapsed
            self.lateral_button_pressed = False
            self.lateral_press_time = None
            self.highlight_button(self.lateral_button, False, "#2196F3")
        elif area == "center" and self.center_button_pressed:
            elapsed = current_time - self.center_press_time
            self.center_time += elapsed
            self.center_button_pressed = False
            self.center_press_time = None
            self.highlight_button(self.center_button, False, "#4CAF50")
        
        self.update_area_time_labels()
        self.page.update()
    
    def highlight_button(self, button, is_pressed, original_color):
        if is_pressed:
            button.bgcolor = "#424242"
            button.shadow = ft.BoxShadow(
                spread_radius=0,
                blur_radius=2,
                color="#000000",
                offset=ft.Offset(2, 2)
            )
        else:
            button.bgcolor = original_color
            button.shadow = None
    
    def update_area_time_labels(self):
        # Calcula tempo atual incluindo botões pressionados
        current_time = time.time()
        
        corner_display = self.corner_time
        if self.corner_button_pressed and self.corner_press_time:
            corner_display += current_time - self.corner_press_time
        
        lateral_display = self.lateral_time
        if self.lateral_button_pressed and self.lateral_press_time:
            lateral_display += current_time - self.lateral_press_time
        
        center_display = self.center_time
        if self.center_button_pressed and self.center_press_time:
            center_display += current_time - self.center_press_time
        
        self.corner_time_text.value = f"Tempo no Canto: {corner_display:.2f} s"
        self.lateral_time_text.value = f"Tempo na Lateral: {lateral_display:.2f} s"
        self.center_time_text.value = f"Tempo no Centro: {center_display:.2f} s"
    
    async def timer_loop(self):
        while True:
            if self.test_running:
                elapsed_total_time = time.time() - self.start_time
                self.remaining_time = self.test_duration - elapsed_total_time
                
                # Atualiza labels de tempo em tempo real
                self.update_area_time_labels()
                
                if self.remaining_time <= 0:
                    self.remaining_time = 0
                    self.timer_text.value = "Tempo Restante: 00:00"
                    self.stop_test(manual_stop=False)
                else:
                    mins = int(self.remaining_time // 60)
                    secs = int(self.remaining_time % 60)
                    self.timer_text.value = f"Tempo Restante: {mins:02d}:{secs:02d}"
                
                self.page.update()
            
            await asyncio.sleep(0.2)
    
    def generate_report(self, e):
        if not self.start_time:
            self.show_snack_bar("Inicie um teste primeiro para gerar o relatório.", "#FF9800")
            return
        
        total_duration = self.test_duration
        
        # Calcula a duração efetiva do teste
        if self.test_running:
            effective_duration = time.time() - self.start_time
        else:
            effective_duration = total_duration - self.remaining_time
        
        # Garante que effective_duration não seja zero
        if effective_duration <= 0:
            effective_duration = 0.001
        
        # Calcula as porcentagens
        corner_percent = (self.corner_time / effective_duration) * 100
        lateral_percent = (self.lateral_time / effective_duration) * 100
        center_percent = (self.center_time / effective_duration) * 100
        
        # Formata o relatório
        report = f"--- Relatório do Teste Open Field ---\n\n"
        report += f"ID do Animal: {self.animal_id}\n"
        report += f"Data/Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Duração Programada do Teste: {total_duration} segundos\n"
        report += f"Duração Efetiva do Teste: {effective_duration:.2f} segundos\n\n"
        report += f"Tempo Acumulado nas Áreas:\n"
        report += f"  Canto: {self.corner_time:.2f} segundos ({corner_percent:.2f}%)\n"
        report += f"  Lateral: {self.lateral_time:.2f} segundos ({lateral_percent:.2f}%)\n"
        report += f"  Centro: {self.center_time:.2f} segundos ({center_percent:.2f}%)\n"
        
        self.report_text.value = report
        
        # Armazena os dados para exportação
        self.test_data = {
            "ID do Animal": self.animal_id,
            "Data/Hora": time.strftime("%Y-%m-%d %H:%M:%S"),
            "Duração Programada (s)": total_duration,
            "Duração Efetiva (s)": effective_duration,
            "Tempo no Canto (s)": self.corner_time,
            "Porcentagem no Canto (%)": corner_percent,
            "Tempo na Lateral (s)": self.lateral_time,
            "Porcentagem na Lateral (%)": lateral_percent,
            "Tempo no Centro (s)": self.center_time,
            "Porcentagem no Centro (%)": center_percent,
        }
        
        # Gera o gráfico
        self.show_pie_chart()
        self.page.update()
    
    def show_pie_chart(self):
        labels = ['Canto', 'Lateral', 'Centro']
        sizes = [self.corner_time, self.lateral_time, self.center_time]
        colors = ['red', 'skyblue', 'forestgreen']
        
        # Remove áreas com tempo zero
        filtered_data = [(label, size, color) for label, size, color in zip(labels, sizes, colors) if size > 0]
        
        if not filtered_data:
            self.chart_container.content = ft.Text(
                "Nenhum tempo registrado para exibir o gráfico.",
                text_align=ft.TextAlign.CENTER,
                color="#666666"
            )
            return
        
        filtered_labels, filtered_sizes, filtered_colors = zip(*filtered_data)
        
        # Cria o gráfico
        fig, ax = plt.subplots(figsize=(6, 5))
        wedges, texts, autotexts = ax.pie(
            filtered_sizes,
            labels=filtered_labels,
            colors=filtered_colors,
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.85
        )
        
        # Ajusta o texto
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontsize(10)
        for text in texts:
            text.set_fontsize(10)
        
        ax.axis('equal')
        ax.set_title("Distribuição de Tempo por Área", fontsize=12, fontweight='bold')
        
        # Converte para base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        image_data = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        # Exibe a imagem
        self.chart_container.content = ft.Image(
            src_base64=image_data,
            width=400,
            height=300,
            fit=ft.ImageFit.CONTAIN
        )
    
    def export_report(self, e):
        if not self.test_data:
            self.show_snack_bar("Nenhum relatório foi gerado para exportar.", "#FF9800")
            return
        
        # Cria um diálogo para salvar arquivo
        def save_file(file_path):
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.report_text.value)
                self.show_snack_bar(f"Relatório exportado com sucesso!", "#4CAF50")
            except Exception as ex:
                self.show_snack_bar(f"Erro ao exportar: {ex}", "#F44336")
        
        # Por enquanto, salva com nome padrão
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_openfield_{self.animal_id}_{timestamp}.txt"
        save_file(filename)
    
    def show_snack_bar(self, message, color):
        snack_bar = ft.SnackBar(
            content=ft.Text(message, color="#FFFFFF"),
            bgcolor=color,
            duration=3000
        )
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()


def main(page: ft.Page):
    app = OpenFieldApp(page)


if __name__ == "__main__":
    ft.app(target=main)
