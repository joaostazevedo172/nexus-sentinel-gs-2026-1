@router.patch("/state", response_model=ClimateState)
async def patch_state(patch: ClimateStatePatch) -> ClimateState:
    # 1. Atualiza o estado na memória/banco
    s = state_store.update(
        temperature=patch.temperature,
        humidity=patch.humidity,
        mesh_activity=patch.meshActivity,
    )
    
    # 2. A MÁGICA (Corrigida): Envia os argumentos diretamente, sem nomeá-ls
    await manager.broadcast(
        "climate",  # O primeiro argumento é o nome do canal (string)
        {           # O segundo argumento é o dicionário com a mensagem
            "type": "climate_update",
            "state": {
                "temperature": round(s.temperature, 2),
                "humidity": round(s.humidity, 2),
                "meshActivity": round(s.mesh_activity, 2),
                "resilience": round(s.resilience, 2),
            }
        }
    )

    # 3. Retorna a resposta HTTP (200 OK)
    return ClimateState(
        temperature=round(s.temperature, 2),
        humidity=round(s.humidity, 2),
        meshActivity=round(s.mesh_activity, 2),
        resilience=round(s.resilience, 2),
    )