# EBSERH UFSC Scraper

Um scraper automatizado para monitorar convocações de concursos públicos do Hospital Universitário da Universidade Federal de Santa Catarina (HU-UFSC) através do site da EBSERH.

## 🎯 Objetivo

Este projeto foi criado para monitorar automaticamente a página de convocações do HU-UFSC, baixando e analisando PDFs de editais em busca de convocações do concurso Nº 1/2024 - EBSERH/NACIONAL. Foi desenvolvido para acompanhar a minha convocação como candidato aprovado em concurso público na vaga de Analista de Tecnologia da Informação, enviando notificações via Telegram quando minha convocação for publicada. Além disso, o projeto também serviu como uma oportunidade para praticar e aplicar meus estudos e aprendizados em programação e automação.

## ✨ Funcionalidades

- **Navegação automática por páginas**: Busca em todas as páginas disponíveis de convocações
- **Detecção inteligente de páginas vazias**: Para automaticamente quando não há mais convocações
- **Download e análise de PDFs**: Baixa cada PDF de convocação e extrai todo o texto
- **Busca inteligente em PDFs**: Procura pelos termos dentro do conteúdo dos documentos
- **Busca por múltiplos termos**: Suporte a vários termos de busca simultaneamente
- **Normalização de texto**: Remove acentos e ignora diferenças de maiúsculas/minúsculas
- **Histórico de URLs**: Não reprocessa documentos já verificados
- **Notificações via Telegram**: Envia alertas quando encontra convocações relevantes
- **Headers de navegador real**: Contorna proteções anti-bot
- **Execução automatizada**: Roda diariamente via GitHub Actions com cron
- **Atualização automática**: Mantém a lista de URLs visitadas sempre atualizada

## 🚀 Instalação

### Pré-requisitos

- Python 3.8+
- Conta no Telegram (para receber notificações)

### Configuração

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd ebserh-ufsc-scraper
```

2. **Ative o ambiente virtual:**
```bash
source venv.sh
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente:**
Crie um arquivo `.env` na raiz do projeto com:
```env
TOKEN_BOT=seu_token_do_bot_telegram
CHAT_ID=seu_chat_id_telegram
```

### Como obter o Token do Bot e Chat ID

1. **Criar um Bot no Telegram:**
   - Fale com [@BotFather](https://t.me/botfather)
   - Use o comando `/newbot`
   - Siga as instruções para criar seu bot
   - Copie o token fornecido

2. **Obter o Chat ID:**
   - Envie uma mensagem para seu bot
   - Acesse: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
   - Copie o `chat.id` da resposta

## 📋 Uso

### Execução Manual

```bash
python3 main.py
```

### Execução Automatizada

O projeto é executado automaticamente via **GitHub Actions** com cron job para monitoramento contínuo:

- **Frequência**: Execução diária
- **Horário**: Configurado via cron no GitHub Actions
- **Atualização automática**: A lista de URLs visitadas é atualizada automaticamente a cada execução
- **Notificações**: Envia alertas via Telegram quando encontra novas convocações

Para configurar manualmente via cron (alternativa local):
```bash
# Executar diariamente às 9h
0 9 * * * cd /caminho/para/projeto && source venv.sh && python main.py
```

## ⚙️ Configuração

### Termos de Busca

Para modificar os termos de busca, edite a lista `termos` na função `main()`. No exemplo atual, está configurado para buscar por:
- **Cargo**: "tecnologia da informação" (cargo para o qual fui aprovado)
- **Nome**: "eduardo rodrigues nogueira" (meu nome)

```python
termos = ["tecnologia da informação", "eduardo rodrigues nogueira"]
```

### URL Base

A URL base pode ser modificada na constante `START_URL`:

```python
START_URL = "https://www.gov.br/ebserh/pt-br/acesso-a-informacao/agentes-publicos/concursos-e-selecoes/concursos/2024/convocacoes/hu-ufsc"
```

## 📁 Estrutura do Projeto

```
ebserh-ufsc-scraper/
├── main.py                 # Script principal
├── enviar_mensagem.py      # Módulo para envio de notificações
├── requirements.txt        # Dependências Python
├── urls_verificadas.txt    # Histórico de URLs verificadas
├── venv.sh                 # Script para ativar ambiente virtual
├── .env                    # Variáveis de ambiente (criar)
└── README.md              # Este arquivo
```

## 🔧 Funcionalidades Técnicas

### Navegação por Páginas
- Navega automaticamente por todas as páginas de convocações
- URLs: `?b_start:int=0`, `?b_start:int=20`, `?b_start:int=40`, etc.
- Para automaticamente quando detecta páginas sem itens

### Detecção de Links
- **Método 1**: Estrutura HTML específica (`content-core → entries → article.entry`)
- **Método 2**: Links que terminam com `.pdf` ou contêm `/view`
- **Método 3**: Fallback para qualquer link dentro de `content-core`

### Processamento de PDFs
- **Download automático**: Baixa cada PDF de convocação encontrado
- **Extração de texto**: Usa PyPDF2 para extrair todo o conteúdo textual
- **Análise completa**: Lê página por página do documento
- **Busca no conteúdo**: Procura pelos termos dentro do texto extraído
- **Validação de PDF**: Verifica se o arquivo é um PDF válido antes de processar

### Busca Inteligente
- Normaliza texto removendo acentos (`ç` → `c`, `ã` → `a`)
- Ignora diferenças de maiúsculas/minúsculas
- Busca por múltiplos termos simultaneamente
- **Busca dentro do conteúdo dos PDFs**, não apenas nas páginas web

### Histórico de URLs
- Mantém registro de URLs já verificadas
- Evita reprocessamento de documentos
- Formato: `URL|STATUS` (COM_TERMO ou SEM_TERMO)

## 📊 Exemplo de Saída

```
Verificando página com https://www.gov.br/ebserh/...?b_start:int=0
Encontrados 20 links na página b_start:int=0
Verificando página com https://www.gov.br/ebserh/...?b_start:int=20
Encontrados 20 links na página b_start:int=20
Verificando página com https://www.gov.br/ebserh/...?b_start:int=40
Encontrados 10 links na página b_start:int=40
Verificando página com https://www.gov.br/ebserh/...?b_start:int=60
Nenhum link encontrado com b_start:int=60, parando a busca.
Total de links únicos encontrados: 50
Iniciando busca por convocações dos termos: tecnologia da informação, eduardo rodrigues nogueira...
URLs já verificadas anteriormente: 50
Baixando PDF de: https://www.gov.br/ebserh/.../edital-no-123.pdf/@@download/file
Tamanho do conteúdo: 245760 bytes
Nenhum termo encontrado em: https://www.gov.br/ebserh/.../edital-no-123.pdf/@@download/file
Baixando PDF de: https://www.gov.br/ebserh/.../edital-no-124.pdf/@@download/file
Tamanho do conteúdo: 189440 bytes
Termo 'eduardo rodrigues nogueira' encontrado em: https://www.gov.br/ebserh/.../edital-no-124.pdf/@@download/file
Novas convocações encontradas, enviando para o Telegram...
Sem novas convocações.
```

## 🛠️ Dependências

- `requests`: Para requisições HTTP
- `beautifulsoup4`: Para parsing HTML
- `pypdf2`: Para leitura de PDFs
- `python-dotenv`: Para variáveis de ambiente
- `unidecode`: Para normalização de texto

## 📝 Licença

Este projeto é de uso pessoal e educacional. Respeite os termos de uso do site da EBSERH.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Adicionar novas funcionalidades

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no repositório.

---

**Desenvolvido para acompanhar a minha convocação como candidato aprovado em concurso público do HU-UFSC** 🏥📚

*Este projeto foi criado para automatizar o monitoramento da minha convocação, evitando a necessidade de verificar manualmente o site da EBSERH todos os dias em busca da publicação da minha convocação. Também representou uma excelente oportunidade para praticar conceitos de web scraping, automação, integração com APIs e desenvolvimento de soluções práticas para problemas reais.*
