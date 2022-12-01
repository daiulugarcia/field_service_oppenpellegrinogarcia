import sys
import cplex

TOLERANCE =10e-6 

class Orden:
    def __init__(self):
        self.id = 0
        self.beneficio = 0
        self.trabajadores_necesarios = 0
    
    def load(self, row):
        self.id = int(row[0])
        self.beneficio = int(row[1])
        self.trabajadores_necesarios = int(row[2])

class FieldWorkAssignment:
    def __init__(self):
        self.cantidad_trabajadores = 0
        self.cantidad_ordenes = 0
        self.ordenes = []
        self.conflictos_trabajadores = []
        self.ordenes_correlativas = []
        self.ordenes_conflictivas = []
        self.ordenes_repetitivas = []
        self.var_dict = {}

    def load(self,filename):
        f = open(filename)
        # Leemos la cantidad de trabajadores
        self.cantidad_trabajadores = int(f.readline())      
        # Leemos la cantidad de ordenes
        self.cantidad_ordenes = int(f.readline())       
        # Leemos cada una de las ordenes.
        self.ordenes = []
        for i in range(self.cantidad_ordenes):
            row = f.readline().split(' ')
            orden = Orden()
            orden.load(row)
            self.ordenes.append(orden)  

        # Leemos la cantidad de conflictos entre los trabajadores
        cantidad_conflictos_trabajadores = int(f.readline()) 
            
        # Leemos los conflictos entre los trabajadores
        self.conflictos_trabajadores = []
        for i in range(cantidad_conflictos_trabajadores):
            row = f.readline().split(' ')
            self.conflictos_trabajadores.append(list(map(int,row)))

        # Leemos la cantidad de ordenes correlativas
        cantidad_ordenes_correlativas = int(f.readline())
            
        # Leemos las ordenes correlativas
        self.ordenes_correlativas = []
        for i in range(cantidad_ordenes_correlativas):
            row = f.readline().split(' ')
            self.ordenes_correlativas.append(list(map(int,row))) 
                    
        # Leemos la cantidad de ordenes conflictivas
        cantidad_ordenes_conflictivas = int(f.readline()) 

        # Leemos las ordenes conflictivas
        self.ordenes_conflictivas = []
        for i in range(cantidad_ordenes_conflictivas):
            row = f.readline().split(' ')
            self.ordenes_conflictivas.append(list(map(int,row)))

        # Leemos la cantidad de ordenes repetitivas
        cantidad_ordenes_repetitivas = int(f.readline())

        # Leemos las ordenes repetitivas
        self.ordenes_repetitivas = []
        for i in range(cantidad_ordenes_repetitivas):
            row = f.readline().split(' ')
            self.ordenes_repetitivas.append(list(map(int,row)))   

        # Se cierra la lectura del archivo
        f.close()

def get_instance_data():
    file_location = "/home/daiana/Desktop/Optimizacion/data/input_data.txt"
    instance = FieldWorkAssignment()
    instance.load(file_location)
    return instance

def add_constraint_matrix(my_problem, data):

#obligatorias    
    
    #no se pueden realizar varias ordenes en un mismo turno si comparten trabajadores 
    for trabajador in range(data.cantidad_trabajadores):
        for turno in range(5):
            for dia in range(6):
                indices = []
                values = []
                for orden in range(data.cantidad_ordenes):
                    indices.append(data.var_dict[f"A{trabajador},{dia},{turno},{orden}"])
                    values.append(1)
                row = [indices,values]
                my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[1])
                
                
   #no toda orden de trabajo tiene que ser resuelta

   #ningún trabajador puede trabajar los 6 días de la planificación
    for trabajador in range(data.cantidad_trabajadores):
        indices = []
        values = []
        for dia in range(6):
            indices.append(data.var_dict[f"D{trabajador},{dia}"])
            values.append(1)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[5])

    for trabajador in range(data.cantidad_trabajadores):
        for dia in range(6):
            indices = []
            values = []
            for turno in range(5):
                for orden in range(data.cantidad_ordenes):
                    indices.append(data.var_dict[f"A{trabajador},{dia},{turno},{orden}"])
                    values.append(1)
            indices.append(data.var_dict[f"D{trabajador},{dia}"])
            values.append(-5)
            row = [indices,values]
            my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[0])
            
    #ningún trabajador puede trabajar los 5 turnos en un día 
    for trabajador in range(data.cantidad_trabajadores):
        for dia in range(6):
            indices = []
            values = []
            for turno in range(5):
                for orden in range(data.cantidad_ordenes):
                    indices.append(data.var_dict[f"A{trabajador},{dia},{turno},{orden}"])
                    values.append(1)
            row = [indices,values]
            my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[4])
 
    #hay pares de ordenes de trabajo que no pueden ser satisfechas en turnos consecutivos de un trabajador
    for corr_i, corr_j in data.ordenes_correlativas:
        for trabajador in range(data.cantidad_trabajadores):
            for dia in range(6):
                for turno in range(4):
                    indices = []
                    values = []
                    indices.append(data.var_dict[f"A{trabajador},{dia},{turno},{corr_i}"])
                    values.append(1)
                    indices.append(data.var_dict[f"A{trabajador},{dia},{turno+1},{corr_j}"])
                    values.append(-1)
                    row = [indices,values]
                    my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[1])
            
    #una orden de trabajo debe tener sus To trabajadores para poder ser resuelta
    for orden in data.ordenes:
        indices = []
        values = []
        for trabajador in range(data.cantidad_trabajadores):
            for turno in range(5):
                for dia in range(6):
                    indices.append(data.var_dict[f"A{trabajador},{dia},{turno},{orden.id}"])
                    values.append(1)
        indices.append(data.var_dict[f"C{orden.id}"])
        values.append(orden.trabajadores_necesarios * -1)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["E"], rhs=[0])
        
     #existen algunos pares de ordenes de trabajo correlativas
    for a, b in data.ordenes_correlativas:
        for dia in range(6):
            for turno in range(4):
                indices = []
                values = []
                indices.append(data.var_dict[f"E{a},{turno},{dia}"])
                values.append(1)
                indices.append(data.var_dict[f"E{b},{turno+1},{dia}"])
                values.append(-1)
                row = [indices,values]
                my_problem.linear_constraints.add(lin_expr=[row], senses=["E"], rhs=[0])

            
  #la diferencia entre el trabajador con mas ordenes asignadas y el trabajador con menos ordenes no puede ser mayor a 10
    for trabajadorA in range(data.cantidad_trabajadores):
        for trabajadorB in range(data.cantidad_trabajadores):
            if trabajadorA != trabajadorB:
                indices = []
                values = []
                indices.append(data.var_dict[f"Q{trabajadorA}"])
                values.append(1)
                indices.append(data.var_dict[f"Q{trabajadorB}"])
                values.append(-1)
                row = [indices,values]
                my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[10])                   
            
#deseables

    #hay conflictos entre algunos trabajadores que hacen que prefieran no ser asignados a una misma orden de trabajo
    for trabajador_i, trabajador_j in data.conflictos_trabajadores:
        for turno in range(5):
            for dia in range(6):
                for orden in range(data.cantidad_ordenes):
                    indices = []
                    values = []
                    indices.append(data.var_dict[f"A{trabajador_i},{dia},{turno},{orden}"])
                    values.append(1)
                    indices.append(data.var_dict[f"A{trabajador_j},{dia},{turno},{orden}"])
                    values.append(1)
                    row = [indices,values]
                    my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[1])

    #hy pares de  ordenes de trabajo que son repetitivas por lo que sería bueno que un mismo trabajador no sea asignado a ambas
    for orden_a, orden_b in data.ordenes_repetitivas:
        for trabajador in range(data.cantidad_trabajadores):
            indices = []
            values = []
            for turno in range(5):
                for dia in range(6):
                    indices.append(data.var_dict[f"A{trabajador},{dia},{turno},{orden_a}"])
                    values.append(1)
                    indices.append(data.var_dict[f"A{trabajador},{dia},{turno},{orden_b}"])
                    values.append(1)
            row = [indices,values]
            my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[1])
            
#función de pagos

    #los trabajadores son remunerados segun la cantidad de ordenes maximas realizadas (ej: si realiza 10, se le paga el mismo importe por las 10) 
    
    for trabajador in range(data.cantidad_trabajadores):
        indices = []
        values = []
        for turno in range(5):
            for dia in range(6):
                for orden in data.ordenes:
                    indices.append(data.var_dict[f"A{trabajador},{dia},{turno},{orden.id}"])
                    values.append(1)
        indices.append(data.var_dict[f"Q{trabajador}"])
        values.append(-1)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["E"], rhs=[0])
  
    for trabajador in range(data.cantidad_trabajadores):
        indices = []
        values = []
        for w in (range(1,5)):
            indices.append(data.var_dict[f"Q{w},{trabajador}"])
            values.append(1)
        indices.append(data.var_dict[f"Q{trabajador}"])
        values.append(-1)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["E"], rhs=[0])

    for trabajador in range(data.cantidad_trabajadores):
        indices = []
        values = []
        for A in (range(1,5)):
            indices.append(data.var_dict[f"L{A}{trabajador}"])
            values.append(1)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[1])
            
    for trabajador in range(data.cantidad_trabajadores):
        pagas_nro_orden={1:5, 2:10, 3:15, 4:20}  
        for lim_nro_orden in pagas_nro_orden:
            indices = []
            values = []
            indices.append(data.var_dict[f"Q{lim_nro_orden},{trabajador}"])
            values.append(1)
            indices.append(data.var_dict[f"L{lim_nro_orden}{trabajador}"])
            values.append(-pagas_nro_orden[lim_nro_orden])
            row = [indices,values]
            my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[0])

def populate_by_row(my_problem, data):
    
    # Definimos y agregamos las variables.
    coeficientes_funcion_objetivo = []
    i = -1
    
    #variable E
    for turno in range(5):
        for dia in range(6):
            for orden in range(data.cantidad_ordenes):
                i +=1
                coeficientes_funcion_objetivo.append(0)
                data.var_dict[f"E{orden},{turno},{dia}"] = i 
                
    #variable A
    for trabajador in range(data.cantidad_trabajadores):
        for turno in range(5):
            for dia in range(6):
                for orden in range(data.cantidad_ordenes):
                    i +=1
                    coeficientes_funcion_objetivo.append(0)
                    data.var_dict[f"A{trabajador},{dia},{turno},{orden}"] = i

    #variables L
    for trabajador in range(data.cantidad_trabajadores):
        for aux in range(1,5):
            i +=1
            coeficientes_funcion_objetivo.append(0)
            data.var_dict[f"L{aux}{trabajador}"] = i 

    #variable C
    for orden in data.ordenes:
        i +=1
        coeficientes_funcion_objetivo.append(orden.beneficio)
        data.var_dict[f"C{orden.id}"] = i 
        
    #variable D
    for trabajador in range(data.cantidad_trabajadores):
        for dia in range(6):
            i +=1
            coeficientes_funcion_objetivo.append(0)
            data.var_dict[f"D{trabajador},{dia}"] = i
        
    #variables booleanas
    lb = [0]*len(coeficientes_funcion_objetivo)
    ub = [1]*len(coeficientes_funcion_objetivo)
    types = ['B']*len(coeficientes_funcion_objetivo)

    #variable Q
    for trabajador in range(data.cantidad_trabajadores):
        i +=1
        coeficientes_funcion_objetivo.append(0)
        data.var_dict[f"Q{trabajador}"] = i
    
    #lower bound es que no trabajen ninguna jordana
    lb = lb + [0] * (data.cantidad_trabajadores)
    #upper bound es que trabajen como maximo 4 turnos de 5 jornadas 
    ub = ub + [4*5] * (data.cantidad_trabajadores)
    types = types + [my_problem.variables.type.integer]*(data.cantidad_trabajadores)
    
    #variables Q segun paga
    pagas_nro_orden = {1: 1000, 2: 1200, 3:1400, 4:1500}
    
    for trabajador in range(data.cantidad_trabajadores):
        for j in range(1,5):
            i +=1
            coeficientes_funcion_objetivo.append(pagas_nro_orden[j]*(-1))
            data.var_dict[f"Q{j},{trabajador}"] = i
            
    lb = lb + [0] * (data.cantidad_trabajadores * 4)
    ub = ub + [5] * (data.cantidad_trabajadores * 4)
    types = types + [my_problem.variables.type.integer]*(data.cantidad_trabajadores * 4) 

    my_problem.variables.add(obj = coeficientes_funcion_objetivo, lb = lb , ub = ub, types = types, names = list(data.var_dict.keys())) 

    # Seteamos direccion del problema
    my_problem.objective.set_sense(my_problem.objective.sense.maximize)
    
    # Definimos las restricciones del modelo. Encapsulamos esto en una funcion. 
    add_constraint_matrix(my_problem, data)

    # Exportamos el LP cargado en myprob con formato .lp. 
    # Util para debug.
    my_problem.write('balanced_assignment.lp')

def solve_lp(my_problem, data):
    
        # Resolvemos 
        my_problem.solve()

        # Output de la solucion  
        x_variables = my_problem.solution.get_values()
        objective_value = my_problem.solution.get_objective_value()
        status = my_problem.solution.get_status()
        status_string = my_problem.solution.get_status_string(status_code = status)

        print('Funcion objetivo: ',objective_value)
        print('Status solucion: ',status_string,'(' + str(status) + ')')

        # Imprimimos las variables usadas.
        for i in range(len(x_variables)):
            if x_variables[i] > TOLERANCE:
                print(f"{list(data.var_dict.keys())[i]}:{x_variables[i]}\n")

def main():
    
    # Obtenemos los datos de la instancia. 
    data = get_instance_data()

    # Definimos el problema de cplex.
    prob_lp = cplex.Cplex()
    
    # Armamos el modelo.
    populate_by_row(prob_lp,data)

    # Resolvemos el modelo.
    solve_lp(prob_lp,data)

if __name__ == '__main__':
    main()
