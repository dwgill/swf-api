import { Middleware } from 'koa';
import * as Router from 'koa-router';
import * as compose from 'koa-compose';
import parseUserIds from '../middleware/parseUserIds';

const index = (): Router.IMiddleware => compose([
    parseUserIds(),
    async (ctx, next) => {
        ctx.body = {
            steamids: ctx.inputSteamids,
            vanities: ctx.inputVanities,
        }
    },
])

export default (): Middleware => {
    const router = new Router();

    router.get('/', index());
    
    return compose([
        router.routes(),
        router.allowedMethods(),
    ]);
};
