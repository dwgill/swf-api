import * as fs from 'fs';
import * as Koa from 'koa';
import * as bodyParser from 'koa-bodyparser';
import "reflect-metadata";
import {createConnection} from 'typeorm';
import routes from './routes';
import SteamUser from './db/entities/SteamUser';
import SteamGame from './db/entities/SteamGame';
import NonMultiplayerSteamApp from './db/entities/NonMultiplayerSteamApp';

console.log('Initializing TypeORM connection.');
createConnection ({
   type: "mysql",
   host: "localhost",
   port: 3306,
   username: "swf",
   password: "password",
   database: "swf",
   entities: [
       SteamUser,
       SteamGame,
       NonMultiplayerSteamApp
   ],
   synchronize: true,
   logging: false,
   charset: 'utf8mb4',
}).then(async connection => {
    console.log('TypeORM connection established.')

    const app = new Koa();
    app.use(bodyParser());
    app.use(routes());

    const port = process.env.PORT || '7000';
    app.listen(port);
}).catch(err => console.log("TypeORM connection error: ", err));
