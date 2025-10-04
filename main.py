import requests
from bs4 import BeautifulSoup
import io
import PyPDF2
import enviar_mensagem as telegram
import os
from unidecode import unidecode

BASE_URL = "https://www.gov.br"
START_URL = "https://www.gov.br/ebserh/pt-br/acesso-a-informacao/agentes-publicos/concursos-e-selecoes/concursos/2024/convocacoes/hu-ufsc"
CHECKED_URLS_FILE = "urls_verificadas.txt"

def load_checked_urls():
    """Carrega URLs já verificadas do arquivo"""
    if not os.path.exists(CHECKED_URLS_FILE):
        return set()
    
    checked_urls = set()
    with open(CHECKED_URLS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and '|' in line:
                url = line.split('|')[0]
                checked_urls.add(url)
    return checked_urls

def save_checked_url(url, contains_term):
    """Salva URL verificada no arquivo"""
    with open(CHECKED_URLS_FILE, 'a', encoding='utf-8') as f:
        status = "COM_TERMO" if contains_term else "SEM_TERMO"
        f.write(f"{url}|{status}\n")


def fetch_entries_from_page(url):
    """Extrai links de uma página específica"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Verifica se a página contém a mensagem de "sem itens"
    page_text = soup.get_text().lower()
    if "atualmente não existem itens" in page_text or "não existem itens nessa pasta" in page_text:
        return []
    
    article_links = []
    
    # Método 1: Seguir a estrutura exata: content-core → entries → article.entry → header → span.summary → a
    content_core = soup.find("div", id="content-core")
    
    if content_core:
        entries_div = content_core.find("div", class_="entries")
        
        if entries_div:
            articles = entries_div.find_all("article", class_="entry")
            
            for article in articles:
                header = article.find("header")
                
                if header:
                    summary = header.find("span", class_="summary")
                    
                    if summary:
                        link = summary.find("a")
                        
                        if link and link.get("href"):
                            href = link["href"]
                            if href.startswith("http"):
                                article_links.append(href)
                            else:
                                article_links.append(BASE_URL + href)
    
    # Método 2: Fallback - procurar por links que terminam com .pdf ou /view
    if not article_links:
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if (href.endswith(".pdf") or 
                "/@@download/file" in href or 
                "/view" in href or
                "edital" in href.lower()):
                if href.startswith("http"):
                    article_links.append(href)
                else:
                    article_links.append(BASE_URL + href)
    
    # Método 3: Fallback - qualquer link dentro de content-core
    if not article_links:
        content_core = soup.find("div", id="content-core")
        if content_core:
            for link in content_core.find_all("a", href=True):
                href = link["href"]
                if href.startswith("http"):
                    article_links.append(href)
                else:
                    article_links.append(BASE_URL + href)
    
    return article_links

def fetch_main_entries():
    """Busca entradas de todas as páginas disponíveis"""
    all_article_links = []
    base_url = "https://www.gov.br/ebserh/pt-br/acesso-a-informacao/agentes-publicos/concursos-e-selecoes/concursos/2024/convocacoes/hu-ufsc"
    
    for start_value in range(0, 1000, 20):  # 0, 20, 40, 60, 80, 100...
        url = f"{base_url}?b_start:int={start_value}"
        print(f"Verificando página com {url}")
        
        try:
            page_links = fetch_entries_from_page(url)
            
            # Se não encontrou nenhum link, provavelmente chegou ao fim
            if not page_links:
                print(f"Nenhum link encontrado com b_start:int={start_value}, parando a busca.")
                break
            
            # Adiciona os links encontrados
            all_article_links.extend(page_links)
            print(f"Encontrados {len(page_links)} links na página b_start:int={start_value}")
            
        except Exception as e:
            print(f"Erro ao acessar b_start:int={start_value}: {e}")
            break
    
    # Remover duplicatas
    all_article_links = list(set(all_article_links))
    print(f"Total de links únicos encontrados: {len(all_article_links)}")
    
    return all_article_links


def fetch_pdf_link_from_entry(entry_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    response = requests.get(entry_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Se a URL já é um link direto para PDF, retorna ela mesma
    if entry_url.endswith(".pdf") or "/@@download/file" in entry_url:
        return entry_url
    
    content = soup.find("div", id="content-core")
    if not content:
        return None
    
    for p in content.find_all("p"):
        a = p.find("a")
        if a and a.get("href", "").endswith("/file"):
            return a["href"] if a["href"].startswith("http") else BASE_URL + a["href"]
    
    return None

def normalize_text(text):
    """Normaliza texto removendo acentos e convertendo para minúsculas"""
    return unidecode(text.lower())

def download_and_check_pdf(pdf_url, search_phrases):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/pdf,application/octet-stream,*/*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    response = requests.get(pdf_url, headers=headers)
    
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
            
            # Normaliza o texto do PDF
            normalized_text = normalize_text(full_text)
            
            # Verifica cada termo de busca
            for phrase in search_phrases:
                normalized_phrase = normalize_text(phrase)
                if normalized_phrase in normalized_text:
                    print(f"Termo '{phrase}' encontrado em: {pdf_url}")
                    return True
            
            print(f"Nenhum termo encontrado em: {pdf_url}")
            return False
    except PyPDF2.errors.PdfReadError as e:
        print(f"Erro ao ler o PDF: {e} | URL: {pdf_url}")
        return False


def main():
    entries = fetch_main_entries()
    termos = ["tecnologia da informação", "eduardo rodrigues nogueira"]
    print(f"Iniciando busca por convocações dos termos: {', '.join(termos)}...")
    
    # Carrega URLs já verificadas
    checked_urls = load_checked_urls()
    print(f"URLs já verificadas anteriormente: {len(checked_urls)}")
    
    links = []
    for entry_url in entries:
        pdf_url = fetch_pdf_link_from_entry(entry_url)
        if not pdf_url:
            continue
        
        # Verifica se a URL já foi verificada
        if pdf_url in checked_urls:
            print(f"URL já verificada anteriormente: {pdf_url}")
            continue
        
        # Verifica o PDF
        contains_term = download_and_check_pdf(pdf_url, termos)
        
        # Salva a URL verificada
        save_checked_url(pdf_url, contains_term)
        
        if contains_term:
            links.append(pdf_url)
        else:
            print(f"Termo não encontrado em: {pdf_url}")
    
    if links:
        print("Novas convocações encontradas, enviando para o Telegram...")
        telegram.enviar_telegram(links)
    else:
        print("Sem novas convocações.")

if __name__ == "__main__":
    main()
