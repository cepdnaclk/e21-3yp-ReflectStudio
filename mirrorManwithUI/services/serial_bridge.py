import serial
import time
import asyncio
import json
import requests

from config.settings import SERIAL_PORT, SERIAL_BAUD, API_URL
from models.app_state import presence_state

async def run_serial_bridge(manager=None):
    """
    Background worker that connects to ESP32 over serial.
    Listens for presence/absence events, updates application state,
    broadcasts notifications to WebSocket manager, and sends LED commands.
    """
    loop = asyncio.get_running_loop()
    print(f"🔌 [Serial Bridge] Starting presence listener on port {SERIAL_PORT}...", flush=True)
    
    while True:
        try:
            # Connect in a separate thread to avoid blocking the main event loop
            ser = await asyncio.to_thread(serial.Serial, SERIAL_PORT, SERIAL_BAUD, timeout=0.5)
            try:
                # Wait for ESP32 auto-reset
                await asyncio.sleep(2)
                print(f"🔌 [Serial Bridge] Connected to ESP32 on {SERIAL_PORT}", flush=True)
                
                def read_loop():
                    while True:
                        raw_line = ser.readline().decode('utf-8', errors='ignore').strip()
                        if not raw_line:
                            continue
                        
                        if "PRESENT" in raw_line:
                            print(">>> Event detected: PRESENT", flush=True)
                            presence_state["status"] = "present"
                            if manager:
                                asyncio.run_coroutine_threadsafe(
                                    manager.broadcast(json.dumps({"type": "presence", "value": "present"})),
                                    loop
                                )
                            else:
                                # Direct execution fallback (standalone script)
                                try:
                                    requests.get(API_URL + "present", timeout=2)
                                except Exception:
                                    pass
                            
                            try:
                                ser.write(b"LED_ON\n")
                                ser.flush()
                            except Exception:
                                pass
                                
                        elif "ABSENT" in raw_line:
                            print(">>> Event detected: ABSENT", flush=True)
                            presence_state["status"] = "absent"
                            if manager:
                                asyncio.run_coroutine_threadsafe(
                                    manager.broadcast(json.dumps({"type": "presence", "value": "absent"})),
                                    loop
                                )
                            else:
                                # Direct execution fallback
                                try:
                                    requests.get(API_URL + "absent", timeout=2)
                                except Exception:
                                    pass
                            
                            try:
                                ser.write(b"LED_OFF\n")
                                ser.flush()
                            except Exception:
                                pass
                                
                # Run the blocking read_loop in a thread
                await asyncio.to_thread(read_loop)
            finally:
                try:
                    ser.close()
                except Exception:
                    pass
            
        except Exception as e:
            print(f"⚠️ [Serial Bridge] Connection/Read error on {SERIAL_PORT}: {e}", flush=True)
            
        await asyncio.sleep(5) # Retry interval

if __name__ == "__main__":
    try:
        asyncio.run(run_serial_bridge())
    except KeyboardInterrupt:
        print("\nStopping Serial Bridge.", flush=True)
