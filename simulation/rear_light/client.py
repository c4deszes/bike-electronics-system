import capnp
import os
import asyncio
import threading
from typing import List
from line_protocol.protocol.transport import LineTransportListener
from concurrent.futures import Future

capnp.remove_import_hook()


class RearLightClient(LineTransportListener):
    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.client = None
        self.rear_light = None
        self.listener = None
        self.brightness = 0
        self._connected = False
        self._loop = None
        self._thread = None
        self._ready = threading.Event()
        
    def _run_async_loop(self):
        """Run the async event loop in a dedicated thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        async def _main():
            async with capnp.kj_loop():
                # Load the schema
                rear_light_capnp = capnp.load(os.path.join(os.path.dirname(__file__), 'rear_light.capnp'))
                
                # Create async connection and keep it alive
                connection = await capnp.AsyncIoStream.create_connection(host=self.host, port=self.port)
                self.client = capnp.TwoPartyClient(connection)
                self.rear_light = self.client.bootstrap().cast_as(rear_light_capnp.RearLight)
                self._connected = True
                self._ready.set()
                
                # Keep running forever to maintain the connection
                while self._connected:
                    await asyncio.sleep(0.1)
        
        # Run the main coroutine which keeps the kj_loop alive
        try:
            self._loop.run_until_complete(_main())
        except Exception as e:
            print(f"Error in async loop: {e}")
            self._ready.set()  # Unblock connect() even on error
    
    def _call_async(self, coro):
        """Execute an async coroutine and return the result synchronously."""
        if not self._connected and not self._ready.is_set():
            raise RuntimeError("Client not connected. Call connect() first.")
        
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()
        
    def connect(self):
        """Establish a connection to the rear light server."""
        if self._connected:
            return
        
        # Start the async loop in a background thread
        self._thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self._thread.start()
        
        # Wait for connection to be established
        self._ready.wait(timeout=5.0)
        if not self._connected:
            raise RuntimeError("Failed to connect to server")
        
    def start(self):
        """Initialize the rear light."""
        if not self._connected:
            self.connect()
        
        async def _start():
            await self.rear_light.initialize()
        
        self._call_async(_start())

    def on_tick(self, delta):
        """Process a simulation tick (blocking)."""
        if not self._connected:
            raise RuntimeError("Client not connected. Call connect() or start() first.")
        
        delta_ms = int(delta * 1000)
        
        async def _on_tick():
            await self.rear_light.onTick(delta_ms)
            brightness = await self.rear_light.getTailLightBrightness()
            brightness = int(brightness.brightness)
            brightness = int(brightness / 10)
            #print(f"Current brightness: {brightness}")
            
            # Notify listener if brightness changed
            if self.listener and brightness != self.brightness:
                self.listener.on_brightness_changed(brightness)
                self.brightness = brightness
        
        self._call_async(_on_tick())
    
    def set_tail_light_state(self, state):
        """Set the tail light state (blocking)."""
        if not self._connected:
            raise RuntimeError("Client not connected. Call connect() or start() first.")
        
        async def _set_state():
            await self.rear_light.setTailLightState(state)
        
        self._call_async(_set_state())

    def on_request(self, request: int) -> List[int] | None:
        """Called when a request is received. Should return the response data or None if not handled."""
        if not self._connected:
            raise RuntimeError("Client not connected. Call connect() or start() first.")

        async def _on_request():
            result = await self.rear_light.onRequest(request)
            if len(result.payload) == 0:        # TODO: should be handled by null return
                return None
            return list(result.payload)
        
        return self._call_async(_on_request())

    def on_request_complete(self, request: int, data: List[int]):
        if not self._connected:
            raise RuntimeError("Client not connected. Call connect() or start() first.")
        
        async def _on_request_complete():
            # Convert list of ints to bytes if needed
            payload = bytes(data) if isinstance(data, list) else data
            await self.rear_light.onRequestComplete(request, payload)

        self._call_async(_on_request_complete())

    def on_error(self, request: int, error_type: str):
        pass
    
    def has_reset_request(self):
        """Check if there's a reset request (blocking)."""
        if not self._connected:
            raise RuntimeError("Client not connected. Call connect() or start() first.")
        
        async def _has_reset():
            result = await self.rear_light.hasResetRequest()
            return result.hasRequest
        
        return self._call_async(_has_reset())
    
    def has_sleep_request(self):
        """Check if there's a sleep request (blocking)."""
        if not self._connected:
            raise RuntimeError("Client not connected. Call connect() or start() first.")
        
        async def _has_sleep():
            result = await self.rear_light.hasSleepRequest()
            return result.hasRequest
        
        return self._call_async(_has_sleep())
    
    def destroy(self):
        """Destroy the rear light and close the connection."""
        if self._connected:
            try:
                async def _destroy():
                    await self.rear_light.destroy()
                
                self._call_async(_destroy())
            except Exception:
                pass  # Ignore errors during cleanup
            finally:
                self._connected = False
                self.client = None
                self.rear_light = None
                
                # Stop the event loop
                if self._loop:
                    self._loop.call_soon_threadsafe(self._loop.stop)
                    if self._thread:
                        self._thread.join(timeout=2.0)
                    self._loop = None
                    self._thread = None
