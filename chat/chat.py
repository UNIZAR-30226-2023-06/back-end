# Read to understand: https://fastapi.tiangolo.com/advanced/websockets/
from typing import List, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

import time
import json

app = FastAPI()

origins = [
  "*" # reacts'
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

msg_type = str | dict[str, Any]

class FIFOQueue:
  def __init__(self, n: int):
    if (n <= 0):
      raise ValueError("n tiene que ser > 0")

    self.n = n
    self.queue = []

  def put(self, item: Any):
    self.queue.append(item)
    if (len(self.queue) > self.n):
      self.queue = self.queue[1:]

class Room:
  def __init__(self, save_last: None | int = None):
    self.msgs = FIFOQueue(save_last) if save_last else None
    self.active_connections: List[WebSocket] = []
  
  def add_msg(self, msg: msg_type):
    if self.msgs:
      self.msgs.put(msg)
    
  def get_msgs(self):
    if not self.msgs:
      return []
    return list(self.msgs.queue)
  
  async def connect(self, websocket: WebSocket):
    await websocket.accept()
    self.active_connections.append(websocket)

  def disconnect(self, websocket: WebSocket):
    self.active_connections.remove(websocket)

  async def send_personal_message(self, message: msg_type, websocket: WebSocket, store: bool = True):
    if store:
      self.add_msg(message)

    if isinstance(message, str):
      await websocket.send_text(message)
    else:
      await websocket.send_json(message)

  async def broadcast(self, message: msg_type, store: bool = True):
    if store:
      self.add_msg(message)

    for connection in self.active_connections:
      if isinstance(message, str):
        await connection.send_text(message)
      else:
        await connection.send_json(message)

class ConnectionManager:
  # TODO: Maybe add garbage collector?
  def __init__(self, save_last: None | int = None):
    self.save_last = save_last
    self.rooms: dict[str, Room] = {}
  
  async def connect(self, room: str, websocket: WebSocket) -> Room:
    if room not in self.rooms:
      self.rooms[room] = Room(self.save_last)
    
    await self.rooms[room].connect(websocket)
    return self.rooms[room]


def is_json(msg: str):
  try:
    return json.loads(msg)
  except ValueError as e:
    return None
 

manager = ConnectionManager(5)
# manager = ConnectionManager()

####### PARTE FRONT-END PARA TESTS #######
# Esto junto con test.html se puede eliminar

from fastapi.responses import HTMLResponse
with open("./test.html", "r") as f:
  html = f.read()

@app.get("/room/{room_id}")
async def get(room_id: str):
  room_html = html.replace("__ROOMID__", room_id)
  return HTMLResponse(room_html)

####### END PARTE FRONT-END PARA TESTS #######

# core
@app.websocket("/chat/{room_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str):
  room = await manager.connect(room_id, websocket)
  try:
    while True:
      msg = await websocket.receive_text()

      if (option := is_json(msg)):
        if option["sync"] == True:
          if ((msgs := room.get_msgs()) != []):
            print(msgs)
            await room.send_personal_message(
              {"sync": msgs}, websocket, store=False)
        continue

      if msg == "":
        continue

      # await room.send_personal_message(f"You wrote: {data}", websocket)
      # await room.send_personal_message({"data": f"You wrote: {data}"}, websocket)
      await room.broadcast({"time": time.time(), "username":username, "msg": msg})
  except WebSocketDisconnect:
    room.disconnect(websocket)
    await room.broadcast({"time": time.time(), "username":username, "msg": "Left the chat"}, store=False)
