from src.auth.interface import AuthorizationInterface


class AbstractAuthorization(AuthorizationInterface):
    def authorized_in_system(
            self,
            imei: str
    ) -> bool:
        raise NotImplementedError(
            f"Method {self.__class__.__name__} not implemented"
        )

    def check_password(
            self,
            imei: str,
            password: str
    ) -> bool:
        return True
