// export const getFileNameFromPath = (filePath: string) => {
//     return filePath.replace(/^.*(\\|\/|:)/, '');
// }

import * as cp from 'child_process';
import * as path from 'path';
import * as md5 from 'md5';
import * as fs from 'fs';
import { remote } from 'electron';
import { getLocalStorage, LocalStorageKey, setLocalStorage } from "./store"

type ValidatorStatus = `success` | `error` | `warning`;
export type ValidatorObj = { status: ValidatorStatus; help: string };
export const defaultValidatorStatus: ValidatorObj = { status: `success`, help: `` };

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
export const getInterpolationModesFromProcess = () => {
    return new Promise<string[]>((resolve, reject) => {

        const python3 = getPython3();
        const binName = getInterpolatory();

        const args = [binName, `-il`];
        const proc = cp.spawn(python3, args)


        let stdoutData = ``;

        proc.stdout.on('data', (data) => {
            // console.log(`Gotten stdout: ${data}`);
            stdoutData = data;
        })

        proc.stdout.on(`end`, () => {
            const ret: string[] = JSON.parse(stdoutData);
            resolve(ret);
        });

        proc.on('close', (code) => {
            if (code !== 0) {
                reject(new Error('Unable to get available interpolation modes'));
                console.error(`Can't get interpolation modes... exited with ${code}`)
            }
        })
    })

}

// get a hashed file path for progress output
export const getProgressFilePath = (args: string[]) => {
    // concat time now and a random float for no collisions
    const rawString = args.join(``) + (new Date()).getTime().toString + Math.random().toString();
    const hash = md5(rawString);

    const filePath = path.join(remote.app.getPath(`temp`), `interpolatory_${hash}.txt`);

    return filePath;
}

export const processProgressFile = async (progressFilePath: string): Promise<string | undefined> => {

    if (fs.existsSync(progressFilePath)) {
        const progString = fs.readFileSync(progressFilePath).toString();
        if (progString.substr(0, 8) === `PROGRESS`) {
            return progString.substr(10);
        }
    }
    return undefined;
}

export const getPercentageFromProgressString = (s: string) => {
    return parseInt(s.substr(0, 3), 10);
}

export type IModeEnumType = { type: "enum", description: string, value: string, enum: string[], enumDescriptions: [] }
export type IModeNumberType = { type: "number", description: string, value: number }
export type InterpolationModeOptions = Record<string, IModeEnumType | IModeNumberType>
export type InterpolationMode = { name: string, description: string, options?: InterpolationModeOptions }
export type InterpolationModeSchema = Record<string, InterpolationMode>

/// from the py get the JSON binary
export const getInterpolationModeSchema = () => {
    return new Promise<InterpolationModeSchema>((resolve, reject) => {

        const python3 = getPython3();
        const binName = getInterpolatory();

        const args = [binName, `-schema`];
        const proc = cp.spawn(python3, args)


        let stdoutData = ``;

        proc.stdout.on('data', (data) => {
            // console.log(`Gotten stdout: ${data}`);
            stdoutData = data;
        })

        proc.stdout.on(`end`, () => {
            const ret: InterpolationModeSchema = JSON.parse(stdoutData);
            resolve(ret);
        });

        proc.on('close', (code) => {
            if (code !== 0) {
                reject(new Error('Unable to get available interpolation modes'));
                console.error(`Can't get interpolation modes... exited with ${code}`)
            }
        })
    })
}


export const snakeCaseToFirstWordCapitalised = (s: string) => {
    return s.split(`_`).map(
        w => {
            /// special words
            if (w === 'me' || w === 'mci') return w.toUpperCase();
            return w.substring(0, 1).toUpperCase() + w.substring(1)
        }
    ).join(` `);
}

export const iModeToString = (iMode: InterpolationMode) => {
    let ret = iMode.name;

    if (iMode.options) {
        ret += `:`;
        ret += (
            Object.entries(iMode.options).map(([key, val]) => `${key}=${val.value}`)
        ).join(`,`)
    }

    return ret;
}

export const iModeToPrettyString = (iMode: InterpolationMode) => {
    let ret = iMode.name;

    if (iMode.options) {
        ret += `: `
        ret += (
            Object.entries(iMode.options).map(([key, val]) => `${snakeCaseToFirstWordCapitalised(key)}=${val.value}`)
        ).join(`, `)
    }

    return ret
}