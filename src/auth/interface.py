from abc import ABCMeta


class AuthorizationInterface(object, metaclass=ABCMeta):
    def authorized_in_system(
            self,
            imei: str
    ) -> bool:
        """
        method to check unit in the system for message with login packet
        for connection with imei in all message need use another method
        :param imei: imei IoT device
        :return: bool (True - unit in system, False - unit not in system)
        """

    def check_password(
            self,
            imei: str,
            password: str
    ) -> bool:
        """
        Check password unit, if exist on system
        :param imei: imei IoT device
        :param password: check passwort in client storage
        :return: bool (True - if password is valid, False)
        """
