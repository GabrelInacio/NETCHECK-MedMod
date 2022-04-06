import socket
import mysql.connector
from _thread import *




def check(mod_hash, mod_op, mod_id):
    mydb = mysql.connector.connect(
        host="localhost",
        database="netbaseofdata",
        user="root",
        password=""
    )
    mycursor = mydb.cursor()
    sql = """SELECT hash_modulo FROM modulo WHERE id = %s""" % (mod_id)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    hash_real = "None"
    hash_real = str(myresult[0][0])
    if hash_real == "None":
        sql2 = """UPDATE modulo SET hash_modulo = '%s', operadora = '%s' WHERE id = %s""" % (mod_hash, mod_op, mod_id)
        mycursor.execute(sql2)
        mydb.commit()
        mycursor.close()
        mydb.close()
        return True
    else:
        mycursor.close()
        mydb.close()
        if hash_real == mod_hash:
            return True
        else:
            return False


def threaded_client(connection):
    while True:
        insercoes = []
        valores = connection.recv(1024)
        valores = valores.decode('utf-8')
        pos_i = 0
        pos_f = 0
        for caracter in range(0, len(valores)):
            if valores[caracter] == ",":
                insercoes.append(valores[pos_i:(pos_f+1)])
                pos_i = caracter + 1
            else:
                pos_f = caracter
        vel_up = insercoes[0]
        vel_down = insercoes[1]
        data_medicao = insercoes[2]
        operadora = insercoes[3]
        mod_id = insercoes[4]
        mod_hash = insercoes[5]
        mydb = mysql.connector.connect(
            host="localhost",
            database="netbaseofdata",
            user="root",
            password=""
        )
        if check(mod_hash, operadora, mod_id):
            mycursor = mydb.cursor()
            sql = """INSERT INTO medicao(vel_up, vel_down, operadora, data_medicao, id_modulo, ativo) VALUES (%s, %s, '%s', '%s', %s, %s)""" % (vel_up, vel_down, operadora, data_medicao, mod_id, 1)
            mycursor.execute(sql)
            mydb.commit()

            sql3 = """UPDATE modulo SET operadora = '%s' WHERE id = %s""" % (operadora, mod_id)
            mycursor.execute(sql3)

            sql2 = """SELECT intervalo FROM modulo WHERE id = %s""" % (mod_id)
            mycursor.execute(sql2)

            myresult = mycursor.fetchall()
            atualizacoes = []
            mycursor.close()
            mydb.close()
            for item in myresult:
                atualizacoes.append(item[0])
            info = str(atualizacoes[0])
            connection.sendall(info.encode('utf-8'))
            return False
    connection.shutdown(SHUT_RDWR)
    connection.close()

ServerSocket = socket.socket()
host = ''
port = 1235
ThreadCount = 0
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Estabelecendo Conexão..')
ServerSocket.listen(5)

while True:
    Client, address = ServerSocket.accept()
    print('Conectado em: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, ))
    ThreadCount += 1
    print('Número da Thread: ' + str(ThreadCount))
ServerSocket.close()