from copy import deepcopy
import numpy as np
def gauss(A, B):
  A = np.linalg.inv(A)
  AB = np.dot(A,B)
  return(AB)

def transposed(matriz):
    trans = []
    for i in range(len(matriz[0])):
        aux = []
        for j in range(len(matriz)):
            aux.append(matriz[j][i])
        trans.append(aux)

    return trans



def mult(a, b):
    result = 0
    if len(a) != len(b):
        print('Gauss error')
        exit()

    for i in range(len(a)):
        result += a[i] * b[i]

    return result


def column(A, index):
    col = []
    for i in range(len(A)):
        col.append(A[i][index])
    return col


def print_matrix(mat, nome):
    print('\nMatrix {}:'.format(nome))
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            print(mat[i][j], end='\t')
        print()
    print('\n')

from tabulate import tabulate
from prettytable import PrettyTable
from termcolor import colored


#add the identity matrix to matrix A
def add_identity(A, quant_rest):
    for i in range(quant_rest):
        for j in range(quant_rest):
            if i == j:
                A[i].append(1)
            else:
                A[i].append(0)


#deletes artificial variables from the list of non-basic ones and deletes columns related to artificial variables
def fimFase1(A, nVarArtificial, Non_basic_vars):
    for i in range(nVarArtificial):
        Non_basic_vars.remove(len(A[0]) - 1 - i)

    for i in range(len(A)):
        for j in range(nVarArtificial):
            A[i].pop(-1)


def standard_form(problem_type, objective_function, restrictions, operators, b):
    fase1 = True
    A = []
    basic_vars = []
    Non_basic_vars = []
    nVarArtificial = 0

    if problem_type == 'max':  #turns to min if max
        objective_function = [(x * -1) for x in objective_function]

    for i in range(len(b)): #check for negative constraint and multiply the line by -19
        if b[i] < 0:
            b[i] *= -1
            for j in range(len(restrictions[0])):
                restrictions[i][j] *= -1

            if operators[i] == '<=':
                operators[i] = '>='
            elif operators[i] == '>=':
                operators[i] = '<='

    #creation of matrix A
    for i in range(len(restrictions)):
        lin = []
        for j in range(len(restrictions[0])):
            lin.append(restrictions[i][j])
        A.append(lin)

    #adds columns of slack and excess variables
    for i in range(len(operators)):
        if operators[i] == '<=':
            objective_function.append(0)  #adds the cost of the slack variable to the objective function
            for j in range(len(A)):
                if i == j:
                    A[j].append(1)
                else:
                    A[j].append(0)
        elif operators[i] == '>=':
            objective_function.append(0)  #adds the cost of the excess variable to the objective function
            for j in range(len(A)):
                if i == j:
                    A[j].append(-1)
                else:
                    A[j].append(0)

    #checks the need for phase 1
#     if '<=' in operators:
#         fase1 = True

    #selects the first basic variables
    for i in range(len(restrictions[0])):
        Non_basic_vars.append(i)

    # selects basic and non-basic variables
    if fase1:
        add_identity(A, len(restrictions))
        nVarArtificial = len(restrictions)

        for i in range(len(restrictions)):
            basic_vars.append(len(A[0]) - len(restrictions) + i)
            objective_function.append(0)

        for i in range(len(Non_basic_vars), len(A[0]) - len(restrictions)):
            Non_basic_vars.append(i)
    else:
        for i in range(len(restrictions)):
            basic_vars.append(i + len(restrictions[0]))

    print_matrix(A, 'A')
    print('Objective function: {}'.format(objective_function))
    print('Vector b: {}'.format(b))
    #ic('Vector b: {}'.format(b))
    print('Index of Basic variables: {}'.format(basic_vars))
    print('Index of Non-basic variables: {}'.format(Non_basic_vars))
    print('Fase 1: {}'.format(fase1))
    print('Number of artificial variables: {}'.format(nVarArtificial))

    return A, objective_function, b, basic_vars, Non_basic_vars, fase1, nVarArtificial


def update_B(A, BS):
    B = []

    for i in range(len(A)):
        line = []
        for j in range(len(BS)):
            line.append(A[i][BS[j]])

        B.append(line)

    return B

#n=len(basic_vars) + len(Non_basic_vars)
def step1(B, b, basic_vars, n):
    XB = gauss(B, b)

    X = [0] * n
    for i in range(len(basic_vars)):
        X[basic_vars[i]] = XB[i]

    print('XB :', end='')
    for i in XB:
        print('{:.2f}'.format(i), end=' ')
    print()

    print('X:', end='')
    for i in X:
        print('{:.2f}'.format(i), end=' ')
    print()
    return XB, X


def step2_1(B, basic_vars, objective_function):
    costs = []
    for i in basic_vars:
        costs.append(objective_function[i]) # takes the costs of basic variables in the objective function
    lbda = gauss(transposed(B), costs) # performs the gauss between the transposed B matrix and the costs of the basic variables

    print('lambda(shadow price):', end='')
    for i in lbda:
        print('{:.2f}'.format(i), end=' ')
    print()
    #print('vetor lbda: {}'.format(lbda))
    return lbda


def step2_2(objective_function, lbda, A, Non_basic_vars):
    vet_cnk = []
    for cn in range(len(Non_basic_vars)):
        cnk = objective_function[Non_basic_vars[cn]] - mult(lbda, column(A, Non_basic_vars[cn]))
        vet_cnk.append(cnk)

    print('SN: ', end='')
    for i in vet_cnk:
        print('{:.2f}'.format(i), end=' ')
    print()
    return vet_cnk

 #step 2.3 and 3
def step3(vet_cnk, step1):
    finish= False
    menor = min(vet_cnk)
    k = vet_cnk.index(menor)
    if menor < 0:
        print('\033[35msolution is not optimal\033[m')
        print('Entering: SN{}'.format(k + 1))
    elif step1 is True:
        finish = True
        print('\033[31mInfeasible problem\033[m')
    else:
        print('\033[35mOptimal solution found\033[m')
        finish = True
    return finish, k


def step4(B, A, Non_basic_vars, k):
    y = gauss(B, column(A, Non_basic_vars[k]))

    print('y: ', end='')
    for i in y:
        print('{:.2f}'.format(i), end=' ')
    print()
    #print("y=",y)
    return y


def step5(XB, y):
    if max(y) <= 0:
        print('Unlimited optimal solution')
        return None, True
    #aux mokhafafe komakie
    aux = []
    for i in range(len(y)):
        if y[i] > 0:
            aux.append(XB[i] / y[i])
        else:
            aux.append(-1)

    menor = [aux[0], 0]
    for i in range(1, len(aux)):
        if (menor[0] > aux[i] > 0) or menor[0] <= 0:
            menor[0] = aux[i]
            menor[1] = i
    leaver = menor[1]
    print('Leaving: B{}'.format(leaver + 1))
    return leaver, False


def step5_fase1(XB, y):
    if max(y) <= 0:
        print('Infeasible Original Problem')
        return None, True

    aux = float('inf')
    leaver = 0

    for i in range(len(XB)):
        if y[i] > 0 and XB[i]/y[i] < aux:
            aux = XB[i]/y[i]
            leaver = i

    print('Leaving: B{}'.format(leaver + 1))
    return leaver, False


def step6(BS, N, entrant, leaver):
    aux = BS[leaver]
    BS[leaver] = N[entrant]
    N[entrant] = aux
    return BS, N


def step6_fase1(BS, N, entrant, leaver, nVarArtificial):
    finish = True
    aux = BS[leaver]
    BS[leaver] = N[entrant]
    print('leaver = x'+str(aux+1))
    print('entrant = x'+str(N[entrant]+1))
    N[entrant] = aux

    totalVars = len(BS) + len(N)
    for i in range(len(BS)):
        for j in range(nVarArtificial):
            if BS[i] == totalVars - 1 - j:
                finish = False

    return BS, N, finish


def printInfo(basic_vars, Non_basic_vars, B, itr,B_inv,objective_function,CB):
    print('\n')
    print('\033[34mIteration: {}\033[m'.format(itr))
    print_matrix(B, 'B')
    #print_matrix(B_inv, 'B_inverse')
    print('Index of basic variables: {}'.format(basic_vars))
    print('Index of non-basic variables: {}'.format(Non_basic_vars))
    print('\n')
    print('CB :',CB)
        

def final(restrictions, objective_function, problem_type, X):
    print('\n\n')
    optimal_solution = 0
    for i in range(len(restrictions[0])):
        optimal_solution += objective_function[i] * X[i]

    for i in range(len(restrictions[0])):
        print('X{} = {}'.format(i + 1, X[i]))
    #if tipo_prob == 'max':
    if problem_type == 'max':
        optimal_solution *= -1
    print('Optimal solution = {}'.format(optimal_solution))

