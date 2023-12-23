import express, { Application } from 'express';
import { setupWsRoutes } from '@/websocket-service';

export function createServer(): Application {
    const app = express();
    setupWsRoutes(app);
    return app;
}

const app = createServer();

const port = 3000;

console.log(`Starting server on port ${port}`)
app.listen(port)
