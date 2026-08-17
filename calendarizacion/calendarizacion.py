from pathlib import Path
import sys

# Importamos las variables obtenidas en la fase 1

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from programacion_lineal.optimizacion_horas import (
    X_HO_1,
    X_HO_2,
    X_HO_3,
    X_HC_1,
    X_HC_2,
    X_HC_3,
    X_HFD_1,
    X_HFD_2,
    X_HFD_3,
)

var_values = {
    "X_HO_1": X_HO_1.varValue,
    "X_HO_2": X_HO_2.varValue,
    "X_HO_3": X_HO_3.varValue,
    "X_HC_1": X_HC_1.varValue,
    "X_HC_2": X_HC_2.varValue,
    "X_HC_3": X_HC_3.varValue,
    "X_HFD_1": X_HFD_1.varValue,
    "X_HFD_2": X_HFD_2.varValue,
    "X_HFD_3": X_HFD_3.varValue,
}



