# Arquitetura e Modelagem: Marketplace de Barbearias

Este documento descreve a arquitetura e o esquema de banco de dados do sistema de agendamento de serviços para barbearias e profissionais autônomos.

## 1. Arquitetura Backend (Django e PostgreSQL)

Utilizaremos o padrão **MSC (Model-Service-Controller)** adaptado ao ecossistema do **Django REST Framework (DRF)**:

*   **Models:** Classes representando a persistência de dados no PostgreSQL baseadas na especificação de negócio.
*   **Services:** Lógica de negócio isolada (ex: validação de choque de horários cruzando `agendamentos`, `disponibilidades` e `bloqueios`).
*   **Controllers / API ViewSets:** Mapeamento DRF consumindo as lógicas do Service e publicando as APIs JSON.

## 2. Modelagem Relacional do Banco de Dados

A base de dados adotará preferencialmente **UUIDs** como chaves primárias e manterá a seguinte estrutura rigorosa:

### Autenticação e Usuários
*   **users**
    *   `id` (UUID, PK)
    *   `nome` (String)
    *   `cpf` (String, Unique)
    *   `rg` (String)
    *   `email` (String, Unique)
    *   `senha` (String, Hash/PBKDF2)
    *   `tipo` (Enum: 'CLIENTE', 'PROFISSIONAL')
    *   `created_at`, `updated_at` (Timestamp)

*   **enderecos**
    *   `id` (UUID, PK)
    *   `estabelecimento_id` (FK -> estabelecimentos.id)
    *   `cliente_id` (FK -> users.id)
    *   `rua`, `numero`, `bairro`, `cidade`, `estado`, `cep` (String)

### Estabelecimentos e Profissionais
*   **estabelecimentos**
    *   `id` (UUID, PK)
    *   `nome` (String)
    *   `descricao` (Text)
    *   `fotos` (JSON / Array de URLs)
    *   `created_at`, `updated_at` (Timestamp)

*   **profissionais**
    *   `id` (UUID, PK)
    *   `user_id` (FK -> users.id, restringe a 1 por usuário)
    *   `estabelecimento_id` (FK -> estabelecimentos.id, opcional. 1 profissional = max 1 estabelecimento at a time)
    *   `cargo` (Enum: 'ADMIN', 'FUNCIONARIO')
    *   `atende_domicilio` (Boolean)
    *   `is_vip` (Boolean, Default: False)
    *   `score` (Decimal)
    *   `created_at`, `updated_at` (Timestamp)

*   **convites**
    *   `id` (UUID, PK)
    *   `estabelecimento_id` (FK -> estabelecimentos.id)
    *   `profissional_id` (FK -> profissionais.id)
    *   `status` (Enum: 'PENDENTE', 'ACEITO', 'RECUSADO')
    *   `created_at`, `expira_em` (Timestamp)

*   **servicos**
    *   `id` (UUID, PK)
    *   `estabelecimento_id` (FK -> estabelecimentos.id)
    *   `nome` (String)
    *   `descricao` (Text)
    *   `preco` (Decimal)
    *   `duracao_min` (Int)
    *   `ativo` (Boolean, Default: True)

### Gestão de Agenda
*   **disponibilidades**
    *   `id` (UUID, PK)
    *   `profissional_id` (FK -> profissionais.id)
    *   `dia_semana` (Int: Ex. 0 para Domingo à 6 para Sábado)
    *   `hora_inicio` (Time)
    *   `hora_fim` (Time)

### Agendamentos e Interações
*   **agendamentos**
    *   `id` (UUID, PK)
    *   `cliente_id` (FK -> users.id)
    *   `profissional_id` (FK -> profissionais.id)
    *   `servico_id` (FK -> servicos.id)
    *   `data_hora` (Datetime)
    *   `status` (Enum: 'PENDENTE', 'ACEITO', 'RECUSADO', 'CONCLUIDO', 'CANCELADO')
    *   `tipo_atendimento` (Enum: 'LOCAL', 'DOMICILIO')
    *   `valor` (Decimal) - *Salva o preço no ato.*
    *   `created_at`, `updated_at` (Timestamp)
    *   *Índices Únicos:* `(profissional_id, data_hora)` para evitar double booking de mesma query.

*   **avaliacoes**
    *   `id` (UUID, PK)
    *   `cliente_id` (FK -> users.id)
    *   `profissional_id` (FK -> profissionais.id)
    *   `agendamento_id` (FK -> agendamentos.id)
    *   `nota` (Int)
    *   `comentario` (Text)
    *   `created_at` (Timestamp)

## 3. Comportamento das Regras de Negócio Injetadas

A estrutura apresentada resolve grandes problemas arquiteturais de forma inteligente:

1.  **Proteção de Agenda (Anti-Double Booking):** O cruzamento da tabela `disponibilidades` valida se um slot de horário é viável. A restrição de índice único `(profissional_id, data_hora)` age como salvaguarda dura de banco.
2.  **Snapshot de Dinheiro:** Manter o campo `valor` explícito dentro de `agendamentos` assegura que balanços financeiros nunca sejam corrompidos se o dono alterar o valor de um Serviço.
3.  **Roles nos Estabelecimentos:** O dono possui o campo `cargo = 'ADMIN'` no modelo de profissional e ele pode disparar um Convite gerando registros na tabela `convites`. O destinatário, ao aceitar, atualiza seu `estabelecimento_id` e seu `cargo = 'FUNCIONARIO'`.
4.  **Integração e Domicílio:** A flag `atende_domicilio` em `profissionais` e `tipo_atendimento` em `agendamentos`.

## 4. Estrutura Sugerida de Apps Django
Pela natureza modular do Django, separamos os apps baseados na arquitetura de negócios:
```text
apps/
  ├── accounts/     # Modelos: User, Endereços
  ├── vendors/      # Modelos: Estabelecimento, Profissionais, Convites, Serviços
  ├── booking/      # Modelos: Disponibilidade, Agendamentos
  └── feedback/     # Modelos: Avaliação
```
