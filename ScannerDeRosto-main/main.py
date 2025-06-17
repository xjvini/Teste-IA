# main.py - VERSÃO FINAL COM BANCO DE DADOS SQLITE

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Label, Frame, Entry, Button, Text
import cv2
import json # Manteremos para formatar os detalhes das emoções
import os
from PIL import Image, ImageTk
from detector import process_frame_for_gui
import threading
import sqlite3 # << NOVO: Importa a biblioteca do SQLite
from datetime import datetime # << NOVO: Para registrar a data e hora

# Variáveis globais
current_image_path = None
analysis_data = None

# ---- FUNÇÕES DO BANCO DE DADOS ----

def setup_database():
    """Cria o arquivo do banco de dados e a tabela 'analises' se não existirem."""
    conn = sqlite3.connect('analises.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_identificador TEXT NOT NULL,
            emocao_dominante TEXT,
            confianca TEXT,
            caminho_imagem TEXT,
            detalhes_emocoes TEXT,
            data_hora TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_result_to_db():
    """Salva os resultados da análise no banco de dados SQLite."""
    nome_id = name_entry.get().strip()
    if not nome_id:
        messagebox.showerror("Erro", "Por favor, insira um nome para identificar a análise.")
        return
    
    # Prepara os dados para inserção
    emocao_dominante = analysis_data.get('emocao_detectada', 'N/A')
    confianca = analysis_data.get('confianca', 'N/A')
    caminho_imagem = analysis_data.get('caminho_original', 'N/A')
    # Usamos JSON para guardar o dicionário completo de emoções em um campo de texto
    detalhes_emocoes = json.dumps(analysis_data.get('emotion', {}))
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = sqlite3.connect('analises.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analises (nome_identificador, emocao_dominante, confianca, caminho_imagem, detalhes_emocoes, data_hora)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nome_id, emocao_dominante, confianca, caminho_imagem, detalhes_emocoes, data_hora))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", f"Análise para '{nome_id}' salva com sucesso no banco de dados!")
        reset_ui()
    except Exception as e:
        messagebox.showerror("Erro de Banco de Dados", f"Não foi possível salvar a análise: {e}")


def view_history():
    """Busca os dados do banco de dados e os exibe na aba de informações."""
    try:
        conn = sqlite3.connect('analises.db')
        cursor = conn.cursor()
        # Busca todos os registros, ordenando pelos mais recentes
        cursor.execute("SELECT nome_identificador, emocao_dominante, confianca, data_hora FROM analises ORDER BY data_hora DESC")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            messagebox.showinfo("Histórico Vazio", "Nenhuma análise foi salva no banco de dados ainda.")
            return

        # Formata o histórico para exibição
        history_string = "HISTÓRICO DE ANÁLISES\n"
        history_string += "-----------------------\n\n"
        for row in rows:
            history_string += f"Nome: {row[0]}\n"
            history_string += f"Emoção: {row[1]} ({row[2]})\n"
            history_string += f"Data: {row[3]}\n"
            history_string += "-----------------------\n"
        
        # Exibe na aba de texto
        update_info_tab(history_string, is_history=True)

    except Exception as e:
        messagebox.showerror("Erro de Banco de Dados", f"Não foi possível carregar o histórico: {e}")


# ---- FUNÇÕES DA INTERFACE (com pequenas modificações) ----
def run_analysis():
    # (Esta função permanece a mesma da etapa anterior)
    global analysis_data
    frame = cv2.imread(current_image_path)
    if frame is None:
        messagebox.showerror("Erro de Leitura", "Não foi possível ler o arquivo de imagem.")
        reset_ui(); return
    processed_frame_cv2, analysis_data = process_frame_for_gui(frame)
    if analysis_data is None:
        messagebox.showwarning("Análise Falhou", "Nenhum rosto foi detectado.")
        reset_ui(); return
    analysis_data["caminho_original"] = current_image_path
    processed_frame_rgb = cv2.cvtColor(processed_frame_cv2, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(processed_frame_rgb)
    display_image(img)
    status_label.config(text=f"Resultado: {analysis_data['emocao_detectada']} ({analysis_data['confianca']})")
    update_info_tab(analysis_data)
    show_save_controls(True)


def update_info_tab(data, is_history=False):
    """Exibe dados detalhados ou o histórico na aba de informações."""
    info_text_widget.config(state="normal")
    info_text_widget.delete('1.0', tk.END)
    
    if is_history:
        info_text_widget.insert('1.0', data)
    else:
        # Lógica para exibir detalhes de uma única análise (como antes)
        info_string = f"DETALHES DA DETECÇÃO ATUAL\n"
        info_string += f"---------------------------\n"
        info_string += f"Arquivo: {os.path.basename(data.get('caminho_original', 'N/A'))}\n"
        info_string += f"Emoção Dominante: {data.get('emocao_detectada', 'N/A')}\n\n"
        info_string += f"Distribuição de Emoções:\n"
        emotions = data.get('emotion', {})
        for emotion, value in emotions.items():
            info_string += f"  - {emotion.capitalize()}: {value:.2f}%\n"
        info_text_widget.insert('1.0', info_string)
        
    info_text_widget.config(state="disabled")

# (As outras funções como select_image, reset_ui, show_save_controls, display_image permanecem as mesmas da etapa anterior)
def select_image():
    global current_image_path, analysis_data
    filepath = filedialog.askopenfilename(title="Selecione uma imagem", filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp")])
    if not filepath: return
    current_image_path = filepath
    analysis_data = None
    reset_ui(clear_image=False)
    display_image(current_image_path)
    status_label.config(text="Analisando... Por favor, aguarde.")
    threading.Thread(target=run_analysis, daemon=True).start()

def reset_ui(clear_image=True):
    if clear_image:
        image_label.config(image='')
        image_label.image = None
    show_save_controls(False)
    name_entry.delete(0, tk.END)
    status_label.config(text="Selecione uma imagem para começar.")
    select_button.config(state="normal")
    info_text_widget.config(state="normal")
    info_text_widget.delete('1.0', tk.END)
    info_text_widget.config(state="disabled")

def show_save_controls(visible):
    if visible: save_frame.pack(pady=10); select_button.config(state="disabled")
    else: save_frame.pack_forget()

def display_image(image_source):
    img = Image.open(image_source) if isinstance(image_source, str) else image_source
    img.thumbnail((380, 250))
    img_tk = ImageTk.PhotoImage(image=img)
    image_label.config(image=img_tk)
    image_label.image = img_tk


# ---- CONFIGURAÇÃO DA JANELA PRINCIPAL ----
root = tk.Tk()
root.title("Analisador de Expressões v2.0") # Versão final!
root.geometry("450x550")

notebook = ttk.Notebook(root)
notebook.pack(pady=15, padx=15, fill="both", expand=True)
analysis_tab, info_tab = Frame(notebook), Frame(notebook)
analysis_tab.pack(fill="both", expand=True); info_tab.pack(fill="both", expand=True)
notebook.add(analysis_tab, text='Análise Principal'); notebook.add(info_tab, text='Detalhes e Histórico')

# ---- WIDGETS DA ABA DE ANÁLISE ----
select_button = Button(analysis_tab, text="1. Selecionar Imagem", command=select_image, font=("Helvetica", 12))
select_button.pack(fill='x', padx=10, pady=5)
status_label = Label(analysis_tab, text="Selecione uma imagem para começar.", pady=10)
status_label.pack()
image_label = Label(analysis_tab)
image_label.pack(pady=10)
save_frame = Frame(analysis_tab)
Label(save_frame, text="2. Digite um nome e salve ou inicie uma nova análise:").pack(fill='x')
name_entry = Entry(save_frame, width=40)
name_entry.pack(pady=5)
buttons_subframe = Frame(save_frame)
buttons_subframe.pack(pady=5)
# O botão de salvar agora chama a nova função de banco de dados
Button(buttons_subframe, text="Salvar Resultado", command=save_result_to_db).pack(side='left', padx=10)
Button(buttons_subframe, text="Nova Análise", command=reset_ui).pack(side='right', padx=10)
show_save_controls(False)

# ---- WIDGETS DA ABA DE INFORMAÇÕES ----
# Adiciona um botão para ver o histórico
Button(info_tab, text="Ver Histórico de Análises", command=view_history).pack(pady=10)
info_text_widget = Text(info_tab, wrap='word', font=("Courier New", 10), state="disabled")
info_text_widget.pack(expand=True, fill="both", padx=10, pady=5)

# ---- INICIALIZAÇÃO ----
setup_database() # Garante que o banco de dados e a tabela existam ao iniciar
root.mainloop()