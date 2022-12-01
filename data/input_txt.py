import random
# Trabajadores (numero superior a 5)
Trabajadores =15
#Ordenes
Ordenes = 400
#Conflic trabajadores (siempre un valor par)
n_conflicto = 6
#Ordenes correlativas 
n_ordenes_correlativas = 10
#ordebnes conflictivas 
n_ordenes_conflictivas = 4
#ordenes rep.
n_ordenes_repetitivas = 10

Lista = [] #Lista que guarda todo

#Lista de trabajos
Lista.append(Trabajadores)
lista_No_ordenes = random.sample(range(1000,9999),Ordenes)
lo = []
lista_ordenes = []

for i in range(Ordenes):
    lo.append([i,lista_No_ordenes[i-1], random.randint(1,6)])
Lista.append(lo)


#Trabajadores conflictivos
Lista_trab_conflicto = random.sample(range(1,Trabajadores+1),n_conflicto)
tc = []
for i in range(0,n_conflicto,2):
    tc.append([Lista_trab_conflicto[i], Lista_trab_conflicto[i+1]])
Lista.append(tc)

Lista_trab = random.sample(range(1,(Ordenes+1)),(n_ordenes_correlativas*2+n_ordenes_conflictivas*2+n_ordenes_repetitivas*2)) #Tiene todos,conflictivo, correlativo, recurrente 

oc=[] #ordenes correlativas
for i in range(0,n_ordenes_correlativas*2,2):
    oc.append([Lista_trab[i],Lista_trab[i+1]])

Lista.append(oc)


ocf = [] #ordenes conflictivas

for i in range(n_ordenes_correlativas*2,((n_ordenes_conflictivas+n_ordenes_correlativas)*2),2):
    ocf.append([Lista_trab[i],Lista_trab[i+1]])

Lista.append(ocf)

orr = [] #ordenes recurrentes

for i in range(((n_ordenes_conflictivas+n_ordenes_correlativas)*2),((n_ordenes_conflictivas+n_ordenes_correlativas+n_ordenes_repetitivas)*2),2):
    orr.append([Lista_trab[i],Lista_trab[i+1]])

Lista.append(orr)

with open(r'/home/daiana/Desktop/Optimizacion/data/input_data.txt', 'w') as fp:
    for i in Lista:
        if type(i)==list:
            fp.write("%s\n" % len(i))
            
            for j in i:
                if type(j) == int:
                    fp.write('%s\n' % str(j))
                else:
                    s = ' '
                    fp.write('%s\n' % s.join([str(elem) for elem in j])) 
        else:
            fp.write("%s\n" % i)

print(Lista)

    














