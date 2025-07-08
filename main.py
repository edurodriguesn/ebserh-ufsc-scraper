import requests
from bs4 import BeautifulSoup
import io
import PyPDF2
import enviar_mensagem as telegram

BASE_URL = "https://www.gov.br"
START_URL = "https://www.gov.br/ebserh/pt-br/acesso-a-informacao/agentes-publicos/concursos-e-selecoes/concursos/2024/convocacoes/hu-ufsc"

def fetch_main_entries():
    response = requests.get(START_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    entries_div = soup.find("div", class_="entries")
    if not entries_div:
        print("Div com class='entries' não encontrada.")
        return []
    article_links = []
    for article in entries_div.find_all("article", class_="entry"):
        summary = article.find("span", class_="summary")
        if summary and summary.find("a"):
            href = summary.find("a")["href"]
            if href.startswith("http"):
                article_links.append(href)
            else:
                article_links.append(BASE_URL + href)
    return article_links


def fetch_pdf_link_from_entry(entry_url):
    response = requests.get(entry_url)
    soup = BeautifulSoup(response.text, "html.parser")
    content = soup.find("div", id="content-core")
    if not content:
        return None
    for p in content.find_all("p"):
        a = p.find("a")
        if a and a.get("href", "").endswith("/file"):
            return a["href"] if a["href"].startswith("http") else BASE_URL + a["href"]
    return None

def download_and_check_pdf(pdf_url, search_phrase):
    response = requests.get(pdf_url)
    
    # Verifica se é um PDF antes de continuar
    if "application/pdf" not in response.headers.get("Content-Type", ""):
        print(f"URL não retornou um PDF válido: {pdf_url}")
        return False

    try:
        with io.BytesIO(response.content) as pdf_file:
            print(f"Baixando PDF de: {pdf_url}")
            print(f"Tamanho do conteúdo: {len(response.content)} bytes")
            reader = PyPDF2.PdfReader(pdf_file)
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() or ""
            return search_phrase.lower() in full_text.lower()
    except PyPDF2.errors.PdfReadError as e:
        print(f"Erro ao ler o PDF: {e} | URL: {pdf_url}")
        return False


def main():
    entries = fetch_main_entries()
    termo = "tecnologia da informação"
    print(f"Iniciando busca por convocações de {termo}...")
    links = []
    for entry_url in entries:
        pdf_url = fetch_pdf_link_from_entry(entry_url)
        if not pdf_url:
            continue
        if download_and_check_pdf(pdf_url, termo):
            links.append(pdf_url)
    if links:
        print("Novas convocações encontradas, enviando para o Telegram...")
        telegram.enviar_telegram(links)
    else:
        print("Sem novas convocações.")

if __name__ == "__main__":
    main()
