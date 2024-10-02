// Função para enviar uma requisição GET
function metodoGET() {
    fetch('/dados')
        .then(response => response.json())
        .then(data => {
            document.getElementById('get-response').textContent = JSON.stringify(data, null, 2);
        });
}

// Função para enviar uma requisição POST
function metodoPOST() {
    const nome = document.getElementById('nome').value;
    const valor = document.getElementById('valor').value;
    fetch('/dados', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nome, valor })
    }).then(response => response.json())
      .then(data => {
          document.getElementById('post-response').textContent = JSON.stringify(data, null, 2);
      });
}

// Função para enviar uma requisição PUT
function metodoPUT() {
    const nome = document.getElementById('nome-put').value;
    const valor = document.getElementById('valor-put').value;
    fetch(`/dados/${nome}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ valor })
    }).then(response => response.json())
      .then(data => {
          document.getElementById('put-response').textContent = JSON.stringify(data, null, 2);
      });
}

// Função para enviar uma requisição DELETE
function metodoDELETE() {
    const nome = document.getElementById('nome-delete').value;
    fetch(`/dados/${nome}`, {
        method: 'DELETE'
    }).then(response => response.json())
      .then(data => {
          document.getElementById('delete-response').textContent = JSON.stringify(data, null, 2);
      });
}
