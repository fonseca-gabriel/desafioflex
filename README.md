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

Para efeitos de melhor compreensão, segue a estrutura da base de dados utilizada no projeto:


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

O tipo de base de dados utilizado pode ser escolhido entre MySQL ou SQLite3.

Para optar por um ou outro, basta alterar a variável `database` no início da aplicação (`app.py`).

#### SQLite3

Caso deseje utilizar o **SQLite3**, a variável deve ser definida para a string 'sqlite3':
```
database = 'sqlite3'
```


#### MySQL
Para utilizar o **MySQL**, a variável `database` recebe a string 'mysql':
```
database = 'mysql'
```

No caso do MySQL pode-se ainda optar por utilizá-lo em uma versão stand-alone, de modo que o banco de dados seja executado na máquina local e em sua porta padrão: `127.0.0.1:3306`.

Para utilizar o MySQL localmente, basta alterar a variável `mysql_host` para o valor 'local':
```
mysql_host = 'local'
```

Já para utilizá-lo dentro da estrutura do docker compose, a varíavel deve ser alterado para 'docker':
```
mysql_host = 'docker'
```

## Execução da aplicação
Ajustados os parâmetros para definição do banco de dados, é possível, portanto, executar o projeto em alguns cenários diferentes.

Em ambos os casos pode-se utilizar o script `create_test_database.py` para popular alguns dados iniciais de teste na base de dados:

```commandline
$ python create_test_database.py 
Apagando dados do banco...
Criando novo banco de dados...
Criando grupos...
Adicionando grupos...
Criando certificados...
Adicionando certificados...
Salvando dados no banco de dados...
Dados populados com sucesso!

```

O script criará 4 grupos e 4 certificados de teste, de modo a facilitar a visualização do projeto em execuação em um primeiro momento.

### Executando localmente, stand-alone

Para executar o projeto localmente, basta rodar a aplicação manualmente, independentemente do banco de dados selecionado:

```python app.py```

*PS: para utilizar o banco de dados MySQL localmente é necessário que o mesmo já esteja inicializado e rodando na porta 3306. Além disso o procedimento de migração deve ter sido executado, de modo a criar o banco de dados, conforme descrito no tópico "Base de dado/MySQL"* 

### Executando com docker-compose, localmente

Para utilizar e estrutura "dockerizada", vale reforçar a necessidade das variáveis da aplicação estarem setadas da seguinte maneira:

```
database = 'mysql'
mysql_host = 'docker'
```



## Testes
A cobertura de testes ainda é limitada. A mesma deve ser executada com o `pytest`, executando o comando na pasta raiz do projeto, onde encontra-se o arquivo `test_app.py`, responsável pelos mesmos.

```
pytest
```

Outras considerações a respeito dos testes foram adicionadas no tópico de pendências e melhorias.


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

- Implementação de mais testes, de preferência seguindo a prática de desenvolvimento orientado por testes.
- Utilizar algum processo automatizado para realização dos testes, preferencialmente junto à uma estrutura de CI/CD, como o GitHub Actions.
- Utilização de arquivo com variáveis de ambiente para facilitar a execução e deploy do projeto em diferentes circunstâncias (desenvolvimento, teste, diferentes bases de dados, diferentes infraestruturas, etc).
- Tratamento correto para as questões que envolvem o timezone.


