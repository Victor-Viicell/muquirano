# Sistema Muquirano 💰

Sistema de controle financeiro pessoal desenvolvido em Python com interface gráfica moderna. O Muquirano oferece uma solução completa para gerenciamento de receitas e despesas, com suporte a transações parceladas, recorrentes e análises avançadas.

## 📋 Funcionalidades

### 🔐 Autenticação e Usuários

- Sistema de login seguro com senhas hashadas (bcrypt)
- Registro de novos usuários
- Suporte a múltiplos usuários no mesmo sistema

### 💳 Gerenciamento de Transações

- **Transações Simples**: Receitas e despesas únicas
- **Transações Parceladas**: Divisão automática em parcelas mensais
- **Transações Recorrentes**: Repetição automática (mensal, semanal, anual)
- Edição e exclusão de transações individuais ou em grupo
- Busca e filtros avançados

### 📊 Análises e Relatórios

- Relatórios financeiros por período
- Gráficos de pizza (distribuição receita/despesa)
- Gráficos de barras (evolução mensal)
- Previsões simples baseadas em histórico
- Cálculo automático de saldo líquido

### 🎨 Interface Moderna

- Design responsivo e intuitivo
- Tema moderno com cores harmoniosas
- Ícones visuais para melhor usabilidade
- Validação de formulários em tempo real

## 🚀 Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal
- **PySide6**: Interface gráfica (Qt for Python)
- **SQLite**: Banco de dados local
- **Pandas**: Análise de dados
- **Matplotlib**: Geração de gráficos
- **bcrypt**: Hash seguro de senhas
- **python-dateutil**: Manipulação avançada de datas

## 📁 Estrutura do Projeto

```
muquirano/
├── src/
│   ├── app/
│   │   ├── main.py           # Ponto de entrada da aplicação
│   │   ├── ui.py             # Interface gráfica completa
│   │   ├── analysis.py       # Módulo de análises e relatórios
│   │   └── utils.py          # Funções utilitárias
│   └── db/
│       ├── database.py       # Operações de banco de dados
│       └── data_models.py    # Modelos de dados (User, Transaction)
├── README.md                 # Este arquivo
└── requirements.txt          # Dependências do projeto
```

## 🔧 Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos para instalação

1. **Clone o repositório**

```bash
git clone https://github.com/seu-usuario/muquirano.git
cd muquirano
```

2. **Crie um ambiente virtual (recomendado)**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

### Dependências principais (requirements.txt)

```
PySide6>=6.5.0
pandas>=1.5.0
matplotlib>=3.6.0
bcrypt>=4.0.0
python-dateutil>=2.8.0
```

## 🏃‍♂️ Como Executar

1. **Execute a aplicação**

```bash
python src/app/main.py
```

2. **Primeiro uso**
   - Na tela de login, clique em "Registrar" para criar seu primeiro usuário
   - Escolha um nome de usuário e senha (mínimo 4 caracteres)
   - Faça login com suas credenciais

## 📖 Manual de Uso

### Criando Transações

#### Transação Simples

1. Clique em "➕ Nova Transação"
2. Selecione o tipo (Receita/Despesa)
3. Digite o valor e descrição
4. Escolha a data
5. Clique em "Salvar"

#### Transação Parcelada

1. Na tela de nova transação
2. Defina o **valor total**
3. Aumente o **número de parcelas**
4. O sistema divide automaticamente o valor
5. Gera parcelas com datas mensais consecutivas

#### Transação Recorrente

1. Marque "🔄 Configurar como Transação Recorrente"
2. Defina o **valor por ocorrência**
3. Escolha a frequência (Mensal/Semanal/Anual)
4. Defina quantas ocorrências gerar
5. O sistema cria todas automaticamente

### Editando Transações

- **Edição Individual**: Modifica apenas a transação selecionada
- **Edição em Grupo**: Para transações parceladas/recorrentes
  - ✅ Aplicar descrição a todo o grupo
  - ✅ Aplicar valor a futuras ocorrências recorrentes

### Relatórios e Análises

1. Clique em "📊 Relatórios"
2. Selecione o período desejado
3. Clique em "Gerar Relatório/Previsão"
4. Visualize gráficos com os botões específicos

## 🗄️ Banco de Dados

O sistema utiliza SQLite com duas tabelas principais:

### Tabela `users`

- `id`: Identificador único
- `name`: Nome do usuário (único)
- `password`: Senha hashada com bcrypt

### Tabela `transactions`

- `id`: Identificador único
- `user_id`: Referência ao usuário
- `type`: Tipo (receita/despesa)
- `amount`: Valor da transação
- `date`: Data no formato YYYY-MM-DD
- `description`: Descrição da transação
- Campos para agrupamento de parcelas/recorrências

## 🔒 Segurança

- **Senhas**: Todas as senhas são hashadas usando bcrypt
- **Validação**: Validação rigorosa de entrada de dados
- **Banco Local**: Dados armazenados localmente no SQLite
- **Sessões**: Sistema de autenticação por sessão

## 🎯 Funcionalidades Avançadas

### Filtros e Busca

- Busca por descrição
- Filtro por tipo (receita/despesa)
- Ordenação personalizável
- Período de datas

### Exclusão Inteligente

- **Exclusão Individual**: Remove apenas uma transação
- **Exclusão de Grupo**: Remove todas as parcelas/ocorrências relacionadas

### Previsões

- Baseadas na média dos últimos 3 meses
- Estimativas para receitas e despesas futuras
- Cálculo automático de tendências

## 🐛 Solução de Problemas

### Erro ao iniciar a aplicação

```bash
# Verifique se o Python está corretamente instalado
python --version

# Verifique se as dependências estão instaladas
pip list | grep PySide6
```

### Banco de dados não encontrado

- O banco é criado automaticamente na primeira execução
- Arquivo `muquirano.db` será criado no diretório da aplicação

### Problemas de interface gráfica

- Certifique-se de que o PySide6 está instalado corretamente
- Em alguns sistemas Linux, pode ser necessário instalar bibliotecas Qt adicionais

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 👨‍💻 Autor

**Viicell** - Desenvolvido com ❤️ em Python

---

## 📚 Documentação Técnica

### Arquitetura

- **Padrão MVC**: Separação clara entre interface, lógica e dados
- **Modular**: Cada componente em arquivo separado
- **Orientado a Objetos**: Classes bem definidas e reutilizáveis

### API do Banco de Dados

Principais funções disponíveis em `src/db/database.py`:

```python
# Usuários
add_user(name: str, password: str) -> Optional[User]
check_user_password(username: str, password: str) -> Optional[User]
get_all_usernames() -> List[str]

# Transações
add_transaction(user_id, type, amount, date, description, ...) -> List[Transaction]
get_transactions_by_user(user_id, filters...) -> List[Transaction]
update_transaction(transaction_id, ...) -> bool
delete_transaction(transaction_id) -> bool
```

### Extensibilidade

O sistema foi projetado para fácil extensão:

- Novos tipos de transação
- Diferentes frequências de recorrência
- Novos tipos de relatório
- Integração com APIs externas

---

_Documentação atualizada em 2025_
