import { WebSocket } from 'ws';
import { relayMessage } from './relay';

interface Room {
  id: string;
  clients: Map<string, WebSocket>;
  createdAt: number;
}

const rooms = new Map<string, Room>();

function generateRoomId(): string {
  return `room_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function getOrCreateRoom(roomId?: string): Room {
  if (roomId && rooms.has(roomId)) {
    return rooms.get(roomId)!;
  }
  
  const newRoomId = roomId || generateRoomId();
  const room: Room = {
    id: newRoomId,
    clients: new Map(),
    createdAt: Date.now(),
  };
  rooms.set(newRoomId, room);
  return room;
}

function removeClientFromRoom(clientId: string, room: Room): void {
  room.clients.delete(clientId);
  if (room.clients.size === 0) {
    rooms.delete(room.id);
    console.log(`[Rooms] Room ${room.id} deleted (empty)`);
  }
}

export function handleConnection(ws: WebSocket): void {
  let clientId: string | null = null;
  let room: Room | null = null;

  ws.on('message', (data: Buffer) => {
    try {
      const message = JSON.parse(data.toString());
      
      switch (message.type) {
        case 'join':
          // Create or join room
          room = getOrCreateRoom(message.roomId);
          clientId = message.clientId || `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          room.clients.set(clientId, ws);
          
          console.log(`[Rooms] Client ${clientId} joined room ${room.id} (${room.clients.size} clients)`);
          
          // Send confirmation
          ws.send(JSON.stringify({
            type: 'joined',
            roomId: room.id,
            clientId: clientId,
            clientCount: room.clients.size,
          }));
          break;

        case 'offer':
        case 'answer':
        case 'ice-candidate':
          // Relay WebRTC signaling messages
          if (room) {
            relayMessage(room, clientId!, message);
          }
          break;

        case 'ping':
          ws.send(JSON.stringify({ type: 'pong' }));
          break;

        default:
          console.warn(`[Rooms] Unknown message type: ${message.type}`);
      }
    } catch (error) {
      console.error(`[Rooms] Error handling message:`, error);
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Invalid message format',
      }));
    }
  });

  ws.on('close', () => {
    if (room && clientId) {
      removeClientFromRoom(clientId, room);
      console.log(`[Rooms] Client ${clientId} disconnected from room ${room.id}`);
    }
  });

  ws.on('error', (error) => {
    console.error(`[Rooms] WebSocket error:`, error);
    if (room && clientId) {
      removeClientFromRoom(clientId, room);
    }
  });

  // Send welcome message
  ws.send(JSON.stringify({
    type: 'welcome',
    message: 'Connected to signaling server',
  }));
}

export function getRoomStats(): { roomCount: number; totalClients: number } {
  let totalClients = 0;
  rooms.forEach((room) => {
    totalClients += room.clients.size;
  });
  return {
    roomCount: rooms.size,
    totalClients,
  };
}

