from src.services.timer_service import Timer
import requests

def diagnose_page_loading(url):
    results = {}
    import socket
    hostname = url.split('/')[2]
    with Timer() as t:
        ip = socket.gethostbyname(hostname)
    results["dns"] = t.result
    results['ip'] = ip

    with Timer() as t:
        response = requests.get(url)
    results["response"] = t.result
    server_time = response.elapsed.total_seconds()
    results["server_time"] = server_time
    results['size'] = len(response.content)

    return results
if __name__ == "__main__":
    url = "https://github.com/forenton/SFMProject"
    diagnosis = diagnose_page_loading(url)
    print(f"IP address: {diagnosis['ip']}")
    print(f"DNS: {diagnosis['dns']} сек")
    print(f"Сервер: {diagnosis['server_time']} сек")
    print(f"Всего: {diagnosis['response']} сек")
    print(f"Размер: {diagnosis['size']} байт")
