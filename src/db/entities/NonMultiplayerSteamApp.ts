import { Entity, PrimaryColumn } from 'typeorm';

@Entity()
export default class NonMultiplayerSteamApp {
    @PrimaryColumn()
    appid: number;
}