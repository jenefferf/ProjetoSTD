from threading import Thread
import zmq
import pickle

class Mestre:

    def __init__(self, nomeArquivo, port):
        self.nomeArquivo = nomeArquivo
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind("tcp://*:%d" % port)
        self.run = True
        self.listaDeEscravos = {} # [socket.addres] = (boolean, string)
        self.contador = 0
        self.runEscravos = {}
        self.abreArquivoDeSenha()

    def abreArquivoDeSenha(self):
        with open(self.nomeArquivo, 'r') as arquivo:
            dadosArquivo = arquivo.readlines()
            self.arquivo = ' '.join(dadosArquivo)

    def processaMensagemEscravo(self, endereco, mensagem):
        if mensagem == b"disponivel":
            arquivoSenha = "arq" + self.arquivo
            self.socket.send_multipart([endereco, arquivoSenha.encode()])
            solicitaStatus = "status"
            self.socket.send_multipart([endereco, solicitaStatus.encode()])
        elif mensagem == b'True':
            pass
        elif mensagem[:39] == b"Execucao finalizada. Senhas quebradas: ":
            print(mensagem)
            return mensagem

    # get = tabela_hash[chave]
    # tabela_hash[chave] = set

    def criaIDProcesso(self):
        self.contador = self.contador + 1
        return 'escravo-' + str(self.contador)

    def registraID(self, endereco):
        if endereco not in self.listaDeEscravos.keys():
            nome = self.criaIDProcesso()
            self.listaDeEscravos[endereco] = (True, nome)
            self.runEscravos[nome] = (True, endereco)

    def escutaPorta(self):
        while self.run:
            endereco, mensagem = self.socket.recv_multipart()
            self.registraID(endereco)
            self.processaMensagemEscravo(endereco, mensagem)
            # print(endereco)
            print(mensagem)

    def escutaPortaThread(self):
        thread = Thread(target=self.escutaPorta)
        thread.start()


    def distribuiTarefa(self, nomeEscravo, metodoQuebra):
        escravo = self.runEscravos[nomeEscravo]
        metodoQuebraCodificado = metodoQuebra.encode()
        if escravo[0]:
            escravo[0] = False
            self.socket.send_multipart([escravo[1], metodoQuebraCodificado])

# Interface de interação com o usuário
if __name__ == '__main__':

    listaComandos = ["-i=All4", "-i=All5", "-i=All6", "-i=All7"]
    mestre = Mestre("senhas.txt", 55000)
    mestre.escutaPortaThread()
    print("------- Bem vindo ao Breaking Bad Passwd ------")
    # print("Existem ", mestre.processosAtivos)
    # print("Processo ", mestre.idProcesso(), "Status: ", mestre.statusProcessos())
    # print("Informe o id do processo que deseja usar")
    # idProcesso = input()
    # print("Escolha o método tentativa de quebra de senha: ")
    # print("1. Senhas até 4 caracteres")
    # print("2. Senhas até 5 caracteres")
    # print("3. Senhas até 6 caracteres")
    # print("4. Senhas até 7 caracteres")
    # opcaoUsuario = input()

    # if opcaoUsuario == 1:
    #     mestre.distribuiTarefa(idProcesso, listaComandos.__getitem__(0))
    # elif opcaoUsuario == 2:
    #     mestre.distribuiTarefa(idProcesso, listaComandos.__getitem__(1))
    # elif opcaoUsuario == 3:
    #     mestre.distribuiTarefa(idProcesso, listaComandos.__getitem__(2))
    # elif opcaoUsuario == 4:
    #     mestre.distribuiTarefa(idProcesso, listaComandos.__getitem__(3))
    # else:
    #     print("Opção inválida")


