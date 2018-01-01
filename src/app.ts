import * as fs from 'fs';
import * as Koa from 'koa';
import * as bodyParser from 'koa-bodyparser';
import "reflect-metadata";
import {createConnection} from 'typeorm';
import routes from './routes';
import SteamUser from './db/entities/SteamUser';
import SteamGame from './db/entities/SteamGame';

console.log('Initializing TypeORM connection.');
createConnection ({
   type: "mysql",
   host: "localhost",
   port: 3306,
   username: "root",
   password: "admin",
   database: "swf",
   entities: [
       SteamUser,
       SteamGame,
   ],
   synchronize: true,
   logging: false,
}).then(async connection => {
    console.log('TypeORM connection established.')

    const app = new Koa();
    app.use(bodyParser());
    app.use(routes());

    const port = process.env.PORT || '7000';
    app.listen(port);

}).catch(err => console.log("TypeORM connection error: ", err));
