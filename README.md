# 📊 Tesouro Analytics

**Tesouro Analytics** é um projeto de análise e automação de dados públicos do Tesouro Direto, criado como exemplo de integração entre múltiplos componentes modernos de desenvolvimento de software.  
O sistema coleta dados de vendas do Tesouro Direto (CSV público do portal [dados.gov.br](https://dados.gov.br/dados/conjuntos-dados/vendas-do-tesouro-direto1)), armazena-os em banco NoSQL, executa tarefas assíncronas, gera estimativas automáticas de potencial de venda e envia alertas por e-mail semanalmente.

---

## 🧱 Arquitetura e Componentes Técnicos

O projeto foi desenvolvido com foco em **modularidade e escalabilidade**, utilizando tecnologias amplamente aplicadas em sistemas modernos.

### 🔹 Backend
- **Python 3.11 + Flask** – API REST para ingestão e consulta de dados de vendas.  
- **Pandas** – Leitura e transformação de dados CSV.  
- **Scikit-learn** – Regressão linear simples para estimar o potencial de vendas.  

### 🔹 Mensageria e Tarefas
- **Celery** – Agendador e executor de tarefas assíncronas.  
- **Celery Beat** – Dispara tarefas periodicamente (ex: a cada 2 dias).  
- **RabbitMQ** – Broker de mensageria para comunicação entre workers.  
- **Redis** – Backend de cache e controle de estado do Celery.

### 🔹 Persistência
- **MongoDB** – Banco NoSQL para armazenar os registros históricos de vendas e previsões.

### 🔹 Observabilidade e DevOps
- **Docker + Docker Compose** – Containerização e orquestração local.  
- **Grafana + Prometheus (futuro)** – Monitoramento e visualização de métricas.  

---

## ⚙️ Como Executar

### 1. Clonar o projeto
```bash
git clone https://github.com/lucasamarante42/tesouro-analytics.git
cd tesouro-analytics
````

### 2. Subir os containers

```bash
docker compose up --build
```

### 3. Verificar serviços

| Serviço   | Porta   | Descrição                                                |
| --------- | ------- | -------------------------------------------------------- |
| Flask API | `5000`  | Endpoints REST                                           |
| RabbitMQ  | `15672` | Painel: [http://localhost:15672](http://localhost:15672) |
| Grafana   | `3000`  | Dashboard (admin/admin)                                  |
| MongoDB   | `27017` | Banco NoSQL                                              |
| Redis     | `6379`  | Cache Celery                                             |

---

## 🔄 Lógica do Negócio

O sistema executa o seguinte fluxo automatizado:

1. **Ingestão de Dados**

   * Um arquivo CSV com colunas como:

     ```
     Tipo Titulo;Vencimento do Titulo;Data Venda;PU;Quantidade;Valor
     Tesouro Educa+;15/12/2030;04/10/2023;3202,94;327,98;1050500,98
     ```
   * É lido com o `pandas`, tratado e normalizado (conversão de datas e valores numéricos).

2. **Armazenamento**

   * Cada linha do CSV é inserida no MongoDB em uma coleção `vendas_tesouro`.

3. **Cálculo do Potencial de Vendas**

   * O sistema agrupa os dados por **Data Venda** e calcula o **total diário de vendas**.
   * A partir da série temporal, aplica-se uma **regressão linear simples** (usando `scikit-learn`) para estimar a tendência futura de vendas.
   * Isso permite prever o **volume potencial esperado** nos próximos dias.

4. **Geração de Relatório**

   * Um relatório semanal é criado automaticamente via **tarefa Celery Beat**, contendo:

     * Top 5 títulos mais vendidos;
     * Valor total vendido na última semana;
     * Estimativa para o próximo período.

5. **Envio de E-mail (simulado ou configurável)**

   * O Celery envia um e-mail (ou loga em console) com o resumo da análise.

---

## 📈 Exemplo de Fluxo e Estimativa

### 🔹 Exemplo de Dados de Entrada

| Data Venda | Tipo Titulo    | Valor (R$) |
| ---------- | -------------- | ---------- |
| 04/10/2023 | Tesouro Educa+ | 1.050.500  |
| 05/10/2023 | Tesouro Educa+ | 1.120.000  |
| 06/10/2023 | Tesouro RendA+ | 1.350.000  |
| 09/10/2023 | Tesouro RendA+ | 1.500.000  |

---

### 🔹 Passo 1: Agrupamento Diário

| Dia   | Total de Vendas (R$) |
| ----- | -------------------: |
| 04/10 |            1.050.500 |
| 05/10 |            1.120.000 |
| 06/10 |            1.350.000 |
| 09/10 |            1.500.000 |

---

### 🔹 Passo 2: Regressão Linear

A regressão linear busca encontrar uma **reta** que melhor se ajusta à série de vendas ao longo do tempo:

```
y = a * x + b
```

onde:

* `x` = índice do dia (1, 2, 3, …)
* `y` = total de vendas
* `a` = coeficiente angular (tendência)
* `b` = intercepto

Com base nesses pontos, o modelo estima a tendência de crescimento e calcula o **valor esperado de vendas para o próximo dia útil**.

**Exemplo:**

```
Estimativa próxima venda ≈ 1.620.000 R$
```

---

### 🔹 Passo 3: Resultado da Estimativa

O resultado é armazenado em uma coleção MongoDB chamada `estimativas` com estrutura:

```json
{
  "data_prevista": "2023-10-10",
  "valor_estimado": 1620000.0,
  "modelo": "regressao_linear",
  "gerado_em": "2023-10-09T23:00:00Z"
}
```

---

## 🧠 Conceitos Envolvidos

| Conceito              | Descrição                                                       |
| --------------------- | --------------------------------------------------------------- |
| **ETL**               | Extração do CSV, transformação via Pandas e carga no MongoDB    |
| **Regressão Linear**  | Técnica estatística para estimar tendências de crescimento      |
| **Mensageria**        | RabbitMQ distribui tarefas assíncronas Celery                   |
| **Cache**             | Redis guarda estado das tarefas Celery                          |
| **Infra como Código** | Containers Docker compõem o ambiente completo                   |
| **Observabilidade**   | Grafana e Prometheus (em expansão) coletam métricas de execução |

---

## 📊 Monitoramento e Observabilidade

O projeto **Tesouro Analytics** possui um ambiente completo de **monitoramento e observabilidade**, utilizando **Prometheus**, **Grafana** e **MongoDB**.  
Essas ferramentas permitem acompanhar métricas de performance, histórico de execuções e status das tarefas assíncronas do Celery.

---

### 🧠 Prometheus

O **Prometheus** é responsável pela **coleta e armazenamento das métricas** expostas pelo backend no endpoint `/metrics`.

Essas métricas incluem:

- Uso de CPU e memória do processo;
- Coleta de lixo (GC);
- Métricas customizadas do projeto:
  - `tesouro_last_total`: último total processado;
  - `tesouro_last_est_next_7`: estimativa de vendas para os próximos 7 dias.

#### 🔗 Acesso Local

```

[http://localhost:9090](http://localhost:9090)

```

#### ⚙️ Configuração

- **Scrape target:** `http://app:5000/metrics`
- **Intervalo de coleta:** 10 segundos  
- **Arquivo de configuração:** `prometheus.yml`

---

### 📈 Grafana

O **Grafana** é usado para **visualizar as métricas** coletadas pelo Prometheus em dashboards dinâmicos e interativos.

#### 🔗 Acesso Local

```

[http://localhost:3000](http://localhost:3000)
Usuário: admin
Senha: admin

```

#### 📊 Recursos Principais

- Dashboard “**Tesouro Analytics - Metrics**” (pode ser importado via JSON);
- Painéis com:
  - Último total processado (`tesouro_last_total`);
  - Estimativa de vendas futuras (`tesouro_last_est_next_7`);
  - Uso de CPU e memória da aplicação;
- Atualização automática a cada 10 segundos.

---

### 🍃 MongoDB

O **MongoDB** é o **banco de dados principal** do projeto, utilizado para armazenar:

- Resultados processados pelo pipeline;
- Histórico de execuções e métricas de análise;
- Dados intermediários utilizados pelos endpoints `/history` e `/report`.

#### 🔗 Acesso Local

```

Host: localhost
Porta: 27017
Database: tesouro_db

docker exec -it mongo mongosh
use tesouro_db
show collections
db.nome_da_colecao.countDocuments()

```

> 💡 Quando o ambiente é iniciado com Docker Compose, o MongoDB é levantado automaticamente junto com os demais serviços.

---

### 🧾 Resumo dos Serviços

| Serviço         | Função Principal                            | URL Local                      | Porta  |
|-----------------|---------------------------------------------|--------------------------------|--------|
| **Backend (App)** | API principal e exportação de métricas       | http://localhost:5000          | 5000   |
| **Prometheus**   | Coleta e armazena métricas da aplicação      | http://localhost:9090          | 9090   |
| **Grafana**      | Visualização gráfica das métricas coletadas  | http://localhost:3000          | 3000   |
| **MongoDB**      | Banco de dados de resultados e históricos    | mongodb://localhost:27017      | 27017  |

---

### 🚀 Dica — Importar o Dashboard do Grafana

1. Acesse o **Grafana**: [http://localhost:3000](http://localhost:3000)
2. Faça login com:
   - Usuário: `admin`
   - Senha: `admin`
3. Vá até **Dashboards → Import**
4. Importe o arquivo `grafana-dashboard.json` (se disponível no repositório)
5. Selecione a fonte de dados **Prometheus**
6. Salve e visualize as métricas do projeto em tempo real 🎯

---


