Bun.serve({
    fetch(req, server) {
        if (server.upgrade(req)) {
            return;
        }
        return new Response('WS upgrade failed', { status: 500 });
    }, // upgrade logic
    websocket: {
      message(ws, message) {
        console.log('Got a message!', message);
      }, // a message is received
      open(ws) {}, // a socket is opened
      close(ws, code, message) {}, // a socket is closed
      drain(ws) {}, // the socket is ready to receive more data
    },
    port: 3000,
});
