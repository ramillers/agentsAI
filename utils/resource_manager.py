# utils/resource_manager.py

# Módulo para registrar entregas de recursos pelos agentes
import constantes
_deliveries = {}


def register_delivery(agent_id, type_resource = None):

    # Determina valor do recurso
    if type_resource != None:
        if agent_id not in _deliveries:
            _deliveries[agent_id] = {}
            _deliveries[agent_id]["val"] = 0
            _deliveries[agent_id]["resources"] = {}
            _deliveries[agent_id]["resources"][type_resource] = 1
            _deliveries[agent_id]["val"] += constantes.RESOURCE_VALUES[type_resource]

        else:
            if type_resource not in _deliveries[agent_id]["resources"]:
                _deliveries[agent_id]["resources"][type_resource] = 1
                _deliveries[agent_id]["val"] += constantes.RESOURCE_VALUES[type_resource]

            else:
                _deliveries[agent_id]["resources"][type_resource] += 1
                _deliveries[agent_id]["val"] += constantes.RESOURCE_VALUES[type_resource]


            #NAO TA SOMANDO ;-;

        print(f"[DELIVERY] Agente {agent_id} entregou valor {constantes.RESOURCE_VALUES[type_resource]}. Total = {_deliveries[agent_id]["val"]}")
    
    elif agent_id in _deliveries:
        return _deliveries[agent_id] #voU RETtorna isso aqui Retorno uma String
    else:
        return 0
