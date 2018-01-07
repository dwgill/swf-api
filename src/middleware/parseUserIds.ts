import { IMiddleware } from 'koa-router';
import * as compose from 'koa-compose';
import * as _ from 'lodash';
import { parseUserProfileUrl, InvalidUserID, SteamIDUserID, VanityUserID } from '../util/parseUserProfileUrl';
import parseUserIdentifiers from '../util/parseUserIdentifiers';

const steamid_re = /^[0-9]+$/;
const vanity_re  = /^[0-9a-zA-Z-_]+$/;

const parseUserIds = (): IMiddleware => async (ctx, next) => {
    const users: string[] = [].concat(ctx.query.user)
        .filter(usrVal => typeof usrVal === 'string' && usrVal.length > 0);

    const { steamids, vanities, invalids } = parseUserIdentifiers(users);
    
    ctx.assert(invalids.length === 0, 422, `invalid users ${invalids}`);

    ctx.inputSteamids = steamids;

    ctx.inputVanities = vanities;

    await next();
};

export default parseUserIds;