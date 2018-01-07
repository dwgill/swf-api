import NonMultiplayerSteamApp from './entities/NonMultiplayerSteamApp';

const nonGameAppFromOldJSON = (oldJSON: any): NonMultiplayerSteamApp => {
    const newNonGameApp = new NonMultiplayerSteamApp();
    newNonGameApp.appid = parseInt(oldJSON.appid as string);
    return newNonGameApp;
}

export default nonGameAppFromOldJSON;