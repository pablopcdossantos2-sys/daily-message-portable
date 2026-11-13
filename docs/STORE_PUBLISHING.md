# Publicação na Microsoft Store (gratuito)

## 1. Antes de tudo
1. Crie uma conta de desenvolvedor no **Partner Center** (conta pessoal).
2. **Reserve o nome** do app (ex.: "Daily Message").
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
O arquivo `release/DailyMessage_<versão>_x64.msix` **não precisa ser assinado**: a Store assina. Não é gerado ZIP portátil.
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

## 6. Atualizações
Aumente `__version__` em `src/dailymessage/__init__.py`, gere o MSIX novamente e envie uma nova submissão.
