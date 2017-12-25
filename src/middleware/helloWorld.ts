import { IMiddleware } from 'koa-router';

export default (): IMiddleware => async (ctx, next) => {
    ctx.body = {
        status: 'success',
        result: 'hello world',
    };
    await next();
};