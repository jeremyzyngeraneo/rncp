from armonik.client.results import ArmoniKResults
from armonik.common import Filter


def list_results(client: ArmoniKResults, result_filter: Filter):
    page = 0
    results = client.list_results(result_filter, page=page)
    while len(results[1]) > 0:
        for result in results[1]:
            print(f"Result ID: {result.result_id}")
        page += 1
        results = client.list_results(result_filter, page=page)

    print(f"\nTotal results: {results[0]}\n")


def hello():
    return "Hello, Result!"
