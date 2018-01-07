import { Entity, Column, PrimaryColumn, ManyToMany, JoinTable, CreateDateColumn } from 'typeorm';
import SteamGame from './SteamGame';

@Entity()
export default class SteamUser {
    @PrimaryColumn()
    steamid: number;

    @Column({
        nullable: true,
        type: 'text',
    })
    realName: string;

    @Column({
        type: 'text',
    })
    userName: string;

    @Column({ nullable: true })
    vanity: string;

    @Column({
        nullable: true,
        type: 'text',
    })
    avatarUrl: string;

    @Column({
        type: 'text',
    })
    profileUrl: string;

    @ManyToMany(type => SteamGame, game => game.owners)
    @JoinTable()
    games: SteamGame[];

    @CreateDateColumn()
    createdDate: Date;
    
}
