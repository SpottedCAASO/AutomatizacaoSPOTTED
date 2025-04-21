# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2025 Seu Nome
#
# Este programa é software livre: você pode redistribuí-lo e/ou modificá-lo
# sob os termos da Licença Pública Geral GNU publicada pela Free Software Foundation,
# na versão 3 da licença ou qualquer versão posterior.
#
# Este programa é distribuído na expectativa de que seja útil,
# mas SEM NENHUMA GARANTIA; nem mesmo a garantia implícita de
# COMERCIABILIDADE ou ADEQUAÇÃO A UM DETERMINADO PROPÓSITO.
# Veja a Licença Pública Geral GNU para mais detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa. Se não, veja <https://www.gnu.org/licenses/>.
# Primeira versão feita por confuser e depois editada pelo PIX (do #SpottedCAASO)
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import re
import requests
from emoji import is_emoji

# ─── CONFIGURAÇÕES ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

image_path = os.path.join(BASE_DIR, "assets", "Formato 45 Preto.png")
excel_path = os.path.join(BASE_DIR, "assets", "Planilha.xlsx")
output_path = os.path.join(BASE_DIR, "output")
TWEMOJI_PATH = os.path.join(BASE_DIR, "twemoji", "72x72")

text_area_width = 885
text_area_height = 990
text_area_top_left = ((1080 - text_area_width) // 2, 160)

main_font_path = os.path.join(BASE_DIR, "fonts", "nourd_bold.ttf")
emoji_font_path = os.path.join(BASE_DIR, "fonts", "NotoColorEmoji-Regular.ttf")

min_font_size = 30
max_font_size = 60

extra_paragraph_spacing = 50
line_spacing = 15

def tokenize_text(text):
    tokens = []
    i = 0
    while i < len(text):
        if is_emoji(text[i]):
            tokens.append(text[i])
            i += 1
        elif text[i].isspace():
            space = text[i]
            i += 1
            while i < len(text) and text[i].isspace():
                space += text[i]
                i += 1
            tokens.append(space)
        else:
            word = text[i]
            i += 1
            while i < len(text) and not is_emoji(text[i]) and not text[i].isspace():
                word += text[i]
                i += 1
            tokens.append(word)
    return tokens

def get_emoji_image(char):
    codepoint = '-'.join(f"{ord(c):x}" for c in char)
    local_path = os.path.join(TWEMOJI_PATH, f"{codepoint}.png")

    # Se já existe localmente, retorna
    if os.path.exists(local_path):
        return Image.open(local_path).convert("RGBA")

    # Caso contrário, tenta baixar do CDN do Twemoji
    url = f"https://github.com/twitter/twemoji/tree/master/assets/72x72/{codepoint}.png"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            os.makedirs(TWEMOJI_PATH, exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(response.content)
            return Image.open(local_path).convert("RGBA")
    except Exception as e:
        print(f"[ERRO AO BAIXAR EMOJI] {codepoint}: {e}")

    print(f"[EMOJI NÃO ENCONTRADO] Código: {codepoint}")
    return None

def wrap_text(draw, text, font, max_width):
    paragraphs = text.split('\n')
    lines = []
    for paragraph in paragraphs:
        if not paragraph.strip():
            lines.append("<PARAGRAPH_BREAK>")
            continue
        tokens = tokenize_text(paragraph)
        current_line = []
        line_width = 0
        for token in tokens:
            token_width = 0
            if is_emoji(token):
                emoji_img = get_emoji_image(token)
                token_width = emoji_img.width if emoji_img else font.size
            else:
                bbox = draw.textbbox((0, 0), token, font=font)
                token_width = bbox[2] - bbox[0]

            if line_width + token_width <= max_width:
                current_line.append(token)
                line_width += token_width
            else:
                lines.append("".join(current_line))
                current_line = [token]
                line_width = token_width
        if current_line:
            lines.append("".join(current_line))
        lines.append("<PARAGRAPH_BREAK>")
    if lines and lines[-1] == "<PARAGRAPH_BREAK>":
        lines.pop()
    return lines

def get_line_height(line, font, draw):
    if line == "<PARAGRAPH_BREAK>":
        return extra_paragraph_spacing
    height = 0
    for char in line:
        if is_emoji(char):
            height = max(height, font.size + line_spacing)
        else:
            bbox = draw.textbbox((0, 0), char, font=font)
            height = max(height, bbox[3] - bbox[1] + line_spacing)
    return height

def split_lines_into_pages(lines, font, draw):
    pages = []
    current_page = []
    current_height = 0
    for line in lines:
        line_height = get_line_height(line, font, draw)
        if current_height + line_height > text_area_height and current_page:
            pages.append(current_page)
            current_page = [line]
            current_height = line_height
        else:
            current_page.append(line)
            current_height += line_height
    if current_page:
        pages.append(current_page)
    return pages

def find_optimal_font(text, draw):
    font_size = min_font_size
    lines = wrap_text(draw, text, ImageFont.truetype(main_font_path, font_size), text_area_width)
    pages = split_lines_into_pages(lines, ImageFont.truetype(main_font_path, font_size), draw)

    if len(pages) == 1:
        while font_size < max_font_size:
            next_font = ImageFont.truetype(main_font_path, font_size + 1)
            test_lines = wrap_text(draw, text, next_font, text_area_width)
            test_pages = split_lines_into_pages(test_lines, next_font, draw)
            if len(test_pages) > 1:
                break
            font_size += 1
            lines = test_lines
            pages = test_pages
        return ImageFont.truetype(main_font_path, font_size), pages
    else:
        num_pages = len(pages)
        best_font_size = font_size
        while font_size < max_font_size:
            next_font = ImageFont.truetype(main_font_path, font_size + 1)
            test_lines = wrap_text(draw, text, next_font, text_area_width)
            test_pages = split_lines_into_pages(test_lines, next_font, draw)
            if len(test_pages) > num_pages:
                break
            font_size += 1
            lines = test_lines
            pages = test_pages
            best_font_size = font_size
        return ImageFont.truetype(main_font_path, best_font_size), pages

def draw_text_with_emojis(draw, x, y, text, base_font, color, image):
    current_x = x
    for char in text:
        if is_emoji(char):
            emoji_img = get_emoji_image(char)
            if emoji_img:
                emoji_resized = emoji_img.resize((base_font.size, base_font.size), Image.LANCZOS)
                image.paste(emoji_resized, (current_x, y), emoji_resized)
                current_x += emoji_resized.width
            else:
                draw.rectangle([current_x, y, current_x + base_font.size, y + base_font.size], outline=color, width=2)
                current_x += base_font.size
        else:
            font = ImageFont.truetype(main_font_path, base_font.size)
            bbox = draw.textbbox((0, 0), char, font=font)
            draw.text((current_x, y), char, font=font, fill=color)
            current_x += bbox[2] - bbox[0]

def draw_page(image, lines, font):
    draw = ImageDraw.Draw(image)
    color = get_contrasting_color(image)
    total_height = sum(get_line_height(line, font, draw) for line in lines)
    y = text_area_top_left[1] + max((text_area_height - total_height) // 2, 0)
    for line in lines:
        if line == "<PARAGRAPH_BREAK>":
            y += extra_paragraph_spacing
        else:
            line_width = 0
            for char in line:
                if is_emoji(char):
                    emoji_img = get_emoji_image(char)
                    line_width += emoji_img.width if emoji_img else font.size
                else:
                    bbox = draw.textbbox((0, 0), char, font=font)
                    line_width += bbox[2] - bbox[0]
            x = text_area_top_left[0] + (text_area_width - line_width) // 2
            draw_text_with_emojis(draw, x, y, line, font, color, image)
            y += get_line_height(line, font, draw)

def get_contrasting_color(image):
    bg_color = image.getpixel((text_area_top_left[0] + 1, text_area_top_left[1] + 1))
    return (255, 255, 255) if sum(bg_color[:3]) < 382 else (0, 0, 0)

def create_images_for_text(text, count):
    base_img = Image.open(image_path)
    draw = ImageDraw.Draw(base_img)
    font, pages = find_optimal_font(text, draw)
    for i, page in enumerate(pages, start=1):
        img = Image.open(image_path)
        draw_page(img, page, font)
        img.save(os.path.join(output_path, f"post_{count}_{i}.png"))

if not os.path.exists(output_path):
    os.makedirs(output_path)

df = pd.read_excel(excel_path, usecols=[0])
for idx, row in df.iterrows():
    text = str(row[0])
    create_images_for_text(text.upper(), idx + 1)
