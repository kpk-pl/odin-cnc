#!/usr/bin/etc python

import re
import types
import Queue

class Rule:
    def __init__(self, regexp, handler):
        self.regexp = regexp
        self.regex_c = re.compile(regexp)
        self.handler = handler
        
class Payload:
    def __init__(self, message, match, time=None):
        self.message = message
        self.match = match
        self.timestamp = time
        
class HandlerResult:
    def __init__(self, handler, match):
        self.handler = handler
        self.match = match

class MsgDispatcher:
    def __init__(self, prompt=None):
        self.dispatch_rules = []
        self.default_handler = lambda x: None
        self.all_handler = lambda x: None
        self.prompt = prompt
        self.lprompt = len(self.prompt) if self.prompt else None
 
    def dispatch(self, message):
        if self.prompt and len(message.payload) >= self.lprompt and message.payload[0:self.lprompt] == self.prompt:
            msg = message.payload[self.lprompt:]
        else:
            msg = message.payload
            
        if len(msg) > 0:           
            handlers = self.get_handlers(msg)
            for h in handlers:
                payload = Payload(msg, h.match, message.timestamp)
                if isinstance(h.handler, Queue.Queue):
                    h.handler.put(payload)
                else:
                    h.handler(payload)
                
    def get_handlers(self, message):
        handlers = []
        for rule in self.dispatch_rules:
            match = rule.regex_c.match(message)
            if match:
                handlers.append(HandlerResult(rule.handler, match))
        if len(handlers) == 0:
            handlers.append(HandlerResult(self.default_handler, None))
        if self.all_handler:
            handlers.append(HandlerResult(self.all_handler, None))
        return handlers

    def register(self, regex, function):
        self.dispatch_rules.append(Rule(re.compile(regex), function))

    def register_default(self, handler):
        self.default_handler = handler
        
    def register_all(self, handler):
        self.all_handler = handler
                 
if __name__ == '__main__':  
    pass