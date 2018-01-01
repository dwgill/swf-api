import { Entity, Column, PrimaryColumn, ManyToMany } from 'typeorm';
import { transformer as stringArrayTransformer } from '../../util/serializeStringArray';
import SteamUser from './SteamUser';


@Entity()
export default class SteamGame {
    @PrimaryColumn()
    appid: number;
    
    @Column()
    name: string;

    @Column({ nullable: true })
    imageUrl: string;

    @Column({
        nullable: true,
        type: 'varchar',
        transformer: stringArrayTransformer,
    })
    platforms: string[];

    @Column({
        nullable: true,
        type: 'varchar',
        transformer: stringArrayTransformer,
    })
    tags: string[];

    @Column({
        nullable: true,
        type: 'varchar',
        transformer: stringArrayTransformer,
    })
    genres: string[];

    @Column()
    numGlobalOwners: number;

    @Column({ nullable: true })
    developer: string;
    
    @Column({ nullable: true })
    publisher: string;

    @Column({ nullable: true })
    storePageUrl: string;

    @Column()
    free: boolean;

    @Column({ nullable: true })
    price: number;

    @Column({ nullable: true })
    multiplayer: boolean;

    @ManyToMany(type => SteamUser, user => user.games)
    owners: SteamUser[];
}