import customtkinter as ctk
import os
import sys
import webbrowser

BRAND_GREEN = "#7AC142"
BRAND_GREEN_HOVER = "#629B35"
BRAND_RED = "#E31E24"
BRAND_RED_HOVER = "#B9181D"
BG_COLOR = "#121212"          
CARD_COLOR = "#1E1E1E"        
INPUT_BG = "#2A2A2A"          

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def criar_input(master, placeholder, width):
    return ctk.CTkEntry(master, placeholder_text=placeholder, width=width, height=50, font=("Arial", 16), fg_color=INPUT_BG, border_width=0, corner_radius=8)

def aplicar_mascara_fixa(event):
    entry = event.widget
    texto = entry.get()
    numeros = ''.join(filter(str.isdigit, texto))
    if len(numeros) > 11: numeros = numeros[:11]
    formatado = numeros
    if len(numeros) > 2: formatado = f"({numeros[:2]}) {numeros[2:]}"
    if len(numeros) > 7: formatado = f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    cursor_pos = entry.index(ctk.INSERT)
    entry.delete(0, 'end')
    entry.insert(0, formatado)
    entry.icursor(cursor_pos + (len(formatado) - len(texto)))

def abrir_whatsapp(telefone):
    num = ''.join(filter(str.isdigit, telefone))
    if num:
        if not num.startswith("55"): num = "55" + num
        webbrowser.open(f"https://wa.me/{num}")