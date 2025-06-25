import os
import markdown
import pdfkit

BOOK_ROOT = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_DIR = os.path.join(BOOK_ROOT, "chapters")
COVERS_DIR = os.path.join(BOOK_ROOT, "covers")
APPENDICES_DIR = os.path.join(BOOK_ROOT, "appendices")
ASSETS_DIR = os.path.join(BOOK_ROOT, "assets")
CSS_FILE = os.path.join(ASSETS_DIR, "css", "style.css")
OUTPUT_HTML = os.path.join(BOOK_ROOT, "book_combined.html")
OUTPUT_PDF = os.path.join(BOOK_ROOT, "AI_Enhanced_Product_Management.pdf")

def collect_markdown_files(directory):
    return sorted([
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".md")
    ])

def convert_markdown_to_html(md_file):
    with open(md_file, "r", encoding="utf-8") as f:
        text = f.read()
        return markdown.markdown(text, extensions=["extra", "toc", "tables"])

def read_html(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        text = f.read()
        return text

def merge_sections_to_html():
    html_parts = []

    # Cover Page - COM CLASSE ESPECIAL PARA SEM MARGEM
    cover_html = os.path.join(COVERS_DIR, "cover_en.html")
    if os.path.exists(cover_html):
        cover_content = read_html(cover_html)
        # Envolver a capa em uma div com classe especial
        html_parts.append("<div class='cover-page no-margin'>")
        html_parts.append(cover_content)
        html_parts.append("</div>")
        html_parts.append("<div class='page-break'></div>")

    # Chapters - COM MARGEM NORMAL
    for md in collect_markdown_files(CHAPTERS_DIR):
        html_parts.append("<div class='content-page with-margin'>")
        html_parts.append(convert_markdown_to_html(md))
        html_parts.append("</div>")
        html_parts.append("<div class='page-break'></div>")

    # Appendices - COM MARGEM NORMAL
    for md in collect_markdown_files(APPENDICES_DIR):
        html_parts.append("<div class='content-page with-margin'>")
        html_parts.append(convert_markdown_to_html(md))
        html_parts.append("</div>")
        html_parts.append("<div class='page-break'></div>")

    # CSS INCORPORADO PARA CONTROLAR MARGENS
    css_styles = """
    <style>
        /* Reset global */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        /* Página da capa - SEM MARGEM */
        .cover-page.no-margin {
            margin: 0 !important;
            padding: 0 !important;
            width: 100vw;
            height: 100vh;
            page-break-after: always;
        }
        
        .cover-page.no-margin .cover {
            margin: 0 !important;
            width: 148mm !important;
            height: 210mm !important;
            page-break-after: always;
        }
        
        /* Páginas de conteúdo - COM MARGEM */
        .content-page.with-margin {
            margin: 15mm;
            padding: 0;
            page-break-after: always;
        }
        
        /* Quebra de página */
        .page-break {
            page-break-after: always;
            height: 0;
            margin: 0;
            padding: 0;
        }
        
        /* Estilos específicos para impressão */
        @media print {
            .cover-page.no-margin {
                margin: 0 !important;
                padding: 0 !important;
            }
            
            .content-page.with-margin {
                margin: 15mm !important;
            }
            
            @page:first {
                margin: 0;
            }
            
            @page {
                margin: 15mm;
                size: A5;
            }
        }
        
        /* Importar CSS externo se existir */
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

def generate_pdf(html_path):
    options = {
        "enable-local-file-access": "",
        "page-size": "A5",
        # REMOVER MARGENS GLOBAIS - SERÃO CONTROLADAS POR CSS
        "margin-top": "0mm",
        "margin-bottom": "0mm", 
        "margin-left": "0mm",
        "margin-right": "0mm",
        "encoding": "UTF-8",
        "print-media-type": "",
        "no-pdf-compression": "",
        # Opções adicionais para melhor controle
        "disable-smart-shrinking": "",
        "zoom": 1.0,
    }

    pdfkit.from_file(html_path, OUTPUT_PDF, options=options)
    print(f"✅ PDF generated at: {OUTPUT_PDF}")

if __name__ == "__main__":
    html_file = merge_sections_to_html()
    generate_pdf(html_file)