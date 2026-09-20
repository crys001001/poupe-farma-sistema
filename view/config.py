import os
import sys
import webbrowser

import customtkinter as ctk


APP_NAME = "Sistema de Cadastro"
APP_VERSION = "1.2.0"

BRAND_GREEN = "#72C746"
BRAND_GREEN_HOVER = "#5AA535"
BRAND_RED = "#E05252"
BRAND_RED_HOVER = "#B93D3D"
BRAND_YELLOW = "#E7B93F"

BG_COLOR = "#0B100D"
SIDEBAR_COLOR = "#111713"
CARD_COLOR = "#161E19"
CARD_HOVER = "#1B2720"
INPUT_BG = "#202A24"
BORDER_COLOR = "#2C3931"
TEXT_COLOR = "#F3F7F4"
TEXT_MUTED = "#9BA9A0"
FONT_FAMILY = "Segoe UI"


def resource_path(relative_path):
    base = getattr(
        sys,
        "_MEIPASS",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
    return os.path.join(base, relative_path)


def criar_input(master, placeholder, width, *, height=48):
    return ctk.CTkEntry(
        master,
        placeholder_text=placeholder,
        width=width,
        height=height,
        font=(FONT_FAMILY, 15),
        fg_color=INPUT_BG,
        border_color=BORDER_COLOR,
        border_width=1,
        corner_radius=10,
    )


def aplicar_mascara_fixa(event):
    entry = event.widget
    numeros = "".join(filter(str.isdigit, entry.get()))[:11]

    if len(numeros) <= 2:
        texto = numeros
    else:
        restante = numeros[2:]
        texto = f"({numeros[:2]}) {restante}"
        if len(restante) > 4:
            texto = f"({numeros[:2]}) {restante[:-4]}-{restante[-4:]}"

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

    # Números nacionais têm 10 ou 11 dígitos. Só considera o 55
    # como código do Brasil quando ele realmente veio junto do número.
    if not (numero.startswith("55") and len(numero) in (12, 13)):
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
        corner_radius=16,
        border_width=1,
        border_color=BORDER_COLOR,
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
        font=(FONT_FAMILY, 11, "bold"),
        text_color=TEXT_MUTED,
    ).pack(anchor="w", padx=15, pady=(11, 2))

    fonte = (FONT_FAMILY, 16, "bold") if destaque else (FONT_FAMILY, 14)

    ctk.CTkLabel(
        frame,
        text=valor,
        font=fonte,
        text_color=cor,
        wraplength=wraplength,
        justify="left",
    ).pack(anchor="w", padx=15, pady=(0, 12))

    return frame
