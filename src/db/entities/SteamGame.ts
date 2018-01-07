import { Entity, Column, PrimaryColumn, ManyToMany, UpdateDateColumn, CreateDateColumn } from 'typeorm';
import { transformer as stringArrayTransformer } from '../../util/serializeStringArray';
import SteamUser from './SteamUser';


@Entity()
export default class SteamGame {
    @PrimaryColumn()
    appid: number;
    
    @Column({ type: 'text' })
    name: string;

    @Column({
        nullable: true,
        type: 'text',
    })
    imageUrl: string;

    @Column({
        nullable: true,
        type: 'varchar',
        transformer: stringArrayTransformer,
    })
    platforms: string[];

    @Column({
        nullable: true,
        type: 'text',
        transformer: stringArrayTransformer,
    })
    tags: string[];

    @Column({
        nullable: true,
        type: 'text',
        transformer: stringArrayTransformer,
    })
    genres: string[];

    @Column()
    numGlobalOwners: number;

    @Column({
        nullable: true,
        type: 'text',
    })
    developer: string;
    
    @Column({
        nullable: true,
        type: 'text',
    })
    publisher: string;

    @Column({
        nullable: true,
        type: 'text',
    })
    storePageUrl: string;

    @Column()
    free: boolean;

    @Column({ nullable: true })
    price: number;

    @ManyToMany(type => SteamUser, user => user.games)
    owners: SteamUser[];

    @UpdateDateColumn()
    updatedDate: Date;

    @CreateDateColumn()
    createdDate: Date;
}