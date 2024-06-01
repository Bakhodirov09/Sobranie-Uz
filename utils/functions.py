from utils.db_api.database_settings import get_all_radius


async def check_km(km, total):
    all_radius = await get_all_radius()
    applicable_radius = None
    applicable_sum = None
    for radius in all_radius:
        if int(km) <= radius['radius']:
            applicable_radius = radius['radius']
            applicable_sum = radius['sum']
            break
    if applicable_radius is None:
        return None

    if total < applicable_sum:
        return f"Total sum is mast {applicable_sum}"

    return True
    