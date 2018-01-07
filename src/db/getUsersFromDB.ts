import { getRepository } from 'typeorm';
import SteamUser from './entities/SteamUser';
import SteamGame from './entities/SteamGame';
import sqlSet from '../util/sqlSet';

interface args {
    vanities: string[],
    steamids: number[],
}

const getUsersFromDB = async ({ vanities, steamids }: args) => {
    const steam_user_repo = await getRepository(SteamUser);

    const users = await steam_user_repo.createQueryBuilder('user')
        .leftJoinAndSelect('user.games', 'game')
        .where('user.vanity in :vanities', { vanities: sqlSet(vanities) })
        .orWhereInIds(steamids)
        .getMany();

    return users;
}

export default getUsersFromDB;