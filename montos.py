from getpass import getpass
from os import system,mkdir,rmdir,remove
from pathlib import Path
from os import listdir,system
from os.path import isfile,join,isdir
from ast import literal_eval as le
from copy import deepcopy
import re
import hashlib
d = {"cdir":"/","usrlist":{},'usr':'','basepath':str(Path("").absolute())}
oldopen = open
def open(file,mode='r',buffering=-1,encoding= None,errors= None,newline= None,closefd= True,ignorePerm=False):
    if ignorePerm:
        pass
    elif mode == 'r':
        if not checkperm(file,"r",False):
            print("Error: User does not have permission to read file.")
            return
    elif mode == 'w' or mode == 'a':
        if not checkperm(file,"w",False):
            print("Error: User does not have permission to write to file.")
            return
    return oldopen(file,mode,buffering,encoding,errors,newline,closefd)
def pathify(rpath,systemp=False):
    p = d['basepath'].split('/')
    if rpath[0] != '/':
        p.extend([i for i in d['cdir'].split('/') if i != ''])
    rpath = rpath.replace('\\','/').split('/')
    if rpath[0] == '':
        rpath.pop(0)
    for i in rpath:
        if i == '..':
            if '/'.join(p) != d['basepath']:
                p.pop()
        elif i == '~':
            p = d['basepath'].split('/')
            p.append(d['usr']+'/home')
        else:
            p.append(i)
    c = '/'.join(p)
    if not systemp:
        c=tomonp(c)
    return c
def tomonp(c):
    return c.replace(d['basepath'],'',1)
def stitch(cmdl,pl=True):
    cmdl = deepcopy(cmdl)
    if pl:
        cmdl.pop(0)
    return ' '.join(cmdl)
def argparse(cmdl,argdict={"bool":[],"kwargs":[]}):
    cmdl = deepcopy(cmdl)
    retd = {"args":[cmdl[0]],'bool':[],'kwargs':{}}
    cmdl.pop(0)
    for i in argdict['bool']:
        if i in cmdl:
            cmdl.remove(i)
            retd['bool'].append(i)
    for i in argdict['kwargs']:
        c = cmdl.find(i) if i in cmdl else None
        if c != None:
            retd['kwargs'] = cmdl[c+1]
            cmdl.pop(c)
            cmdl.pop(c+1)
    for i in cmdl:
        retd['args'].append(i)
    return retd
def clear():
    system('clear')
def changedir(pth,pathfy=False):
    if pathfy:
        pth = pathify(pth,True)
    if Path(pth).exists():
        d['cdir'] = tomonp(pth)
    else:
        print(f"Invalid Path: \"{tomonp(pth)}\"")
def cd(cmdl):
    pth = pathify(stitch(cmdl),True)
    changedir(pth)
def moncomp(cmdl):
    pathname = stitch(cmdl)
    t = open(pathify(pathname,True))
    if t == None:
        return
    t = t.read()
    t = re.sub(r"\/\*[^\*]*\*\/",'',t)
    t = re.sub(r"\\.",'',t,flags=re.DOTALL).split(" ")
    data = []
    for i in t:
        try:
            data.append(chr(int(i)))
        except ValueError:
            data.append(i)
    f = open(pathify(pathname[::-1].replace('fmb.','',1)[::-1]+'.mon',True),'w')
    if f != None:
        f.write(''.join(data))
        setdefperm(pathify(pathname[::-1].replace('fmb.','',1)[::-1]+'.mon',True))
        f.close()
def ls(cmdl):
    def format(item,p):
        onlyfiles = [f for f in listdir(p) if isfile(join(p,f))]
        if item in onlyfiles:
            if item.endswith('.mon'):
                print('\33[32m'+str(item),end=' ')
            elif item.endswith('.tar.gz') or item.endswith('.tgz') or item.endswith('.zip'):
                print('\33[91m'+str(item),end=' ')
            else:
                print('\33[0m'+str(item),end=' ')
        else:
            print('\33[34m'+str(item),end=' ')
    def ls(p,hidden=False):
        for item in listdir(p):
            if item.startswith('.'):
                if hidden:
                    format(item,p)
            else:
                format(item,p)
    args = argparse(cmdl,{"bool":["-a","--all"],'kwargs':[]})
    h =  '-a' in args['bool'] or '--all' in args['bool']
    di = stitch(args['args'])
    if di == '':
        di = d['cdir']
    di = pathify(di,True)
    if not Path(di).exists():
        print("ls: Path Does Not Exist.")
        return
    ls(di,h)
    print('\33[0m')
def exit_cmd(cmdl):
    quit()
def adduser(cmdl):
    if not d['usr'] == 'root':
        print("Error: Users can only be added by root. (Hint: Use sudo adduser).")
        return
    a = argparse(cmdl,{"bool":[],'kwargs':['-p','--permissions','-f','--filepermissions']})
    permissions = 'cs'
    fperm = 'rwx'
    if '-p' in list(a['kwargs'].keys()):
        permissions = a['kwargs']['-p']
    elif '--permissions' in list(a['kwargs'].keys()):
        permissions = a['kwargs']['--permissions']
    if '-f' in list(a['kwargs'].keys()):
        fperm = a['kwargs']['-f']
    elif '--filepermissions' in list(a['kwargs'].keys()):
        fperm = a['kwargs']['--filepermissions']
    if not a[1] in list(d['usrlist'].keys()) and a[1] != 'root':
        d['usrlist'][a[1]] = hashlib.sha512(a[2].encode()).hexdigest()
        open('../.users','w',ignorePerm=True).write(str(d['usrlist']))
        perm = le(open('../.permissions').read(),ignorePerm=True)
        perm['general'][a[1]] = permissions
        perm['fileperm'][a[1]] = fperm
        open('../.permissions','w',ignorePerm=True).write(str(perm))
        mkdir(pathify("/"+a[1],True))
        mkdir(pathify("/"+a[1]+'/home',True))
        mkdir(pathify("/"+a[1]+'/programs',True))
        print("Note: Montos reboot required for changes to take effect.")
    else:
        print("Error: Invalid username or username in use.")
def changepass(cmdl):
    if d['usr'] == 'root':
        print("Error: Can not change password of root.")
        return
    cpwd = hashlib.sha512(getpass("Current Password: ").encode()).hexdigest()
    npwd = hashlib.sha512(getpass("New Password: ").encode()).hexdigest()
    cnpwd = hashlib.sha512(getpass("Confirm New Password: ").encode()).hexdigest()
    if cpwd != d['usrlist'][d['usr']]:
        print("Error: Incorrect Password")
        return
    if npwd != cnpwd:
        print("Error: Passwords do not match.")
        return
    d['usrlist'][d['usr']] = npwd
    open('../.users','w',ignorePerm=True).write(str(d['usrlist']))
    print("Password changed.")
def sudo(cmdl):
    if not checkuperm('s'):
        print(f"Error: User {d['usr']} can not use sudo.")
        return
    ousr = d['usr']
    d['usr'] = 'root'
    execcmd(stitch(cmdl))
    d['usr'] = ousr
def reboot(cmdl):
    open('../.montos.rebootf','w',ignorePerm=True).write("")
    exit()
def shutdown(cmdl):
    open('../.montos.shutdownf','w',ignorePerm=True).write("")
    exit()
builtins = {'cd':cd,'quit':exit_cmd,'moncomp':moncomp,'ls':ls,'sudo':sudo,'adduser':adduser,'changepass':changepass,'reboot':reboot,'shutdown':shutdown}
def runmon(fpath,cmdl,f=[],pvar={}):
    if f == []:
        f = [i for i in open(fpath,ignorePerm=True).read()]
        if f[0] != chr(0):
            print("Error: Not .mon format (Doesn't start with a NUL character)")
            return
        elif f[-1] != chr(1):
            print("File is not an executable.")
            return
        f.pop()
        f.pop(0)
    om = []
    mode = 0
    datr = []
    atcdat = []
    varname = []
    retain = []
    var = {'builtin.path':[d['cdir']],"builtin.thisfile":[fpath],"builtin.user":[d['usr']]}
    for i,t in pvar.items():
        var[i] = t
    funct = {}
    used_methods = [str(i) for i in range(1,12)]
    c = 0
    for i in cmdl:
        var[f'builtin.arg.{str(c)}'] = i
        c += 1
    var['builtin.arg.stitch'] = stitch(cmdl)
    for i in f:
        if i == chr(2) and mode == 0:
            mode = 1
        elif i == chr(3) and mode == 1:
            if datr[0][0] == chr(4):
                clear()
                datr = []
                atcdat = []
                mode = 0
            else:
                mode = 2
                atcdat.append(datr)
                datr = []
        elif i == chr(4) and mode == 2:
            atcdat.append(datr)
            datr = []
            if atcdat[0][0] == chr(0):
                print(''.join([i for i in atcdat[1]]),end='')
            elif atcdat[0][0] == chr(1):
                var[''.join(atcdat[1])] = atcdat[2]
            elif atcdat[0][0] == chr(2):
                var[''.join(atcdat[1])] = input()
            elif atcdat[0][0] == chr(5):
                print(f'\033[{ord(atcdat[1][0])}m',end='')
            elif atcdat[0][0] == chr(8):
                var[''.join(atcdat[1])] = pathify(''.join(atcdat[2]))
            elif atcdat[0][0] == chr(9):
                mkdir(pathify(''.join(atcdat[1]),True))
            elif atcdat[0][0] == chr(10):
                if ''.join(atcdat[1]) == ''.join(atcdat[2]):
                    var[''.join(atcdat[3])] = [chr(1)]
                else:
                    var[''.join(atcdat[3])] = [chr(0)]
            elif atcdat[0][0] == chr(11):
                v = ''.join(atcdat[1])
                if v != chr(0) and v != '':
                    fn = ''.join(atcdat[2])
                    pvars = {}
                    if len(atcdat) > 3:
                        atcdat.pop(0)
                        atcdat.pop(0)
                        atcdat.pop(0)
                        c = 0
                        for v in funct[fn][0]:
                            pvars[v] = atcdat[c]
                            c += 1
                    for i,t in runmon(fpath,cmdl,funct[fn][1],pvars).items():
                        var[i] = t
            elif atcdat[0][0] == chr(12):
                if not checkperm(fpath,'c',False):
                    print("Error: Executable does not have permission to change permissions")
                elif not checkuperm('c'):
                    print("Error: User does not have permission to change file permissions.")
                else:
                    if len(atcdat) == 5:
                        usr = ''.join(atcdat[4])
                    else:
                        usr = d['usr']
                    if ''.join(atcdat[1]) == chr(0):
                        addperm(pathify(''.join(atcdat[3]),True),''.join(atcdat[2]),usr)
                    elif ''.join(atcdat[1]) == chr(1):
                        subtrperm(pathify(''.join(atcdat[3]),True),''.join(atcdat[2]),usr)
                    elif ''.join(atcdat[1]) == chr(2):
                        setperm(pathify(''.join(atcdat[3]),True),''.join(atcdat[2]),usr)
            elif atcdat[0][0] == chr(14):
                f = open(pathify(''.join(atcdat[1]),True))
                if f != None:
                    var[''.join(atcdat[2])] = [f.read()]
                    f.close()
                else:
                    var[''.join(atcdat[2])] = [""]
            elif atcdat[0][0] == chr(15):
                f = open(pathify(''.join(atcdat[1]),True),'w')
                if f != None:
                    f.write(''.join(atcdat[2]))
                    f.close()
            elif atcdat[0][0] == chr(16):
                f = open(pathify(''.join(atcdat[1]),True),'a')
                if f != None:
                    f.write(''.join(atcdat[2]))
                    f.close()
            elif atcdat[0][0] == chr(17):
                cnt = -1
                if len(atcdat) == 6:
                    cnt = int(''.join(atcdat[5]))
                var[''.join(atcdat[4])] = ''.join(atcdat[3]).replace(''.join(atcdat[1]),''.join(atcdat[2]),cnt)
            elif atcdat[0][0] == chr(18):
                pth = pathify(''.join(atcdat[1]),True)
                if not Path(pth).exists():
                    print("Error: File/Directory does not exist.")
                elif isfile(pth):
                    if not checkperm(pth,'w',False):
                        print("Error: User does not have permission to delete file.")
                    else:
                        remove(pth)
                elif isdir(pth):
                    if not checkperm(pth,'d',False):
                        print("Error: User does not have permission to delete directory.")
                    else:
                        try:
                            rmdir(pth)
                        except OSError:
                            if len(atcdat) == 3 and ''.join(atcdat[2]) == chr(1):
                                def rem(c):
                                    for i in listdir(c):
                                        p = join(c,i)
                                        if isdir(p):
                                            rem(p)
                                            rmdir(p)
                                        else:
                                            remove(p)
                                rem(pth)
            elif atcdat[0][0] == chr(19):
                pth = pathify(''.join(atcdat[1]),True)
                var[''.join(atcdat[2])] = [chr(1)] if isdir(pth) else [chr(0)]
            else:
                fn = ''.join(atcdat[0])
                pvars = {}
                if fn in list(funct.keys()):
                    c = 1
                    for i in funct[fn][0]:
                        pvars[i] = atcdat[c]
                        c += 1
                    for i,t in runmon(fpath,cmdl,funct[fn][1],pvars).items():
                        var[i] = t
            atcdat = []
            mode = 0
        elif i == chr(5) and mode == 2:
            atcdat.append(datr)
            datr = []
        elif i == chr(6) and mode != 3:
            om.insert(0,mode)
            mode = 3
        elif mode == 3:
            mode = om[0]
            om.pop(0)
            if mode != 0:
                datr.append(i)
        elif i == chr(7) and mode != 7:
            om.insert(0,mode)
            mode = 4
            varname.insert(0,'')
        elif mode == 4:
            if i == chr(8):
                mode = om[0]
                om.pop(0)
                try:
                    datr.extend(var[varname[0]])
                except KeyError:
                    print(f"Error (fatal): Variable {varname[0]} does not exist.")
                    return
                varname.pop(0)
            else:
                varname[0] += i
        elif i == chr(9) and mode == 0:
            mode = 5
        elif mode == 5 and i == chr(3):
            mode = 6
            atcdat.append(datr)
            atcdat.append([])
            datr = []
        elif i == chr(5) and mode == 6:
            atcdat[-1].append(datr)
            datr = []
        elif i == chr(4) and mode == 6:
            mode = 7
            atcdat[-1].append(datr)
            datr = []
        elif i == chr(10) and mode == 7:
            atcdat.append(datr)
            datr = []
            mode = 0
            fn = ''.join(atcdat[0])
            if fn in used_methods:
                print("Error: Function could not be created: Function name is CONST.")
            else:
                funct[fn] = [[''.join(i) for i in atcdat[1]],atcdat[2]]
                if funct[fn][0] == ['']:
                    funct[fn][0] = []
            atcdat = []
        else:
            if mode != 0:
                datr.append(i)
    rval = {}
    for i in retain:
        rval[i] = vars[i]
    return rval
def boot():
    print("Loading .users file...")
    d['usrlist'] = le(open('../.users',ignorePerm=True).read())
    print("Checking .permissions file...")
    perm = le(open('../.permissions',ignorePerm=True).read())
    for i in list(perm['fs'].keys()):
        if not Path(i).exists():
            del perm['fs'][i]
    mod = [False]
    def check(f):
        for i in listdir(f):
            p = join(f,i)
            if isdir(p):
                check(p)
            if not p in list(perm['fs'].keys()):
                mod[0] = True
                perm['fs'][p] = perm['fileperm']
            for ii in d['usrlist'].keys():
                if not ii in list(perm['fs'][p].keys()):
                    perm['fs'][p][ii] = perm['fileperm'][ii]
    check(d['basepath'])
    if mod[0]:
        open('../.permissions','w',ignorePerm=True).write(str(perm))
    login()
def print_enter(*args,**kwargs):
    print(*args,**kwargs)
    input("Press Enter to Continue... ")
def login():
    clear()
    print("Weclome to Montos Version 0.0.1A!")
    usr = input("Username: ")
    passwd = hashlib.sha512(getpass(prompt='Password: ').encode()).hexdigest()
    if usr in d['usrlist'] and passwd == d['usrlist'][usr]:
        usr = 'default'
        d['usr'] = usr
        clear()
        print(f"Montos 0.0.1A User {usr}.")
        changedir(f'/{usr}/home',True)
        main()
    else:
        print_enter('Incorrect Login.')
        login()
def checkperm(f,mode,pthfy=True):
    perm = le(open('../.permissions',ignorePerm=True).read())
    if pthfy:
        ptfy = pathify(f,True)
    else:
        ptfy = f
    if not ptfy in list(perm['fs'].keys()):
        return mode in perm['fileperm'][d['usr']]
    return mode in perm['fs'][ptfy][d['usr']]
def checkuperm(mode):
    perm = le(open('../.permissions',ignorePerm=True).read())
    return mode in perm['general'][d['usr']]
def setdefperm(file):
    perm = le(open('../.permissions',ignorePerm=True).read())
    if not file in list(perm['fs'].keys()):
        perm['fs'][file] = perm['fileperm']
        open('../.permissions','w',ignorePerm=True).write(str(perm))
def addperm(file,perms,usr):
    perm = le(open('../.permissions',ignorePerm=True).read())
    perm['fs'][file][usr] += perms
    open('../.permissions','w',ignorePerm=True).write(str(perm))
def subtrperm(file,perms,usr):
    perm = le(open('../.permissions',ignorePerm=True).read())
    perm['fs'][file][usr] = perm['fs'][file][d['usr']].replace(perms,'')
    open('../.permissions','w',ignorePerm=True).write(str(perm))
def setperm(file,perms,usr):
    perm = le(open('../.permissions',ignorePerm=True).read())
    perm['fs'][file][usr] = perms
    open('../.permissions','w',ignorePerm=True).write(str(perm))
def execcmd(cmd):
    cmdl = cmd.split(' ')
    if cmdl[0] in list(builtins.keys()):
        builtins[cmdl[0]](cmdl)
    elif Path(pathify(cmdl[0]+'.mon',True)).exists():
        if not checkperm(pathify(cmdl[0]+'.mon'),'x',False):
            print(f"User {d['usr']} does not have permission to execute.")
            return
        runmon(pathify(cmdl[0]+'.mon',True),cmdl)
    elif Path(pathify(f'/{d["usr"]}/programs/'+cmdl[0]+'.mon',True)).exists():
        if not checkperm(pathify(f'/{d["usr"]}/programs/'+cmdl[0]+'.mon',False),'x'):
            print(f"User {d['usr']} does not have permission to execute.")
            return
        runmon(pathify(f'/{d["usr"]}/programs/'+cmdl[0]+'.mon',True),cmdl)
    elif Path(pathify('/universal/programs/'+cmdl[0]+'.mon',True)).exists():
        if not checkperm(pathify('/universal/programs/'+cmdl[0]+'.mon',False),'x'):
            print(f"User {d['usr']} does not have permission to execute.")
            return
        runmon(pathify('/universal/programs/'+cmdl[0]+'.mon',True),cmdl)
    else:
        print('Command not found.')
    print('\033[0m',end='')
def main():
    print(f"Montos {d['cdir']} > ",end='')
    cmd = input()
    execcmd(cmd)
    main()
boot()