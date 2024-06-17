from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import json
import sys
from datetime import datetime
import pytz
import psycopg2
import os

sys.stdout.flush()

app = Flask(__name__)

# Dados de usuário para validar
usuario_valido = 'admin'
senha_valida = '123'

# Configurações do SQLite
DATABASE = os.path.join(os.environ['VERCEL_TMP'], 'alunos.db')

@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    usuario_digitado = request.form.get('usuario')
    senha_digitada = request.form.get('senha')

    if usuario_digitado == usuario_valido and senha_digitada == senha_valida:
        # Se as credenciais são válidas, redireciona para a página principal
        return redirect(url_for('pagina_principal'))
    else:
        # Se as credenciais são inválidas, exibe uma mensagem de erro
        return render_template('login.html', erro='Credenciais inválidas. Tente novamente.')


@app.route('/principal')
def pagina_principal():
    try:
        conn = psycopg2.connect(
            host="silly.db.elephantsql.com",
            database="ttrillsq",
            user="ttrillsq",
            password="6vYRHBpb3g9DzhB9hKlYj6rGZnoJZWzy"
        )
        cur = conn.cursor()
        cur.execute('SELECT id, nome, ano, turno, credito FROM alunos ORDER BY ano, turno, nome')
        alunos = cur.fetchall()

        # Organizar os alunos por ano e turno
        alunos_por_turno_e_ano = {}
        for aluno in alunos:
            ano = aluno['ano']
            turno = aluno['turno']

            if turno not in alunos_por_turno_e_ano:
                alunos_por_turno_e_ano[turno] = {}

            if ano not in alunos_por_turno_e_ano[turno]:
                alunos_por_turno_e_ano[turno][ano] = []

            alunos_por_turno_e_ano[turno][ano].append(aluno)

        # Passar informações dos turnos para o template
        turnos = set(aluno['turno'] for aluno in alunos)
        return render_template('principal.html', alunos_por_turno_e_ano=alunos_por_turno_e_ano, turnos=turnos)
    except Exception as e:
        print(f"Erro ao carregar a página principal: {e}")
        return render_template('erro.html', erro=str(e)), 500


# Função para criar a tabela se ela não existir
def create_table():
    conn = psycopg2.connect(
        host="silly.db.elephantsql.com",
        database="ttrillsq",
        user="ttrillsq",
        password="6vYRHBpb3g9DzhB9hKlYj6rGZnoJZWzy"
    )
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id SERIAL PRIMARY KEY,
            nome TEXT,
            turno TEXT,
            ano TEXT,
            responsavel TEXT,
            contato TEXT,
            credito TEXT,
            segunda TEXT DEFAULT '0,00',
            terca TEXT DEFAULT '0,00',
            quarta TEXT DEFAULT '0,00',
            quinta TEXT DEFAULT '0,00',
            sexta TEXT DEFAULT '0,00'
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS historico_consumo (
            id SERIAL PRIMARY KEY,
            aluno_id INTEGER,
            data TEXT,
            valor REAL,
            tipo_transacao TEXT,
            FOREIGN KEY (aluno_id) REFERENCES alunos(id)
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Rota para lidar com o envio do formulário
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    create_table()
    if request.method == 'POST':
        nome = request.form.get('nome')
        turno = request.form.get('turno')
        ano = request.form.get('ano')
        responsavel = request.form.get('responsavel')
        contato = request.form.get('contato')
        credito = request.form.get('credito')

        if not all([nome, turno, ano, responsavel, contato, credito]):
            return 'Erro: todos os campos são obrigatórios', 400

        segunda = '0,00'
        terca = '0,00'
        quarta = '0,00'
        quinta = '0,00'
        sexta = '0,00'

        try:
            # Inserir dados no banco de dados
            conn = psycopg2.connect(
                host="silly.db.elephantsql.com",
                database="ttrillsq",
                user="ttrillsq",
                password="6vYRHBpb3g9DzhB9hKlYj6rGZnoJZWzy"
            )
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO alunos (nome, turno, ano, responsavel, contato, credito, segunda, terca, quarta, quinta, sexta) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                (nome, turno, ano, responsavel, contato, credito, segunda, terca,
                 quarta, quinta, sexta))
            conn.commit()
            cur.close()
            conn.close()
        except psycopg2.Error as e:
            return f'Erro ao inserir dados no banco de dados: {e}', 500

        # Redirecionar para a página de cadastro
        return render_template('cadastro.html',
                             success_message='Cadastro realizado com sucesso!')

    return render_template('cadastro.html')


# Rota para exibir a lista de alunos
@app.route('/lista_alunos')
def lista_alunos():
  # Consultar dados dos alunos no banco de dados
  with psycopg2.connect(
    host="silly.db.elephantsql.com",
    database="ttrillsq",
    user="ttrillsq",
    password="6vYRHBpb3g9DzhB9hKlYj6rGZnoJZWzy"
  ) as conn:
    cur = conn.cursor()
    cur.execute(
        'SELECT id, nome, turno, ano, responsavel, contato, credito FROM alunos ORDER BY ano, turno, nome'
    )
    alunos = cur.fetchall()

  # Organizar os alunos por ano e turno
  alunos_por_turno_e_ano = {}
  for aluno in alunos:
    ano = aluno['ano']
    turno = aluno['turno']

    if turno not in alunos_por_turno_e_ano:
      alunos_por_turno_e_ano[turno] = {}

    if ano not in alunos_por_turno_e_ano[turno]:
      alunos_por_turno_e_ano[turno][ano] = []

    alunos_por_turno_e_ano[turno][ano].append(aluno)

  # Passar informações dos turnos para o template
  turnos = set(aluno['turno'] for aluno in alunos)

  return render_template('lista_alunos.html',
                         alunos_por_turno_e_ano=alunos_por_turno_e_ano,
                         turnos=turnos)



# Rota para editar alunos
@app.route('/editar_aluno/<int:aluno_id>', methods=['GET', 'POST'])
def editar_aluno(aluno_id):
    if request.method == 'GET':
        # Consultar dados do aluno pelo ID e passar para o template
        with psycopg2.connect(
            host="silly.db.elephantsql.com",
            database="ttrillsq",
            user="ttrillsq",
            password="6vYRHBpb3g9DzhB9hKlYj6rGZnoJZWzy"
        ) as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM alunos WHERE id = %s', (aluno_id, ))
            aluno = cur.fetchone()

        return render_template('editar_aluno.html', aluno=aluno)
    elif request.method == 'POST':
        # Obter os dados atualizados do formulário
        nome = request.form.get('nome')
        ano = request.form.get('ano')
        turno = request.form.get('turno')
        responsavel = request.form.get('responsavel')
        contato = request.form.get('contato')
        credito = request.form.get('credito')

        # Atualizar os dados no banco de dados
        with psycopg2.connect(
            host="silly.db.elephantsql.com",
            database="ttrillsq",
            user="ttrillsq",
            password="6vYRHBpb3g9DzhB9hKlYj6rGZnoJZWzy"
        ) as conn:
            cur = conn.cursor()
            cur.execute(
                '''
                    UPDATE alunos
                    SET nome=%s, ano=%s, turno=%s, responsavel=%s, contato=%s, credito=%s
                    WHERE id=%s
                ''', (nome, ano, turno, responsavel, contato, credito, aluno_id))

        # Redirecionar para a lista de alunos após a edição
        return redirect(url_for('lista_alunos'))

# Rota para exibir o histórico de consumo de um aluno
@app.route('/historico/<int:aluno_id>')
def historico(aluno_id):
    # Consultar histórico de consumo do aluno no banco de dados
    with psycopg2.connect(
        host="silly.db.elephantsql.com",
        database="ttrillsq",
        user="ttrillsq",
        password="6vYRHBpb3g9DzhB9hKlYj6rGZnoJZWzy"
    ) as conn:
        cur = conn.cursor()
        cur.execute(
            'SELECT data, valor, tipo_transacao FROM historico_consumo WHERE aluno_id = %s ORDER BY data DESC',
            (aluno_id, ))
        historico_consumo = cur.fetchall()

    # Consultar dados do aluno para exibir na página
    with psycopg2.connect(
        host="silly.db.elephantsql.com",
        database="ttrillsq",
        user="ttrillsq",
        password="6vYRHBpb3g9DzhB9hKlYj6rGZnoJZWzy"
    ) as conn:
        cur = conn.cursor()
        cur.execute('SELECT nome, credito FROM alunos WHERE id = %s', (aluno_id, ))
        aluno = cur.fetchone()

    return render_template('historico.html',
                         aluno=aluno,
                         historico_consumo=historico_consumo)

# Modifique a rota /atualizar_consumo_diario para lidar com a atualização dos valores diários
@app.route('/atualizar_consumo_diario', methods=['POST'])
def atualizar_consumo_diario():
    try:
        data = json.loads(request.data)
        aluno_id = int(data['alunoId'])
        dia_semana = data['diaSemana']
        consumo_diario = float(data['consumoDiario'])

        # Atualizar o consumo diário no banco de dados
        with psycopg2.connect(
            host="silly.db.elephantsql.com",
            database="ttrillsq",
            user="ttrillsq",
            password="6vYRHBpb3g9DzhB9hKlYj6rGZnoJZWzy"
        ) as conn:
            cur = conn.cursor()
            cur.execute(f'UPDATE alunos SET {dia_semana} = %s WHERE id = %s',
                        (consumo_diario, aluno_id))
            conn.commit()

        # Atualizar o valor total da semana no banco de dados
        with psycopg2.connect(
            host="silly.db.elephantsql.com",
            database="ttrillsq",
            user="ttrillsq",
            password="6vYRHBpb3g9DzhB9hKlYj6rGZnoJZWzy"
        ) as conn:
            cur = conn.cursor()
            cur.execute(
                'UPDATE alunos SET credito = credito + %s WHERE id = %s',
                (consumo_diario, aluno_id))
            conn.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Rota para subtrair crédito do aluno
@app.route('/subtrair_credito/<int:aluno_id>/<float:valor>')
def subtrair_credito(aluno_id, valor):
    try:
        # Subtrair crédito do aluno no banco de dados
        with psycopg2.connect(
            host="silly.db.elephantsql.com",
            database="ttrillsq",
            user="ttrillsq",
            password="6vYRHBpb3g9DzhB9hKlYj6rGZnoJZWzy"
        ) as conn:
            cur = conn.cursor()
            cur.execute('UPDATE alunos SET credito = credito - %s WHERE id = %s',
                        (valor, aluno_id))
            conn.commit()

        # Registrar transação no histórico de consumo
        with psycopg2.connect(
            host="silly.db.elephantsql.com",
            database="ttrillsq",
            user="ttrillsq",
            password="6vYRHBpb3g9DzhB9hKlYj6rGZnoJZWzy"
        ) as conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO historico_consumo (aluno_id, data, valor, tipo_transacao) VALUES (%s, NOW(), %s, %s)',
                        (aluno_id, valor, 'saida'))
            conn.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Rota para realizar pagamento do aluno
@app.route('/realizar_pagamento/<int:aluno_id>/<float:valor>', methods=['POST'])
def realizar_pagamento(aluno_id, valor):
    try:
        # Realizar pagamento do aluno no banco de dados
        with psycopg2.connect(
            host="silly.db.elephantsql.com",
            database="ttrillsq",
            user="ttrillsq",
            password="6vYRHBpb3g9DzhB9hKlYj6rGZnoJZWzy"
        ) as conn:
            cur = conn.cursor()
            cur.execute('UPDATE alunos SET credito = credito + %s WHERE id = %s',
                        (valor, aluno_id))
            conn.commit()

        # Registrar transação no histórico de consumo
        with psycopg2.connect(
            host="silly.db.elephantsql.com",
            database="ttrillsq",
            user="ttrillsq",
            password="6vYRHBpb3g9DzhB9hKlYj6rGZnoJZWzy"
        ) as conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO historico_consumo (aluno_id, data, valor, tipo_transacao) VALUES (%s, NOW(), %s, %s)',
                        (aluno_id, valor, 'entrada'))
            conn.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Rota para excluir aluno
@app.route('/excluir_aluno/<int:aluno_id>', methods=['DELETE'])
def excluir_aluno(aluno_id):
    try:
        # Excluir aluno do banco de dados
        with psycopg2.connect(
            host="silly.db.elephantsql.com",
            database="ttrillsq",
            user="ttrillsq",
            password="6vYRHBpb3g9DzhB9hKlYj6rGZnoJZWzy"
        ) as conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM alunos WHERE id = %s', (aluno_id,))
            conn.commit()

        # Excluir histórico de consumo do aluno
        with psycopg2.connect(
            host="silly.db.elephantsql.com",
            database="ttrillsq",
            user="ttrillsq",
            password="6vYRHBpb3g9DzhB9hKlYj6rGZnoJZWzy"
        ) as conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM historico_consumo WHERE aluno_id = %s', (aluno_id,))
            conn.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    create_table()
    app.run(debug=True)

