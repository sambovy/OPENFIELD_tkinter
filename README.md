# Sistema Open Field - Versão Flet

## Análise do Sistema Original (Tkinter)

O sistema original em Tkinter é uma aplicação para análise comportamental de animais em teste de campo aberto, com as seguintes funcionalidades:

### Funcionalidades Principais:
- **Configuração do teste**: ID do animal e duração
- **Cronômetro de contagem regressiva**
- **Três áreas de marcação**: Canto (vermelho), Lateral (azul claro), Centro (verde)
- **Marcação de tempo em tempo real** ao pressionar/segurar os botões
- **Relatório detalhado** com estatísticas e porcentagens
- **Gráfico de pizza** mostrando distribuição de tempo
- **Exportação do relatório** para arquivo TXT

## Nova Versão em Flet

### Melhorias Implementadas:

1. **Interface Moderna e Responsiva**
   - Design mais limpo e moderno
   - Melhor organização visual com containers e bordas
   - Cores e tipografia mais atrativas

2. **Interação Simplificada**
   - Botões de área agora funcionam como toggle (clique para ativar/desativar)
   - Feedback visual melhorado com sombras e destacamento
   - Mensagens de status via SnackBar

3. **Multiplataforma**
   - Funciona em Windows, macOS, Linux
   - Pode ser executada como aplicativo web
   - Possibilidade de compilar para mobile

4. **Melhor Experiência do Usuário**
   - Validação de entrada mais clara
   - Mensagens de feedback mais informativas
   - Layout responsivo que se adapta ao tamanho da janela

### Principais Diferenças:

| Aspecto | Tkinter (Original) | Flet (Nova Versão) |
|---------|-------------------|-------------------|
| **Interação dos Botões** | Pressionar e segurar | Clique para toggle |
| **Feedback Visual** | Mudança de cor simples | Sombras e efeitos visuais |
| **Mensagens** | Popup dialogs | SnackBar moderno |
| **Layout** | Grid fixo | Layout responsivo |
| **Gráficos** | Matplotlib integrado | Matplotlib como imagem base64 |
| **Exportação** | Dialog nativo | Nome automático com timestamp |

### Arquivos:

- `openfield.py` - Versão original em Tkinter
- `openfield_flet_simple.py` - Nova versão em Flet (funcional)
- `openfield_flet.py` - Primeira tentativa (com erros)
- `openfield_flet_fixed.py` - Segunda tentativa (com erros)
- `openfield_flet_final.py` - Terceira tentativa (com erros)
- `README.md` - Esta documentação
- `requirements.txt` - Dependências do projeto

## Como Executar

### Versão Tkinter:
```bash
python openfield.py
```

### Versão Flet (Recomendada):
```bash
python openfield_flet_simple.py
```

## Dependências

### Tkinter:
- tkinter (incluído no Python)
- matplotlib

### Flet:
- flet
- matplotlib

## Instalação das Dependências

```bash
pip install flet matplotlib
```

## Funcionalidades Preservadas

Todas as funcionalidades principais do sistema original foram preservadas:

1. ✅ Configuração de ID do animal e duração do teste
2. ✅ Timer de contagem regressiva
3. ✅ Marcação de tempo nas três áreas (Canto, Lateral, Centro)
4. ✅ Cálculo automático de tempos e porcentagens
5. ✅ Geração de relatório detalhado
6. ✅ Gráfico de pizza com distribuição de tempo
7. ✅ Exportação de relatório em formato texto

## Vantagens da Versão Flet

1. **Modernização**: Interface mais atrativa e profissional
2. **Multiplataforma**: Funciona em mais sistemas operacionais
3. **Web Ready**: Pode ser facilmente convertida para aplicação web
4. **Manutenibilidade**: Código mais limpo e organizados
5. **Escalabilidade**: Mais fácil de adicionar novas funcionalidades
6. **UX Melhorada**: Interação mais intuitiva com feedback visual melhor

## Possíveis Melhorias Futuras

- Integração com banco de dados para histórico de testes
- Dashboard com múltiplos animais
- Exportação para formatos Excel/CSV
- Análises estatísticas avançadas
- Versão web para acesso remoto
- Sincronização em nuvem
