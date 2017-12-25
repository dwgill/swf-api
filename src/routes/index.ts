import { Middleware } from 'koa';
import * as Router from 'koa-router';
import * as compose from 'koa-compose';

import helloWorld from '../middleware/helloWorld';

export default (): Middleware => {
    const router = new Router();

    router.get('/', helloWorld());
    
    return compose([
        router.routes(),
        router.allowedMethods(),
    ]);
};
