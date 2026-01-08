import { IncomingMessage, ServerResponse } from 'http';
import { getRoomStats } from './rooms';

export function healthCheck(req: IncomingMessage, res: ServerResponse): void {
  const stats = getRoomStats();
  
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    status: 'ok',
    timestamp: new Date().toISOString(),
    rooms: stats,
  }));
}

