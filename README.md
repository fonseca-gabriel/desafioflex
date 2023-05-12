# Desafioflex

## Descrição
API REST para gerenciamento de certificados, contendo cadastro, listagem, edição e deleção dos certificados e grupos associados.

A API utiliza Python 3.10 e Flask na versão 2.3.1, banco SQLite 3 para ambiente de desenvolvimento e MySQL 8.0 em ambiente de produção.

Foi utilizado o SQLAlchemy como ORM e o Flask-Migrate para tratar as migrações do banco de dados.

Outras bibliotecas, dependências e respectivas versões podem ser verificadas no arquivo `requirements.txt` contida neste projeto.


## Preparação do ambiente

O projeto foi desenvolvido de forma a ser executado utilizando diferentes cenários, embora esse ponto pode ser melhorado/simplificado, conforme destacado no ítem de pendências e melhorias.

Para facilitar a execução nesses diferentes cenários, serão criados tópicos específicos para cada um deles.


### Estrutura de arquivos

Segue a árvore de arquivos do projeto:

```
.
├── app.py
├── create_test_database.py
├── deploy_on_docker.sh
├── docker-compose.yml
├── Dockerfile
├── .dockerignore
├── entrypoint.sh
├── .gitignore
├── nginx
│   ├── Dockerfile
│   └── nginx.conf
├── README.md
├── requirements.txt
└── test_app.py

```

### Base de dados


#### MySQL

Quando usado o MySQL como banco de dados para a aplicação, toda a estrutura da base de dados é gerada com o `sql-migrate`, utilizando a sequência de comandos abaixo.

Importante destacar que no ambiente "dockerizado" essa sequência de comandos já é automaticamente executada pelo entrypoint do serviço "web".



```
flask db init
```
Inicializa a estrutura de diretórios necessária para as migrações

```
flask db migrate -m "Initial migration"
```
Cria a migração inicial com base no modelo de dados definido e um arquivo de migração na pasta migrations com as alterações necessárias para criar as tabelas no banco de dados.

```
flask db upgrade
```
Aplica a migração para criar as tabelas no banco de dados.


##### Estrutura da base de dados

```
mysql> show tables;
+-----------------------+
| Tables_in_desafioflex |
+-----------------------+
| alembic_version       |
| certificate_group     |
| certificates          |
| groups                |
+-----------------------+
4 rows in set (0.00 sec)
```
```
mysql> desc desafioflex.alembic_version;
+-------------+-------------+------+-----+---------+-------+
| Field       | Type        | Null | Key | Default | Extra |
+-------------+-------------+------+-----+---------+-------+
| version_num | varchar(32) | NO   | PRI | NULL    |       |
+-------------+-------------+------+-----+---------+-------+
1 row in set (0.00 sec)
```
```
mysql> desc desafioflex.certificates;
+--------------+--------------+------+-----+---------+----------------+
| Field        | Type         | Null | Key | Default | Extra          |
+--------------+--------------+------+-----+---------+----------------+
| id           | int          | NO   | PRI | NULL    | auto_increment |
| username     | varchar(30)  | NO   | UNI | NULL    |                |
| name         | varchar(255) | NO   |     | NULL    |                |
| description  | varchar(255) | YES  |     | NULL    |                |
| expiration   | int          | NO   |     | NULL    |                |
| created_at   | datetime     | YES  |     | NULL    |                |
| updated_at   | datetime     | YES  |     | NULL    |                |
| expirated_at | datetime     | YES  |     | NULL    |                |
+--------------+--------------+------+-----+---------+----------------+
8 rows in set (0.00 sec)
```
```
mysql> desc desafioflex.groups;
+-------------+--------------+------+-----+---------+----------------+
| Field       | Type         | Null | Key | Default | Extra          |
+-------------+--------------+------+-----+---------+----------------+
| id          | int          | NO   | PRI | NULL    | auto_increment |
| name        | varchar(30)  | NO   | UNI | NULL    |                |
| description | varchar(255) | YES  |     | NULL    |                |
| created_at  | datetime     | YES  |     | NULL    |                |
| updated_at  | datetime     | YES  |     | NULL    |                |
+-------------+--------------+------+-----+---------+----------------+
5 rows in set (0.00 sec)
```
```
mysql> desc desafioflex.certificate_group;
+----------------+------+------+-----+---------+-------+
| Field          | Type | Null | Key | Default | Extra |
+----------------+------+------+-----+---------+-------+
| certificate_id | int  | NO   | PRI | NULL    |       |
| group_id       | int  | NO   | PRI | NULL    |       |
+----------------+------+------+-----+---------+-------+
2 rows in set (0.00 sec)
```


### Selecionando base de dados e ambiente de deploy

### Ambiente de desenvolvimento, com SQLite3

### Ambiente de desenvolvimento, com MySQL

### Ambiente de produção, com MySQL e docker compose

## Testes

## Docker compose

Para facilitar o deploy nos mais variados ambientes, a aplicação e serviços complementares foram estruturados em containers docker e relacionados através do docker composer (vide arquivo `docker-compose.yml`).

Nessa estrutura três serviços foram definidos:

- **web**: Utiliza a imagem `python:3.10-alpine3.17`, definida em um Dockerfile. Container responsável por rodar a aplicação, servida através do serviço `guinicorn`. 
- **nginx**: Realiza o proxy reverso dos acessos aos endpoints da API. Utiliza a imagem `nginx:1.23.4-bullseye`, construída a partir de um Dockerfile.  
- **db**: MySQL, utilizando a imagem `mysql:8.0`. As variáveis de ambiente usadas pela imagem foram definidas no próprio arquivo do docker compose.

## Considerações

## Dificuldades encontradas

## Pendências e pontos de melhoria

Devido a limitação de tempo e minha falta de experiência com as tecnologias utilizadas nesse projeto, o mesmo não pode ser considerado concluído.

Alguns ajustes e implementações ainda carecem de finalização. Seguem alguns desses pontos:

- Implementação de mais testes.
- Utilização de arquivo com variáveis de ambiente para facilitar a execução e deploy do projeto em diferentes circunstâncias (desenvolvimento, teste, diferentes bases de dados, diferentes infraestruturas, etc).
- Tratamento correto para as questões que envolvem o timezone.

