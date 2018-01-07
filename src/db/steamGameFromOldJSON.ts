import SteamGame from './entities/SteamGame';

const steamGameFromOldJSON = ({
    appid,
    developer,
    free,
    genres,
    global_owners,
    image_url,
    is_game,
    multiplayer,
    name,
    platforms,
    price,
    publisher,
    stale_date,
    store_page_url,
    tags,
}): SteamGame => {
    if (!is_game || !parseInt(multiplayer)) {
        return null;
    }
    const newGame = new SteamGame();

    newGame.appid = parseInt(appid);
    newGame.name = name;
    newGame.imageUrl = image_url;
    newGame.platforms = (platforms as string || '').split(';');
    newGame.tags = (tags as string || '').split(';'); 
    newGame.genres = (genres as string || '').split(';');
    newGame.numGlobalOwners = parseInt(global_owners);
    newGame.developer = developer;
    newGame.publisher = publisher;
    newGame.storePageUrl = store_page_url;
    newGame.free = !!parseInt(free);
    newGame.price = !price ? null : parseInt(price); 

    return newGame;
}

export default steamGameFromOldJSON;