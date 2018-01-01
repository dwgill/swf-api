import { Entity, PrimaryColumn } from 'typeorm';

@Entity()
export default class NonGameApp {
    @PrimaryColumn()
    appid: number;
}