// export const getFileNameFromPath = (filePath: string) => {
//     return filePath.replace(/^.*(\\|\/|:)/, '');
// }

import * as path from 'path';
import { remote } from 'electron';
import { getLocalStorage, LocalStorageKey, setLocalStorage } from "./store"

export const getPython3 = () => {
    return (getLocalStorage(LocalStorageKey.PythonPath) ?? `python3`);
}

export const setPython3 = (filePath: string) => {
    if (setLocalStorage(LocalStorageKey.PythonPath, filePath)) {
        return true;
    }
    throw new Error('Unable to set Python path');
}

export const getInterpolatory = () => {
    return (getLocalStorage(LocalStorageKey.InterpolatoryPath) ?? path.join(process.resourcesPath, `python`, `main.py`));
}

export const setInterpolatory = (filePath: string) => {
    if (setLocalStorage(LocalStorageKey.InterpolatoryPath, filePath)) {
        return true;
    }
    throw new Error('Unable to set Interpolatory path');
}

export const closeApp = () => {
    const w = remote.getCurrentWindow();
    w.close();
}

export const minApp = () => {
    const w = remote.getCurrentWindow();
    w.minimize();
}

export const maxApp = () => {
    const w = remote.getCurrentWindow();
    if (!w.isMaximized()) {
        w.maximize();
    } else {
        w.unmaximize();
    }
}

export const reloadApp = () => {
    const w = remote.getCurrentWindow();
    w.reload();
}