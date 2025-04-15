class NoNextNode(Exception):
    def __init__(self,msg="There is no more node in path",error_code=1001):
        self.title="NoNextNode"
        self.msg=msg
        self.error_code=error_code
        super().__init__(self.msg)
    
    def __str__(self):
        return f"[Error Code {self.error_code} {self.title}]{self.msg}"
    
class NoPathFound(Exception):
    def __init__(self,msg="There is no path found",error_code=1002):
        self.title="NoPathFound"
        self.msg=msg
        self.error_code=error_code
        super().__init__(self.msg)
    
    def __str__(self):
        return f"[Error Code {self.error_code} {self.title}]{self.msg}"