import aiohttp
import asyncio

def get_tasks(url, session, operations, number_questions, params):
    """Create a list of tasks for asyncio to perform asynchronously."""
    tasks = []
    for i in range(number_questions):
        tasks.append(session.get(f"{url}/{operations}", params=params, ssl=False))
    return tasks

async def get_math_data(url, operations, number_questions, params):
    """Asynchronously call math api to return a list of math expressions."""
    results = []
    async with aiohttp.ClientSession() as session:
            tasks = get_tasks(url, session, operations, number_questions, params)
            responses = await asyncio.gather(*tasks)
            for response in responses:
                results.append(await response.json())
    return results