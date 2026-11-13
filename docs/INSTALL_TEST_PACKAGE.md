# Instalar o Daily Message de teste

Este kit instala a versão de validação do Daily Message no Windows. Ele inclui:
- DailyMessage-validation.msix: aplicativo de teste, assinado com um certificado temporário;
- DailyMessage-test.cer: somente o certificado público, sem chave privada;
- Install-DailyMessage-Test.cmd e Install-DailyMessage-Test.ps1: instaladores assistidos.

## Instalação

1. Extraia todos os arquivos do ZIP para uma pasta.
2. Clique duas vezes em Install-DailyMessage-Test.cmd.
3. O Windows exibirá uma solicitação de administrador (UAC), pois o certificado de assinatura precisa ser confiado no repositório Computador Local → Pessoas Confiáveis.
4. Aceite a solicitação. O script confere se o certificado corresponde à assinatura do MSIX, importa apenas o certificado público e instala o aplicativo.
5. Depois da confirmação, abra Daily Message pelo menu Iniciar.

O erro 0x800B010A acontece quando o Windows não consegue construir uma cadeia de certificados confiável. Um pacote assinado com certificado autoassinado para teste não é confiável automaticamente. A Microsoft orienta importar o certificado de teste em Computador Local → Pessoas Confiáveis; importar no repositório do usuário atual não é suficiente para o App Installer em alguns cenários. Não é necessário e não é recomendado instalar este certificado no repositório de Autoridades de Certificação Raiz Confiáveis.

## Importante

- Este pacote serve somente para validação técnica. Ele não é o pacote final da Microsoft Store.
- O certificado foi criado apenas para este build. Um novo build poderá gerar outro certificado; nesse caso, use o certificado incluído no mesmo ZIP.
- O instalador não compartilha nem instala a chave privada do certificado.
- Para remover o aplicativo, use Configurações do Windows → Aplicativos → Aplicativos instalados → Daily Message → Desinstalar.
- Para remover o certificado de teste depois, abra certlm.msc, entre em Pessoas Confiáveis → Certificados, localize o certificado criado para este build e remova somente esse certificado. Não remova certificados de outros programas.

A instalação do pacote de teste exige autorização administrativa para confiar o certificado no computador. A versão distribuída pela Microsoft Store será assinada pela própria Store e não exigirá que o usuário instale um certificado de desenvolvedor.
