import { Application } from 'express';
import expressWs, { Application as WsApplication } from 'express-ws';

export function setupWsRoutes(app: Application) {
    expressWs(app);
    const wsApp = app as WsApplication;
    wsApp.ws('/transcribe', function(ws, req) {
        ws.on('message', function(msg) {
            console.log('Got a message!!!', msg);
        });
    });
}
