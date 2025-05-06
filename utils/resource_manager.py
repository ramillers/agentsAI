# utils/resource_manager.py

# Módulo para registrar entregas de recursos pelos agentes

_deliveries = {}

def register_delivery(agent_id, resource=None, query_only=False):
    """
    Registra uma entrega de recurso pelo agente.
    Se query_only=True, retorna a soma total entregue por esse agente.
    """
    if query_only:
        return _deliveries.get(agent_id, 0)

    # Determina valor do recurso
    val = 0
    if hasattr(resource, 'value'):
        val = resource.value
    elif isinstance(resource, (int, float)):
        val = resource

    # Atualiza o registro
    _deliveries.setdefault(agent_id, 0)
    _deliveries[agent_id] += val
    print(f"[DELIVERY] Agente {agent_id} entregou valor {val}. Total = {_deliveries[agent_id]}")
    return _deliveries[agent_id]
