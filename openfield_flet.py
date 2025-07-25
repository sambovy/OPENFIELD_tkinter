import flet as ft
import time
import asyncio
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import base64
import io


class OpenFieldApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Teste de Campo Aberto - Marcação de Áreas"
        self.page.window_width = 1400
        self.page.window_height = 1000
        self.page.window_min_width = 1400
        self.page.window_min_height = 1000
        self.page.window_resizable = True
        self.page.window_maximized = True
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = "#F8F9FA"
        self.page.padding = 20
        
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
        # Labels de tempo com estilo moderno (criados primeiro)
        self.corner_time_text = ft.Text("Canto: 0.00 s", 
                                        color="#6B7280", 
                                        size=11,
                                        weight=ft.FontWeight.W_500)
        self.lateral_time_text = ft.Text("Lateral: 0.00 s", 
                                        color="#6B7280", 
                                        size=11,
                                        weight=ft.FontWeight.W_500)
        self.center_time_text = ft.Text("Centro: 0.00 s", 
                                       color="#6B7280", 
                                       size=11,
                                       weight=ft.FontWeight.W_500)
        
        # Campos de configuração
        self.animal_id_field = ft.TextField(
            label="ID do Animal",
            width=250,
            value="",
            bgcolor="#F8F9FA",
            border_color="#E5E7EB",
            focused_border_color="#6366F1",
            border_radius=6,
            content_padding=10
        )
        
        self.duration_field = ft.TextField(
            label="Duração do Teste (segundos)",
            width=250,
            value="300",
            keyboard_type=ft.KeyboardType.NUMBER,
            bgcolor="#F8F9FA",
            border_color="#E5E7EB",
            focused_border_color="#6366F1",
            border_radius=6,
            content_padding=10
        )
        
        config_section = ft.Container(
            content=ft.Column([
                ft.Text("Configurações do Teste", 
                        style=ft.TextThemeStyle.HEADLINE_SMALL,
                        color="#2E3440",
                        weight=ft.FontWeight.W_600),
                ft.Container(height=4),
                self.animal_id_field,
                ft.Container(height=3),
                self.duration_field,
            ]),
            padding=12,
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=8,
            margin=ft.margin.only(bottom=8),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color="#00000010",
                offset=ft.Offset(0, 1)
            )
        )
        
        # Timer e controles
        self.timer_text = ft.Text(
            "Tempo Restante: 00:00",
            style=ft.TextThemeStyle.HEADLINE_SMALL,
            text_align=ft.TextAlign.CENTER,
            color="#2E3440",
            weight=ft.FontWeight.W_600
        )
        
        self.start_button = ft.ElevatedButton(
            "Iniciar Teste",
            on_click=self.start_test,
            bgcolor="#10B981",
            color="#FFFFFF",
            width=100,
            height=32,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                elevation=2
            )
        )
        
        self.stop_button = ft.ElevatedButton(
            "Parar Teste",
            on_click=self.stop_test,
            bgcolor="#EF4444",
            color="#FFFFFF",
            width=100,
            height=32,
            disabled=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                elevation=2
            )
        )
        
        control_section = ft.Container(
            content=ft.Column([
                ft.Text("Controle do Teste", 
                        style=ft.TextThemeStyle.HEADLINE_SMALL,
                        color="#2E3440",
                        weight=ft.FontWeight.W_600),
                ft.Container(height=4),
                self.timer_text,
                ft.Container(height=6),
                ft.Row([
                    self.start_button,
                    self.stop_button
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                ft.Container(height=8),
                ft.Divider(color="#E5E7EB", height=1),
                ft.Container(height=6),
                ft.Text("Tempo por Área:", 
                        color="#2E3440", 
                        size=12,
                        weight=ft.FontWeight.W_600),
                ft.Container(height=4),
                ft.Container(
                    content=ft.Column([
                        self.corner_time_text,
                        ft.Container(height=2),
                        self.lateral_time_text,
                        ft.Container(height=2),
                        self.center_time_text,
                    ]),
                    padding=ft.padding.all(6),
                    bgcolor="#F8F9FA",
                    border_radius=4,
                ),
            ]),
            padding=10,
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=8,
            margin=ft.margin.only(bottom=8),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color="#00000010",
                offset=ft.Offset(0, 1)
            )
        )
        
        # Botões de área com design moderno
        self.corner_button = ft.Container(
            content=ft.Text("Canto", color="#FFFFFF", size=13, weight=ft.FontWeight.BOLD),
            bgcolor="#F87171",
            padding=12,
            border_radius=10,
            alignment=ft.alignment.center,
            width=120,
            height=55,
            on_click=lambda e: self.toggle_area_button("corner"),
            disabled=True,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color="#F8717140",
                offset=ft.Offset(0, 2)
            )
        )
        
        self.lateral_button = ft.Container(
            content=ft.Text("Lateral", color="#FFFFFF", size=13, weight=ft.FontWeight.BOLD),
            bgcolor="#60A5FA",
            padding=12,
            border_radius=10,
            alignment=ft.alignment.center,
            width=120,
            height=55,
            on_click=lambda e: self.toggle_area_button("lateral"),
            disabled=True,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color="#60A5FA40",
                offset=ft.Offset(0, 2)
            )
        )
        
        self.center_button = ft.Container(
            content=ft.Text("Centro", color="#FFFFFF", size=13, weight=ft.FontWeight.BOLD),
            bgcolor="#34D399",
            padding=12,
            border_radius=10,
            alignment=ft.alignment.center,
            width=120,
            height=55,
            on_click=lambda e: self.toggle_area_button("center"),
            disabled=True,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color="#34D39940",
                offset=ft.Offset(0, 2)
            )
        )
        
        area_section = ft.Container(
            content=ft.Column([
                ft.Text("Marcação de Áreas", 
                        style=ft.TextThemeStyle.HEADLINE_SMALL,
                        color="#2E3440",
                        weight=ft.FontWeight.W_600),
                ft.Text("Clique para alternar entre as áreas", 
                       color="#6B7280", 
                       size=11),
                ft.Container(height=8),
                ft.Row([
                    self.corner_button,
                    self.lateral_button
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                ft.Container(height=6),
                ft.Row([
                    self.center_button
                ], alignment=ft.MainAxisAlignment.CENTER),
            ]),
            padding=10,
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=8,
            expand=True,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color="#00000010",
                offset=ft.Offset(0, 1)
            )
        )
        
        # Coluna esquerda
        left_column = ft.Column([
            config_section,
            control_section,
            area_section
        ], expand=True)
        
        # Relatório com design moderno
        self.report_text = ft.Text(
            "Nenhum relatório gerado ainda.",
            selectable=True,
            expand=True,
            color="#4B5563",
            size=13
        )
        
        report_section = ft.Container(
            content=ft.Column([
                ft.Text("Relatório do Teste", 
                        style=ft.TextThemeStyle.HEADLINE_SMALL,
                        color="#2E3440",
                        weight=ft.FontWeight.W_600),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Container(
                        content=self.report_text,
                        padding=12,
                    ),
                    bgcolor="#F8F9FA",
                    border=ft.border.all(1, "#E5E7EB"),
                    border_radius=8,
                    height=150,
                ),
                ft.Container(height=12),
                ft.Row([
                    ft.ElevatedButton(
                        "📊 Gerar Relatório",
                        on_click=self.generate_report,
                        bgcolor="#6366F1",
                        color="#FFFFFF",
                        width=140,
                        height=40,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=6),
                            elevation=2
                        )
                    ),
                    ft.ElevatedButton(
                        "💾 Exportar",
                        on_click=self.export_report,
                        bgcolor="#059669",
                        color="#FFFFFF",
                        width=120,
                        height=40,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=6),
                            elevation=2
                        )
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ]),
            padding=15,
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=10,
            margin=ft.margin.only(bottom=12),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=6,
                color="#00000010",
                offset=ft.Offset(0, 2)
            )
        )
        
        # Container para o gráfico com design moderno
        self.chart_container = ft.Container(
            content=ft.Text("Gráfico será exibido após gerar o relatório.", 
                           text_align=ft.TextAlign.CENTER,
                           color="#6B7280"),
            padding=15,
            bgcolor="#F8F9FA",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=8,
            expand=True,
            alignment=ft.alignment.center
        )
        
        chart_section = ft.Container(
            content=ft.Column([
                ft.Text("Distribuição de Tempo por Área", 
                        style=ft.TextThemeStyle.HEADLINE_SMALL,
                        color="#2E3440",
                        weight=ft.FontWeight.W_600),
                ft.Container(height=10),
                self.chart_container
            ]),
            padding=15,
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=10,
            expand=True,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=6,
                color="#00000010",
                offset=ft.Offset(0, 2)
            )
        )
        
        # Coluna direita
        right_column = ft.Column([
            report_section,
            chart_section
        ], expand=True)
        
        # Layout principal com espaçamento moderno
        main_row = ft.Row([
            ft.Container(content=left_column, expand=1, padding=ft.padding.only(right=8)),
            ft.Container(content=right_column, expand=1, padding=ft.padding.only(left=8))
        ], expand=True, spacing=0)
        
        self.page.add(main_row)
    
    def start_test(self, e):
        # Validações
        if not self.animal_id_field.value.strip():
            self.show_snack_bar("Por favor, insira o ID do Animal.", "#EF4444")
            return
        
        try:
            duration = int(self.duration_field.value)
            if duration <= 0:
                raise ValueError
        except ValueError:
            self.show_snack_bar("Por favor, insira uma duração válida (número inteiro positivo).", "#EF4444")
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
            self.show_snack_bar(f"Teste para {self.animal_id} finalizado!", "#10B981")
        
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
            self.highlight_button(self.corner_button, True, "#F87171")
        elif area == "lateral":
            self.lateral_button_pressed = True
            self.lateral_press_time = current_time
            self.highlight_button(self.lateral_button, True, "#60A5FA")
        elif area == "center":
            self.center_button_pressed = True
            self.center_press_time = current_time
            self.highlight_button(self.center_button, True, "#34D399")
        
        self.page.update()
    
    def release_area_button(self, area):
        current_time = time.time()
        
        if area == "corner" and self.corner_button_pressed:
            elapsed = current_time - self.corner_press_time
            self.corner_time += elapsed
            self.corner_button_pressed = False
            self.corner_press_time = None
            self.highlight_button(self.corner_button, False, "#F87171")
        elif area == "lateral" and self.lateral_button_pressed:
            elapsed = current_time - self.lateral_press_time
            self.lateral_time += elapsed
            self.lateral_button_pressed = False
            self.lateral_press_time = None
            self.highlight_button(self.lateral_button, False, "#60A5FA")
        elif area == "center" and self.center_button_pressed:
            elapsed = current_time - self.center_press_time
            self.center_time += elapsed
            self.center_button_pressed = False
            self.center_press_time = None
            self.highlight_button(self.center_button, False, "#34D399")
        
        self.update_area_time_labels()
        self.page.update()
    
    def highlight_button(self, button, is_pressed, original_color):
        if is_pressed:
            # Cores mais escuras quando pressionado
            if original_color == "#F87171":  # Canto
                button.bgcolor = "#DC2626"
            elif original_color == "#60A5FA":  # Lateral
                button.bgcolor = "#2563EB"
            elif original_color == "#34D399":  # Centro
                button.bgcolor = "#059669"
            
            button.shadow = ft.BoxShadow(
                spread_radius=0,
                blur_radius=15,
                color="#00000030",
                offset=ft.Offset(0, 6)
            )
        else:
            button.bgcolor = original_color
            # Restaura sombra original baseada na cor
            if original_color == "#F87171":
                shadow_color = "#F8717140"
            elif original_color == "#60A5FA":
                shadow_color = "#60A5FA40"
            else:
                shadow_color = "#34D39940"
                
            button.shadow = ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=shadow_color,
                offset=ft.Offset(0, 4)
            )
    
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
        
        self.corner_time_text.value = f"Canto: {corner_display:.2f} s"
        self.lateral_time_text.value = f"Lateral: {lateral_display:.2f} s"
        self.center_time_text.value = f"Centro: {center_display:.2f} s"
    
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
            self.show_snack_bar("Inicie um teste primeiro para gerar o relatório.", "#F59E0B")
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
                color="#6B7280"
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
            width=350,
            height=250,
            fit=ft.ImageFit.CONTAIN
        )
    
    def export_report(self, e):
        if not self.test_data:
            self.show_snack_bar("Nenhum relatório foi gerado para exportar.", "#F59E0B")
            return
        
        # Cria um diálogo para salvar arquivo
        def save_file(file_path):
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.report_text.value)
                self.show_snack_bar(f"Relatório exportado com sucesso!", "#10B981")
            except Exception as ex:
                self.show_snack_bar(f"Erro ao exportar: {ex}", "#EF4444")
        
        # Por enquanto, salva com nome padrão
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_openfield_{self.animal_id}_{timestamp}.txt"
        save_file(filename)
    
    def show_snack_bar(self, message, color):
        snack_bar = ft.SnackBar(
            content=ft.Text(message, color="#FFFFFF", weight=ft.FontWeight.W_500),
            bgcolor=color,
            duration=3000,
            behavior=ft.SnackBarBehavior.FLOATING,
            action="OK",
            action_color="#FFFFFF"
        )
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()


def main(page: ft.Page):
    app = OpenFieldApp(page)


if __name__ == "__main__":
    ft.app(target=main)
