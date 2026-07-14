import os
import sys
import webbrowser

import customtkinter as ctk


APP_NAME = "Poupe Farma"
APP_VERSION = "0.9.1"

BRAND_GREEN = "#7AC142"
BRAND_GREEN_HOVER = "#629B35"
BRAND_RED = "#E31E24"
BRAND_RED_HOVER = "#B9181D"
BRAND_YELLOW = "#E5B800"

BG_COLOR = "#121212"
CARD_COLOR = "#1E1E1E"
INPUT_BG = "#2A2A2A"
TEXT_MUTED = "#AAAAAA"


def resource_path(relative_path):
    base = getattr(
        sys,
        "_MEIPASS",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
    return os.path.join(base, relative_path)


def criar_input(master, placeholder, width):
    return ctk.CTkEntry(
        master,
        placeholder_text=placeholder,
        width=width,
        height=50,
        font=("Arial", 16),
        fg_color=INPUT_BG,
        border_width=0,
        corner_radius=8,
    )


def aplicar_mascara_fixa(event):
    entry = event.widget
    numeros = "".join(filter(str.isdigit, entry.get()))[:11]

    if len(numeros) <= 2:
        texto = numeros
    elif len(numeros) <= 7:
        texto = f"({numeros[:2]}) {numeros[2:]}"
    else:
        texto = f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"

    entry.delete(0, "end")
    entry.insert(0, texto)
    entry.icursor("end")


def formatar_telefone(telefone):
    numeros = "".join(filter(str.isdigit, telefone or ""))

    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"

    if len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"

    return str(telefone or "").strip() or "Não informado"


def formatar_endereco(dados, fallback="Endereço não informado"):
    endereco = str(dados.get("endereco") or "").strip()
    numero = str(dados.get("numero") or "").strip()
    bairro = str(dados.get("bairro") or "").strip()
    complemento = str(dados.get("complemento") or "").strip()

    partes = []

    if endereco:
        partes.append(f"{endereco}, {numero}" if numero else endereco)
    elif numero:
        partes.append(f"Nº {numero}")

    if bairro:
        partes.append(bairro)

    if complemento:
        partes.append(complemento)

    return " - ".join(partes) if partes else fallback


def texto_opcional(valor, fallback="Não informado"):
    texto = str(valor or "").strip()
    texto_util = (
        texto.replace("Nº", "")
        .replace("N°", "")
        .replace(",", "")
        .replace("-", "")
        .replace(".", "")
        .strip()
    )
    return texto if texto_util else fallback


def abrir_whatsapp(telefone):
    numero = "".join(filter(str.isdigit, telefone or ""))

    if not numero:
        return

    if not numero.startswith("55"):
        numero = "55" + numero

    webbrowser.open(f"https://wa.me/{numero}")


def criar_popup(master, titulo, largura, altura):
    janela = ctk.CTkToplevel(master)
    janela.title(titulo)
    janela.resizable(False, False)
    janela.configure(fg_color=BG_COLOR)
    janela.transient(master.winfo_toplevel())
    janela.grab_set()

    janela.update_idletasks()
    x = janela.winfo_screenwidth() // 2 - largura // 2
    y = janela.winfo_screenheight() // 2 - altura // 2
    janela.geometry(f"{largura}x{altura}+{x}+{y}")

    card = ctk.CTkFrame(
        janela,
        fg_color=CARD_COLOR,
        corner_radius=18,
        border_width=1,
        border_color="#303030",
    )
    card.pack(fill="both", expand=True, padx=22, pady=22)

    return janela, card


def criar_bloco_info(
    master,
    titulo,
    valor,
    cor="white",
    destaque=False,
    wraplength=510,
):
    frame = ctk.CTkFrame(
        master,
        fg_color=INPUT_BG,
        corner_radius=10,
    )
    frame.pack(fill="x", padx=26, pady=6)

    ctk.CTkLabel(
        frame,
        text=titulo,
        font=("Arial", 10, "bold"),
        text_color=TEXT_MUTED,
    ).pack(anchor="w", padx=15, pady=(11, 2))

    fonte = ("Arial", 16, "bold") if destaque else ("Arial", 14)

    ctk.CTkLabel(
        frame,
        text=valor,
        font=fonte,
        text_color=cor,
        wraplength=wraplength,
        justify="left",
    ).pack(anchor="w", padx=15, pady=(0, 12))

    return frame