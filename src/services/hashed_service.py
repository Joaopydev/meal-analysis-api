import bcrypt

class HashedPasswordService:
    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(8)).decode("utf-8")
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password)