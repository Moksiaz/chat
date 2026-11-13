import os
import asyncio
import http
from collections import deque
import websockets

polaczeni_klienci = set()
# Przechowuje w pamięci ostatnie 50 wiadomości
historia_czatu = deque(maxlen=50)

async def obsluga_klienta(websocket):
    polaczeni_klienci.add(websocket)
    print(f"Nowy użytkownik dołączył. Aktywnych: {len(polaczeni_klienci)}")
    
    try:
        # 1. Wysyłamy historię czatu osobie, która właśnie dołączyła
        for stara_wiadomosc in historia_czatu:
            await websocket.send(stara_wiadomosc)

        # 2. Odbieramy nowe wiadomości i zapisujemy je w historii
        async for wiadomosc in websocket:
            historia_czatu.append(wiadomosc)
            
            for klient in list(polaczeni_klienci):
                try:
                    await klient.send(wiadomosc)
                except websockets.exceptions.ConnectionClosed:
                    pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        polaczeni_klienci.discard(websocket)
        print(f"Użytkownik wyszedł. Aktywnych: {len(polaczeni_klienci)}")

def health_check(connection, request):
    if request.path == "/healthz" or "Upgrade" not in request.headers:
        return connection.respond(http.HTTPStatus.OK, "Serwer czatu dziala poprawnie!\n")
    return None

async def main():
    port = int(os.environ.get("PORT", 8765))
    async with websockets.serve(
        obsluga_klienta,
        "0.0.0.0",
        port,
        process_request=health_check
    ):
        print(f"Serwer czatu wystartował na porcie {port}...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
