🖼️ Spotted Image Generator
Este é um script em Python para gerar imagens otimizadas para redes sociais a partir de textos armazenados em uma planilha do Excel. Ele cuida automaticamente da formatação do texto, dimensionamento da fonte, quebra em múltiplas imagens (caso o texto não caiba em uma só), e renderização de emojis com o estilo Twemoji do Twitter.

✨ Funcionalidades
📄 Leitura de textos a partir de uma planilha Excel (.xlsx)

🔡 Ajuste automático do tamanho da fonte entre 30px e 60px

🧱 Quebra de texto automática com centralização vertical e horizontal

🧑‍🎨 Emojis renderizados com imagens Twemoji

🖼️ Geração de uma ou mais imagens por texto, respeitando o layout predefinido

🗂️ Salvamento automático das imagens geradas na pasta output/

🛠️ Requisitos
Python 3.8+

Bibliotecas Python:

Pillow

pandas

emoji

requests

openpyxl (para ler arquivos .xlsx)

Você pode instalar as dependências com:

bash
Copiar
Editar
pip install -r requirements.txt
📁 Estrutura de Pastas
bash
Copiar
Editar
assets/
├── Formato 45 Preto.png       # Imagem base
├── Planilha.xlsx              # Planilha com os textos
fonts/
├── nourd_bold.ttf             # Fonte principal
twemoji/
├── 72x72/                     # Pasta onde os emojis são salvos (baixados se necessário)
output/
├── post_1_1.png               # Exemplo de imagem gerada
▶️ Como usar
Coloque sua imagem base em assets/Formato 45 Preto.png.

Preencha sua planilha no Excel com os textos na coluna 15 (índice 14).

Execute o script:
python SP.py

As imagens serão salvas na pasta output/.

⚠️ Observações
Emojis são baixados diretamente do repositório Twemoji, mas salvos localmente após o primeiro uso.

Caso o texto não caiba em uma imagem, ele será automaticamente quebrado em várias imagens com redistribuição de linhas para melhor aproveitamento do espaço.
Esse programa foi pensado para o @SpottedCAASO. Mas pode ser usado para outros contextos (desde que você deixe sua cópia e modificações pública também)

GPLv3
