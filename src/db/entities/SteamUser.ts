import { Entity, Column, PrimaryColumn, ManyToMany, JoinTable } from 'typeorm';
import SteamGame from './SteamGame';

@Entity()
export default class SteamUser {
    @PrimaryColumn()
    steamid: number;

    @Column()
    realName: string;

    @Column()
    userName: string;

    @Column({ nullable: true })
    vanity: string;

    @Column()
    avatarUrl: string;

    @Column()
    profileUrl: string;

    @ManyToMany(type => SteamGame, game => game.owners)
    @JoinTable()
    games: SteamGame[];
}
