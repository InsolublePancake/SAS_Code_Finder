import re, os, sys
from getAllCode import *

def delPara(st):
    """Finds and deletes parenthetical pairs and text. Where parentheses are nested it the inner most pair is deleted first then it works its way outwards"""
    para1 = re.compile(r'\([^()]*?\)') # single parenthesis pair
    while re.search(para1, st):
        st = st[:re.search(para1, st).start(0)] + st[re.search(para1, st).end(0):]
    return st

def delComment(st):
    """Finds and removes comments and associated syntax in the form of: /* COMMENTS */ """
    comment = re.compile(r'\/\*[^/]*?\*\/') #single comment 
    return re.sub(comment, '', st)
    
def getDataSteps(sas):
    """"""""
    macro = re.compile(r'%if.*%do;(.*?)%end;', re.IGNORECASE|re.DOTALL)
      
    dpat7 = re.compile(r'(?<=data )([^;]+?);\s*(?:retain [^;]+;\s*)*(?:length [^;]+;\s*)*\s*(?:set|merge)\s*([^;]*?);', re.IGNORECASE|re.DOTALL)
    ddict = {}
    sourceDict = {}

    for step in sas.split('FILE ------->  ')[1:]:
        pat = re.compile(r'^.+?[.]SAS', re.IGNORECASE|re.DOTALL)
        f = re.search(pat, step)
        fname = f.group().strip()
        matches = re.findall(dpat7, step)
        
        for i in matches:
            for outdata in delComment(delPara(i[0])).split():
                out = outdata.lower().strip()
                out = re.sub(macro, '\1 ', out)
                sourceDict.setdefault(out, [])
                if fname not in sourceDict[out]:
                    sourceDict[out].append(fname)
                else: pass
                if out.upper() == '_NULL_': 
                    break
                else: pass
                
                for indata in delComment(delPara(i[1])).lower().split():
                    indata = re.sub(macro, '\1 ', indata)
                    if indata == outdata: 
                        break
                    else:
                        ddict.setdefault(out, [])
                        if indata not in ddict[out]:
                            ddict[out].append(indata.lower().strip())
                        o2 = '--> ' + indata.lower().strip() # testing

    return ddict, sourceDict


def getProcSortSteps(sas, datadict, sourceDict):
    splitfilepat = re.compile(r'^.+?[.]SAS', re.IGNORECASE|re.DOTALL) # Matches name of .sas file
    #macros1 = re.compile(r'%[^;]+;')
    macro = re.compile(r'%if.*%do;(.*?)%end;', re.IGNORECASE|re.DOTALL)
    #comments = re.compile(r'\/\*[^/]*\*\/')
    #sas = re.sub(macros1, '', sas)
    #sas = re.sub(comments, '', sas)
    dStepPat= re.compile(r'(?:proc\s*sort\s*data\s*=\s*)([^;]*?)(out\s*=\s*)([^;]*);', re.IGNORECASE|re.DOTALL)

    for sas in sas.split('FILE ------->  ')[1:]:
        f = re.search(splitfilepat, sas)
        fname = f.group().strip() #get .sas filename
        #print(fname)

        #Get entirety of each Proc Sort step
        matches = re.findall(dStepPat, sas)
        for i in matches:
            # process input dataset
            indata = i[0].split()[0].lower() ##
            indata = re.sub(macro, '\1 ', indata)
            # process output dataset
            outdata = i[2].split()[0].lower().strip() ##
            outdata = delComment(delPara(outdata))
            outdata = re.sub(macro, '\1 ', outdata)
            
            sourceDict.setdefault(outdata, [])
            if fname not in sourceDict[outdata]:
                sourceDict[outdata].append(fname)
            else:
                pass
            if indata == outdata:
                break
            else:
                datadict.setdefault(outdata, [])
                if indata not in datadict[outdata]:
                    datadict[outdata].append(indata)
                else: pass
    
    return datadict, sourceDict



def getSQLsteps(sas, datadict, sourceDict):
    splitfilepat = re.compile(r'^.+?[.]SAS', re.IGNORECASE|re.DOTALL) # Matches name of .sas file
    psql = re.compile(r'(?<=proc sql).*?(?=quit;)', re.DOTALL | re.IGNORECASE) #Matches proc sql step
    table = re.compile(r'(?<=create table)\s*(.*?)\s*(?=as)(.*)', re.DOTALL | re.IGNORECASE) #Matches output table name
    froms = re.compile(r'(?<=from|join)(\s*[^\s()]*)(?:.*?)(?<=from|join)(\s*[^\s()]*)(?:.*?)(?<=from|join)(\s*[^\s()]*)', re.DOTALL | re.IGNORECASE) #Matches input tables
    macro = re.compile(r'%if.*%do;(.*?)%end;', re.IGNORECASE|re.DOTALL)

    for sas in sas.split('FILE ------->  ')[1:]:
        f = re.search(splitfilepat, sas.upper())
        fname = f.group().strip() #get .sas filename
        #print(fname)

        # get each proc sql data step
        matches = re.findall(psql, sas)
        for i in matches:
            i = i.lstrip('; ')

            # Get all datasets in TABLE statement
            for x in re.findall(table, i): # Matches out table name, and returns table name x[0] and the remainder of the data step x[1]
                outdata = delComment(delPara(x[0].strip('\n\t ;').lower()))
                outdata = re.sub(macro, '\1 ', outdata)
                sourceDict.setdefault(outdata,[])
                #Add the filename to the sourceDict if it's not already in it.
                if fname not in sourceDict[outdata]:
                    sourceDict[outdata].append(fname)
                else:
                    pass

                # Search remainder of datastep for FROM statements
                inputs = re.findall(froms, x[1])
                for input in inputs:
                    for ips in input:
                        indata = delComment(delPara(ips.strip('\n\t ;').lower()))
                        indata = re.sub(macro, '\1 ', indata) 
                        if indata == outdata: #Prevent infinite loop
                            break # break and pass do the same thing here
                        elif indata == '': 
                            pass
                        else:
                            datadict.setdefault(outdata, [])
                            if indata not in datadict[outdata]:
                                datadict[outdata].append(indata)
                            else: pass
         
    return datadict, sourceDict


def getProcSumm(sas, datadict, sourceDict):
    splitfilepat = re.compile(r'^.+?[.]SAS', re.IGNORECASE|re.DOTALL) # Matches name of .sas file
    psum = re.compile(r'(?<=proc summary data)[\s=]*(.*?)run;', re.DOTALL | re.IGNORECASE) #Matches entire proc summary step
    options = re.compile(r'nway|missing|chartype|completetypes|printidvars|;', re.IGNORECASE) #Matches proc summary options  (for deletion)
    output = re.compile(r'(?<=output out)[\s=]*([^;]*?);', re.IGNORECASE) # matches output dataset
    meansum = re.compile(r'( sum|mean)[\s=]*[\w\d]*', re.IGNORECASE) # matches output options (for deletion)
    #meansum = re.compile(r'(\ssum|\smean)[\s=]*[\w\d]*', re.IGNORECASE)
    macro = re.compile(r'%if.*%do;(.*?)%end;', re.IGNORECASE|re.DOTALL)
    
    for step in sas.split('FILE ------->  ')[1:]:
        f = re.search(splitfilepat, step)
        fname = f.group().strip() #get .sas filename
        #print(fname)
        
        #Get entirety of each Proc Sort step
        matches = re.findall(psum, step)
        for m in matches:
            indat = re.search(r'(.*?);', m).group().strip()
            indat = re.sub(options, '', indat)
            indat = delComment(delPara(indat))
            indat = re.sub(macro, '\1 ', indat)
            out = re.search(output, m).group(1)
            out = delComment(delPara(out))
            out = re.sub(meansum, '', out)
            out = re.sub(macro, '\1 ', out)
                    
            indata = indat.lower() #testing
            outdata = out.lower() # Does this need a Try/Except?
            
            sourceDict.setdefault(outdata, [])
            if fname not in sourceDict[outdata]:
                sourceDict[outdata].append(fname)
            else: pass
            if indata == outdata:
                break
            else:
                datadict.setdefault(outdata, [])
                if indata not in datadict[outdata]:
                    datadict[outdata].append(indata)
                else: pass
    
    return datadict, sourceDict



def findParent(datadict, dset, bigList, checked=('_null_'), oldchain = ''):  #, count=0):
    """Searches the dataset dictionary to find all the antecedent datasets of the starting dataset"""
    
    dset = dset.lower()
    tList = list(checked)
    tList.append(dset)
    checked = set(tList)
    chain = oldchain + ' <-- ' + dset
    
    if datadict.get(dset):
        for v in datadict[dset]:
            if v in checked:
                p = chain.lstrip('<- ')
                bigList.append(p)
                #print(p)
            else:
                findParent(datadict, v, bigList, checked, chain) #, count)
                    
    #If no (more) parents: print chain as it is.
    else:
        # If no parent datasets found, output string
        p = chain.lstrip('<- ')
        bigList.append(p)
        #print(p)
    return


def compileDict(infile, delComments=False):
    comments = re.compile(r'\/\*.*?\*\/', re.DOTALL)
    if delComments:
        SASFile = re.sub(comments, '', open(infile).read())
    else:
        SASFile = open(infile).read()
        
    ddict, sdict = getDataSteps(SASFile)
    ddict, sdict = getProcSortSteps(SASFile, ddict, sdict)
    ddict, sdict = getSQLsteps(SASFile, ddict, sdict)
    ddict, sdict = getProcSumm(SASFile, ddict, sdict)

    return ddict, sdict


def dataAntecedents(ddict, output):
    bigList = []
    for d in sorted(ddict.keys()):
        findParent(ddict, d, bigList)
    with open(output, 'w') as outfile:
        for item in sorted(bigList):
            outfile.write(item)
            outfile.write('\n')
    os.popen(output)
    return 



def dataOrigin(sdict, output):
    with open(output, 'w') as outfile:
        for item in sorted(sdict.keys()):
            line = item + " " + (30-len(item))*"-" + ">" + ", ".join(sdict[item]) + '\n'
            outfile.write(line)
    os.popen(output)
    return



def ask():
    while True: #Get all code file
        getCode = input("""\n\nType Y to create a compilation of .SAS files.\nType N if you already have a compilation file and do not need to update it.\n""").lower()
                        
        if getCode == 'y': #Create allCode file
            while True:
                #source = None
                try:
                    directory = os.path.realpath(input("""\n\nEnter the path of the top-level of your code directory.\nAll code in the directory and its sub-directories\nwill be combined into a single text document:\n>> """))
                    if os.path.isdir(directory):
                        #source = textCombiner(rootDir=directory, filetype=".sas", outname="AllCode.txt")
                        source = True
                        break    
                    else:
                        print("Path doesn't exist")
                        continue
                                            
                except SyntaxError:
                    print("Error! If you have entered a path with a trailing backslash, remove it and try again")
            break

        elif getCode == 'n':
            break
        else:
            print("That isn't an option.")


    #If text file already exists, get path.       
    while source == None:
        try:
            input_source = os.path.realpath(input('\n\nEnter the path for the combined code file \n(this will be a .txt file):\n>> '))
            if input_source.lower().endswith('.txt') and os.path.exists(input_source):
                source = input_source
            elif not input_source.lower().endswith('.txt'):
                print("Please enter the path for a valid txt file.")
                pass
            else:
                print("Path doesn't exist")
                pass
        except:
            print("Invalid input")
            pass

    
    #Get output directory
    while True: 
        try:
            output = os.path.realpath(input('\n\nEnter the path for the output folder\nIf this is the same folder just press the up arrow key:\n>> '))
            if os.path.isdir(output):
                allCodeFile = os.path.join(directory, "AllCode.txt") 
                textCombiner(rootDir=directory, filetype=".sas", outname=allCodeFile)
                break
            else:
                print("Path doesn't exist")
                pass
        except SyntaxError:
            print("Error! If you have entered a path with a trailing backslash, remove it and try again")
            pass
    
    choice = None
    while choice not in ['1','2','3']:
        choice = input('\n\nEnter 1 for a list of antecedent datasets.\nEnter 2 for a list of where each dataset is created.\nEnter 3 for both:\n>> ') 
    
    ddict, sdict = compileDict(allCodeFile, delComments=True)
    if choice == '1':
        dataAntecedents(ddict, os.path.join(output, 'dataFamily.txt'))
    elif choice == '2':
        dataOrigin(sdict, os.path.join(output, 'dataSources.txt'))
    elif choice == '3':
        dataAntecedents(ddict, os.path.join(output, 'dataFamily.txt'))
        dataOrigin(sdict, os.path.join(output, 'dataSources.txt'))
    else:
        print('This choice should not be possible')
    print(choice, ' Done')
    #print(os.path.join(output, 'dataSources'))
    return ddict, sdict


if __name__ == "__main__":
    ddict, sdict = ask()


