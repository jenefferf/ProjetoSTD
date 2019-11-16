import zmq
from threading import  Thread
import subprocess
import pickle

class Escravo:

    #Construtor da classe
    def __init__(self, port):
        self.arquivo = None
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.servers_ip = "localhost"
        self.socket.connect("tcp://%s:%d" % (self.servers_ip, self.port))
        self.run  = True
        self.socket.send_string("disponivel")
        self.statusEscravo = True

    #Método que recebe como parâmetro a string com os dados do arquivo de senhas e recriar este arquivo
    def escreveDadosRecebidos(self, arquivoSenhas):
        self.arquivo = open("senhas1.txt", "w+")
        self.arquivo.write(arquivoSenhas)
        self.arquivo.close()

    #Método que recebe como parâmetro o método de quebra de senha e executa o software John
    def quebraSenhas(self, comando):
        execucaoComando = subprocess.check_output(["john", comando, "senhas1.txt"], stderr=subprocess.DEVNULL)
        execucaoComando = subprocess.check_output(["john", "--show", "senhas1.txt"], stderr=subprocess.DEVNULL)
        self.socket.send_string("Execucao finalizada. Senhas quebradas: " + execucaoComando.decode())
        self.statusEscravo = True

    #Método que finaliza a execução do processo de quebra
    def finalizaExecucaoProcesso(self):
        self.run = False

    #Método para processar as mensagens do mestre e fazer as chamadas de outros métodos para tratar
    def processaMensagensMestre(self, mensagem):
        if mensagem[:3] == "arq":
            self.escreveDadosRecebidos(mensagem[3:])
        elif mensagem == "status":
            if self.statusEscravo:
                self.socket.send_string("True")
                if mensagem == "Comando de quebra":
                    self.quebraSenhas(mensagem[17:])
                    self.statusEscravo = False
                    self.socket.send_string("Trabalhando")
            else:
                self.socket.send_string("Ocupado")
        elif mensagem == "Finalize o processo":
           self.finalizaExecucaoProcesso()

    #Método para troca de mensagens entre o Mestre e o Escravo
    def escutaPorta(self):
        while self.run:
            mensagem = self.socket.recv_multipart()
            self.processaMensagensMestre(mensagem[0].decode())
            print(mensagem)

    #Thread de execução do método escutaPorta
    def escutaPortaThread(self):
        thread = Thread(target=self.escutaPorta)
        thread.start()

    #Thread de execução do método quebraSenha
    def quebraSenhasThread(self):
        thread = Thread(targe=self.quebraSenhas())
        thread.start()

#função main
if __name__ == '__main__':
    print("Rodando escravo")
    escravo = Escravo(55000)
    escravo.quebraSenhas("-i=All8")
    escravo.escutaPortaThread()
