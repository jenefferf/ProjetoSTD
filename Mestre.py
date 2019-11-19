from threading import Thread
import zmq

class Mestre:

    #Construtor da classe
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

    #Método que faz a leitura do arquivo de senhas
    def abreArquivoDeSenha(self):
        with open(self.nomeArquivo, 'r') as arquivo:
            dadosArquivo = arquivo.readlines()
            self.arquivo = ' '.join(dadosArquivo)

    #Método para processar as mensagens do escravos e fazer as devidas trativas de acordo com as mensagens
    def processaMensagemEscravo(self, endereco, mensagem):
        if mensagem == b"disponivel":
            arquivoSenha = "arq" + self.arquivo
            self.socket.send_multipart([endereco, arquivoSenha.encode()])
        elif mensagem == b"Trabalhando":
            nomeEscravo = self.listaDeEscravos[endereco][1]
            self.listaDeEscravos[endereco][0] = False
            self.runEscravos[nomeEscravo][0] = False
            print("Processo em execução")
        elif mensagem[:39] == b"Execucao finalizada. Senhas quebradas: ":
            nomeEscravo = self.listaDeEscravos[endereco][1]
            self.listaDeEscravos[endereco][0] = True
            self.runEscravos[nomeEscravo][0] = True
            print(mensagem.decode())
        elif mensagem == b"Processo finalizado":
            nomeEscravo = self.listaDeEscravos[endereco][1]
            self.listaDeEscravos[endereco][0] = True
            self.runEscravos[nomeEscravo][0] = True
            print("Processo finalizado")

    #Método para finalizar as tarefas realizadas pelos escravos
    def finalizaProcessoEscravo(self, nomeEscravo):
        escravo = self.runEscravos[nomeEscravo]
        print("Comando de finalize")
        mensagem = "Finalize o processo"
        self.socket.send_multipart([escravo[1], mensagem.encode()])
        print("Enviado")

    # Método que retorna a lista de escravos
    def getEscravos(self):
        return self.listaDeEscravos

    #Cria um id legível para o usuário de cada escravo conectado
    def criaIDProcesso(self):
        self.contador = self.contador + 1
        return 'escravo-' + str(self.contador)

    #Método para salvar os escravos conectados ao mestre
    #em duas tabelas: uma para o usuário ter acesso ao nome do escravo e seu status (listaEscravos)
    #e outra com o endereço e o status de cada escravo para que o mestre possa encaminhar os dados
    def registraID(self, endereco):
        if endereco not in self.listaDeEscravos.keys():
            nome = self.criaIDProcesso()
            self.listaDeEscravos[endereco] = [True, nome]
            self.runEscravos[nome] = [True, endereco]

    def escutaPorta(self):
        while self.run:
            endereco, mensagem = self.socket.recv_multipart()
            self.registraID(endereco)
            self.processaMensagemEscravo(endereco, mensagem)
            # print(endereco)
            # print(mensagem)

    #Thread para escutar a porta de comunicação com os escravos
    def escutaPortaThread(self):
        thread = Thread(target=self.escutaPorta)
        thread.start()

    #Método que distribui a tarefa para os escravos e seta os escravos como ocupados (False)
    def distribuiTarefa(self, nomeEscravo, metodoQuebra):
        escravo = self.runEscravos[nomeEscravo]
        mensagem = "Comando de quebra" + metodoQuebra
        if escravo[0]:
            novoEscravo = [False, escravo[1]]
            self.runEscravos[nomeEscravo] = novoEscravo
            self.socket.send_multipart([escravo[1], mensagem.encode()])

    #Método com a interface de interação com o usuário
    def menuUsuario(self):
        while(1):
            print("Pressione enter para começar a interação...")
            input()
            listaEscravos = self.getEscravos()
            if(len(listaEscravos) == 0):
                print("Não há processos conectados, tente novamente...")
                continue
            print("Existem ", len(listaEscravos), " processos conectados ao mestre")
            print("Informação ao usuário: status True representa que o processo está livre para receber novos comandos")
            print("Status False significa que o processo está ocupado trabalhando")
            listaComandos = ["-i=All4", "-i=All5", "-i=All6", "-i=All7"]
            for k, v in listaEscravos.items():
                 print("ID do processo: ", v[1], "Status: ", v[0])
            print("Informe o id do processo que deseja usar")
            idProcesso = input()
            print("Escolha o método tentativa de quebra de senha: ")
            print("1. Senhas até 4 caracteres")
            print("2. Senhas até 5 caracteres")
            print("3. Senhas até 6 caracteres")
            print("4. Senhas até 7 caracteres")
            print("5. Para encerrar um processo")
            print("6. Para encerrar todos os processos")
            opcaoUsuario = eval(input())

            if opcaoUsuario == 1:
                mestre.distribuiTarefa(idProcesso, listaComandos.__getitem__(0))
            elif opcaoUsuario == 2:
                mestre.distribuiTarefa(idProcesso, listaComandos.__getitem__(1))
            elif opcaoUsuario == 3:
                mestre.distribuiTarefa(idProcesso, listaComandos.__getitem__(2))
            elif opcaoUsuario == 4:
                mestre.distribuiTarefa(idProcesso, listaComandos.__getitem__(3))
            elif opcaoUsuario == 5:
                print("Informe o ID do processo")
                idProcesso = input()
                mestre.finalizaProcessoEscravo(idProcesso)
            elif opcaoUsuario == 6:
                for k, v in listaEscravos.items():
                    mestre.finalizaProcessoEscravo(v[1])
            else:
                print("Opção inválida")

    #Thread de execução da interface de interação com o usuário
    def menuUsuarioThread(self):
        thread = Thread(target=self.menuUsuario)
        thread.start()

# Interface de interação com o usuário
if __name__ == '__main__':
    print("------- Bem vindo ao Breaking Bad Passwd ------")
    print("Esperando conexões...")
    mestre = Mestre("senhas.txt", 45000)
    mestre.escutaPortaThread()
    mestre.menuUsuarioThread()
