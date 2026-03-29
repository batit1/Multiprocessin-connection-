import base64
import multiprocessing
import multiprocessing.connection
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

DIRECCION_MASTER = ('localhost', 6000) 
CLAVE_RED = b'secreto'
NOMBRE_DICCIONARIO = "diccionario-original(1).txt"
ITERACIONES = 500_000

def descifrar_aes_pbkdf2(mensaje_cifrado, password):
    try:
        datos = base64.b64decode(mensaje_cifrado)
        salt, iv, cifrado = datos[:16], datos[16:32], datos[32:]
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERACIONES, backend=default_backend())
        key = kdf.derive(password.encode())
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        raw = decryptor.update(cifrado) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(raw) + unpadder.finalize()
    except: return None

def worker_ataque(args):
    mensaje, claves_chunk = args
    for c in claves_chunk:
        res = descifrar_aes_pbkdf2(mensaje, c)
        if res: return f"Clave: {c} | Texto: {res.decode()}"
    return None

def main_espia():
    with open(NOMBRE_DICCIONARIO, "r", encoding="utf-8", errors="ignore") as f:
        claves = [l.strip() for l in f if l.strip()]

    print(" Espía conectando...")
    try:
        conn = multiprocessing.connection.Client(DIRECCION_MASTER, authkey=CLAVE_RED)
        misiones = conn.recv()
        print(f" Recibidas {len(misiones)} misiones.")

        resultados = []
        num_cores = multiprocessing.cpu_count()
        with multiprocessing.Pool(num_cores) as pool:
            for m in misiones:
                chunk_size = (len(claves) // num_cores) + 1
                chunks = [(m, claves[j:j+chunk_size]) for j in range(0, len(claves), chunk_size)]
                for r in pool.imap_unordered(worker_ataque, chunks):
                    if r:
                        resultados.append(r)
                        break
        
        conn.send(resultados)
        print(" ¡Trabajo enviado!")
        conn.close()
    except Exception as e:
        print(f" Error: {e}")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main_espia()