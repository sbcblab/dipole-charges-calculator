#Bruno Iochins Grisci 2018
#http://sbcb.inf.ufrgs.br/home

# Usage: python getvector.py file1.csv file2-esp.mol2 1.0 0.0
# Usage: python getvector.py file1.csv file2-esp.mol2 module_coeficient (1.0 is default)  molecule_charge (0.0 is default)

import sys
import numpy as np
from numpy import genfromtxt
from scipy.optimize import lsq_linear

'''It reads the .csv file, it should follow this format for each text line:
index, atom_name, fixed_flag, x, y, z, ref_charge, charge_lower_bound, charge_upper_bound
And each line represents an atom.'''

csv_name = sys.argv[1]
mol2_name = sys.argv[2]
coef = float(sys.argv[3])
mol_charge = float(sys.argv[4])

esp = genfromtxt(csv_name, delimiter=',')

'''POS is the matrix of atoms positions X, Y, Z, it is transposed in order to
convert the .mol2 (and .csv) notation to the shape needed for the linear problem.
  mol2         linear problem
X0 Y0 Z0      X0 X1 X2 ... Xn
X1 Y1 Z1  ->  Y0 Y1 Y2 ... Yn
X2 Y2 Z2      Z0 Z1 Z2 ... Zn
...
Xn Yn Zn '''

POS = np.transpose(esp[:,3:6])
C_ref = esp[:,-3]
C_lb = esp[:,-2]
C_up = esp[:,-1]

'''The fixed flag: 0 if not fixed, 1 if fixed
Atoms marked as fixed (= 1) will have their charges fixed to the value of their
lower bound charges.
For fixed atoms the values of the lower bound and upper bound charge should be the same.'''

fixed = esp[:,2]

'''If the lower and upper bounds for a charge are equal, i. e., that charge
value should be constant, a small value is added to the upper charge so the
algorithm can run.'''
for bound in xrange(C_lb.size):
        if C_lb[bound] == C_up[bound]:
                C_up[bound] = C_up[bound] + 0.000001

K_ref = np.dot(POS, C_ref)

'''In order to satisfy the condition that the sum of all charges must be = mol_charge,
a row of coeficients all equal 1.0 is appended at the end of the POS matrix and
the value mol_charge is appended at the end of the vector of charges references. This
way, when solving the linear problem, one of the equations will be
1 * c0 + 1 * c1 + ... + 1 * cn = mol_charge '''
#Creates a new vector with 1.0 in all positions and add it as last row in the POS matrix
one_row = np.zeros(shape=(1,POS.shape[1]))
one_row.fill(1.0)
POS = np.vstack([POS, one_row])
#Add mol_charge at the end of the reference vector for charges
K_ref = np.append(K_ref, [mol_charge])

'''For each atom marked with the fixed flag = 1, a row of coeficients all
equal 0.0 is appended at the end of the POS matrix, except for the coeficient of
the marked atom, that is equal 1.0, and the value of its lower bound charge is
appended at the end of the vector of charges references. This way, when solving
the linear problem, one of the equations will be
0 * c0 + 0 * c1 + ... + 1 * cmarked + ... 0 * cn = lb_charge '''
for flag in xrange(fixed.size):
    if fixed[flag] == 1:
        #Creates a new vector with 0.0 in all positions except the position of
        #the flag = 1 and adds it as last row in the POS matrix
        new_row = np.zeros(shape=(1,POS.shape[1]))
        new_row[:,flag] = 1.0
        POS = np.vstack([POS, new_row])
        #Add the lower bound charge of the marked atom at the end of the
        #reference vector for charges
        K_ref = np.append(K_ref, [C_lb[flag]])

'''Solving the linear problem POS * C_pred = K_ref
We want to know the vector C_pred of new charge values that preserves the
module and orientation of vector K_ref, and also obeys the constraints of lower
and upper bounds for each charge and keeps the sum of all charges = mol_charge'''

'''We also added a coefficient to multiply the K_ref in cases we want a slightly
different vector module but still the same direction'''

K_ref = K_ref * coef

C_pred = lsq_linear(POS, K_ref, bounds=(C_lb, C_up), lsmr_tol='auto', verbose=1)
C_pred = C_pred['x']
print('Check if charges respect constraints:')
for i in xrange(len(C_pred)):
    if C_pred[i] >= C_lb[i] and C_pred[i] <= C_up[i]:
        print(str(C_pred[i]) + ' OK!')
    else:
        print(str(C_pred[i]) + ' outside ' + str(C_lb[i], C_up[i])) 
print('Charges: \n' + str(C_pred))
print('Molecule total charge: ' + str(sum(C_pred)))

'''The next lines read a .mol2 file and change its charges to the new charges
in C_pred, saving the new results in a *-lsql.mol2 file'''

in_f  = open(mol2_name, 'r')
out_f = open(mol2_name.replace('esp', 'lsql'), 'w')

# Copy the @<TRIPOS>MOLECULE section
for i in xrange(8):		#acessing the atoms
        l = in_f.readline()
        out_f.write(l)

# Copy the @<TRIPOS>ATOM section changing the charge value
for c in C_pred:
        l = in_f.readline()
        l = list(l)
        str_c = str(c)
        if c >= 0.0:
                str_c = ' ' + str_c
        l[-12:-2] = str_c
        out_f.write(''.join(l))

# Copy the @<TRIPOS>BOND section
l = in_f.readline()
while l:		#acessing the atoms
        out_f.write(l)
        l = in_f.readline()

in_f.close()
out_f.close()
