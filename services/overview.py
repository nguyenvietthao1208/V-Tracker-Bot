from services.match import get_matches


async def get_overview(region, name, tag):

    data = await get_matches(
        region,
        name,
        tag,
        size=100
    )

    if data is None:
        return None

    return data