import tkinter as tk
from flask import Flask, jsonify, request, Response, render_template
import xml.etree.ElementTree as ET
import logging
from threading import Thread
import os
import signal

app = Flask(__name__)

# Variável para controlar o estado do servidor
servidor_ativo = False
endereco_servidor = '127.0.0.1'
porta_servidor = 5000
servidor_thread = None

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

# Rota para a página principal
@app.route('/')
def index():
    return render_template('index.html')

# Função para iniciar o servidor Flask numa thread
def iniciar_servidor(endereco, porta):
    global servidor_ativo
    servidor_ativo = True
    app.run(host=endereco, port=porta, debug=False, use_reloader=False)

def desligar_servidor():
    global servidor_ativo
    if servidor_ativo:
        os.kill(os.getpid(), signal.SIGINT)
        servidor_ativo = False
        logging.info('Servidor desligado.')

def correr_servidor(endereco, porta):
    global servidor_thread
    servidor_thread = Thread(target=iniciar_servidor, args=(endereco, porta))
    servidor_thread.daemon = True
    servidor_thread.start()

# Interface gráfica com Tkinter
def criar_janela():
    janela = tk.Tk()
    janela.title('Servidor Flask com Métodos HTTP')

    tk.Label(janela, text="Endereço:").pack(pady=5)
    endereco_input = tk.Entry(janela)
    endereco_input.pack(pady=5)
    endereco_input.insert(0, endereco_servidor)

    tk.Label(janela, text="Porta:").pack(pady=5)
    porta_input = tk.Entry(janela)
    porta_input.pack(pady=5)
    porta_input.insert(0, str(porta_servidor))

    def ligar_servidor():
        endereco = endereco_input.get()
        porta = int(porta_input.get())
        correr_servidor(endereco, porta)
        log_text.insert(tk.END, f'Servidor iniciado em {endereco}:{porta}\n')

    def desligar_servidor_gui():
        desligar_servidor()
        log_text.insert(tk.END, 'Servidor desligado.\n')

    def sair():
        desligar_servidor()
        janela.quit()

    tk.Button(janela, text='Ligar Servidor', command=ligar_servidor).pack(pady=5)
    tk.Button(janela, text='Desligar Servidor', command=desligar_servidor_gui).pack(pady=5)
    tk.Button(janela, text='Sair', command=sair).pack(pady=5)

    log_text = tk.Text(janela, height=10)
    log_text.pack(pady=10)

    janela.mainloop()

# Criar o ficheiro XML se ainda não existir
criar_estrutura_xml()

# Iniciar a interface gráfica (Tkinter)
criar_janela()
