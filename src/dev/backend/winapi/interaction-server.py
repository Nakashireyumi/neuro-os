from ...utils.winapi_management import start_windows_api_server, stop_windows_api_server

if __name__ == "__main__":
    try:
        start_windows_api_server()
    except [KeyboardInterrupt, Exception] as e:
        print(e)
        stop_windows_api_server()