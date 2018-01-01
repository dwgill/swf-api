import * as _ from 'lodash';
import { parseUserProfileUrl, InvalidUserID, SteamIDUserID, VanityUserID } from './parseUserProfileUrl';

const steamid_re = /^[0-9]+$/;
const vanity_re  = /^[0-9a-zA-Z-_]+$/;

const parseUserIdentifiers = (users: string[]): {
    steamids: string[],
    vanities: string[],
    invalids: string[],
} => {
    const [users_steamids, users_non_steamids] = _.partition(users, val => steamid_re.test(val));
    const [users_vanities, users_other] = _.partition(users_non_steamids, val => vanity_re.test(val));
    const [users_url, users_invalid] = _(users_other)
        .map(val => val.replace(/^https?:\/\//, ''))
        .map(val => val.replace(/\/$/, ''))
        .partition(val => val.startsWith('steamcommunity.com/'))
        .value();

    const [parsed_urls, invalid_urls] = _(users_url)
        .map(parseUserProfileUrl)
        .partition(({kind}) => kind !== 'invalid')
        .value();

    const all_invalids = _(invalid_urls as InvalidUserID[])
        .map(({value}) => value)
        .concat(users_invalid)
        .value();

    const [parsed_steamids, parsed_vanities] = _(parsed_urls as (SteamIDUserID | VanityUserID)[])
        .partition(({kind}) => kind == 'steamid')
        .value();

    const all_steamids = _(parsed_steamids as SteamIDUserID[])
        .map(({id}) => id)
        .concat(users_steamids)
        .value();

    const all_vanities = _(parsed_vanities as VanityUserID[])
        .map(({id}) => id)
        .concat(users_vanities)
        .value();

    return {
        steamids: all_steamids,
        vanities: all_vanities,
        invalids: all_invalids,
    };
};

export default parseUserIdentifiers;