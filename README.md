# Assistente de Organização de Arquivos (Python) 🤖📁

Bem-vindo ao **Assistente de Organização Automática**! Uma aplicação profissional para Windows, projetada para monitorar continuamente as pastas do seu sistema e organizar arquivos magicamente em segundo plano, utilizando algoritmos inteligentes e Machine Learning.

---

## 🌟 Funcionalidades

- **Monitoramento em Tempo Real:** Fica de olho nas pastas selecionadas (Desktop, Downloads, Documentos, etc.) utilizando a biblioteca leve e eficiente `watchdog`.
- **Organização Baseada em Regras & IA:**
  - Classifica de imediato pelas extensões de arquivo mais conhecidas (Imagens, Vídeos, Documentos, Compactados, etc).
  - Em arquivos sem extensão ou com falsas extensões, utiliza Magic Numbers para identificar a verdadeira natureza do arquivo.
  - O sistema de IA (com TF-IDF e KMeans via `scikit-learn`) tenta sugerir categorias para arquivos desconhecidos e puramente textuais baseando-se no seu conteúdo!
- **Silencioso & Leve:** Fica escondido na bandeja do sistema do Windows.
- **Histórico Completo:** Registra toda e qualquer modificação com um histórico detalhado contendo hora, origem, destino, tamanho e checksum SHA256 do arquivo. Possibilidade de consultar o tamanho total limpo!
- **Proteção Contra Arquivos em Uso:** Se você está baixando um arquivo pelo navegador ou editando um Word, o assistente aguarda o processo terminar antes de organizar.
- **Opção de Desfazer:** Cometeu um erro ou se arrependeu de ter movido um arquivo específico? O Dashboard possui um botão "Desfazer Última Ação".

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.14+**
- **CustomTkinter:** Interface Gráfica moderna em modo Dark.
- **PyInstaller:** Usado para compilar a aplicação num executável estático (`.exe`) sem depender de instalações no PC de destino.
- **scikit-learn & joblib:** Para os modelos de agrupamento inteligentes de machine learning.
- **python-magic-bin:** Ferramenta infalível para inspecionar assinaturas hexadecimais (Magic Numbers) de arquivos obscuros.
- **SQLite3:** Banco de dados relacional leve e embutido para histórico.

---

## 🚀 Como Executar

Se preferir rodar a partir do código fonte:

1. Clone o repositório.
2. Instale as dependências executando:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie o aplicativo:
   ```bash
   python main.py
   ```

*(Um ícone aparecerá na bandeja do sistema, no canto inferior direito do Windows. Clique nele para abrir o Painel Completo).*

## 📦 Como Compilar (.exe)

O projeto acompanha um script para gerar o binário de Windows sem dores de cabeça.

1. Execute:
   ```bash
   python build.py
   ```
2. Após cerca de um minuto, procure pelo seu `AssistenteOrganizacao.exe` compilado dentro da pasta `dist/AssistenteOrganizacao/` recém gerada.

---

## 💡 Customizações de Pastas

Abra o Dashboard (Painel de Controle) através do ícone na bandeja do sistema para adicionar facilmente novas pastas customizadas para monitoramento. O arquivo mestre `config.json` será atualizado de forma dinâmica.

---

Desenvolvido com Python 🐍 e muita Automação!
