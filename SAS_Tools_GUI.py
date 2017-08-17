import os, re, sys, tkinter
from tkinter import messagebox
from SAS_Structure_Tools import *

#create new window
window = tkinter.Tk()

#format the window
window.title("SAS Code Structure Tool")
window.geometry("450x200")
#window.wm_iconbitmap('filename.ico') #add personalise icon



def RunIt():

    #test whether a valid ROOT directory has been entered
    try:
        #if a valid path is given it is set as the root directory.
        if os.path.isdir(entry1.get()):
            rootDirectory = os.path.realpath(entry1.get())
        else:
            messagebox.showwarning(
                "Open directory",
                "Not a valid directory path\n(%s)" % entry1.get()
                )
            return
    except:
        with open("Log.txt", 'w') as logfile:
                logfile.write("Error")
                logfile.write(e)
        messagebox.showwarning(
                "Open directory error",
                "Not a valid directory path\n(%s)" % entry1.get()
                )
        return



    #test whether a valid OUTPUT directory has been entered.
    #if left blank output it defaults to the source directory without prompting.
    if not entry2.get():
        outDirectory = rootDirectory

    #if valid path given it is set as the output location
    elif os.path.isdir(entry2.get()):
        outDirectory = os.path.realpath(entry2.get())
        
    #otherwise user promted to accept outputting to the source directory.
    else:
        if messagebox.askyesno(title="Invalid path",
                               message="Invalid path given.\nClick Yes to output to the source directory\nOr No to cancel and enter a valid path."):
            outDirectory = rootDirectory
        else:
            return



    #Test whether user has write permission for the OUTPUT directory.            
    try: 
        #create output file name
        allCodeFile = os.path.join(outDirectory, "AllCode.txt")
        #create compilation code file
        textCombiner(rootDir=rootDirectory, filetype=".sas", outname=allCodeFile)
        
    except (IOError, PermissionError):
        if messagebox.askyesno(title="Permission Error",
                               message="You do not have permission to write to this directory.\nClick Yes to output to the source directory\nOr No to cancel and enter a valid path."):
            outDirectory = rootDirectory
        else:
            outDirectory = None

    except:
        if messagebox.askyesno(title="Error!",
                               message="Click Yes to output to the source directory\nOr No to cancel and enter a valid path."):
            outDirectory = rootDirectory
        else:
            return
            
    finally:
        #if an invalid outDirectory is given and the user does not agree to default to the root directory
        #then the outDirectory will have been set to None and the following step will end the function.
        if not outDirectory:
            return

        #With valid input and output directories given the code compilation and analysis programs are called:
        else:
            #create output file name
            allCodeFile = os.path.join(outDirectory, "AllCode.txt")
            #create compilation code file
            textCombiner(rootDir=rootDirectory, filetype=".sas", outname=allCodeFile)
            #analyse code for datasets
            ddict, sdict = compileDict(allCodeFile, delComments=True)
            #output dataset family structure file
            dataAntecedents(ddict, os.path.join(outDirectory, 'dataFamily.txt'))
            #output datasource text file
            dataOrigin(sdict, os.path.join(outDirectory, 'dataSources.txt'))


#create a label widget called 'label1'
label0 = tkinter.Label(window, text="""\nEnter the root directory of the code to be analysed.
Enter an output directory if different to the above.
Blank output field defaults to the root directory)\n""")


#create a label widget called 'label1'
label1 = tkinter.Label(window, text='Root Directory')
#create a text entry widget called 'entry1'
inDir = tkinter.StringVar()
entry1 = tkinter.Entry(window, textvariable=inDir, width=60)


#create a label widget called 'label2'
label2 = tkinter.Label(window, text='[Output Directory]')
#create a text entry widget called 'entry1'
outDir = tkinter.StringVar()
entry2 = tkinter.Entry(window, textvariable=outDir, width=60)

#create a button widget called 'button1'
button1 = tkinter.Button(window, text='Analyse', command=RunIt)

#pack (Add) the widgets into the window
label0.pack()
label1.pack()
entry1.pack()
label2.pack()
entry2.pack()
button1.pack()


#draw the window and start program
window.mainloop()            
