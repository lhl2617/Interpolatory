// export const getFileNameFromPath = (filePath: string) => {
//     return filePath.replace(/^.*(\\|\/|:)/, '');
// }

import * as cp from 'child_process';
import * as path from 'path';
import { remote } from 'electron';
import { getLocalStorage, LocalStorageKey, setLocalStorage } from "./store"

type ValidatorStatus = `success` | `error` | `warning`;
export type ValidatorObj = { status: ValidatorStatus; help: string };

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

// get interpolation modes
export const getInterpolationModesFromProcess = async () => {
    return new Promise<string[]>((resolve, reject) => {

        const python3 = getPython3();
        const binName = getInterpolatory();

        const args = [binName, `-if`];
        const proc = cp.spawn(python3, args)


        let stdoutData = ``;
        let stderrData = ``;

        proc.stdout.on('data', (data) => {
            // console.log(`Gotten stdout: ${data}`);
            stdoutData = data;
        })

        proc.stderr.on('data', (data) => {
            stderrData += data.toString();
        })

        proc.on('close', (code) => {
            if (code !== 0) {
                reject(new Error('Unable to get available interpolation modes'));
                console.error(`Can't get interpolation modes... exited with ${code}`)
            }
            else {
                const ret: string[] = JSON.parse(stdoutData);
                resolve(ret);
            }
        })
    })

}