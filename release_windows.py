from os import chdir,system,isfile,remove
chdir('montos')
system("run_montos")
chdir('../')
if isfile('.montos.rebootf'):
    remove('.montos.rebootf')
    system("montos")
elif isfile(".montos.shutdownf"):
    remove(".montos.shutdownf")
    system("shutdown /s /f /t 0")