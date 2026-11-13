# Roteiro de validação funcional no Windows

Este roteiro complementa os testes automatizados e o teste de instalação executados pelo GitHub Actions. Ele deve ser repetido com a versão instalada pela Microsoft Store antes da submissão final.

## O que o CI já verifica

O pipeline para Windows:

1. instala as dependências;
2. importa as APIs WinRT usadas para armazenamento e StartupTask;
3. executa os testes automatizados;
4. cria o pacote MSIX;
5. assina uma cópia separada com certificado temporário;
6. instala a cópia de teste no Windows;
7. confirma que o pacote tem os dois executáveis e que a extensão StartupMessageTask aponta para StartupMessageRunner.exe, desativada por padrão;
8. executa o modo de diagnóstico dentro da identidade MSIX, consultando a StartupTask e gravando/removendo um arquivo no espaço LocalState;
9. publica como artefato apenas o MSIX não assinado, destinado à submissão à Store.

A cópia assinada e o certificado temporário servem exclusivamente ao teste automático. Não os envie à Store.

## Testes manuais obrigatórios

Faça os testes em uma conta Windows comum, sem privilégios administrativos, após instalar o aplicativo pela Store.

### 1. Primeira execução e configurações

- [ ] Abrir o StartupMessage pelo menu Iniciar.
- [ ] Confirmar que a janela de configurações abre sem console ou erro.
- [ ] Adicionar blocos de texto, imagem e checklist.
- [ ] Reordenar blocos, remover um bloco e salvar.
- [ ] Fechar e abrir novamente; confirmar título, ordem, conteúdo e imagens.
- [ ] Alternar tema, cor de destaque e idioma; confirmar que o conteúdo digitado não se perde.
- [ ] Confirmar que as imagens importadas continuam disponíveis após reiniciar o computador.

### 2. Inicialização com Windows

- [ ] Na primeira execução, ativar **Iniciar junto com o Windows**.
- [ ] Confirmar que o Windows registra StartupMessage em Configurações → Aplicativos → Inicialização e no Gerenciador de Tarefas → Aplicativos de inicialização.
- [ ] Sair da sessão e entrar novamente (ou reiniciar); confirmar que StartupMessageRunner.exe apresenta a mensagem.
- [ ] Desativar a opção dentro do StartupMessage; entrar novamente e confirmar que a mensagem não aparece.
- [ ] Ativar novamente e desativar pelo painel de Inicialização do Windows; confirmar que o aplicativo reflete o estado bloqueado pelo usuário.
- [ ] Confirmar que o usuário consegue abrir as configurações manualmente mesmo com a inicialização automática desligada.

Observação: o usuário precisa abrir o aplicativo pelo menos uma vez para registrar a tarefa de inicialização. O controle final também fica disponível nas configurações do Windows.

### 3. Contador e bloqueio de fechamento

- [ ] Definir 5 segundos e abrir a prévia; verificar contador regressivo.
- [ ] Enquanto o contador estiver ativo, confirmar X e OK desabilitados e minimização impedida.
- [ ] Após zerar o contador, confirmar que OK e X liberam o fechamento quando não houver checklist obrigatória.
- [ ] Com checklist obrigatória, confirmar que a janela continua bloqueada após zerar o tempo enquanto houver itens pendentes.
- [ ] Marcar todos os itens; confirmar liberação.
- [ ] Desmarcar um item; confirmar que o bloqueio volta.
- [ ] Confirmar que checklist não obrigatória não bloqueia a saída.

### 4. Texto, imagens e dimensões

- [ ] Testar mensagem curta e texto próximo de 20.000 caracteres.
- [ ] Confirmar rolagem do conteúdo e permanência do rodapé com contador e OK visíveis.
- [ ] Redimensionar e maximizar a janela; confirmar quebra automática de texto sem cortes.
- [ ] Adicionar imagem panorâmica, imagem vertical e imagem pequena; confirmar proporção preservada e que a imagem pequena não é ampliada.
- [ ] Testar tema claro, escuro e sistema.
- [ ] Testar escala de tela 100%, 125% e 150%, além de monitor secundário quando disponível.
- [ ] Confirmar que GIF mostra o primeiro quadro, conforme limite documentado.

### 5. Limites de segurança do sistema

- [ ] Confirmar que a janela não impede abrir Gerenciador de Tarefas ou Ctrl+Alt+Del.
- [ ] Confirmar que o Windows permite desligar/reiniciar normalmente.
- [ ] Confirmar que não são necessários privilégios administrativos para o uso normal do aplicativo.

## Dados a registrar

Anote versão do Windows, arquitetura, escala de tela, resultado de cada teste e qualquer mensagem de erro. Se houver falha, anexe o arquivo de log local do StartupMessage e uma captura de tela, removendo informações privadas da mensagem antes de compartilhar.

## Conclusão

O build e o teste de instalação no CI são validações automatizadas; não substituem os testes de interface e de reinicialização feitos em uma sessão real de usuário. Só considere a versão pronta para submissão depois de concluir os testes manuais acima em Windows 10 e Windows 11.
