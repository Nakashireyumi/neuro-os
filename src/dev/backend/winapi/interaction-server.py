import signal
import sys
import atexit

from ...utils.winapi_management import start_windows_api_server, stop_windows_api_server

def signal_handler(sig, frame):
    """Handle termination signals gracefully"""
    sig_name = signal.Signals(sig).name if hasattr(signal, 'Signals') else str(sig)
    print(f"\n[SIGNAL] Interaction server received {sig_name}, shutting down...")
    stop_windows_api_server()
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Register cleanup on normal exit
    atexit.register(stop_windows_api_server)
    
    try:
        proc = start_windows_api_server()
        if proc:
            print(f"[INTERACTION-SERVER] Started with PID: {proc.pid}")
            print("[INTERACTION-SERVER] Press Ctrl+C to stop")
            # Wait for the process to finish
            proc.wait()
    except KeyboardInterrupt:
        print("\n[INTERACTION-SERVER] Interrupted, shutting down...")
        stop_windows_api_server()
    except Exception as e:
        print(f"[INTERACTION-SERVER] Error: {e}")
        stop_windows_api_server()
