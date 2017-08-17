def textCombiner(rootDir='.', filetype=".sas", outname="AllCode.txt"):

    '''Walks through directory tree starting at [rootDir] by default, opening any 
    text file with extension [filetype] default ".sas", and writes the combined 
    files to a text doc [outname] in the rootDir, default "AllCode.txt" 
    
    NOTE: if adding a root filepath as an argument add double backslashes in 
    place of single ones: e.g. C:\\Directory\\Subdirectory\\Code 
    Similarly, to write the output to folder other than the logs location, 
    add the filepath with double backslashes.'''

    import os
    
    with open(outname, "w") as outfile:
        for dirName, subdirList, fileList in os.walk(rootDir):
            #print(dirName)
            for fname in fileList:
                #print(fname)
                filepath = "\\".join([dirName, fname])
                if fname.endswith(filetype):
                    with open(filepath, "r") as f:
                        print(fname)
                        theDir = "DIRECTORY -->  {}\n".format(dirName.upper())
                        theFile = "FILE ------->  {}".format(fname.upper())
                        outfile.write(theDir)
                        outfile.write(theFile)
                        outfile.write('\n\n')
                        for line in f:
                            outfile.write(line)
                        outfile.write('\n\nEND OF SAS FILE\n')
                        outfile.write('~' * 71)
                        outfile.write('\n\n\nSTART FILE\n\n')
                else:
                    pass
    print('Done.')