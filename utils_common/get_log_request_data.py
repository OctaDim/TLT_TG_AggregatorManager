from fastapi import Request

async def log_all_request_data(request: Request) -> None:
    headers = dict(request.headers)
    body = await request.body()
    body_str = await request.body()
    body_str = body_str.decode('utf-8')
    request_json = await request.json()

    print(f"REQUEST INCOMING DATA:\n"
          f"\tmethod: {request.method}\n"
          f"\turl: {request.url}\n"
          f"\theaders: {headers}\n"
          f"\tquery params: {request.query_params or "None"}\n"
          f"\traw body: {body}\n"
          f"\tbody string: {body_str}\n"
          f"\trequest json: {request_json}\n")
