from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

KEY_CORRECTA = "SOSA-VIP-2026"

HTML_PANEL = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOSA MOD MANAGER PRO</title>
    <style>
        body { background-color: #0d1117; color: white; font-family: sans-serif; text-align: center; padding: 15px; margin: 0; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; margin: 10px auto; max-width: 450px; }
        h2 { color: #58a6ff; margin-bottom: 5px; }
        .cat-title { color: #2ea043; font-weight: bold; margin-top: 15px; text-align: left; font-size: 14px; border-bottom: 1px solid #30363d; padding-bottom: 3px; }
        input, select { width: 95%; padding: 10px; margin: 6px 0; border-radius: 6px; border: 1px solid #30363d; background: #0d1117; color: white; box-sizing: border-box; }
        button { width: 95%; padding: 12px; margin: 8px 0; border-radius: 6px; border: none; font-weight: bold; cursor: pointer; }
        .btn-main { background: #238636; color: white; }
        .btn-opt { background: #21262d; color: #c9d1d9; border: 1px solid #30363d; text-align: left; font-size: 13px; }
        .btn-opt:hover { background: #30363d; color: white; }
        .hidden { display: none; }
    </style>
</head>
<body>

    <h2>🔥 SOSA MOD MANAGER WEB 🔥</h2>
    <p style="font-size: 12px; color: #8b949e;">Termux Edition (TURBO)</p>

    <!-- LOGIN CON KEY -->
    <div id="login-box" class="card">
        <h3>ACCESO RESTRINGIDO</h3>
        <input type="text" id="key-input" placeholder="Pega tu KEY aquí...">
        <button class="btn-main" onclick="verificarKey()">ENTRAR AL PANEL</button>
    </div>

    <!-- PANEL PRINCIPAL -->
    <div id="panel-box" class="card hidden">
        
        <div class="cat-title">🌈 COMBOS HOLO (NO ANTENA)</div>
        <button class="btn-opt" onclick="seleccionarOpcion(1)">[1] Holo(NoAnt) + WH GameObject</button>
        <button class="btn-opt" onclick="seleccionarOpcion(2)">[2] Holo(NoAnt) + WH Transform</button>
        <button class="btn-opt" onclick="seleccionarOpcion(3)">[3] Solo Holo(NoAnt)</button>

        <div class="cat-title">📡 COMBOS HOLO (ANTENA)</div>
        <button class="btn-opt" onclick="seleccionarOpcion(4)">[4] Holo(Antena) + WH GameObject</button>
        <button class="btn-opt" onclick="seleccionarOpcion(5)">[5] Holo(Antena) + WH Transform</button>
        <button class="btn-opt" onclick="seleccionarOpcion(6)">[6] Solo Holo(Antena)</button>

        <div class="cat-title">👻 COMBOS SIN HOLO</div>
        <button class="btn-opt" onclick="seleccionarOpcion(7)">[7] WH GameObjectCollider</button>
        <button class="btn-opt" onclick="seleccionarOpcion(8)">[8] WH Transform</button>

        <div class="cat-title">🌈 INDIVIDUALES</div>
        <button class="btn-opt" onclick="seleccionarOpcion(9)">[9] Solo Holo (No Antena)</button>
        <button class="btn-opt" onclick="seleccionarOpcion(10)">[10] Solo Holo (Antena)</button>
        <button class="btn-opt" onclick="seleccionarOpcion(11)">[11] Solo WH GameObjectCollider</button>
        <button class="btn-opt" onclick="seleccionarOpcion(12)">[12] Solo WH Transform</button>

        <div class="cat-title">🛠️ HERRAMIENTAS</div>
        <button class="btn-opt" onclick="seleccionarOpcion(13)">[13] Renombrador FileInfo</button>
        <button class="btn-opt" onclick="seleccionarOpcion(14)">[14] Entrar a apartado CRC32 (Spoof)</button>
    </div>

    <!-- FORMULARIO DE RUTAS Y EJECUCIÓN -->
    <div id="form-box" class="card hidden">
        <h3 id="opcion-titulo">Configurar Opción</h3>
        
        <input type="text" id="ruta-origen" placeholder="Ruta de archivos ORIGINALES...">
        <input type="text" id="ruta-destino" placeholder="Ruta de carpeta MODIFICADOS...">
        
        <button class="btn-main" onclick="ejecutarAccion()">INICIAR PROCESO</button>
        <button class="btn-opt" style="text-align:center;" onclick="volverAlPanel()">← Volver al Panel</button>
    </div>

    <script>
        let opcionSeleccionada = 0;

        function verificarKey() {
            let userKey = document.getElementById('key-input').value;
            fetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: userKey})
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'ok') {
                    document.getElementById('login-box').classList.add('hidden');
                    document.getElementById('panel-box').classList.remove('hidden');
                } else {
                    alert('❌ KEY Incorrecta');
                }
            });
        }

        function seleccionarOpcion(opc) {
            opcionSeleccionada = opc;
            document.getElementById('opcion-titulo').innerText = 'Opción Seleccionada: [' + opc + ']';
            document.getElementById('panel-box').classList.add('hidden');
            document.getElementById('form-box').classList.remove('hidden');
        }

        function volverAlPanel() {
            document.getElementById('form-box').classList.add('hidden');
            document.getElementById('panel-box').classList.remove('hidden');
        }

        function ejecutarAccion() {
            let origen = document.getElementById('ruta-origen').value;
            let destino = document.getElementById('ruta-destino').value;

            if(!origen || !destino) {
                alert('⚠️ Debes ingresar ambas rutas para continuar.');
                return;
            }

            alert('🚀 Ejecutando opción ' + opcionSeleccionada + '\\nOrigen: ' + origen + '\\nDestino: ' + destino);
        }
    </script>
</body>
</html>
'''

@app.route('/')
def inicio():
    return render_template_string(HTML_PANEL)

@app.route('/login', methods=['POST'])
def login():
    datos = request.get_json()
    if datos.get('key') == KEY_CORRECTA:
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    