import random
import pandas as pd
import pulp
import streamlit as st

# Función para ingresar cuántos días tendrá el horario
def ingresar_dias_del_horario():
    dias = st.slider("¿Cuántos días tendrá tu horario?", min_value=1, max_value=5, value=5)
    return dias

# Función para seleccionar el turno (mañana o tarde)
def seleccionar_turno():
    turno = st.selectbox("Seleccione el turno", options=["mañana", "tarde"])
    return turno

# Función para asignar los horarios según el turno seleccionado
def asignar_horarios_por_turno(dias_semana, turno):
    if turno == "mañana":
        horario_entrada = 7  # 7:00 AM
        horario_salida = 13  # 1:00 PM
    elif turno == "tarde":
        horario_entrada = 13  # 1:00 PM
        horario_salida = 19  # 7:00 PM
    
    horarios_por_dia = {}
    for dia in dias_semana:
        horarios_por_dia[dia] = (horario_entrada, 0, horario_salida, 0)
    
    return horarios_por_dia

# Función para ingresar la cantidad de cursos
def ingresar_cantidad_de_cursos():
    cantidad = st.number_input("¿Cuántos cursos desea ingresar?", min_value=1, value=1)
    return cantidad

# Función para ingresar los nombres de los cursos
def ingresar_nombres_de_cursos(cantidad_cursos):
    cursos = []
    for i in range(cantidad_cursos):
        curso = st.text_input(f"Ingrese el nombre del curso {i+1}: ")
        cursos.append(curso)
    return cursos

# Función para ingresar las horas semanales por cada curso
def ingresar_horas_por_curso(cursos):
    horas_por_curso = {}
    for curso in cursos:
        horas = st.number_input(f"Ingrese la cantidad de horas semanales para el curso {curso}", min_value=1, value=1)
        horas_por_curso[curso] = horas
    return horas_por_curso

# Función para ingresar el número de opciones a generar
def ingresar_numero_de_opciones():
    opciones = st.number_input("¿Cuántas opciones de horarios desea generar?", min_value=1, value=1)
    return opciones

# Definir los días de la semana
dias_semana_completa = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

# Función para ingresar las horas máximas por curso por día
def ingresar_max_horas_por_curso_por_dia():
    max_horas = st.number_input("¿Cuántas horas máximas por día puede llevar un curso?", min_value=1, value=3)
    return max_horas

# Modificación en la función optimizar_horario
def optimizar_horario(horas_por_materia, dias_semana, max_horas_por_dia=6, max_horas_por_curso_por_dia=3, aleatoriedad=False):
    # Crear el problema de optimización
    prob = pulp.LpProblem("Optimización_de_Horarios", pulp.LpMinimize)

    # Crear las variables de decisión (horas asignadas por curso en cada día)
    variables = {}
    for curso in horas_por_materia:
        for dia in dias_semana:
            variables[(curso, dia)] = pulp.LpVariable(f"{curso}_{dia}", lowBound=0, cat='Integer')

    # Función objetivo: minimizar las horas no asignadas o desbalanceadas
    prob += pulp.lpSum([variables[(curso, dia)] for curso in horas_por_materia for dia in dias_semana])

    # Restricciones: Cada curso debe tener asignado exactamente su número de horas semanales
    for curso, horas in horas_por_materia.items():
        prob += pulp.lpSum([variables[(curso, dia)] for dia in dias_semana]) == horas

    # Restricción: Las horas asignadas en cada día no deben exceder las horas máximas por día
    for dia in dias_semana:
        prob += pulp.lpSum([variables[(curso, dia)] for curso in horas_por_materia]) <= max_horas_por_dia

    # Restricción: Las horas por curso en cada día no deben exceder el máximo de 3 horas por curso por día
    for curso in horas_por_materia:
        for dia in dias_semana:
            prob += variables[(curso, dia)] <= max_horas_por_curso_por_dia

    # Resolver el problema
    prob.solve()

    # Convertir el horario optimizado en un formato de horario visual
    horario_optimizado = {dia: [] for dia in dias_semana}
    for curso in horas_por_materia:
        for dia in dias_semana:
            horas_asignadas = pulp.value(variables[(curso, dia)])
            if horas_asignadas > 0:
                for _ in range(int(horas_asignadas)):
                    horario_optimizado[dia].append(curso)

    # Agregar aleatoriedad si se solicita
    if aleatoriedad:
        for dia in dias_semana:
            random.shuffle(horario_optimizado[dia])  # Mezcla los cursos de cada día aleatoriamente

    # Crear DataFrame similar al código base
    horario_df = pd.DataFrame.from_dict(horario_optimizado, orient='index').fillna('')
    
    return horario_df

# Función principal para generar y mostrar los horarios
def generar_y_mostrar_horarios():
    dias_totales = ingresar_dias_del_horario()
    dias_semana = dias_semana_completa[:dias_totales]
    turno = seleccionar_turno()
    horarios_por_dia = asignar_horarios_por_turno(dias_semana, turno)
    cantidad_cursos = ingresar_cantidad_de_cursos()
    cursos = ingresar_nombres_de_cursos(cantidad_cursos)
    horas_por_materia = ingresar_horas_por_curso(cursos)
    num_opciones = ingresar_numero_de_opciones()

    # Ingresar las horas máximas por curso por día
    max_horas_por_curso_por_dia = ingresar_max_horas_por_curso_por_dia()

    for i in range(num_opciones):
        # Introducimos aleatoriedad en la generación de opciones
        aleatoriedad = i > 0  # Para la primera opción no hay aleatoriedad, para las demás sí
        horario_optimizado = optimizar_horario(
            horas_por_materia, dias_semana, max_horas_por_curso_por_dia=max_horas_por_curso_por_dia, aleatoriedad=aleatoriedad)
        
        st.subheader(f"Horario Opción {i+1}")
        st.dataframe(horario_optimizado)

# Ejecutar la función principal
if __name__ == "__main__":
    st.title("Generador de Horarios")
    generar_y_mostrar_horarios()
