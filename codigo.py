import multiprocessing.connection
import glob
import time

DIRECCION = ('localhost', 6000) 
CLAVE_RED = b'secreto'

def comandante():
    archivos = glob.glob("mensajes_cifrados_*.txt")
    if not archivos:
        print(" No hay archivos de mensajes!")
        return
    
    with open(archivos[0], "r") as f:
        misiones = [l.strip() for l in f if l.strip()]

    print(f" COMANDANTE ONLINE en {DIRECCION}")
    print(f" Cargadas {len(misiones)} misiones de {archivos[0]}")
    
    servidor = multiprocessing.connection.Listener(DIRECCION, authkey=CLAVE_RED)
    
    while True:
        try:
            with servidor.accept() as conn:
                print(f" Agente conectado: {servidor.last_accepted}")
                start = time.time()
                
                conn.send(misiones) 
                resultados = conn.recv() 
                
                print(f"\n MISIONES DESCIFRADAS POR EL AGENTE:")
                for res in resultados:
                    print(f"   -> {res}")
                
                print(f"⏱️ Tiempo récord: {time.time() - start:.2f}s\n")
        except Exception as e:
            print(f" Conexión cerrada o error: {e}")

if __name__ == "__main__":
    comandante()