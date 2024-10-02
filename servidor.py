import tkinter as tk
from flask import Flask, jsonify, request, Response, render_template
import xml.etree.ElementTree as ET
import logging
from threading import Thread

app = Flask(__name__)

logging.basicConfig(filename='servidor.log', level=logging.INFO, 
                    format='%(asctime)s %(message)s', filemode='w')

ficheiro_xml = 'dados.xml'

def criar_estrutura_xml():
    root = ET.Element('dados')
    tree = ET.ElementTree(root)
    tree.write(ficheiro_xml)

def adicionar_dado_xml(nome, valor):
    tree = ET.parse(ficheiro_xml)
    root = tree.getroot()
    dado = ET.SubElement(root, 'dado')
    ET.SubElement(dado, 'nome').text = nome
    ET.SubElement(dado, 'valor').text = valor
    tree.write(ficheiro_xml)

def obter_dados_xml():
    tree = ET.parse(ficheiro_xml)
    root = tree.getroot()
    dados = [{'nome': dado.find('nome').text, 'valor': dado.find('valor').text} for dado in root.findall('dado')]
    return dados

@app.route('/dados', methods=['GET'])
def obter_dados():
    dados = obter_dados_xml()
    logging.info('GET: Obtenção de dados')
    return jsonify(dados)

@app.route('/dados', methods=['POST'])
def adicionar_dado():
    if request.is_json:
        data = request.get_json()
        nome = data.get('nome')
        valor = data.get('valor')
        if nome and valor:
            adicionar_dado_xml(nome, valor)
            logging.info(f'POST: Dado adicionado - {nome}: {valor}')
            return jsonify({'message': 'Dado adicionado com sucesso'}), 201
        else:
            return jsonify({'error': 'Dados inválidos'}), 400
    return jsonify({'error': 'Formato inválido, esperado JSON'}), 415

@app.route('/dados/<nome>', methods=['PUT'])
def atualizar_dado(nome):
    if request.is_json:
        data = request.get_json()
        novo_valor = data.get('valor')
        if novo_valor:
            tree = ET.parse(ficheiro_xml)
            root = tree.getroot()
            for dado in root.findall('dado'):
                if dado.find('nome').text == nome:
                    dado.find('valor').text = novo_valor
                    tree.write(ficheiro_xml)
                    logging.info(f'PUT: Dado atualizado - {nome}: {novo_valor}')
                    return jsonify({'message': f'Dado {nome} atualizado com sucesso'}), 200
            return jsonify({'error': f'Dado {nome} não encontrado'}), 404
        return jsonify({'error': 'Valor inválido'}), 400
    return jsonify({'error': 'Formato inválido, esperado JSON'}), 415

@app.route('/dados/<nome>', methods=['DELETE'])
def remover_dado(nome):
    tree = ET.parse(ficheiro_xml)
    root = tree.getroot()
    for dado in root.findall('dado'):
        if dado.find('nome').text == nome:
            root.remove(dado)
            tree.write(ficheiro_xml)
            logging.info(f'DELETE: Dado {nome} removido')
            return jsonify({'message': f'Dado {nome} removido com sucesso'}), 200
    return jsonify({'error': f'Dado {nome} não encontrado'}), 404

# Rota para servir a página web
@app.route('/')
def index():
    return render_template('index.html')

# Função para correr o servidor Flask numa thread separada
def correr_servidor():
    app.run(debug=False, use_reloader=False)

# Criar a GUI com Tkinter
def criar_janela():
    janela = tk.Tk()
    janela.title('Servidor Flask com Métodos HTTP')

    janela.mainloop()

# Iniciar o ficheiro XML se ainda não existir
criar_estrutura_xml()

servidor_thread = Thread(target=correr_servidor)
servidor_thread.daemon = True
servidor_thread.start()

criar_janela()
