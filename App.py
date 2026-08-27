from flask import Flask, render_template_string, request, jsonify
import os, shutil, json, zlib

app = Flask(__name__)

# ==========================================
# CONFIGURACIÓN VIP & REDES
# ==========================================
KEY_CORRECTA = "SOSA-VIP-2026"
DURACION_KEY = "30 Días (VIP PERMANENTE)"

LINK_WHATSAPP = "https://whatsapp.com/channel/0029VbDZQuIHLHQctWBaoB2N" 
LINK_TELEGRAM = "https://t.me/tu_canal_aqui"

def hex_a_rgba(hex_str):
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 6:
        r = int(hex_str[0:2], 16) / 255.0
        g = int(hex_str[2:4], 16) / 255.0
        b = int(hex_str[4:6], 16) / 255.0
        return {"r": round(r, 4), "g": round(g, 4), "b": round(b, 4), "a": 1.0}
    return {"r": 0.0, "g": 1.0, "b": 0.5, "a": 1.0}

def calcular_crc32(path_archivo):
    with open(path_archivo, 'rb') as f:
        crc = zlib.crc32(f.read())
    return f"{crc & 0xFFFFFFFF:08X}"

def procesar_archivos(datos):
    opcion = int(datos.get('opcion', 0))
    origen = datos.get('origen', '')
    destino = datos.get('destino', '')
    nuevo_nombre = datos.get('nuevo_nombre', '')
    color_holo_hex = datos.get('color_holo', '#00ff88')
    color_antena_hex = datos.get('color_antena', '#ff0055')

    if not os.path.exists(origen):
        return False, f"La ruta de origen no existe: {origen}"

    # HERRAMIENTA 13: Renombrador FileInfo
    if opcion == 13:
        if not nuevo_nombre:
            return False, "Debes ingresar el nuevo nombre para los archivos."
        
        if not os.path.exists(destino):
            os.makedirs(destino, exist_ok=True)

        archivos = [f for f in os.listdir(origen) if os.path.isfile(os.path.join(origen, f))]
        if not archivos:
            return False, "La carpeta de origen está vacía."

        modificados = 0
        for i, archivo in enumerate(archivos, 1):
            path_origen = os.path.join(origen, archivo)
            ext = os.path.splitext(archivo)[1]
            path_destino = os.path.join(destino, f"{nuevo_nombre}_{i}{ext}")
            shutil.copy2(path_origen, path_destino)
            modificados += 1

        return True, f"¡Renombrado exitoso! Se guardaron {modificados} archivos con el patrón '{nuevo_nombre}_X'."

    # HERRAMIENTA 14: Apartado CRC32 (Spoof / Verificación)
    if opcion == 14:
        archivos = [f for f in os.listdir(origen) if os.path.isfile(os.path.join(origen, f))]
        if not archivos:
            return False, "La carpeta de origen está vacía."

        resumen_crc = []
        for archivo in archivos:
            path_file = os.path.join(origen, archivo)
            crc_val = calcular_crc32(path_file)
            resumen_crc.append(f"{archivo} ➔ CRC32: [{crc_val}]")

        return True, "CRC32 Calculado con éxito:\n" + "\n".join(resumen_crc[:10])

    # OPCIONES 1 A 12: Procesamiento de Dumps y Modificación de Colores
    if not os.path.exists(destino):
        os.makedirs(destino, exist_ok=True)

    archivos = os.listdir(origen)
    if not archivos:
        return False, "La carpeta de origen está vacía."

    rgba_holo = hex_a_rgba(color_holo_hex)
    rgba_antena = hex_a_rgba(color_antena_hex)

    # Identificar si la opción requiere Antena
    usa_antena = opcion in [4, 5, 6, 10]

    modificados = 0
    for archivo in archivos:
        path_origen = os.path.join(origen, archivo)
        path_destino = os.path.join(destino, archivo)
        
        if os.path.isfile(path_origen):
            try:
                with open(path_origen, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if "m_SavedProperties" in data and "m_Colors" in data["m_SavedProperties"]:
                    m_colors = data["m_SavedProperties"]["m_Colors"]
                    
                    for item in m_colors:
                        prop_nombre = item[0]
                        if prop_nombre in ["_Color_Tex", "_Color_DisTex", "_Mask_Dis", "_TintColor"]:
                            item[1] = rgba_holo
                        elif prop_nombre in ["_OutlineColor"] and usa_antena:
                            item[1] = rgba_antena

                    with open(path_destino, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4)
                    
                    modificados += 1
                else:
                    shutil.copy2(path_origen, path_destino)
                    modificados += 1

            except Exception:
                shutil.copy2(path_origen, path_destino)
                modificados += 1

    return True, f"¡Modificación exitosa! Se procesaron {modificados} archivos."

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
        
        .social-box {{ display: flex; gap: 10px; margin-top: 15px; }}
        .btn-social {{
            flex: 1; padding: 10px; border-radius: 8px; text-decoration: none;
            font-weight: bold; font-size: 13px; color: white; display: inline-block;
        }}
        .btn-wa {{ background: #25D366; }}
        .btn-tg {{ background: #0088cc; }}

        .cat-title {{ 
            color: #58a6ff; font-weight: bold; margin-top: 16px; 
            text-align: left; font-size: 12px; border-bottom: 1px solid #21262d; padding-bottom: 4px; 
        }}
        .color-picker-group {{
            display: flex; justify-content: space-between; align-items: center;
            background: #0d1117; padding: 8px 12px; border-radius: 8px;
            border: 1px solid #30363d; margin: 8px 0;
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
        .hidden {{ display: none !important; }}
        #status-msg {{ margin-top: 12px; font-size: 13px; font-weight: bold; white-space: pre-wrap; word-break: break-all; }}
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
        <button class="btn-opt" onclick="seleccionarOpcion(1, false, false)">[1] Holo(NoAnt) + WH GameObject</button>
        <button class="btn-opt" onclick="seleccionarOpcion(2, false, false)">[2] Holo(NoAnt) + WH Transform</button>
        <button class="btn-opt" onclick="seleccionarOpcion(3, false, false)">[3] Solo Holo(NoAnt)</button>

        <div class="cat-title">📡 COMBOS HOLO (ANTENA)</div>
        <button class="btn-opt" onclick="seleccionarOpcion(4, true, false)">[4] Holo(Antena) + WH GameObject</button>
        <button class="btn-opt" onclick="seleccionarOpcion(5, true, false)">[5] Holo(Antena) + WH Transform</button>
        <button class="btn-opt" onclick="seleccionarOpcion(6, true, false)">[6] Solo Holo(Antena)</button>

        <div class="cat-title">👻 COMBOS SIN HOLO</div>
        <button class="btn-opt" onclick="seleccionarOpcion(7, false, false)">[7] WH GameObjectCollider</button>
        <button class="btn-opt" onclick="seleccionarOpcion(8, false, false)">[8] WH Transform</button>

        <div class="cat-title">🌈 INDIVIDUALES</div>
        <button class="btn-opt" onclick="seleccionarOpcion(9, false, false)">[9] Solo Holo (No Antena)</button>
        <button class="btn-opt" onclick="seleccionarOpcion(10, true, false)">[10] Solo Holo (Antena)</button>
        <button class="btn-opt" onclick="seleccionarOpcion(11, false, false)">[11] Solo WH GameObjectCollider</button>
        <button class="btn-opt" onclick="seleccionarOpcion(12, false, false)">[12] Solo WH Transform</button>

        <div class="cat-title">🛠️ HERRAMIENTAS</div>
        <button class="btn-opt" onclick="seleccionarOpcion(13, false, true)">[13] Renombrador FileInfo</button>
        <button class="btn-opt" onclick="seleccionarOpcion(14, false, false)">[14] Entrar a apartado CRC32 (Spoof)</button>

        <div class="social-box">
            <a href="{LINK_WHATSAPP}" target="_blank" class="btn-social btn-wa">💬 WhatsApp</a>
            <a href="{LINK_TELEGRAM}" target="_blank" class="btn-social btn-tg">✈️ Telegram</a>
        </div>
    </div>

    <!-- FORMULARIO DE CONFIGURACIÓN -->
    <div id="form-box" class="card hidden">
        <h3 id="opcion-titulo" style="color: #58a6ff; margin-top:0;">Configurar Opción</h3>
        
        <!-- SELECTOR HOLO (NO MUESTRA EN CRC32 NI RENOMBRADOR) -->
        <div id="group-holo" class="color-picker-group">
            <label>🎨 Color Holo/Personaje:</label>
            <input type="color" id="color-holo" value="#00ff88">
        </div>

        <!-- SELECTOR ANTENA (SOLO SI TIENE ANTENA LA OPCIÓN) -->
        <div id="group-antena" class="color-picker-group hidden">
            <label>📡 Color Antena:</label>
            <input type="color" id="color-antena" value="#ff0055">
        </div>

        <!-- CAMPO EXCLUSIVO DE RENOMBRAR -->
        <input type="text" id="nuevo-nombre" class="hidden" placeholder="🏷️ Nuevo nombre base (ej. Mod_Asset)...">

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

    function seleccionarOpcion(opc, tieneAntena, esRenombrador) {{
        opcionSeleccionada = opc;
        document.getElementById('opcion-titulo').innerText = 'OPCIÓN [' + opc + '] SELECCIONADA';
        document.getElementById('status-msg').innerText = '';

        // Control dinámico de la interfaz según la herramienta
        let gHolo = document.getElementById('group-holo');
        let gAntena = document.getElementById('group-antena');
        let inputNombre = document.getElementById('nuevo-nombre');
        let inputDestino = document.getElementById('ruta-destino');

        // Reiniciar visibilidad
        gHolo.classList.remove('hidden');
        gAntena.classList.add('hidden');
        inputNombre.classList.add('hidden');
        inputDestino.classList.remove('hidden');

        if (tieneAntena) {{
            gAntena.classList.remove('hidden');
        }}

        if (esRenombrador) {{
            gHolo.classList.add('hidden');
            inputNombre.classList.remove('hidden');
        }}

        if (opc === 14) {{ // Apartado CRC32
            gHolo.classList.add('hidden');
            gAntena.classList.add('hidden');
            inputDestino.classList.add('hidden'); // Solo requiere carpeta de origen
        }}

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
        let nuevoNombre = document.getElementById('nuevo-nombre').value.trim();
        let colorHolo = document.getElementById('color-holo').value;
        let colorAntena = document.getElementById('color-antena').value;
        let statusDiv = document.getElementById('status-msg');

        if(!origen) {{
            alert('⚠️ Debes ingresar al menos la ruta de origen.');
            return;
        }}

        statusDiv.style.color = '#e3b341';
        statusDiv.innerText = '⏳ Procesando...';

        fetch('/procesar', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{
                opcion: opcionSeleccionada,
                origen: origen,
                destino: destino,
                nuevo_nombre: nuevoNombre,
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
      
