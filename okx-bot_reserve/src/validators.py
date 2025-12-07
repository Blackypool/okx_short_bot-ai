import logging

class Validators:
    @staticmethod
    def validate_price(price: float) -> bool:
        return price > 0
    
    @staticmethod
    def validate_size(size: float, min_size: float = 0.001) -> bool:
        return size >= min_size and size <= 1000
    
    @staticmethod
    def validate_rr(rr: float, min_rr: float = 4.0) -> bool:
        return rr >= min_rr
    
    @staticmethod
    def validate_leverage(leverage: int) -> bool:
        return 1 <= leverage <= 125
