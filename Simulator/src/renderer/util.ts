// export const getFileNameFromPath = (filePath: string) => {
//     return filePath.replace(/^.*(\\|\/|:)/, '');
// }

import { remote } from 'electron';
import { getLocalStorage, LocalStorageKey, setLocalStorage } from "./store"

export const getPython3 = () => {
    return (getLocalStorage(LocalStorageKey.PythonPath) ?? `python3`);
}

export const setPython3 = (path: string) => {
    if (setLocalStorage(LocalStorageKey.PythonPath, path)) {
        return true;
    }
    throw new Error('Unable to set Python path');
}

export const getInterpolatory = () => {
    return (getLocalStorage(LocalStorageKey.InterpolatoryPath) ?? `C:\\Users\\lhlee\\Documents\\Interpolatory\\Simulator\\src\\python\\main.py`);
}

export const setInterpolatory = (path: string) => {
    if (setLocalStorage(LocalStorageKey.InterpolatoryPath, path)) {
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