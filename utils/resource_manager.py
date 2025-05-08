# utils/resource_manager.py

# Módulo para registrar entregas de recursos pelos agentes

_deliveries = {}

def register_delivery(agent_id, val=None):

    # Determina valor do recurso
    if val != None:
        if agent_id not in _deliveries:
            _deliveries[agent_id] = val

        else:
            _deliveries[agent_id] += val

        print(f"[DELIVERY] Agente {agent_id} entregou valor {val}. Total = {_deliveries[agent_id]}")
    
    elif agent_id in _deliveries:
        return _deliveries[agent_id]
    else:
        return 0
