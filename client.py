import socket
import speedtest
from datetime import datetime
import sched, time
from getmac import get_mac_address
import netifaces
from requests import get
import hashlib
import os

def screen_clear():
    if os.name == "posix":
        _ = os.system("clear")
    else:
        _ = os.system("cls")
    print("Realizando Medições...")
intervalo = (1)

def encrypt_string(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

def get_machine_default_gateway_ip():
    gws = netifaces.gateways()
    gateway = gws['default'][netifaces.AF_INET][0]

    return gateway


def medicao():
    id_mod = 2
    data_medicao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    screen_clear()
    try:
        s = speedtest.Speedtest()
        vel_up = round(s.upload() * (10 ** -6), 2)
        vel_down = round(s.download() * (10 ** -6), 2)

    except:
        vel_up = 0
        vel_down = 0

    ip_host = get_machine_default_gateway_ip()
    mac = get_mac_address(ip=ip_host)
    ip_externo = get('https://api.ipify.org').text
    endereco = 'http://ip-api.com/json/'+str(ip_externo)
    resultado_request = get(endereco)
    json_longo = resultado_request.json()
    operadora = json_longo["isp"]
    print(mac)
    print(ip_host)
    dados = str(vel_up) + "," + str(vel_down) + "," + str(data_medicao) + "," + operadora + "," + str(id_mod) + "," + str(encrypt_string(
        mac))+","
    return dados


def comunicacao():
    valores = medicao()
    ClientSocket = socket.socket()
    host = '127.0.0.1'
    port = 1235
    print('Estabelecendo conexão')
    try:
        ClientSocket.connect((host, port))
    except socket.error as e:
        print(str(e))

    while True:
        envio = str(valores)
        ClientSocket.send(envio.encode('utf-8'))
        resposta = ClientSocket.recv(1024)
        resposta = resposta.decode('utf-8')
        global intervalo
        intervalo = float(1)*60
        print("Medição realizada com sucesso!")
        return False
    ClientSocket.shutdown(SHUT_RDWR)
    ClientSocket.close()


s = sched.scheduler(time.time, time.sleep)
def repita(sc):
    try:
        comunicacao()
        global intervalo
        s.enter(intervalo, 1, repita, (sc,))
    except:
        print("falha na medição!")
        comunicacao()
        s.enter(intervalo, 1, repita, (sc,))
s.enter(intervalo, 1, repita, (s,))
s.run()


