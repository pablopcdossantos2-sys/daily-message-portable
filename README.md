# Daily Message — Microsoft Store

[![build](https://github.com/pablopcdossantos2-sys/daily-message-portable/actions/workflows/build.yml/badge.svg)](https://github.com/pablopcdossantos2-sys/daily-message-portable/actions/workflows/build.yml)
![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-0078D4)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-green)

Aplicativo **gratuito, distribuído exclusivamente pela Microsoft Store** para Windows que exibe uma **mensagem personalizada sempre que o computador inicia** — de um simples "Bom dia!" a textos longos, com **imagens** e **checklists interativas**. A mensagem permanece na tela por um **tempo obrigatório definido por você** e só pode ser fechada depois do contador zerar (e, se houver checklist obrigatória, depois de marcar todos os itens).

<!-- Adicione capturas de tela em docs/screenshots e referencie aqui -->
<!-- ![Configurações](docs/screenshots/settings.png) ![Mensagem](docs/screenshots/message.png) -->

## ✨ Recursos

- 🚀 **Inicia com o Windows** (opcional, liga/desliga com um clique)
- 🧱 **Mensagem em blocos**, na ordem que você quiser:
  - 📝 **Texto** — curto ou muito longo (até 30.000 caracteres), em estilo título, normal ou nota
  - 🖼️ **Imagem** — PNG, JPG, GIF (1º quadro), BMP ou WebP, com legenda opcional
  - ✅ **Checklist interativa** — itens que você marca ao abrir o computador; pode ser **obrigatória** para fechar a janela
- 🪟 **Janela flexível**: ajusta o tamanho ao conteúdo, pode ser redimensionada/maximizada, quebra o texto automaticamente, rola quando o conteúdo é grande e **nunca distorce as imagens**
- ⏳ **Tempo obrigatório** (3 a 600 s) com **contador regressivo** abaixo da mensagem
- 🔒 Enquanto a saída não é permitida, o **X** da janela e o botão **Ok** ficam **esmaecidos e inativos**; Alt+F4 e minimizar também são bloqueados
- 🎨 Visual moderno: tema **claro / escuro / sistema**, 4 cores de destaque, cantos arredondados
- 👀 Botão **Visualizar** para testar antes de salvar
- 🌎 Português (Brasil) e inglês
- 🔐 **100% offline** ([Privacidade](PRIVACY.md))

## 📥 Instalação

A versão de usuário será distribuída exclusivamente pela **Microsoft Store**. Não haverá ZIP portátil nem instalação manual.

## 🚀 Como usar

1. Abra o **Daily Message**.
2. Defina o **título** e monte o conteúdo com **+ Texto**, **+ Imagem** e **+ Checklist** (use ↑ ↓ para reordenar e ✕ para remover).
3. Em uma checklist, escreva **um item por linha** e deixe **"Obrigatória para fechar a janela"** marcada para exigir todos os itens.
4. Defina o **tempo obrigatório** (em segundos).
5. Ative **Iniciar junto com o Windows**.
6. Clique em **Visualizar** para testar (a prévia usa no máximo 5 s) e em **Salvar**.

> As marcações das checklists **não são salvas**: a cada inicialização do Windows, todos os itens começam desmarcados.

## 🔒 Como funciona o bloqueio (e seus limites)

A janela só pode ser fechada quando **o tempo zerou E todos os itens obrigatórios estão marcados**. Até lá ela fica sempre visível, o **X** é desabilitado via API do Windows, o **Ok** permanece inativo e minimizar é impedido (redimensionar e maximizar continuam permitidos).

Por design — e por exigência das políticas da Microsoft Store — o app **não** interfere no sistema: você ainda pode usar o **Gerenciador de Tarefas**, **Ctrl+Alt+Del** e **desligar/reiniciar** o computador normalmente. O limite máximo de tempo é de 10 minutos.

## ⚙️ Inicialização automática

| Distribuição | Mecanismo |
|---|---|
| **Microsoft Store (MSIX)** | `windows.startupTask` (API `StartupTask`). Também gerenciável em *Configurações → Aplicativos → Inicialização*. |

`DailyMessageRunner.exe` exibe a mensagem no boot; `DailyMessage.exe` abre as configurações.

## 🛠️ Desenvolvimento

Requer **Windows 10/11** e **Python 3.10+** (recomendado 3.12).

```powershell
git clone https://github.com/pablopcdossantos2-sys/daily-message-portable.git
cd daily-message-portable
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python packaging/make_assets.py          # ícones placeholder
python launcher.py --settings            # abre as configurações
python launcher.py --startup --no-delay  # simula a mensagem de boot
python -m pytest -q                      # testes
```

Antes de considerar o aplicativo pronto para publicação, conclua o [roteiro de validação funcional no Windows](docs/WINDOWS_VALIDATION.md). O CI também instala uma cópia assinada temporariamente para validar o registro MSIX e as APIs WinRT; o artefato publicado pelo workflow é somente o MSIX não assinado.

## 📦 Gerar o pacote MSIX

O empacotamento requer Windows 10/11 SDK (makeappx.exe) e os valores de identidade fornecidos pelo Partner Center. Execute packaging/build.ps1 com IdentityName, Publisher, PublisherDisplayName e DisplayName. O MSIX será criado em release/. A versão destinada à Store não precisa ser assinada localmente; a Microsoft assina o pacote durante a publicação. Consulte docs/STORE_PUBLISHING.md.

## 🗂️ Estrutura

```
src/dailymessage/   código-fonte (GUI, blocos, mídia, autostart, config, i18n, Win32)
packaging/          PyInstaller (.spec), AppxManifest, build.ps1
tests/              testes automatizados
docs/               guia de publicação na Store
```

## 🗺️ Ideias futuras

Formatação rica (negrito/links), GIF animado, múltiplas mensagens por dia da semana, importar/exportar mensagens.

## 🤝 Contribuindo

Issues e PRs são bem-vindos! Rode `python -m pytest` antes de enviar.

## 📄 Licença

[MIT](LICENSE) © pablopcdossantos2-sys
