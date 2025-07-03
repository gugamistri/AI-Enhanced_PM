import os
import sys
import markdown
import pdfkit
from PyPDF2 import PdfMerger

BOOK_ROOT = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_DIR = os.path.join(BOOK_ROOT, "chapters")
COVERS_DIR = os.path.join(BOOK_ROOT, "covers")
APPENDICES_DIR = os.path.join(BOOK_ROOT, "appendices")
ASSETS_DIR = os.path.join(BOOK_ROOT, "assets")
CSS_FILE = os.path.join(ASSETS_DIR, "css", "style.css")
OUTPUT_HTML = os.path.join(BOOK_ROOT, "book_combined.html")

# Novo: idioma opcional via argumento de linha de comando
def get_lang():
    if len(sys.argv) > 1:
        return sys.argv[1].lower()
    return "en"

LANG = get_lang()

# Novo: nome do PDF de saída depende do idioma
OUTPUT_PDF = os.path.join(
    BOOK_ROOT,
    f"AI_Enhanced_Product_Management{'_' + LANG if LANG != 'en' else ''}.pdf"
)
COVER_PDF = os.path.join(BOOK_ROOT, f"cover_only_{LANG}.pdf")
BOOK_PDF = os.path.join(BOOK_ROOT, f"book_content_{LANG}.pdf")
COVER_HTML = os.path.join(BOOK_ROOT, f"cover_only_{LANG}.html")
BOOK_HTML = os.path.join(BOOK_ROOT, f"book_content_{LANG}.html")

def collect_markdown_files(directory, lang=None):
    files = []
    for f in os.listdir(directory):
        if lang and lang != "en":
            if f.endswith(f"_{lang}.md"):
                files.append(os.path.join(directory, f))
        else:
            # Pega apenas arquivos sem sufixo de idioma
            if f.endswith(".md") and not f.endswith(f"_{'pt'}.md"):
                files.append(os.path.join(directory, f))
    return sorted(files)

def convert_markdown_to_html(md_file):
    with open(md_file, "r", encoding="utf-8") as f:
        text = f.read()
        return markdown.markdown(text, extensions=["extra", "toc", "tables"])

def read_html(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        text = f.read()
        return text

def extract_title_from_markdown(md_file):
    """Extrai o primeiro título H1 do arquivo markdown"""
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Procura por títulos H1 com diferentes formatos
            if line.startswith("# "):
                title = line[2:].strip()
                # Remove markdown adicional como asteriscos
                title = title.replace("*", "").replace("**", "")
                return title
            elif line.startswith("#") and not line.startswith("##"):
                title = line[1:].strip()
                title = title.replace("*", "").replace("**", "")
                return title
    
    # Fallback: usar nome do arquivo
    basename = os.path.basename(md_file).replace(".md", "")
    return basename.replace("_", " ").title()

def generate_table_of_contents(lang=None):
    """Gera o HTML do índice com base nos capítulos disponíveis"""
    toc_entries = []
    page_counter = 2  # Página 1 é a capa, página 2 é o índice
    
    # Título do índice baseado no idioma
    toc_title = "Índice" if lang == "pt" else "Table of Contents"
    
    # Introdução
    intro_files = collect_markdown_files(CHAPTERS_DIR, lang=lang)
    intro_file = None
    for f in intro_files:
        if "introduction" in os.path.basename(f).lower():
            intro_file = f
            break
    
    if intro_file:
        title = extract_title_from_markdown(intro_file)
        page_counter += 1
        toc_entries.append({"title": title, "page": page_counter})
    
    # Capítulos
    chapter_files = [f for f in intro_files if "chapter_" in os.path.basename(f) and "introduction" not in os.path.basename(f).lower()]
    chapter_files.sort(key=lambda x: int(os.path.basename(x).split("_")[1].split(".")[0]) if "chapter_" in x else 0)
    
    for chapter_file in chapter_files:
        title = extract_title_from_markdown(chapter_file)
        page_counter += 1
        toc_entries.append({"title": title, "page": page_counter})
    
    # Apêndices
    appendix_files = collect_markdown_files(APPENDICES_DIR, lang=lang)
    for appendix_file in appendix_files:
        title = extract_title_from_markdown(appendix_file)
        page_counter += 1
        toc_entries.append({"title": title, "page": page_counter})
    
    # Debug: Verificar se há entradas
    if not toc_entries:
        toc_html = f"<div class='toc'><h1>{toc_title}</h1>"
        toc_html += "<p style='color: red; font-size: 14pt;'>ERRO: Nenhum capítulo encontrado para o índice!</p>"
        toc_html += "</div>"
        return toc_html
    
    # Gerar HTML do índice
    toc_html = f"<div class='toc'><h1>{toc_title}</h1>"
    toc_html += f"<p style='color: blue; font-size: 10pt; margin-bottom: 20px;'</p>"
    
    for entry in toc_entries:
        toc_html += f'''
        <div class="toc-entry">
            <span class="toc-title">{entry["title"]}</span>
            <span class="toc-dots"></span>
            <span class="toc-page-number">{entry["page"]}</span>
        </div>
        '''
    toc_html += "</div>"
    
    return toc_html

def merge_sections_to_html():
    html_parts = []

    # Cover Page
    cover_html = os.path.join(COVERS_DIR, f"cover_{LANG}.html") if LANG != "en" else os.path.join(COVERS_DIR, "cover_en.html")
    if os.path.exists(cover_html):
        cover_content = read_html(cover_html)
        html_parts.append("<div class='cover-page'>")
        html_parts.append(cover_content)
        html_parts.append("</div>")
        html_parts.append("<div class='page-break'></div>")

    # Table of Contents
    toc_content = generate_table_of_contents(lang=LANG)
    html_parts.append("<div class='toc-page'>")
    html_parts.append(toc_content)
    html_parts.append("</div>")
    html_parts.append("<div class='page-break'></div>")

    # Separar introdução dos capítulos
    all_chapter_files = collect_markdown_files(CHAPTERS_DIR, lang=LANG)
    
    # Introdução primeiro
    intro_files = [f for f in all_chapter_files if "introduction" in os.path.basename(f).lower()]
    for md in intro_files:
        html_parts.append("<div class='content-page'>")
        html_parts.append(convert_markdown_to_html(md))
        html_parts.append("</div>")
        html_parts.append("<div class='page-break'></div>")

    # Capítulos ordenados
    chapter_files = [f for f in all_chapter_files if "chapter_" in os.path.basename(f) and "introduction" not in os.path.basename(f).lower()]
    chapter_files.sort(key=lambda x: int(os.path.basename(x).split("_")[1].split(".")[0]) if "chapter_" in x else 0)
    
    for md in chapter_files:
        html_parts.append("<div class='content-page'>")
        html_parts.append(convert_markdown_to_html(md))
        html_parts.append("</div>")
        html_parts.append("<div class='page-break'></div>")

    # Appendices
    for md in collect_markdown_files(APPENDICES_DIR, lang=LANG):
        html_parts.append("<div class='content-page'>")
        html_parts.append(convert_markdown_to_html(md))
        html_parts.append("</div>")
        html_parts.append("<div class='page-break'></div>")

    # CSS INCORPORADO PARA CONTROLAR MARGENS E FONTE
    font_path = os.path.join(ASSETS_DIR, "fonts", "OpenSans-Regular.ttf")
    css_styles = f"""
    <style>
        @font-face {{
            font-family: 'OpenSans';
            src: url('file://{font_path}') format('truetype');
            font-weight: normal;
            font-style: normal;
        }}
        
        /* Reset global */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'OpenSans', Arial, sans-serif;
        }}
        
        body {{
            font-family: 'OpenSans', Arial, sans-serif;
            line-height: 1.6;
            font-size: 10pt;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'OpenSans', Arial, sans-serif;
            font-weight: normal;
            margin-bottom: 0.5em;
        }}
        
        p {{
            margin-bottom: 1em;
            text-align: justify;
        }}
        
        .cover-page {{ margin: 0 !important; padding: 0 !important; page-break-after: always; }}
        .toc-page {{ padding: 0; page-break-after: always; }}
        .content-page {{ padding: 0; page-break-after: always; }}
        .page-break {{ page-break-after: always; height: 0; margin: 0; padding: 0; }}
        
        /* Estilos específicos por tipo de página */
        .cover-page * {{ font-family: 'OpenSans', Arial, sans-serif; }}
        
        /* Estilos para índice */
        .toc {{ 
            padding: 20px; 
            background-color: white;
            color: black;
        }}
        .toc h1 {{ 
            font-size: 18pt; 
            margin-bottom: 30px; 
            text-align: center; 
            font-weight: bold;
            color: black !important;
            font-family: 'OpenSans', Arial, sans-serif !important;
        }}
        .toc-entry {{ 
            margin-bottom: 12px; 
            display: flex; 
            align-items: baseline;
            line-height: 1.6;
            color: black;
        }}
        .toc-title {{ 
            flex: 0 0 auto; 
            margin-right: 10px; 
            font-size: 12pt;
            color: black !important;
            font-family: 'OpenSans', Arial, sans-serif !important;
        }}
        .toc-dots {{ 
            flex: 1; 
            border-bottom: 2px dotted #333; 
            margin: 0 8px; 
            height: 1px;
            margin-bottom: 4px;
        }}
        .toc-page-number {{ 
            flex: 0 0 auto; 
            font-weight: bold; 
            font-size: 12pt;
            color: black !important;
            font-family: 'OpenSans', Arial, sans-serif !important;
        }}
        
        /* Estilos para conteúdo */
        .content-page h1 {{ 
            font-size: 14pt; 
            margin-bottom: 15px; 
            margin-top: 0;
            font-weight: bold;
        }}
        .content-page h2 {{ 
            font-size: 12pt; 
            margin-bottom: 10px; 
            margin-top: 15px;
            font-weight: bold;
        }}
        .content-page h3 {{ 
            font-size: 11pt; 
            margin-bottom: 8px; 
            margin-top: 12px;
            font-weight: bold;
        }}
        .content-page p {{ 
            text-align: justify; 
            margin-bottom: 10px;
            text-indent: 0;
        }}
        .content-page ul, .content-page ol {{ 
            margin-bottom: 0px; 
            padding-left: 0px;
        }}
        .content-page li {{ 
            margin-bottom: 0px; 
        }}
        
        @media print {{
            .cover-page {{ margin: 0 !important; padding: 0 !important; }}
            .toc-page {{ padding: 0 !important; }}
            .content-page {{ padding: 0 !important; }}
            @page:first {{ margin: 0; }}
            @page {{ margin: 20mm 15mm 20mm 15mm; size: A5; }}
        }}
        
        @import url("{CSS_FILE}");
    </style>
    """

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='utf-8'>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {css_styles}
    </head>
    <body>
        {"".join(html_parts)}
    </body>
    </html>
    """

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_template)

    return OUTPUT_HTML

def generate_pdf(html_path, output_pdf, margin_opts=None):
    options = {
        "enable-local-file-access": "",
        "page-size": "A5",
        "encoding": "UTF-8",
        "print-media-type": "",
        "no-pdf-compression": "",
        "disable-smart-shrinking": "",
        "zoom": 1.0,
        "margin-top": "20mm",
        "margin-bottom": "20mm",
        "margin-left": "15mm",
        "margin-right": "15mm",
    }
    pdfkit.from_file(html_path, output_pdf, options=options)
    print(f"✅ PDF gerado: {output_pdf}")

def merge_cover_to_html():
    # Apenas a capa, sem margens
    html_parts = []
    cover_html = os.path.join(COVERS_DIR, f"cover_{LANG}.html") if LANG != "en" else os.path.join(COVERS_DIR, "cover_en.html")
    if os.path.exists(cover_html):
        cover_content = read_html(cover_html)
        html_parts.append("<div class='cover-page no-margin'>")
        html_parts.append(cover_content)
        html_parts.append("</div>")
    css_styles = f"""
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        .cover-page.no-margin {{ margin: 0 !important; padding: 0 !important; width: 100vw; height: 100vh; }}
        .cover-page.no-margin .cover {{ margin: 0 !important; width: 148mm !important; height: 210mm !important; }}
        @media print {{
            .cover-page.no-margin {{ margin: 0 !important; padding: 0 !important; }}
            @page:first {{ margin: 0; }}
            @page {{ margin: 0; size: A5; }}
        }}
        @import url("{CSS_FILE}");
    </style>
    """
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='utf-8'>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {css_styles}
    </head>
    <body>
        {''.join(html_parts)}
    </body>
    </html>
    """
    with open(COVER_HTML, "w", encoding="utf-8") as f:
        f.write(html_template)
    return COVER_HTML

def merge_book_to_html():
    # Conteúdo do livro (sem a capa)
    html_parts = []
    # Aqui você pode adicionar índice, capítulos, apêndices normalmente
    # Chapters
    for md in collect_markdown_files(CHAPTERS_DIR, lang=LANG):
        html_parts.append("<div class='content-page with-margin'>")
        html_parts.append(convert_markdown_to_html(md))
        html_parts.append("</div>")
        html_parts.append("<div class='page-break'></div>")
    # Appendices
    for md in collect_markdown_files(APPENDICES_DIR, lang=LANG):
        html_parts.append("<div class='content-page with-margin'>")
        html_parts.append(convert_markdown_to_html(md))
        html_parts.append("</div>")
        html_parts.append("<div class='page-break'></div>")
    css_styles = f"""
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        .content-page.with-margin {{ padding: 0; page-break-after: always; }}
        .page-break {{ page-break-after: always; height: 0; margin: 0; padding: 0; }}
        @media print {{
            .content-page.with-margin {{ padding: 0 !important; }}
            /* Remover margens do @page */
        }}
        @import url("{CSS_FILE}");
    </style>
    """
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='utf-8'>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {css_styles}
    </head>
    <body>
        {''.join(html_parts)}
    </body>
    </html>
    """
    with open(BOOK_HTML, "w", encoding="utf-8") as f:
        f.write(html_template)
    return BOOK_HTML

def merge_pdfs(cover_pdf, book_pdf, output_pdf):
    merger = PdfMerger()
    merger.append(cover_pdf)
    merger.append(book_pdf)
    merger.write(output_pdf)
    merger.close()
    print(f"✅ PDF final combinado: {output_pdf}")

if __name__ == "__main__":
    # 1. Gerar HTML e PDF da capa
    cover_html = merge_cover_to_html()
    generate_pdf(cover_html, COVER_PDF, {
        "margin-top": "0mm",
        "margin-bottom": "0mm",
        "margin-left": "0mm",
        "margin-right": "0mm",
    })
    # 2. Gerar HTML e PDF do conteúdo do livro
    book_html = merge_book_to_html()
    generate_pdf(book_html, BOOK_PDF)
    # 3. Merge dos dois PDFs
    merge_pdfs(COVER_PDF, BOOK_PDF, OUTPUT_PDF)