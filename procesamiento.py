
import pandas as pd
import numpy as np


def preprocesamiento(dataframe):
    dataframe = pd.DataFrame(dataframe[11::][0::])
    dataframe = dataframe.reset_index(drop=True)
    dataframe = dataframe.rename(columns={"Unnamed: 1": "Longitud de onda"})
    longitud_onda = dataframe["Longitud de onda"].copy()
    return longitud_onda, dataframe


def procesamiento(dataframe: pd.DataFrame):
    concentraciones = []
    for i in range(len(dataframe.columns)):
        try:
            print(float(dataframe.values[0][i]))
        except:
            concentraciones.append(dataframe.columns[i])
    dataframe = dataframe.drop(concentraciones, axis='columns')
    return dataframe


def procesamiento2(dataframe: pd.DataFrame):
    dataframe.columns = [
        f"{dataframe.values[0][i]}" for i in range(dataframe.shape[1])]

    concentraciones = [dataframe.columns[i] for i in range(
        len(dataframe.columns)) if type(dataframe.values[0][i]) == str]
    dataframe = dataframe.drop(concentraciones, axis='columns')
    return dataframe


def longitud_onda_ordenar(dataframe: pd.DataFrame, longitud_onda: pd.DataFrame):
    dataframe.insert(0, "Longitud de onda", longitud_onda.values.tolist())
    concentraciones_dateframe = dataframe.iloc[[0]]

    dataframe = dataframe.drop(dataframe.index[0])
    dataframe = dataframe.sort_values("Longitud de onda")
    dataframe = dataframe.reset_index(drop=True)
    dataframe = dataframe.astype(
        {f'{dataframe.columns[i]}': 'float' for i in range(1, dataframe.shape[1])})
    return dataframe, concentraciones_dateframe


def coeficientes_estimados(x, y):
    n = len(x)
    prod_xy = []
    x_cuad = []
    for i in range(n):
        prod_xy.append(x[i] * y[i])
        x_cuad.append(x[i]**2)

    a1 = ((n*np.sum(prod_xy) - np.sum(x)*np.sum(y)) /
          (n*np.sum(x_cuad) - (np.sum(x))**2))
    a0 = (np.sum(y)/n) - (a1/n) * (np.sum(x))
    return [a1, a0]


def sumatoria_total_cuadrados(y):
    n = len(y)
    y_promedio = (np.sum(y)) / n
    valor = []
    for i in range(n):
        valor.append((y[i] - y_promedio)**2)
    return np.sum(valor)


def sumatoria_residuos(x, y, a1, a0):
    n = len(x)
    valor = []
    for i in range(n):
        valor.append((y[i] - a0 - a1*x[i])**2)
    return np.sum(valor)


def factor_correlacion(sr, st):
    return ((st - sr) / st)**(1/2)


def calcularConcentraciones(Pesomg: float, NoDisoluciones: int, PesoMol: float,
                            volDisolucion: float, volml: float, proporcion: int):
    """
    :param Pesomg: float en miligramos
    :param NoDisoluciones: int 
    :param PesoMol: float peso molecular del biomarcador
    :param volDisolucion: float 
    :param volml: float volumen de agua
    :param proporcion: int proporcion de las concentraciones
    :return: None
    """
    sMadre = ((Pesomg * 1e-3) / (PesoMol * volml * 1e-3)) * 1e6
    sM = sMadre
    uM = [0] * NoDisoluciones
    PPM = [0] * NoDisoluciones
    solucion_madre = [0] * NoDisoluciones
    Agua = [0] * NoDisoluciones

    for i in range(NoDisoluciones):
        uM[i] = round(sM, 4)
        PPM[i] = round(uM[i] * 1e-3 * PesoMol, 4)
        solucion_madre[i] = round(uM[i] * volDisolucion / sMadre, 4)
        Agua[i] = volDisolucion - solucion_madre[i]
        sM = sM / proporcion

    tabla = pd.DataFrame()
    tabla.insert(0, column='Solucion madre', value=solucion_madre)
    tabla.insert(1, column='Agua', value=Agua)
    tabla.insert(2, column='PPM', value=PPM)
    tabla.insert(3, column='mmol', value=uM)
    return tabla


def longitud_onda_ordenar_plantilla(dataframe: pd.DataFrame, longitud_onda: pd.DataFrame):
    dataframe.insert(0, "Longitud de onda", longitud_onda.values.tolist())
    concentraciones_dateframe = dataframe.iloc[[0]]

    dataframe = dataframe.drop(dataframe.index[0])
    dataframe = dataframe.sort_values("Longitud de onda")
    dataframe = dataframe.reset_index(drop=True)
    return dataframe, concentraciones_dateframe


def crear_dataframe_de_dato_plantilla(dataframe, peso_molecular, concentraciones, unidades):
    u_a = ["u.a" if i != 0 else f"{unidades}" for i in range(
        dataframe.shape[1])]
    longitud_onda = []
    aux = 0
    for i in range(dataframe.shape[1]):
        if i > 0:
            concentracion = concentraciones[concentraciones.columns[i]][0]
            if unidades == "mmol/L":
                aux = round(concentracion/peso_molecular, 5)
            elif unidades == "mg/dL":
                aux = round(concentracion/10, 10)
            else:
                aux = concentracion
            longitud_onda.append(aux)
        else:
            longitud_onda.append("Longitud de onda")

    return pd.DataFrame([u_a, longitud_onda], columns=dataframe.columns, index=['0', '1'])


def agrupar_datos_plantilla(data, new_dataframe):
    new_dataframe = new_dataframe.append(data)
    new_dataframe = new_dataframe.reset_index(drop=True)
    return new_dataframe


def checar_info(string: str):
    lista = string.split(',')
    nms = []
    booleano = True
    for i in lista:
        try:
            nms.append(int(i))
        except:
            False

    for i in nms:
        if i >= 190 and i <= 1000:
            pass
        else:
            False
    return nms, booleano


def segmentar(data: pd.DataFrame, longitud_onda, unidades: str, peso_molecular: str, nms):
    new_dataframe2 = pd.DataFrame()
    for i in range(len(nms)):
        valor_longitud_de_onda = longitud_onda[longitud_onda ==
                                               nms[i]].index[0]
        absorbancia = data.values[valor_longitud_de_onda]
        if i == 0:
            concentraciones = data.values[0].tolist()
            if unidades == "mmol/L":
                concentracion_celda2 = list(
                    map(lambda ppm: round(ppm / peso_molecular, 10), concentraciones))
            elif unidades == "mg/dL":
                concentracion_celda2 = list(
                    map(lambda ppm: round(ppm/10, 10), concentraciones))
            else:
                concentracion_celda2 = concentraciones
            new_dataframe2.insert(
                0, "Concentracion celda", concentracion_celda2)

        new_dataframe2.insert(i+1, f"Absorbancia {i+1}", absorbancia.tolist())
    return new_dataframe2


def crear_dataframe_de_datos(dataframe, nms, unidades: str):
    unidades = ["u.a" if i !=
                0 else unidades for i in range(dataframe.shape[1])]
    longitud_onda = []
    for i in range(dataframe.shape[1]):
        if i > 0:
            longitud_onda.append(nms[i - 1])
        else:
            longitud_onda.append("Concentracion celda")
    return pd.DataFrame([unidades, longitud_onda], columns=dataframe.columns, index=['0', '1'])
