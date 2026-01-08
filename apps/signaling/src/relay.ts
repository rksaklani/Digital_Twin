import { WebSocket } from 'ws';
import { Room } from './rooms';

export function relayMessage(room: Room, senderId: string, message: any): void {
  // Relay to all other clients in the room
  let relayed = 0;
  room.clients.forEach((client, clientId) => {
    if (clientId !== senderId && client.readyState === WebSocket.OPEN) {
      try {
        client.send(JSON.stringify({
          ...message,
          from: senderId,
        }));
        relayed++;
      } catch (error) {
        console.error(`[Relay] Error sending to client ${clientId}:`, error);
      }
    }
  });
  
  if (relayed > 0) {
    console.log(`[Relay] Relayed ${message.type} from ${senderId} to ${relayed} client(s)`);
  }
}

