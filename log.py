from datetime import datetime

class Log():
    def __init__(self, origin):
        self.origin = origin
        
    def _log(self, level, message):
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S:%f")
        with open('logs/debug.log', 'a', encoding='utf-8') as f:
            f.write(f"{date:29} {f'[{level}]':10} {f'<{self.origin}>':30} {message}\n")
        
    def debug(self, message):
        self._log('DEBUG', message)
    
    def info(self, message):
        self._log('INFO', message)