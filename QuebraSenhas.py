import subprocess
import threading

class QuebraSenha:
    def __init__(self):
     self.shellProcess = None
     self.output = None
     self.comandoDeQuebra = None


    #Executa o John
    def metodoQuebraSenha(self):
         comando = self.comandoDeQuebra
         self.shellProcess = subprocess.Popen("sleep 200", stdout=subprocess.PIPE, shell=True)
         # self.shellProcess = subprocess.Popen("john " + comando + " senhas1.txt", stdout=subprocess.PIPE, shell=True)
         self.shellProcess.wait()
         outputProcess = subprocess.Popen("john --show senhas1.txt", stdout=subprocess.PIPE, shell=True)
         out, err = outputProcess.communicate()
         self.output = out, err
         self.finalizaExecucaoProcesso()

    # Método que finaliza a execução do processo de quebra
    def finalizaExecucaoProcesso(self):
     self.shellProcess.kill()

    def getOut(self):
        return self.output

    #Thread de execução do John
    def threadQuebraSenhas(self):
     thread = threading.Thread(target=self.metodoQuebraSenha())
     thread.start()