import SteamUser from './entities/SteamUser';

const steamUserFromOldJSON = ({
    avatar_url,
    profile_url,
    realname,
    stale_date,
    steamid,
    username,
    vanityid,
}) => {
    const newUser = new SteamUser();

    newUser.steamid = parseInt(steamid);
    newUser.realName = realname || null;
    newUser.userName = username
    newUser.vanity = vanityid || null;
    newUser.avatarUrl = avatar_url || null;
    newUser.profileUrl = profile_url;

    return newUser;
}