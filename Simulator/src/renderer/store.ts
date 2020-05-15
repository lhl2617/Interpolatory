// localStorage interface

export enum LocalStorageKey {
    PythonPath = "PythonPath"
}


export const getLocalStorage = (key: LocalStorageKey) => {
    return window.localStorage.getItem(key);
}

export const setLocalStorage = (key: LocalStorageKey, value: string) => {
    try {
        window.localStorage.setItem(key, value);
    }
    catch (err) {
        console.error(err);
        return false;
    }
    return true;
}