from datetime import datetime
import os

class Log():
    def __init__(self, origin):
        self.origin = origin
        debug_path = "logs/debug.log"
        trace_path = "logs/trace.log"
        os.makedirs(os.path.dirname(debug_path), exist_ok=True)
        os.makedirs(os.path.dirname(trace_path), exist_ok=True)
        
        
    def _log(self, level, message):
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S:%f")
        with open('logs/debug.log', 'a', encoding='utf-8') as f, open('logs/trace.log', 'a', encoding='utf-8') as f2:
            # COMMENT THIS LINE TO DISABLE TRACE LOGGING
            f2.write(f"{date:29} {f'[{level}]':10} {f'<{self.origin}>':30} {message}\n")
            
            # COMMENT THE FOLLOWING TWO LINES TO DISABLE LOGGING ALTOGETHER
            if level != 'TRACE':
                f.write(f"{date:29} {f'[{level}]':10} {f'<{self.origin}>':30} {message}\n")
        
    def debug(self, message):
        self._log('DEBUG', message)
    
    def info(self, message):
        self._log('INFO', message)
        
    def warn(self, message):
        self._log('WARN', message)
        
    def trace(self, message):
        self._log('TRACE', message)