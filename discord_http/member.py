from typing import Union, TYPE_CHECKING, Optional
from datetime import datetime, timedelta

from .asset import Asset
from .embeds import Embed
from .file import File
from .flag import Permissions, PublicFlags
from .guild import PartialGuild
from .mentions import AllowedMentions
from .object import PartialBase
from .response import ResponseType
from .role import PartialRole, Role
from .user import User, PartialUser
from .view import View
from . import utils

MISSING = utils.MISSING

if TYPE_CHECKING:
    from .message import Message
    from .channel import DMChannel
    from .http import DiscordAPI

__all__ = (
    "PartialMember",
    "Member",
    "ThreadMember",
)


class PartialMember(PartialBase):
    def __init__(self, *, state: "DiscordAPI", guild_id: int, user_id: int):
        super().__init__(id=int(user_id))
        self._state = state

        self._user = PartialUser(state=state, user_id=self.id)
        self.guild_id: int = int(guild_id)

    def __str__(self) -> str:
        return str(self.id)

    def __int__(self) -> int:
        return self.id

    def __repr__(self) -> str:
        return f"<PartialMember id={self.id} guild_id={self.guild_id}>"

    @property
    def guild(self) -> PartialGuild:
        """ `PartialGuild`: The guild of the member """
        return PartialGuild(state=self._state, guild_id=self.guild_id)

    async def fetch(self) -> "Member":
        """ `Fetch`: Fetches the member from the API """
        r = await self._state.query(
            "GET",
            f"/guilds/{self.guild_id}/members/{self.id}"
        )

        return Member(
            state=self._state,
            guild=self.guild,
            data=r.response
        )

    async def send(
        self,
        content: Optional[str] = MISSING,
        *,
        channel_id: Optional[int] = MISSING,
        embed: Optional[Embed] = MISSING,
        embeds: Optional[list[Embed]] = MISSING,
        file: Optional[File] = MISSING,
        files: Optional[list[File]] = MISSING,
        view: Optional[View] = MISSING,
        tts: Optional[bool] = False,
        type: Union[ResponseType, int] = 4,
        allowed_mentions: Optional[AllowedMentions] = MISSING,
    ) -> "Message":
        """
        Send a message to the user

        Parameters
        ----------
        content: `Optional[str]`
            Content of the message
        channel_id: `Optional[int]`
            Channel ID of the user, leave empty to create a DM
        embed: `Optional[Embed]`
            Embed of the message
        embeds: `Optional[list[Embed]]`
            Embeds of the message
        file: `Optional[File]`
            File of the message
        files: `Optional[Union[list[File], File]]`
            Files of the message
        view: `Optional[View]`
            Components to add to the message
        tts: `Optional[bool]`
            Whether the message should be sent as TTS
        type: `Optional[ResponseType]`
            Type of the message
        allowed_mentions: `Optional[AllowedMentions]`
            Allowed mentions of the message

        Returns
        -------
        `Message`
            The message sent
        """
        return await self._user.send(
            content,
            channel_id=channel_id,
            embed=embed,
            embeds=embeds,
            file=file,
            files=files,
            view=view,
            tts=tts,
            type=type,
            allowed_mentions=allowed_mentions
        )

    async def create_dm(self) -> "DMChannel":
        """ `DMChannel`: Create a DM channel with the user """
        return await self._user.create_dm()

    async def ban(
        self,
        *,
        reason: Optional[str] = None,
        delete_message_days: Optional[int] = 0,
        delete_message_seconds: Optional[int] = 0,
    ) -> None:
        """
        Ban the user

        Parameters
        ----------
        reason: `Optional[str]`
            The reason for banning the user
        delete_message_days: `Optional[int]`
            How many days of messages to delete
        delete_message_seconds: `Optional[int]`
            How many seconds of messages to delete

        Raises
        ------
        `ValueError`
            - If delete_message_days and delete_message_seconds are both specified
            - If delete_message_days is not between 0 and 7
            - If delete_message_seconds is not between 0 and 604,800
        """
        payload = {}
        if delete_message_days and delete_message_seconds:
            raise ValueError("Cannot specify both delete_message_days and delete_message_seconds")

        if delete_message_days:
            if delete_message_days not in range(0, 8):
                raise ValueError("delete_message_days must be between 0 and 7")
            payload["delete_message_seconds"] = int(timedelta(days=delete_message_days).total_seconds())

        if delete_message_seconds:
            if delete_message_seconds not in range(0, 604801):
                raise ValueError("delete_message_seconds must be between 0 and 604,800")
            payload["delete_message_seconds"] = delete_message_seconds

        await self._state.query(
            "PUT",
            f"/guilds/{self.guild_id}/bans/{self.id}",
            reason=reason,
            json=payload
        )

    async def unban(self, *, reason: Optional[str] = None) -> None:
        """
        Unban the user

        Parameters
        ----------
        reason: `Optional[str]`
            The reason for unbanning the user
        """
        await self._state.query(
            "DELETE",
            f"/guilds/{self.guild_id}/bans/{self.id}",
            reason=reason,
            res_method="text"
        )

    async def kick(self, *, reason: Optional[str] = None) -> None:
        """
        Kick the user

        Parameters
        ----------
        reason: `Optional[str]`
            The reason for kicking the user
        """
        await self._state.query(
            "DELETE",
            f"/guilds/{self.guild_id}/members/{self.id}",
            reason=reason,
            res_method="text"
        )

    async def edit(
        self,
        *,
        nick: Optional[str] = MISSING,
        roles: Union[list[Union[PartialRole, Role, int]], None] = MISSING,
        mute: Optional[bool] = MISSING,
        deaf: Optional[bool] = MISSING,
        communication_disabled_until: Union[timedelta, datetime, int, None] = MISSING,
        channel_id: Optional[int] = MISSING,
    ) -> "Member":
        """
        Edit the member

        Parameters
        ----------
        nick: `Optional[str]`
            The new nickname of the member
        roles: `Optional[list[Union[PartialRole, Role, int]]]`
            Roles to make the member have
        mute: `Optional[bool]`
            Whether to mute the member
        deaf: `Optional[bool]`
            Whether to deafen the member
        communication_disabled_until: `Optional[Union[timedelta, datetime, int]]`
            How long to disable communication for (timeout)
        channel_id: `Optional[int]`
            The channel ID to move the member to

        Returns
        -------
        `Member`
            The edited member

        Raises
        ------
        `TypeError`
            - If communication_disabled_until is not timedelta, datetime, or int
        """
        payload = {}

        if nick is not MISSING:
            payload["nick"] = nick
        if isinstance(roles, list) and roles is not MISSING:
            payload["roles"] = [
                role.id if isinstance(role, (PartialRole, Role)) else role
                for role in roles
            ]
        if mute is not MISSING:
            payload["mute"] = mute
        if deaf is not MISSING:
            payload["deaf"] = deaf
        if channel_id is not MISSING:
            payload["channel_id"] = channel_id
        if communication_disabled_until is not MISSING:
            _timeout_value = None
            _now = datetime.utcnow()

            match communication_disabled_until:
                case x if isinstance(x, timedelta):
                    _timeout_value = _now + x
                case x if isinstance(x, datetime):
                    _timeout_value = x
                case x if isinstance(x, int):
                    _timeout_value = _now + timedelta(seconds=x)
                case None:
                    _timeout_value = None
                case _:
                    raise TypeError(
                        "Invalid type for communication_disabled_until, "
                        "must be timedelta, datetime, int or NoneType "
                    )

            payload["communication_disabled_until"] = _timeout_value.isoformat()

        r = await self._state.query(
            "PATCH",
            f"/guilds/{self.guild_id}/members/{self.id}",
            json=payload
        )

        return Member(
            state=self._state,
            guild=self.guild,
            data=r.response
        )

    async def add_roles(
        self,
        *roles: Union[PartialRole, Role, int],
        reason: Optional[str] = None
    ) -> None:
        """
        Add roles to someone

        Parameters
        ----------
        *roles: `Union[PartialRole, Role, int]`
            Roles to add to the member
        reason: `Optional[str]`
            The reason for adding the roles

        Parameters
        ----------
        reason: `Optional[str]`
            The reason for adding the roles
        """
        for role in roles:
            if isinstance(role, (PartialRole, Role)):
                role = role.id

            await self._state.query(
                "PUT",
                f"/guilds/{self.guild_id}/members/{self.id}/roles/{role}",
                reason=reason
            )

    async def remove_roles(
        self,
        *roles: Union[PartialRole, Role, int],
        reason: Optional[str] = None
    ) -> None:
        """
        Remove roles from someone

        Parameters
        ----------
        reason: `Optional[str]`
            The reason for removing the roles
        """
        for role in roles:
            if isinstance(role, (PartialRole, Role)):
                role = role.id

            await self._state.query(
                "DELETE",
                f"/guilds/{self.guild_id}/members/{self.id}/roles/{role}",
                reason=reason
            )

    @property
    def mention(self) -> str:
        """ `str`: The mention of the member """
        return f"<@!{self.id}>"


class ThreadMember(PartialBase):
    def __init__(self, *, state: "DiscordAPI", data: dict):
        super().__init__(id=int(data["user_id"]))
        self._state = state

        self.flags: int = data["flags"]
        self.join_timestamp: datetime = utils.parse_time(data["join_timestamp"])

    def __str__(self) -> str:
        return str(self.id)

    def __int__(self) -> int:
        return self.id


class Member(PartialMember):
    def __init__(self, *, state: "DiscordAPI", guild: PartialGuild, data: dict):
        super().__init__(
            state=state,
            guild_id=guild.id,
            user_id=data["user"]["id"]
        )

        self._user = User(state=state, data=data["user"])

        self.avatar: Optional[Asset] = None

        self.flags: int = data["flags"]
        self.pending: bool = data.get("pending", False)
        self._raw_permissions: Optional[int] = utils.get_int(data, "permissions")
        self.nick: Optional[str] = data.get("nick", None)
        self.joined_at: datetime = utils.parse_time(data["joined_at"])
        self.roles: list[PartialRole] = [
            PartialRole(state=state, guild_id=self.guild.id, role_id=int(r))
            for r in data["roles"]
        ]

        self._from_data(data)

    def __str__(self) -> str:
        return str(self._user)

    def __repr__(self) -> str:
        return (
            f"<Member id={self.id} name='{self.name}' "
            f"global_name='{self._user.global_name}'>"
        )

    def _from_data(self, data: dict) -> None:
        has_avatar = data.get("avatar", None)
        if has_avatar:
            self.avatar = Asset._from_guild_avatar(
                self.guild.id, self.id, has_avatar
            )

    @property
    def resolved_permissions(self) -> Permissions:
        """
        `Optional[Permissions]` Returns permissions from an interaction,
        will be None if used in `Member.fetch()`
        """
        if self._raw_permissions is None:
            return Permissions(0)
        return Permissions(self._raw_permissions)

    @property
    def name(self) -> str:
        """ `str`: Returns the username of the member """
        return self._user.name

    @property
    def global_name(self) -> Optional[str]:
        """
        Gives the global display name of a member if available

        Returns
        -------
        `Optional[str]`
            Returns the global display name of a member if available, bots will return None
        """
        return self._user.global_name

    @property
    def discriminator(self) -> Optional[str]:
        """
        Gives the discriminator of the member if available

        Returns
        -------
        `Optional[str]`
            Discriminator of a user who has yet to convert or a bot account.
            If the user has converted to the new username, this will reutnr None
        """
        return self._user.discriminator

    @property
    def public_flags(self) -> PublicFlags:
        """ `int`: Returns the public flags of the member """
        return self._user.public_flags or PublicFlags(0)

    @property
    def banner(self) -> Optional[Asset]:
        """ `Optional[Asset]`: Returns the banner of the member if available """
        return self._user.banner

    @property
    def avatar_decoration(self) -> Optional[Asset]:
        """ `Optional[Asset]`: Returns the avatar decoration of the member """
        return self._user.avatar_decoration

    @property
    def display_name(self) -> str:
        """ `str`: Returns the display name of the member """
        return self.nick or self.global_name or self.name

    @property
    def display_avatar(self) -> Optional[Asset]:
        """ `Optional[Asset]`: Returns the display avatar of the member """
        return self.avatar or self._user.avatar

    @property
    def original_avatar(self) -> Optional[Asset]:
        """ `Optional[Asset]`: Shortcut for `User.original_avatar` """
        return self._user.original_avatar

    @property
    def original_banner(self) -> Optional[Asset]:
        """ `Optional[Asset]`: Shortcut for `User.original_banner` """
        return self._user.original_banner
