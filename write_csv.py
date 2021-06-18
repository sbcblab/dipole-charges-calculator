#Bruno Iochins Grisci 2018
#http://sbcb.inf.ufrgs.br/home

import sys
import re

arq = sys.argv[1]

if arq[-5:] != '.mol2':
    raise Exception('Input file must be a .mol2')

output = arq.replace('.mol2', '.csv')

# Grepping coordenates and charges
def convert(arq, output):

    f = open(arq, "r")
    print('Reading file ' + arq)
    l = "text"

    f_out = open(output, "w")

    l = f.readline() 
    if not l:
        key = not l
    else:
        key = l.strip() != '@<TRIPOS>ATOM'
    while key:
        l = f.readline()
        print(l)
        if not l:
            key = not l
        else:
            key = l.strip() != '@<TRIPOS>ATOM'

    while True:
        l = f.readline()
        print(l)
        if not l: break
        if l.split()[0] == '@<TRIPOS>BOND': break
        if len(l) > 0:
            atom_number = str(l.split()[0]) + ","
            atom_code   = str(l.split()[1]) + ","
            atom_fixed  = "0,"
            atom_X      = str(l.split()[2]) + ","
            atom_Y      = str(l.split()[3]) + ","
            atom_Z      = str(l.split()[4]) + ","
            atom_charge = str(l.split()[8]) + ","
            range_low   = "-1.00,"
            range_high  = "1.00"

            colN = atom_number.ljust(15, " ")
            colC = atom_code.ljust(15, " ")
            colF = atom_fixed.ljust(15, " ")
            col1 = atom_X.ljust(15, " ")
            col2 = atom_Y.ljust(15, " ")
            col3 = atom_Z.ljust(15, " ")
            col4 = atom_charge.ljust(15, " ")
            col5 = range_low.ljust(15, " ")
            col6 = range_high.ljust(15, " ")

    
            f_out.write(colN)
            f_out.write(colC)
            f_out.write(colF)
            f_out.write(col1)
            f_out.write(col2)
            f_out.write(col3)
            f_out.write(col4)
            f_out.write(col5)
            f_out.write(col6)
            f_out.write("\n")

    f.close()
    f_out.close()
    print('Saved file ' + output)

convert(arq,output)
