"""Utlities for the Electrolux Status platform."""

from pyelectroluxocp.oneAppApi import OneAppApi


class pyelectroluxconnect_util:
    """Electrolux Status utlities class."""

    @staticmethod
    def get_session(username, password, client_session, language="eng") -> OneAppApi:
        """Return OneAppApi object."""
        return OneAppApi(username, password, client_session)
