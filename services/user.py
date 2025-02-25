import models
import uuid
import hashlib
import database as db


def create_user(userauth: models.UserAuth) -> int:
    salt = str(uuid.uuid4())
    hash_object = hashlib.sha256(str(userauth.password+salt).encode('utf-8'))
    hashed_password = str(hash_object.hexdigest())
    user_id = db.user.insert(userauth, hashed_password, salt)
    return user_id


def get_user_by_credentials(userlogin: models.UserLogin) -> models.UserInfo:
    res = db.user.check_login(userlogin.login)
    if len(res) == 0:
            raise models.LoginNotExists("login doesn't exist")
    (hash_password_true, salt, user_id) = res[0]
    hash_object = hashlib.sha256(str(userlogin.password+salt).encode('utf-8'))
    hashed_password = str(hash_object.hexdigest())
    if hashed_password != hash_password_true:
        raise models.IncorrectPassword("password is not correct")
    return get_user_info(user_id)


def get_user_info(user_id: int) -> models.UserInfo:
    user_info_model = db.user.get_info(user_id)
    if not user_info_model:
        raise models.UserNotExists('This user_id doesn''t exists')
    return user_info_model