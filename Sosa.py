from flask import Flask, render_template_string, request, jsonify
import os, shutil

app = Flask(__name__)

# ==========================================
# CONFIGURACIÓN VIP & REDES
# ==========================================
KEY_CORRECTA = "SOSA-VIP-2026"
DURACION_KEY = "30 Días (VIP PERMANENTE)"

LINK_WHATSAPP = "https://whatsapp.com/channel/0029VbDZQuIHLHQctWBaoB2N" 
LINK_TELEGRAM = "https://t.me/tu_canal_aqui"

def procesar_archivos(datos):
    origen = datos.get('origen', '')
    destino = datos.get('destino', '')
    color_holo = datos.get('color_holo', '#00ff88')
    color_antena = datos.get('color_antena', '#ff0055')

    if not os.path.exists(origen):
        return False, f"La ruta de origen no existe: {origen}"
    
    if not os.path.exists(destino):
        os.makedirs(destino, exist_ok=True)

    archivos = os.listdir(origen)
    if not archivos:
        return False, "La carpeta de origen está vacía."

    modificados = 0
    for archivo in archivos:
        path_origen = os.path.join(origen, archivo)
        path_destino = os.path.join(destino, archivo)
        
        if os.path.isfile(path_origen):
            try:
                # Intentar leer y reemplazar marcas o colores hexadecimales predeterminados
                with open(path_origen, 'r', encoding='utf-8', errors='ignore') as f:
                    contenido = f.read()

                # Reemplaza valores de color por los seleccionados
                contenido_modificado = contenido.replace("#00ff88", color_holo).replace("#ff0055", color_antena)

                with open(path_destino, 'w', encoding='utf-8') as f:
                    f.write(contenido_modificado)

                modificados += 1
            except Exception:
                # Si es binario o no editable, se copia directamente
                shutil.copy2(path_origen, path_destino)
                modificados += 1

    return True, f"¡Modificación exitosa! Se procesaron {modificados} archivos con los colores seleccionados."

HTML_PANEL = f'''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOSA MOD MANAGER PRO</title>
    <style>
        body {{ 
            background: #080b10; 
            color: #e6edf3; 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
            text-align: center; 
            padding: 15px; 
            margin: 0; 
        }}
        .container {{ max-width: 480px; margin: 0 auto; }}
        .card {{ 
            background: #161b22; 
            border: 1px solid #30363d; 
            border-radius: 14px; 
            padding: 18px; 
            margin: 12px 0; 
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }}
        h2 {{ color: #00ff88; margin-bottom: 4px; font-size: 20px; }}
        .subtitle {{ font-size: 11px; color: #8b949e; letter-spacing: 2px; margin-bottom: 15px; }}
        
        .key-info {{
            background: rgba(88, 166, 255, 0.1);
            border: 1px solid #58a6ff;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 12px;
            font-size: 13px;
            color: #58a6ff;
        }}
        
        .social-box {{
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }}
        .btn-social {{
            flex: 1;
            padding: 10px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            font-size: 13px;
            color: white;
            display: inline-block;
        }}
        .btn-wa {{ background: #25D366; }}
        .btn-tg {{ background: #0088cc; }}

        .cat-title {{ 
            color: #58a6ff; 
            font-weight: bold; 
            margin-top: 16px; 
            text-align: left; 
            font-size: 12px; 
            border-bottom: 1px solid #21262d; 
            padding-bottom: 4px; 
        }}
        .color-picker-group {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #0d1117;
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid #30363d;
            margin: 8px 0;
        }}
        input[type="color"] {{ border: none; width: 35px; height: 35px; border-radius: 50%; cursor: pointer; background: transparent; }}
        input[type="text"] {{ 
            width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; 
            border: 1px solid #30363d; background: #0d1117; color: #00ff88; box-sizing: border-box; 
        }}
        button {{ 
            width: 100%; padding: 12px; margin: 6px 0; border-radius: 8px; 
            border: none; font-weight: bold; cursor: pointer; 
        }}
        .btn-main {{ background: #238636; color: white; font-size: 14px; }}
        .btn-opt {{ background: #161b22; color: #c9d1d9; border: 1px solid #30363d; text-align: left; font-size: 12px; padding: 10px 12px; }}
        .btn-back {{ background: #21262d; color: #8b949e; border: 1px solid #30363d; }}
        .hidden {{ display: none; }}
        #status-msg {{ margin-top: 12px; font-size: 13px; font-weight: bold; }}
    </style>
</head>
<body>

<div class="container">
    <h2>🔥 SOSA MOD MANAGER WEB 🔥</h2>
    <div class="subtitle">VIP PANEL • TERMUX EDITION</div>

    <!-- LOGIN CON KEY -->
    <div id="login-box" class="card">
        <h3 style="margin-top:0; color:#f0883e;">🔑 ACCESO RESTRINGIDO</h3>
        <input type="text" id="key-input" placeholder="Pega tu KEY VIP aquí...">
        <button class="btn-main" onclick="verificarKey()">ENTRAR AL PANEL</button>
        
        <div class="social-box">
            <a href="{LINK_WHATSAPP}" target="_blank" class="btn-social btn-wa">💬 WhatsApp</a>
            <a href="{LINK_TELEGRAM}" target="_blank" class="btn-social btn-tg">✈️ Telegram</a>
        </div>
    </div>

    <!-- PANEL PRINCIPAL -->
    <div id="panel-box" class="card hidden">
        <div class="key-info">
            ⏳ <b>Duración de Key:</b> {DURACION_KEY}<br>
            STATUS: <span style="color:#00ff88;">● ACTIVO</span>
        </div>

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

        <div class="social-box">
            <a href="{LINK_WHATSAPP}" target="_blank" class="btn-social btn-wa">💬 WhatsApp</a>
            <a href="{LINK_TELEGRAM}" target="_blank" class="btn-social btn-tg">✈️ Telegram</a>
        </div>
    </div>

    <!-- FORMULARIO DE CONFIGURACIÓN -->
    <div id="form-box" class="card hidden">
        <h3 id="opcion-titulo" style="color: #58a6ff; margin-top:0;">Configurar Opción</h3>
        
        <div class="color-picker-group">
            <label>🎨 Color Holo/Personaje:</label>
            <input type="color" id="color-holo" value="#00ff88">
        </div>

        <div class="color-picker-group">
            <label>📡 Color Antena:</label>
            <input type="color" id="color-antena" value="#ff0055">
        </div>

        <input type="text" id="ruta-origen" placeholder="📂 Ruta de carpeta ORIGEN...">
        <input type="text" id="ruta-destino" placeholder="🎯 Ruta de carpeta DESTINO...">
        
        <button class="btn-main" id="btn-ejecutar" onclick="ejecutarAccion()">⚡ INICIAR PROCESO</button>
        <div id="status-msg"></div>
        <br>
        <button class="btn-back" onclick="volverAlPanel()">← Volver al Menú</button>
    </div>
</div>

<script>
    let opcionSeleccionada = 0;

    function verificarKey() {{
        let userKey = document.getElementById('key-input').value.trim();
        fetch('/login', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{key: userKey}})
        }})
        .then(res => res.json())
        .then(data => {{
            if (data.status === 'ok') {{
                document.getElementById('login-box').classList.add('hidden');
                document.getElementById('panel-box').classList.remove('hidden');
            }} else {{
                alert('❌ KEY Incorrecta');
            }}
        }});
    }}

    function seleccionarOpcion(opc) {{
        opcionSeleccionada = opc;
        document.getElementById('opcion-titulo').innerText = 'OPCIÓN [' + opc + '] SELECCIONADA';
        document.getElementById('status-msg').innerText = '';
        document.getElementById('panel-box').classList.add('hidden');
        document.getElementById('form-box').classList.remove('hidden');
    }}

    function volverAlPanel() {{
        document.getElementById('form-box').classList.add('hidden');
        document.getElementById('panel-box').classList.remove('hidden');
    }}

    function ejecutarAccion() {{
        let origen = document.getElementById('ruta-origen').value.trim();
        let destino = document.getElementById('ruta-destino').value.trim();
        let colorHolo = document.getElementById('color-holo').value;
        let colorAntena = document.getElementById('color-antena').value;
        let statusDiv = document.getElementById('status-msg');

        if(!origen || !destino) {{
            alert('⚠️ Debes ingresar ambas rutas para continuar.');
            return;
        }}

        statusDiv.style.color = '#e3b341';
        statusDiv.innerText = '⏳ Procesando archivos...';

        fetch('/procesar', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{
                opcion: opcionSeleccionada,
                origen: origen,
                destino: destino,
                color_holo: colorHolo,
                color_antena: colorAntena
            }})
        }})
        .then(res => res.json())
        .then(data => {{
            if(data.exito) {{
                statusDiv.style.color = '#00ff88';
                statusDiv.innerText = data.mensaje;
            }} else {{
                statusDiv.style.color = '#f85149';
                statusDiv.innerText = '❌ ' + data.mensaje;
            }}
        }})
        .catch(err => {{
            statusDiv.style.color = '#f85149';
            statusDiv.innerText = '❌ Error de conexión al servidor.';
        }});
    }}
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

@app.route('/procesar', methods=['POST'])
def procesar():
    datos = request.get_json()
    exito, mensaje = procesar_archivos(datos)
    return jsonify({'exito': exito, 'mensaje': mensaje})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
