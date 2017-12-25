import { IMiddleware } from 'koa-router';
import * as compose from 'koa-compose';
import * as _ from 'lodash';
import { parseUserProfileUrl, InvalidUserID, SteamIDUserID, VanityUserID } from '../util/parseUserProfileUrl';

const steamid_re = /^[0-9]+$/;
const vanity_re  = /^[0-9a-zA-Z-_]+$/;

const parseUserIds = (): IMiddleware => async (ctx, next) => {
    const users: string[] = [].concat(ctx.query.user)
        .filter(usrVal => typeof usrVal === 'string' && usrVal.length > 0);
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

    const total_invalid_users = _(invalid_urls as InvalidUserID[])
        .map(({value}) => value)
        .concat(users_invalid)
        .value();

    ctx.assert(total_invalid_users.length === 0, 422, `invalid users ${total_invalid_users}`);

    const [parsed_steamids, parsed_vanities] = _(parsed_urls as (SteamIDUserID | VanityUserID)[])
        .partition(({kind}) => kind == 'steamid')
        .value();

    ctx.steamids = _(parsed_steamids as SteamIDUserID[])
        .map(({id}) => id)
        .concat(users_steamids)
        .value();

    ctx.vanities = _(parsed_vanities as VanityUserID[])
        .map(({id}) => id)
        .concat(users_vanities)
        .value();

    await next();
};

export default parseUserIds;