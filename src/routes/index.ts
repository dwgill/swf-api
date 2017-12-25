import { Middleware } from 'koa';
import * as Router from 'koa-router';
import * as compose from 'koa-compose';

import parseUserIds from '../middleware/parseUserIds';

export default (): Middleware => {
    const router = new Router();

    router.get('/',
        parseUserIds(),
        async (ctx, next) => {
            ctx.body = {
                steamids: ctx.steamids,
                vanities: ctx.vanities,
            }
        }
    );
    
    return compose([
        router.routes(),
        router.allowedMethods(),
    ]);
};
