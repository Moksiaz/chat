import os
import asyncio
import http
import websockets

polaczeni_klienci = set()

async def obsluga_klienta(websocket):
    polaczeni_klienci.add(websocket)
    print(f"Nowy użytkownik dołączył. Aktywnych: {len(polaczeni_klienci)}")
    try:
        async for wiadomosc in websocket:
            # Rozsyłamy wiadomość do każdego podłączonego klienta
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

# Funkcja odpowiadająca na zwykłe wejście przez przeglądarkę / sprawdzanie stanu przez Render
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
