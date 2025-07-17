import tkinter as tk
from tkinter import messagebox, filedialog
import time
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class OpenFieldApp:
    def __init__(self, master):
        self.master = master
        master.title("Teste de Campo Aberto - Marcação de Áreas")
        master.geometry("1400x700") # Aumenta a largura da janela para duas colunas

        # Configura o grid principal da janela (root) para ter 2 colunas
        master.grid_columnconfigure(0, weight=1) # Coluna da esquerda
        master.grid_columnconfigure(1, weight=1) # Coluna da direita
        master.grid_rowconfigure(0, weight=1) # Apenas uma linha principal

        self.test_running = False
        self.start_time = None
        self.remaining_time = 0
        self.animal_id = tk.StringVar()
        self.test_duration = tk.IntVar(value=300)

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

        self.test_data = {} # Para armazenar os resultados do teste atual para o relatório

        self._create_widgets()

    def _create_widgets(self):
        # --- COLUNA DA ESQUERDA: Aplicação de Teste ---
        self.left_column_frame = tk.Frame(self.master, bd=2, relief="groove") # Borda para visualização
        self.left_column_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.left_column_frame.grid_rowconfigure(0, weight=0) # Config
        self.left_column_frame.grid_rowconfigure(1, weight=0) # Control
        self.left_column_frame.grid_rowconfigure(2, weight=1) # Area (expand)
        self.left_column_frame.grid_columnconfigure(0, weight=1) # Uma coluna que se expande

        # Frame de Configuração
        config_frame = tk.LabelFrame(self.left_column_frame, text="Configurações do Teste", padx=10, pady=10)
        config_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew") # Usa grid dentro do left_column_frame
        config_frame.grid_columnconfigure(1, weight=1) # Permite que a entrada se expanda

        tk.Label(config_frame, text="ID do Animal:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(config_frame, textvariable=self.animal_id, width=30).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(config_frame, text="Duração do Teste (segundos):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(config_frame, textvariable=self.test_duration, width=30).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Frame de Controle do Teste
        control_frame = tk.LabelFrame(self.left_column_frame, text="Controle do Teste", padx=10, pady=10)
        control_frame.grid(row=1, column=0, pady=10, padx=10, sticky="ew") # Usa grid
        control_frame.grid_columnconfigure(0, weight=1) # Coluna para centralizar timer
        control_frame.grid_columnconfigure(1, weight=1) # Coluna para centralizar timer

        self.timer_label = tk.Label(control_frame, text="Tempo Restante: 00:00", font=("Helvetica", 24))
        self.timer_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="nsew") # Span para centralizar

        button_frame = tk.Frame(control_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=5) # Span para centralizar
        self.start_button = tk.Button(button_frame, text="Iniciar Teste", command=self.start_test, width=15, height=2, bg="green", fg="white")
        self.start_button.pack(side="left", padx=10)
        self.stop_button = tk.Button(button_frame, text="Parar Teste", command=self.stop_test, width=15, height=2, bg="red", fg="white", state="disabled")
        self.stop_button.pack(side="left", padx=10)

        # Frame de Marcação de Áreas
        area_frame = tk.LabelFrame(self.left_column_frame, text="Marcação de Áreas (Pressione e Segure)", padx=10, pady=10)
        area_frame.grid(row=2, column=0, pady=10, padx=10, sticky="nsew") # Usa grid e expande
        area_frame.grid_columnconfigure(0, weight=1)
        area_frame.grid_columnconfigure(1, weight=1)
        area_frame.grid_rowconfigure((0,1,2,3,4), weight=0) # Linhas de botões não se expandem
        area_frame.grid_rowconfigure(5, weight=1) # Linha extra para empurrar conteúdo para cima, se necessário

        # Botões das áreas
        self.corner_btn = tk.Button(area_frame, text="Canto", bg="red", fg="white", width=15, height=3, state="disabled")
        self.corner_btn.bind("<ButtonPress-1>", self._on_button_press)
        self.corner_btn.bind("<ButtonRelease-1>", self._on_button_release)
        self.corner_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.lateral_btn = tk.Button(area_frame, text="Lateral", bg="skyblue", width=15, height=3, state="disabled")
        self.lateral_btn.bind("<ButtonPress-1>", self._on_button_press)
        self.lateral_btn.bind("<ButtonRelease-1>", self._on_button_release)
        self.lateral_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.center_btn = tk.Button(area_frame, text="Centro", bg="forestgreen", fg="white", width=15, height=3, state="disabled")
        self.center_btn.bind("<ButtonPress-1>", self._on_button_press)
        self.center_btn.bind("<ButtonRelease-1>", self._on_button_release)
        self.center_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Labels para exibir os tempos acumulados em tempo real
        self.corner_time_label = tk.Label(area_frame, text="Tempo no Canto: 0.00 s")
        self.corner_time_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        self.lateral_time_label = tk.Label(area_frame, text="Tempo na Lateral: 0.00 s")
        self.lateral_time_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        self.center_time_label = tk.Label(area_frame, text="Tempo no Centro: 0.00 s")
        self.center_time_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=2)


        # --- COLUNA DA DIREITA: Relatório e Gráfico ---
        self.right_column_frame = tk.Frame(self.master, bd=2, relief="groove")
        self.right_column_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_column_frame.grid_rowconfigure(0, weight=1) # Relatório de texto (expande)
        self.right_column_frame.grid_rowconfigure(1, weight=0) # Botões de relatório
        self.right_column_frame.grid_rowconfigure(2, weight=2) # Gráfico (expande mais)
        self.right_column_frame.grid_columnconfigure(0, weight=1) # Uma coluna que se expande

        # Frame de Relatórios
        report_frame = tk.LabelFrame(self.right_column_frame, text="Relatório do Teste", padx=10, pady=10)
        report_frame.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")
        report_frame.grid_rowconfigure(0, weight=1) # Faz o Text widget expandir
        report_frame.grid_columnconfigure(0, weight=1)

        self.report_text = tk.Text(report_frame, height=8, state="disabled", wrap="word")
        self.report_text.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")

        # Botões de relatório e exportação
        report_buttons_frame = tk.Frame(self.right_column_frame)
        report_buttons_frame.grid(row=1, column=0, pady=5)
        tk.Button(report_buttons_frame, text="Gerar/Atualizar Relatório", command=self.generate_report, width=25, height=2).pack(side="left", padx=5)
        tk.Button(report_buttons_frame, text="Exportar Relatório (TXT)", command=self.export_report, width=25, height=2).pack(side="left", padx=5)

        # Frame para o gráfico de pizza
        self.chart_frame = tk.LabelFrame(self.right_column_frame, text="Distribuição de Tempo por Área", padx=10, pady=10)
        self.chart_frame.grid(row=2, column=0, pady=10, padx=10, sticky="nsew")
        self.chart_frame.grid_rowconfigure(0, weight=1) # Para o canvas do gráfico
        self.chart_frame.grid_columnconfigure(0, weight=1)


    def start_test(self):
        if self.test_running:
            return

        animal_id = self.animal_id.get().strip()
        if not animal_id:
            messagebox.showwarning("Erro", "Por favor, insira o ID do Animal.")
            return

        try:
            duration = self.test_duration.get()
            if duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Erro", "Por favor, insira uma duração de teste válida (número inteiro positivo).")
            return

        self.test_running = True
        self.start_time = time.time()
        self.remaining_time = duration

        # Resetar todos os tempos e estados dos botões
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

        self._update_area_time_labels()

        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.corner_btn.config(state="normal")
        self.lateral_btn.config(state="normal")
        self.center_btn.config(state="normal")

        # Limpa o gráfico anterior, se houver
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        self.update_timer()

    def stop_test(self, manual_stop=True):
        if not self.test_running:
            return

        self.test_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.corner_btn.config(state="disabled")
        self.lateral_btn.config(state="disabled")
        self.center_btn.config(state="disabled")

        # Garante que qualquer tempo ativo seja contabilizado ao parar o teste
        if self.corner_button_pressed:
            self._on_button_release(event=None, button_name="Canto")
        if self.lateral_button_pressed:
            self._on_button_release(event=None, button_name="Lateral")
        if self.center_button_pressed:
            self._on_button_release(event=None, button_name="Centro")

        self._update_area_time_labels()
        self.generate_report() # Gera o relatório e o gráfico final

        if manual_stop:
            messagebox.showinfo("Teste Finalizado", f"Teste para {self.animal_id.get()} finalizado!")

    def update_timer(self):
        if self.test_running:
            elapsed_total_time = time.time() - self.start_time
            self.remaining_time = self.test_duration.get() - elapsed_total_time

            # Atualizar os tempos das áreas em tempo real (mesmo que o botão esteja pressionado)
            if self.corner_button_pressed and self.corner_press_time:
                current_press_duration = time.time() - self.corner_press_time
                self.corner_time_label.config(text=f"Tempo no Canto: {self.corner_time + current_press_duration:.2f} s")
            if self.lateral_button_pressed and self.lateral_press_time:
                current_press_duration = time.time() - self.lateral_press_time
                self.lateral_time_label.config(text=f"Tempo na Lateral: {self.lateral_time + current_press_duration:.2f} s")
            if self.center_button_pressed and self.center_press_time:
                current_press_duration = time.time() - self.center_press_time
                self.center_time_label.config(text=f"Tempo no Centro: {self.center_time + current_press_duration:.2f} s")


            if self.remaining_time <= 0:
                self.remaining_time = 0
                self.timer_label.config(text="Tempo Restante: 00:00")
                self.stop_test(manual_stop=False)
                return

            mins = int(self.remaining_time // 60)
            secs = int(self.remaining_time % 60)
            self.timer_label.config(text=f"Tempo Restante: {mins:02d}:{secs:02d}")
            self.master.after(200, self.update_timer)

    def _on_button_press(self, event):
        if self.test_running:
            # Garante que, se um botão diferente estiver ativo, seu tempo seja parado e contabilizado
            if self.corner_button_pressed and event.widget != self.corner_btn:
                self._on_button_release(event=None, button_name="Canto")
            if self.lateral_button_pressed and event.widget != self.lateral_btn:
                self._on_button_release(event=None, button_name="Lateral")
            if self.center_button_pressed and event.widget != self.center_btn:
                self._on_button_release(event=None, button_name="Centro")

            # Agora, inicia o tempo para o botão que foi pressionado
            if event.widget == self.corner_btn and not self.corner_button_pressed:
                self.corner_button_pressed = True
                self.corner_press_time = time.time()
                self._highlight_button(self.corner_btn, True)
            elif event.widget == self.lateral_btn and not self.lateral_button_pressed:
                self.lateral_button_pressed = True
                self.lateral_press_time = time.time()
                self._highlight_button(self.lateral_btn, True)
            elif event.widget == self.center_btn and not self.center_button_pressed:
                self.center_button_pressed = True
                self.center_press_time = time.time()
                self._highlight_button(self.center_btn, True)

    def _on_button_release(self, event, button_name=None):
        if not self.test_running:
            return

        if event:
            if event.widget == self.corner_btn and self.corner_button_pressed:
                elapsed = time.time() - self.corner_press_time
                self.corner_time += elapsed
                self.corner_button_pressed = False
                self.corner_press_time = None
                self._update_area_time_labels()
                self._highlight_button(self.corner_btn, False)
            elif event.widget == self.lateral_btn and self.lateral_button_pressed:
                elapsed = time.time() - self.lateral_press_time
                self.lateral_time += elapsed
                self.lateral_button_pressed = False
                self.lateral_press_time = None
                self._update_area_time_labels()
                self._highlight_button(self.lateral_btn, False)
            elif event.widget == self.center_btn and self.center_button_pressed:
                elapsed = time.time() - self.center_press_time
                self.center_time += elapsed
                self.center_button_pressed = False
                self.center_press_time = None
                self._update_area_time_labels()
                self._highlight_button(self.center_btn, False)
        elif button_name:
            if button_name == "Canto" and self.corner_button_pressed:
                elapsed = time.time() - self.corner_press_time
                self.corner_time += elapsed
                self.corner_button_pressed = False
                self.corner_press_time = None
                self._update_area_time_labels()
                self._highlight_button(self.corner_btn, False)
            elif button_name == "Lateral" and self.lateral_button_pressed:
                elapsed = time.time() - self.lateral_press_time
                self.lateral_time += elapsed
                self.lateral_button_pressed = False
                self.lateral_press_time = None
                self._update_area_time_labels()
                self._highlight_button(self.lateral_btn, False)
            elif button_name == "Centro" and self.center_button_pressed:
                elapsed = time.time() - self.center_press_time
                self.center_time += elapsed
                self.center_button_pressed = False
                self.center_press_time = None
                self._update_area_time_labels()
                self._highlight_button(self.center_btn, False)

    def _highlight_button(self, button, is_pressed):
        original_bg = ""
        if button == self.corner_btn:
            original_bg = "red"
        elif button == self.lateral_btn:
            original_bg = "skyblue"
        elif button == self.center_btn:
            original_bg = "forestgreen"

        if is_pressed:
            button.config(relief="sunken", bg="darkgray")
        else:
            button.config(relief="raised", bg=original_bg)

    def _update_area_time_labels(self):
        self.corner_time_label.config(text=f"Tempo no Canto: {self.corner_time:.2f} s")
        self.lateral_time_label.config(text=f"Tempo na Lateral: {self.lateral_time:.2f} s")
        self.center_time_label.config(text=f"Tempo no Centro: {self.center_time:.2f} s")

    def generate_report(self):
        if not self.start_time:
            messagebox.showinfo("Aviso", "Inicie um teste primeiro para gerar o relatório.")
            return

        total_duration = self.test_duration.get()
        # Calcula a duração efetiva do teste
        if self.test_running: # Se o teste ainda está correndo, a duração efetiva é o tempo decorrido até agora
             effective_duration = time.time() - self.start_time
        else: # Se o teste já parou (automaticamente ou manualmente)
             effective_duration = total_duration - self.remaining_time # Tempo total programado - tempo restante

        # Garante que effective_duration não seja zero para evitar divisão por zero
        if effective_duration <= 0:
            effective_duration = 0.001 # Um valor mínimo para evitar erro, embora indique um teste sem duração relevante

        # Calcula as porcentagens
        corner_percent = (self.corner_time / effective_duration) * 100
        lateral_percent = (self.lateral_time / effective_duration) * 100
        center_percent = (self.center_time / effective_duration) * 100

        # Formata o relatório
        report = f"--- Relatório do Teste Open Field ---\n\n"
        report += f"ID do Animal: {self.animal_id.get()}\n"
        report += f"Data/Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Duração Programada do Teste: {total_duration} segundos\n"
        report += f"Duração Efetiva do Teste: {effective_duration:.2f} segundos\n\n"
        report += f"Tempo Acumulado nas Áreas:\n"
        report += f"  Canto: {self.corner_time:.2f} segundos ({corner_percent:.2f}%)\n"
        report += f"  Lateral: {self.lateral_time:.2f} segundos ({lateral_percent:.2f}%)\n"
        report += f"  Centro: {self.center_time:.2f} segundos ({center_percent:.2f}%)\n\n"

        # Exibir no campo de texto do relatório
        self.report_text.config(state="normal")
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, report)
        self.report_text.config(state="disabled")

        # Armazena os dados para o gráfico e exportação
        self.test_data = {
            "ID do Animal": self.animal_id.get(),
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

        # Gera e exibe o gráfico de pizza
        self.show_pie_chart(
            self.test_data["Tempo no Canto (s)"],
            self.test_data["Tempo na Lateral (s)"],
            self.test_data["Tempo no Centro (s)"]
        )


    def show_pie_chart(self, corner_time, lateral_time, center_time):
        # Limpa o frame do gráfico antes de desenhar um novo
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        labels = ['Canto', 'Lateral', 'Centro']
        sizes = [corner_time, lateral_time, center_time]
        colors = ['red', 'skyblue', 'forestgreen']

        # Remove áreas com tempo zero para não aparecerem no gráfico
        filtered_labels = []
        filtered_sizes = []
        filtered_colors = []
        for i, size in enumerate(sizes):
            if size > 0:
                filtered_sizes.append(size)
                filtered_labels.append(labels[i])
                filtered_colors.append(colors[i])

        if not filtered_sizes:
            # Se todos os tempos forem zero, não há gráfico para mostrar
            tk.Label(self.chart_frame, text="Nenhum tempo registrado para exibir o gráfico.", fg="gray").pack(pady=20)
            return

        # Cria a figura para o gráfico de pizza
        fig = plt.Figure(figsize=(5, 4), dpi=100) # Tamanho da figura (largura, altura)
        ax = fig.add_subplot(111)

        # autopct='%1.1f%%' formata a porcentagem com uma casa decimal
        # startangle=90 faz a primeira fatia começar no topo
        wedges, texts, autotexts = ax.pie(filtered_sizes, labels=filtered_labels, colors=filtered_colors,
                                          autopct='%1.1f%%', startangle=90, pctdistance=0.85)

        # Ajusta a cor do texto de porcentagem para ser legível
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontsize(10)
        for text in texts:
            text.set_fontsize(10)

        ax.axis('equal')  # Garante que o círculo seja desenhado como um círculo.
        ax.set_title("Distribuição de Tempo por Área")

        # Integra o gráfico ao Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Adiciona a barra de ferramentas do Matplotlib (zoom, pan, save)
        toolbar = NavigationToolbar2Tk(canvas, self.chart_frame)
        toolbar.update()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True) # Repack para garantir que a barra de ferramentas apareça


    def export_report(self):
        if not self.test_data:
            messagebox.showinfo("Nenhum Dado", "Nenhum relatório foi gerado para exportar.")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")],
                                                title="Salvar Relatório do Teste Open Field")
        if not filepath:
            return

        try:
            report_content = self.report_text.get("1.0", tk.END)
            with open(filepath, mode='w', encoding='utf-8') as file:
                file.write(report_content)
            messagebox.showinfo("Exportação Concluída", f"Relatório exportado com sucesso para:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Erro na Exportação", f"Ocorreu um erro ao exportar o relatório: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = OpenFieldApp(root)
    root.mainloop()