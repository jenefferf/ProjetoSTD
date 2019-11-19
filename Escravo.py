import zmq
import threading
import QuebraSenhas

class Escravo:

    #Construtor da classe
    def __init__(self, port):
        self.arquivo = None
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.servers_ip = "localhost"
        self.socket.connect("tcp://%s:%d" % (self.servers_ip, self.port))
        self.socket.send_string("disponivel")
        self.statusEscravo = True


    #Método que recebe como parâmetro a string com os dados do arquivo de senhas e recriar este arquivo
    def escreveDadosRecebidos(self, arquivoSenhas):
        self.arquivo = open("senhas1.txt", "w+")
        self.arquivo.write(arquivoSenhas)
        self.arquivo.close()

    #Método que recebe como parâmetro o método de quebra de senha e executa o software John
    def quebraSenhas(self, comando):
        quebra_senha = QuebraSenhas.QuebraSenha()
        quebra_senha.comandoDeQuebra = comando
        # print(dir(quebra_senha))
        quebra_senha.metodoQuebraSenha()
        while quebra_senha.getOut() == None: pass
        out = quebra_senha.getOut()
        self.socket.send_string("Execucao finalizada. Senhas quebradas: " + out[0].decode())
        self.statusEscravo = True

    #Método para processar as mensagens do mestre e fazer as chamadas de outros métodos para tratar
    def processaMensagensMestre(self, mensagem):
        print("comando recebido" +  mensagem)
        if mensagem[:3] == "arq":
            self.escreveDadosRecebidos(mensagem[3:])
        elif mensagem == "status":
            if self.statusEscravo:
                self.socket.send_string("True")
            else:
                self.socket.send_string("Trabalhando")
        elif mensagem[:17] == "Comando de quebra":
            if self.statusEscravo:
                self.statusEscravo = False
                self.socket.send_string("Trabalhando")
                self.quebraSenhas(mensagem[17:])
            else:
                self.socket.send_string("Trabalhando")
        elif mensagem == "Finalize o processo":
           self.quebra_senha = QuebraSenhas.QuebraSenha()
           self.quebra_senha.finalizaExecucaoProcesso()
           self.socket.send_string("Processo finalizado")
           self.statusEscravo = True

    #Método para troca de mensagens entre o Mestre e o Escravo
    def escutaPorta(self):
        threading.current_thread().name
        while(True):
            mensagem = self.socket.recv_multipart()
            self.processaMensagensMestre(mensagem[0].decode())
            #print(mensagem)

    #Thread de execução do método escutaPorta
    def escutaPortaThread(self):
        thread = threading.Thread(target=self.escutaPorta, name='porta')
        thread.start()

#função main
if __name__ == '__main__':
    print("Rodando escravo")
    escravo = Escravo(45000)
    escravo.escutaPortaThread()
