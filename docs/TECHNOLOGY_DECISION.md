# Avaliação da tecnologia do StartupMessage

**Data da comparação:** 13/11/2026

## Decisão

Manter Python + CustomTkinter + PyInstaller como implementação principal do StartupMessage. A experiência de compilação C# + WinUI 3 foi avaliada, mas **não foi promovida para a distribuição** porque o primeiro MSIX gerado ficou maior do que o pacote Python medido.

## Medição realizada no Windows CI

| Pacote | Tamanho do arquivo MSIX |
|---|---:|
| Python + PyInstaller | 25.068.273 bytes (23,91 MiB) |
| C# + WinUI 3 | 28.362.779 bytes (27,05 MiB) |
| Diferença | +3.294.506 bytes (+13,14%) |

Os números são tamanhos dos arquivos MSIX produzidos pelo Windows CI. O artefato de teste WinUI 3 também continha pacotes de dependência do Windows App Runtime para arquiteturas diferentes; esses arquivos não foram somados ao tamanho do MSIX principal mostrado na tabela.

## O que a comparação permite concluir

- Nesta configuração, C# + WinUI 3 não deixou o arquivo MSIX menor.
- A diferença de tamanho não prova, por si só, qual versão consome menos memória ou inicializa mais rapidamente. Essas métricas não foram comparadas em sessões equivalentes.
- WinUI 3 continua sendo uma alternativa nativa válida quando a prioridade é integração com a plataforma Windows, mas a migração não se justifica apenas pela expectativa de um instalador menor.
- O protótipo C# foi retirado do fluxo principal e o pipeline de release voltou a validar somente a implementação Python.

## Continuidade

A distribuição segue exclusivamente MSIX. O pipeline Python atual continua:
- executando os testes automatizados;
- verificando as APIs WinRT usadas pelo mecanismo StartupTask;
- gerando e instalando a cópia assinada de teste;
- criando o kit de instalação para teste;
- publicando um MSIX de validação até que a identidade definitiva do Partner Center esteja cadastrada.

Não existe distribuição portátil separada. O pacote com identidade provisória continua proibido para submissão à Microsoft Store.
