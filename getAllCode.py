#!/usr/bin/env python

import os, re
 
def getFileName(allLogsName='AllCode'):
    # Function finds the lowest numbered filename in the form AllLogs(n)
    # that doesn't already exist and assigns it as the new filename
    filepath = os.path.join('.', allLogsName)
    for n in range(1,100):
        newFile = filepath + '{0}.txt'.format(n)
        if os.path.exists(newFile):
            pass
        else:
            return newFile


            
def textCombiner(rootDir='.', filetype=".sas", outname="AllCode.txt"):

    '''Walks through directory tree starting at [rootDir] opening any text 
    files with extension [filetype] default ".sas", and writes the combined 
    files to a text doc [outname] in the rootDir, default "AllCode.txt"
    As the text files are read they are scanned for any %INCLUDE statements 
    that refer to code files found outside of the directory tree , these are
    then appended to the compiled code file (dynamically generated filepaths,
    e.g. those containing macro variables will not be found, but will be 
    listed at the end, along with any files that could not be found.)'''
    

    outpath = os.path.join(rootDir, outname)
    extras = [] #initiate list to contain files paths taken from %include statements

    #creates and opens output file.
    with open(outpath, "w") as outfile:

        #walks down directory tree from rootDir
        for dirName, subdirList, fileList in os.walk(rootDir):

            #for each file found
            for fname in fileList:

                #create file path from directory and filename
                filepath = "\\".join([dirName, fname])
                #filepath = os.path.join(dirName, fname)

                #check file is of type specified by parameter [filetype]
                if fname.endswith(filetype):

                    #compile regex to find %include statements
                    inc = re.compile(r'%include\s+[\'\"]([^;]+)[\'\"];', re.IGNORECASE)

                    #open code file
                    with open(filepath, "r") as f:
                                               
                        #write code file details to output
                        outfile.write('\nSTART FILE\n\n')
                        theDir = "DIRECTORY -->  {}\n".format(dirName.upper())
                        theFile = "FILE ------->  {}".format(fname.upper())
                        outfile.write(theDir)
                        outfile.write(theFile)
                        outfile.write('\n\n')
                        #print(f.read())

                        for line in f.readlines():
                            outfile.write(line)

                            #scan file for %include statements and append any to the extras
                            matches = re.findall(inc, line)
                            if matches:
                                for match in matches:
                                    if match not in extras:
                                        extras.append(match)
                                    else: pass
                            else: pass
                        
                        outfile.write('\n\nEND OF SAS FILE\n')
                        outfile.write('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n')
                        #outfile.write('\n\n\nSTART FILE\n\n')
                else:
                    pass

        macropath = [] #list of filepaths from %include statements that contain macro variables
        notfound = [] #list of filepaths from %include statements that could not be found

        #if any %include statements found
        if extras:
            outfile.write("\n\nTHE FOLLOWING CODE FILES WERE FOUND IN %INCLUDE STATEMENTS AND REFER \nTO FILES OUTSIDE OF THE DIRECTORY TREE DEFINED BY THE ROOT DIRECTORY\n\n")         
            for e in extras:

                #if filepath already included within the directory tree ignore it here
                if e.startswith(rootDir):
                    print("Already included: {}".format(e))
                    pass

                #if filepath includes macro statement add it to the macropath list
                elif '&' in e:
                    print("MACRO in: {}".format(e))
                    macropath.append(e)                    

                #attempt to open file and append details to the output file
                else:
                    print("LEGIT path: {}".format(e))
                    try:
                        with open(e, "r") as ef:
                            outfile.write('\n\n\nSTART FILE\n\n')
                            theDir = "DIRECTORY --> {}\n".format("\\".join(e.split('\\')[:-1]).upper())
                            theFile = "FILE -------> {}\n".format(e.split('\\')[-1].upper())
                            outfile.write(theDir)
                            outfile.write(theFile)
                            outfile.write('\n\n')
                            for line in ef.readlines():
                                outfile.write(line)
                            outfile.write('\n\nEND OF SAS FILE\n')
                            outfile.write('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n')
                            #outfile.write('\n\n\nSTART FILE\n\n')
                    except FileNotFoundError:
                        print("File not found: {}".format(e))
                        notfound.append(e)
                    except error:
                        print("Unknown error with file: {}".format(e))
        if macropath:
            outfile.write("The following file paths include dynamically generated file paths with macro variables\nand it was not possible to add them to the compiled code file:\n\n")
            for m in macropath:
                outfile.write('\n\t')
                outfile.write(m)
        else: pass

        if notfound:
            outfile.write("\n\nThe following files were not found. Check that the file has not been moved \nand that the network drive is currently available:\n")
            for nf in notfound:
                outfile.write('\n\t')
                outfile.write(nf)
        else: pass
        
        
    print('Done')
    os.popen(outpath)
    return outpath
	
					
#if __name__ == "__main__":

