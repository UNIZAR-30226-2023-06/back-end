from logica_juego.constants import TradeState

class Trade:
    def __init__(self, sender: int, reciever: int, resource1: list[int], resource2: list[int]):
        self.sender = sender
        self.reciever = reciever
        self.resource1 = resource1 # [clay, wood, sheep, stone, wheat]
        self.resource2 = resource2 # [clay, wood, sheep, stone, wheat]
        self.accepted: TradeState = TradeState.TRADE_OFFERED

    def accept(self):
        self.accepted = TradeState.TRADE_ACCEPTED
    
    def decline(self):
        self.accepted = TradeState.TRADE_REJECTED
        
