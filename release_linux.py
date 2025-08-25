from os import chdir,system,isfile,remove
chdir('montos')
system("sudo ./run_montos")
chdir('../')
if isfile('.montos.rebootf'):
    remove('.montos.rebootf')
    system("sudo ./montos")
elif isfile(".montos.shutdownf"):
    remove(".montos.shutdownf")
    system("sudo shutdown now")