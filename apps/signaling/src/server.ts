import { WebSocketServer, WebSocket } from 'ws';
import { createServer } from 'http';
import { handleConnection } from './rooms';
import { healthCheck } from './health';

const PORT = process.env.SIGNALING_PORT ? parseInt(process.env.SIGNALING_PORT) : 8080;
const HOST = process.env.SIGNALING_HOST || 'localhost';

const server = createServer((req, res) => {
  if (req.url === '/health') {
    healthCheck(req, res);
    return;
  }
  
  res.writeHead(404);
  res.end('Not found');
});

const wss = new WebSocketServer({ server });

wss.on('connection', (ws: WebSocket, req) => {
  console.log(`[Signaling] New connection from ${req.socket.remoteAddress}`);
  handleConnection(ws);
});

server.listen(PORT, HOST, () => {
  console.log(`[Signaling] Server listening on ws://${HOST}:${PORT}`);
  console.log(`[Signaling] Health check available at http://${HOST}:${PORT}/health`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('[Signaling] SIGTERM received, closing server...');
  wss.close(() => {
    server.close(() => {
      console.log('[Signaling] Server closed');
      process.exit(0);
    });
  });
});

