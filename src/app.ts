import * as fs from 'fs';
import * as Koa from 'koa';
import * as bodyParser from 'koa-bodyparser';
import routes from './routes';

const app = new Koa();

app.use(bodyParser());
app.use(routes());

const port = process.env.PORT || '7000';
app.listen(port);