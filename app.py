from flask import Flask, render_template, request, jsonify
import urllib.request
import urllib.error
import json
import os


app = Flask(__name__)

# CAP_VERIFY_URL = "http://localhost:3000/07ae968e5c/siteverify"
CAP_VERIFY_URL = os.environ.get(
    "CAP_VERIFY_URL",
    "http://cap:3000/27c0c47bef/siteverify"
)

#CAP_SECRET = "sk-rV6S0VS0OblSlzyHETFeGn52MhoJDjDCwzqMtxMKok"
CAP_SECRET = os.environ.get("CAP_SECRET")

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/formulario", methods=["POST"])
def formulario():

    print("\n==========================================")
    print("NUEVA PETICION /api/formulario")
    print("==========================================")

    datos = request.get_json(silent=True) or {}

    nombre = datos.get("nombre")
    email = datos.get("email")
    token = datos.get("capToken")

    print("[1] Datos recibidos desde navegador")
    print("    nombre :", nombre)
    print("    email  :", email)

    if token:
        print("    token  :", token[:50] + "...")
        print("    longitud token:", len(token))
    else:
        print("    token  : NO RECIBIDO")


    if not token:

        print("[ERROR] No se ha recibido token CAP")

        return jsonify({
            "success": False,
            "error": "No se ha recibido token CAP"
        }), 400


    payload_json = {
        "secret": CAP_SECRET,
        "response": token
    }

    payload = json.dumps(payload_json).encode("utf-8")


    print("\n[2] Peticion que vamos a enviar a CAP")
    print("    URL:", CAP_VERIFY_URL)

    # No mostramos el secret completo
    if CAP_SECRET:
        print("    Secret:", CAP_SECRET[:6] + "********")
    else:
        print("    Secret: NO CONFIGURADO")

    print("    response/token:", token[:50] + "...")


    peticion = urllib.request.Request(
        CAP_VERIFY_URL,
        data=payload,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )


    print("\n[3] Enviando peticion a CAP...")


    try:

        with urllib.request.urlopen(peticion) as respuesta:

            status = respuesta.status
            body = respuesta.read().decode("utf-8")

            print("\n[4] RESPUESTA CAP")
            print("    HTTP status:", status)
            print("    Body:", body)

            resultado_cap = json.loads(body)


    except urllib.error.HTTPError as error:

        body_error = error.read().decode(
            "utf-8",
            errors="replace"
        )

        print("\n[4] CAP HA DEVUELTO UN ERROR HTTP")
        print("    HTTP status:", error.code)
        print("    Reason:", error.reason)
        print("    Body:", body_error)

        return jsonify({
            "success": False,
            "error": "CAP ha rechazado la verificacion",
            "cap_http_status": error.code,
            "cap_response": body_error
        }), error.code


    except urllib.error.URLError as error:

        print("\n[4] ERROR DE COMUNICACION CON CAP")
        print("    Error:", error)

        return jsonify({
            "success": False,
            "error": "No se puede conectar con CAP",
            "detalle": str(error)
        }), 500


    except Exception as error:

        print("\n[4] ERROR INESPERADO")
        print("    Tipo:", type(error).__name__)
        print("    Error:", str(error))

        return jsonify({
            "success": False,
            "error": "Error inesperado",
            "detalle": str(error)
        }), 500


    print("\n[5] Resultado interpretado")
    print("    success:", resultado_cap.get("success"))


    if not resultado_cap.get("success"):

        print("[ERROR] CAPTCHA NO VALIDO")

        return jsonify({
            "success": False,
            "error": "CAPTCHA no valido",
            "cap": resultado_cap
        }), 403


    print("\n[OK] CAPTCHA VALIDADO CORRECTAMENTE")
    print("==========================================\n")


    return jsonify({
        "success": True,
        "mensaje": "CAPTCHA validado correctamente",
        "nombre": nombre,
        "email": email
    })

if __name__ == "__main__":

    if not CAP_SECRET:
        raise RuntimeError(
            "No está definida la variable CAP_SECRET"
        )

    app.run(
    host="0.0.0.0",
    port=8080,
    debug=False
    )
