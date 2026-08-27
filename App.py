cat << 'EOF' > app.py
from flask import Flask, render_template_string, request, jsonify
import os, shutil, json, zlib, random

app = Flask(__name__)

KEY_CORRECTA = "SOSA-VIP-2026"
DURACION_KEY = "30 Días (VIP PERMANENTE)"
LINK_WHATSAPP = "https://whatsapp.com/channel/0029VbDZQuIHLHQctWBaoB2N" 
LINK_TELEGRAM = "https://t.me/+18097819224"
URL_LOGO_VIP = "/static/logo.png"

def hex_a_rgba(hex_str):
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 6:
        r = int(hex_str[0:2], 16) / 255.0
        g = int(hex_str[2:4], 16) / 255.0
        b = int(hex_str[4:6], 16) / 255.0
        return {"r": round(r, 4), "g": round(g, 4), "b": round(b, 4), "a": 1.0}
    return {"r": 0.0, "g": 1.0, "b": 0.5, "a": 1.0}

def modificar_clave_recursiva(obj, clave_buscar, nuevo_valor):
    cambios = 0
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == clave_buscar:
                obj[k] = nuevo_valor
                cambios += 1
            else:
                cambios += modificar_clave_recursiva(v, clave_buscar, nuevo_valor)
    elif isinstance(obj, list):
        for item in obj:
            cambios += modificar_clave_recursiva(item, clave_buscar, nuevo_valor)
    return cambios

HTML_PANEL = f'''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOSA MOD MANAGER VIP</title>
    <style>
        body {{ background: #080b10; color: #e6edf3; font-family: sans-serif; text-align: center; padding: 15px; margin: 0; }}
        .container {{ max-width: 480px; margin: 0 auto; }}
        .logo-img {{ width: 140px; height: 140px; object-fit: contain; filter: drop-shadow(0px 0px 14px rgba(255, 0, 0, 0.7)); }}
        .rgb-text {{
            background: linear-gradient(90deg, #ff0000, #ff7300, #fffb00, #00ff2b, #00e1ff, #7a00ff, #ff00c8, #ff0000);
            background-size: 400%; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            animation: rgbAnimation 5s linear infinite; font-weight: 900;
        }}
        @keyframes rgbAnimation {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
        .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 14px; padding: 18px; margin: 12px 0; box-shadow: 0 8px 24px rgba(0,0,0,0.5); }}
        input[type="text"], select {{ width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #30363d; background: #0d1117; color: #00ff88; box-sizing: border-box; }}
        button {{ width: 100%; padding: 12px; margin: 6px 0; border-radius: 8px; border: none; font-weight: bold; cursor: pointer; }}
        .btn-main {{ background: #238636; color: white; }}
        .btn-opt {{ background: #161b22; color: #c9d1d9; border: 1px solid #30363d; text-align: left; font-size: 13px; padding: 10px; }}
        .btn-back {{ background: #21262d; color: #8b949e; border: 1px solid #30363d; }}
        .hidden {{ display: none !important; }}
        .file-list {{ max-height: 150px; overflow-y: auto; text-align: left; background: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 8px; margin: 8px 0; }}
        .file-item {{ padding: 4px; border-bottom: 1px solid #21262d; font-size: 12px; font-family: monospace; color: #58a6ff; }}
        #status-msg {{ margin-top: 12px; font-size: 12px; font-weight: bold; white-space: pre-wrap; text-align: left; background: #0d1117; padding: 10px; border-radius: 8px; border: 1px solid #21262d; }}
    </style>
</head>
<body>
<div class="container">
    <img src="{URL_LOGO_VIP}" alt="SOSA VIP" class="logo-img">
    <h2 class="rgb-text">SOSA MOD MANAGER VIP</h2>

    <div id="login-box" class="card">
        <h3 class="rgb-text">🔑 INICIAR SESIÓN</h3>
        <input type="text" id="key-input" placeholder="Pega tu KEY VIP aquí...">
        <button type="button" class="btn-main" onclick="verificarKey()">ENTRAR AL PANEL</button>
    </div>

    <div id="panel-box" class="card hidden">
        <h3 class="rgb-text">🛠️ EDITOR MANUAL DE DUMPS Y VALORES</h3>
        <button type="button" class="btn-opt" onclick="abrirEditorManual()">[17] Modificar Valor Directo en Dumps (Como en el Video)</button>
        <button type="button" class="btn-opt" onclick="alert('Selecciona la opción 17 para el modo del vídeo')">[18] Modificación por Lotes (Fuerza Color)</button>
    </div>

    <div id="editor-box" class="card hidden">
        <h3 class="rgb-text">📝 DUMP & VALUE EDITOR</h3>
        
        <input type="text" id="origen-dir" placeholder="📂 Ruta carpeta de Dumps ORIGEN...">
        <button type="button" class="btn-opt" style="text-align:center; background:#21262d;" onclick="escaneoCarpeta()">🔍 Cargar y Ver Dumps</button>
        
        <div id="lista-archivos-box" class="file-list hidden"></div>

        <label style="font-size: 12px; text-align: left; display: block; margin-top: 10px;">🏷️ Clave / Propiedad a Cambiar:</label>
        <input type="text" id="target-key" placeholder="Ej: _Color, m_LocalScale, _OutlineColor">

        <label style="font-size: 12px; text-align: left; display: block;">🎯 Nuevo Valor a Inyectar:</label>
        <input type="text" id="target-value" placeholder='Ej: {"r":0, "g":1, "b":0, "a":1} o 100'>

        <input type="text" id="destino-dir" placeholder="🎯 Ruta carpeta DESTINO...">

        <button type="button" class="btn-main" onclick="ejecutarCambioValor()">⚡ APLICAR CAMBIO EN DUMPS</button>
        <div id="status-msg" class="hidden"></div>
        <br>
        <button type="button" class="btn-back" onclick="volverPanel()">← Volver</button>
    </div>
</div>

<script>
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
            }} else {{ alert('❌ KEY Incorrecta'); }}
        }});
    }}

    function abrirEditorManual() {{
        document.getElementById('panel-box').classList.add('hidden');
        document.getElementById('editor-box').classList.remove('hidden');
    }}

    function volverPanel() {{
        document.getElementById('editor-box').classList.add('hidden');
        document.getElementById('panel-box').classList.remove('hidden');
    }}

    function escaneoCarpeta() {{
        let origen = document.getElementById('origen-dir').value.trim();
        if(!origen) {{ alert('Ingresa la ruta de origen'); return; }}
        fetch('/listar_dumps', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{origen: origen}})
        }})
        .then(res => res.json())
        .then(data => {{
            let box = document.getElementById('lista-archivos-box');
            box.classList.remove('hidden');
            if(data.archivos && data.archivos.length > 0) {{
                box.innerHTML = '<b>Archivos Dumps Encontrados (' + data.archivos.length + '):</b><br>' + 
                    data.archivos.map(f => '<div class="file-item">📄 ' + f + '</div>').join('');
            }} else {{
                box.innerHTML = '<span style="color:#ff4d4d;">No se encontraron archivos en la ruta.</span>';
            }}
        }});
    }}

    function ejecutarCambioValor() {{
        let origen = document.getElementById('origen-dir').value.trim();
        let destino = document.getElementById('destino-dir').value.trim();
        let key = document.getElementById('target-key').value.trim();
        let val = document.getElementById('target-value').value.trim();
        let statusDiv = document.getElementById('status-msg');

        if(!origen || !destino || !key || !val) {{
            alert('⚠️ Completa todos los campos'); return;
        }}

        statusDiv.classList.remove('hidden');
        statusDiv.style.color = '#e3b341';
        statusDiv.innerText = '⏳ Editando valor en todos los dumps...';

        fetch('/modificar_valor_directo', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{origen: origen, destino: destino, clave: key, valor: val}})
        }})
        .then(res => res.json())
        .then(data => {{
            if(data.exito) {{
                statusDiv.style.color = '#00ff88';
                statusDiv.innerText = data.mensaje;
            }} else {{
                statusDiv.style.color = '#ff4d4d';
                statusDiv.innerText = '❌ ' + data.mensaje;
            }}
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

@app.route('/listar_dumps', methods=['POST'])
def listar_dumps():
    datos = request.get_json()
    origen = datos.get('origen', '').strip()
    if os.path.exists(origen):
        archivos = [f for f in os.listdir(origen) if os.path.isfile(os.path.join(origen, f))]
        return jsonify({'archivos': archivos})
    return jsonify({'archivos': []})

@app.route('/modificar_valor_directo', methods=['POST'])
def modificar_valor_directo():
    datos = request.get_json()
    origen = datos.get('origen', '').strip()
    destino = datos.get('destino', '').strip()
    clave = datos.get('clave', '').strip()
    valor_raw = datos.get('valor', '').strip()

    try:
        nuevo_valor = json.loads(valor_raw)
    except Exception:
        try:
            nuevo_valor = float(valor_raw) if '.' in valor_raw else int(valor_raw)
        except ValueError:
            nuevo_valor = valor_raw

    if not os.path.exists(origen):
        return jsonify({'exito': False, 'mensaje': 'La carpeta origen no existe.'})

    os.makedirs(destino, exist_ok=True)
    archivos = [f for f in os.listdir(origen) if os.path.isfile(os.path.join(origen, f))]
    
    archivos_modificados = 0
    total_cambios = 0

    for archivo in archivos:
        path_origen = os.path.join(origen, archivo)
        path_destino = os.path.join(destino, archivo)
        
        try:
            with open(path_origen, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            num_cambios = modificar_clave_recursiva(data, clave, nuevo_valor)
            
            if num_cambios > 0:
                with open(path_destino, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                archivos_modificados += 1
                total_cambios += num_cambios
            else:
                shutil.copy2(path_origen, path_destino)
        except Exception:
            shutil.copy2(path_origen, path_destino)

    return jsonify({
        'exito': True, 
        'mensaje': f'¡Éxito! Se reemplazó la propiedad "{clave}" con {total_cambios} reemplazos en {archivos_modificados} dumps.'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF
