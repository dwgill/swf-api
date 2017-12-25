import * as _ from 'lodash';

export interface SteamIDUserID {
    kind: 'steamid',
    id: string,
}

const steamid = (id: string): SteamIDUserID => ({
    kind: 'steamid',
    id,
});

export interface VanityUserID {
    kind: 'vanity',
    id: string,
}

const vanity = (id: string): VanityUserID => ({
    kind: 'vanity',
    id,
});

export interface InvalidUserID {
    kind: 'invalid',
    value: string,
}

const invalid = (value: string): InvalidUserID => ({
    kind: 'invalid',
    value,
});

type ParsedUserProfileUrl = SteamIDUserID | VanityUserID | InvalidUserID;

const profileUrlIsVanity = (profileUrl: string) => /\/id\//.test(profileUrl);

export const parseUserProfileUrl = (url: string): ParsedUserProfileUrl => {
    if (!/\/(id|profiles)\//.test(url)) {
        return invalid(url);
    }

    const stripped_url = url.replace(/^https?:\/\//, '').replace(/\/$/, '');
    const [, profile_or_id, user_id] = _.split(stripped_url, '/');

    if (profile_or_id == 'id') {
        return vanity(user_id);
    } else if (profile_or_id == 'profiles') {
        return steamid(user_id);
    } else {
        return invalid(url);
    }
}

export default parseUserProfileUrl;