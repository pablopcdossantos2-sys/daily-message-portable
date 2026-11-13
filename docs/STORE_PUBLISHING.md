# Publicação na Microsoft Store (gratuito)

## 1. Antes de tudo
1. Crie uma conta de desenvolvedor no **Partner Center** (conta pessoal).
2. **Reserve o nome** do app (ex.: "StartupMessage").
3. Em *Gerenciamento de produtos → Identidade do produto*, copie:
   `Package/Identity/Name`, `Package/Identity/Publisher` (CN=GUID) e `PublisherDisplayName`.

## 2. Gerar o pacote
```powershell
./packaging/build.ps1 `
  -IdentityName "<Package/Identity/Name>" `
  -Publisher "<Package/Identity/Publisher>" `
  -PublisherDisplayName "<PublisherDisplayName>" `
  -DisplayName "<Nome reservado>"
```
O arquivo `release/StartupMessage_<versão>_x64.msix` **não precisa ser assinado**: a Store assina. Não é gerado ZIP portátil.
Substitua os ícones placeholder (`assets/` e `packaging/Assets/`) pela arte final.

## 3. Ficha do app (checklist)
- [ ] Categoria: *Utilitários e ferramentas* · Preço: **Gratuito**
- [ ] Classificação etária (IARC): sem conteúdo sensível, sem internet, sem compras
- [ ] **URL da Política de Privacidade**: link para `PRIVACY.md` (raw do GitHub ou GitHub Pages)
- [ ] Descrição pt-BR e en-US (modelo abaixo)
- [ ] ≥ 1 captura de tela (ideal 3–4: configurações com blocos, mensagem com imagem, mensagem com checklist) em 1366×768 ou maior
- [ ] Ícone de listagem 300×300 (`assets/icon.png` redimensionado)
- [ ] Notas de certificação (modelo abaixo)

## 4. Modelo de descrição (pt-BR)
> Exiba uma mensagem personalizada sempre que o Windows iniciar. Monte a mensagem com textos (curtos ou longos), imagens e checklists interativas. Escolha por quantos segundos ela deve permanecer na tela; enquanto o contador não zerar — e, se você criar uma checklist obrigatória, enquanto os itens não forem marcados — o botão de fechar fica indisponível. Tema claro/escuro, cores de destaque, 100% offline, sem anúncios e sem coleta de dados. Você pode desativar a inicialização automática a qualquer momento, no app ou em Configurações > Aplicativos > Inicialização.

## 5. Notas de certificação (modelo)
> O app declara a capacidade restrita `runFullTrust` porque é um aplicativo desktop Win32 (Python empacotado com PyInstaller) distribuído em MSIX. A inicialização automática usa o `windows.startupTask` (desativado por padrão; o usuário ativa pelo app ou pelo Windows). Como testar: abra o app, escreva um texto, adicione uma checklist com 2 itens, defina 5 s e clique em "Visualizar" — o X e o Ok ficam esmaecidos até o contador zerar e os 2 itens serem marcados. O bloqueio vale apenas para a janela do app; não interfere no Gerenciador de Tarefas nem no desligamento do Windows. O tempo é limitado a 600 s e definido pelo próprio usuário.

## 6. English listing description (en-US)

> Display a personalized message every time you sign in to Windows. Build your message with short or long text, images, and interactive checklists. Choose how long the message must remain on screen; if a checklist is marked as required, every item must also be checked before the window can close. Customize the theme and accent color. The app works offline, has no ads, and does not collect or transmit personal data. Startup is optional and can be managed in the app or in Windows Settings.

## 7. English certification notes

> StartupMessage is a Win32 desktop app packaged as MSIX and declares the restricted runFullTrust capability to run its Python/PyInstaller interface. Automatic startup uses the windows.startupTask extension, disabled by default and enabled only after the user requests it. To test: open the app, add text and a required checklist with two items, set five seconds, and select Preview. The Close and OK controls remain disabled until the countdown reaches zero and both items are checked. The app does not interfere with Task Manager, Ctrl+Alt+Del, or Windows shutdown. The maximum display time is 600 seconds.

## 8. GitHub Actions package identity

Identidade confirmada no Partner Center para este produto:

- `MSIX_IDENTITY_NAME`: `pablopcdsantos.DailyMessage`
- `MSIX_PUBLISHER`: `CN=A3E973B8-1411-4314-B754-F3DADD99C070`
- `MSIX_PUBLISHER_DISPLAY_NAME`: `pablopcdsantos`
- `MSIX_DISPLAY_NAME`: `StartupMessage`

O workflow já utiliza esses valores como padrão. Se desejar, eles também podem ser cadastrados como Repository Variables em Settings → Secrets and variables → Actions → Variables:

- MSIX_IDENTITY_NAME
- MSIX_PUBLISHER
- MSIX_PUBLISHER_DISPLAY_NAME
- MSIX_DISPLAY_NAME

The workflow uses these values automatically. If all four values are present, the artifact is named `StartupMessage-MSIX-STORE`. If any value is missing, the build still runs for technical validation but the artifact is named `StartupMessage-MSIX-VALIDATION-ONLY`; that package must not be submitted to the Store.

## 9. Atualizações

Aumente __version__ em src/dailymessage/__init__.py, gere um novo MSIX e envie a atualização pelo Partner Center. Mantenha a identidade do pacote e incremente a versão MSIX (o quarto componente permanece zero).
