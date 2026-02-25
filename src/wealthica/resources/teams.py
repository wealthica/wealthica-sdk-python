"""
Teams Resource.

Teams represent your Wealthica application and its configuration.
"""

from typing import Any, Dict

from wealthica.resources.base import BaseResource


class Teams(BaseResource):
    """
    Teams API resource.

    This resource allows you to retrieve information about your Wealthica
    team/application configuration.

    Example:
        ```python
        team = wealthica.teams.info()
        print(f"Team: {team['name']}")
        ```
    """

    def info(self) -> Dict[str, Any]:
        """
        Get information about your Wealthica team/application.

        Returns:
            Team information including name, features, and settings.

        Example:
            ```python
            team = wealthica.teams.info()
            print(f"Team: {team['name']}")
            ```
        """
        return self._get(f"/teams/info?client_id={self.client.client_id}")
