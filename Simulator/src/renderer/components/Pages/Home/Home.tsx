import * as React from 'react';
import * as cp from 'child_process';
import * as path from 'path';
import { message, Button, Popconfirm } from 'antd';
import * as commandExists from 'command-exists';
import { getPython3, getInterpolatory } from '../../../util';
import { LocalStorageKey, getLocalStorage, setLocalStorage } from '../../../store';

message.config({ top: 64, maxCount: 3 })

const logo = require('../../../../../assets/img/logo.png').default;

type VerState = { status: "loading" | "done" | "error", ver: string }

type PyVer = VerState;
type BinVer = VerState;

type IState = {
    pyVer: PyVer;
    // pyDeps: Record<string, string>;
    binVer: BinVer;
    dependencyLastInstalledTime: string;
}

const python3 = getPython3();
const binName = getInterpolatory();

export class Home extends React.Component<{}, IState> {

    mounted = false;

    constructor(props: any) {
        super(props);
        this.state = {
            pyVer: { status: "loading", ver: "" },
            binVer: { status: "loading", ver: "" },
            dependencyLastInstalledTime: `Loading...`
        };
        this.mounted = false;
    }


    componentDidMount = () => {
        this.mounted = true;
        this.getPyVer();
    }

    componentWillUnmount = () => {
        this.mounted = false;
    }


    getPyVer = async () => {
        const pyExists = commandExists.sync(python3);

        if (!pyExists) {
            if (this.mounted) message.error(`Python installation not found, please change Python settings`);
            if (this.mounted) this.setState(
                {
                    pyVer: { status: "error", ver: this.state.pyVer.ver },
                    binVer: { status: "error", ver: `Python 3 error` }
                }
            );
            return;
        }
        const proc = cp.spawn(python3, [`-V`]);

        proc.stdout.on('data', (data) => {
            if (this.mounted) this.setState({ pyVer: { status: "done", ver: data.toString() } });
        });

        proc.on('close', (code) => {
            if (code !== 0) {
                if (this.mounted) message.error(`Python installation not found, please change Python settings`);
                if (this.mounted) this.setState(
                    {
                        pyVer: { status: "error", ver: this.state.pyVer.ver },
                        binVer: { status: "error", ver: `Python 3 error` }
                    }
                );
            }
            else {
                // success, now get path and binVer
                this.getBinVer();
            }
        })
    }

    getBinVer = async () => {
        const proc = cp.spawn(python3, [binName, '-ver']);

        proc.stdout.on('data', (data) => {
            const str: string = data.toString();
            const gottenVer = str.substring(str.indexOf('"') + 1, str.lastIndexOf('"'));
            if (this.mounted) this.setState({ binVer: { status: "done", ver: gottenVer } });
        });

        proc.on('close', (code) => {
            if (code !== 0) {
                // TODO:- show modal and exit
                if (this.mounted) this.setState({ binVer: { status: "error", ver: this.state.binVer.ver } });
            }
            else {
                // success, now get deps
                this.getDependencyInfo();
            }
        })
    }

    getDependencyInfo = async () => {
        const dateTime = getLocalStorage(LocalStorageKey.DependencyLastInstallTime);
        if (dateTime) {
            const dateString = new Date(parseInt(dateTime, 10));

            if (this.mounted) this.setState({ dependencyLastInstalledTime: dateString.toString() });
            return;
        }
        
        if (this.mounted) this.setState({ dependencyLastInstalledTime: `N/A` });
    }

    reinstallDependencies = async () => {
        const binPathDir = path.dirname(binName);
        const requirementsTxt = path.join(binPathDir, `requirements.txt`);

        const proc = cp.spawn(python3, [`-m`, `pip`, `install`, `-r`, requirementsTxt]);

        let outErr: string;

        proc.stderr.on(`data`, (data) => {
            outErr += data.toString();
        })

        proc.on(`close`, (code) => {
            if (code !== 0) {
                if (this.mounted) message.error(`Error installing dependencies, please install manually`);
                console.error(outErr);
            }
            else {
                message.info(`Dependencies installed successfully`);
                setLocalStorage(LocalStorageKey.DependencyLastInstallTime, Date.now().toString());
                this.getDependencyInfo();
            }
        })
    }

    // getDeps = async () => {
    //     // read requirements.txt
    //     const proc = cp.spawn(python3, [binName, '-deps']);

    //     let deps: string[];

    //     proc.stdout.on('data', (data) => {
    //         const gottenDeps: string[] = JSON.parse(data.toString())
    //         deps = gottenDeps;
    //     });

    //     proc.on('close', (code) => {
    //         if (code !== 0) {
    //             // TODO:- show option to install deps
    //             if (this.mounted) this.setState({ depError: true })
    //         }
    //         else {
    //             const prePyDeps: Record<string, string> = {};
    //             deps.forEach((dep) => {
    //                 prePyDeps[dep] = `Loading...`
    //             })
    //             if (this.mounted) this.setState({ pyDeps: prePyDeps });
    //             // success, now query deps
    //             deps.forEach((dep) => {
    //                 this.getDepVersion(dep);
    //             })
    //         }
    //     })
    // }

    // get dep version from python and set it in state
    // second argument checkForDepErrorFalse set to true if required to set depError to false
    // getDepVersion = async (dep: string, checkForDepErrorFalse = false) => {
    //     const depProc = cp.spawn(python3, [`-m`, `pip`, `show`, dep]);

    //     let depout: string;

    //     depProc.stdout.on('data', (data) => {
    //         depout += data.toString();
    //     });

    //     depProc.on('close', (depProcCode) => {
    //         if (depProcCode !== 0) {
    //             const newPyDeps = this.state.pyDeps;
    //             newPyDeps[dep] = `N/A`;
    //             if (this.mounted) message.error(`Dependency \`${dep}\` not found, please install missing dependencies`);
    //             if (this.mounted) this.setState({ depError: true, pyDeps: newPyDeps })
    //         }
    //         else {
    //             const vLine = depout
    //                 .split(`\n`)
    //                 .filter((s) => s.includes(`Version`))[0];
    //             const vStr = vLine.substring(9);
    //             const newPyDeps = this.state.pyDeps;
    //             newPyDeps[dep] = vStr;
    //             if (this.mounted) {
    //                 this.setState({ pyDeps: newPyDeps })
    //                 if (checkForDepErrorFalse) {
    //                     const ok = Object.values(newPyDeps)
    //                         .map((ver) => ver !== 'N/A')
    //                         .reduce((a, b) => a && b)
    //                     if (ok && this.mounted) {
    //                         this.setState({ depError: false });
    //                     }
    //                 }
    //             }
    //         }
    //     })
    // }

    // installMissingDependencies = async () => {
    //     const { pyDeps } = this.state;
    //     Object.entries(pyDeps).forEach(([dep, ver]) => {
    //         if (ver === 'N/A') {
    //             if (this.mounted) message.info(`Installing dependency: \`${dep}\``)
    //             const proc = cp.spawn(python3, [`-m`, `pip`, `install`, dep]);

    //             let errMsg: string;

    //             proc.stderr.on('data', (data) => {
    //                 errMsg += data.toString();
    //             })

    //             proc.on('close', (code) => {
    //                 if (this.mounted) {
    //                     if (code !== 0) {
    //                         message.error(`Error installing dependency \`${dep}\`, please install it manually`);
    //                         console.error(errMsg);

    //                     }
    //                     else {
    //                         message.info(`Dependency \`${dep}\` installed successfully`);
    //                         this.getDepVersion(dep, true);
    //                     }
    //                 }
    //             })
    //         }
    //     })
    // }

    renderVer = (ver: VerState) => {
        if (ver.status === "loading") {
            return "Loading...";
        }
        if (ver.status === "error") {
            return <span style={{ color: 'red' }}>Error</span>
        }
        return ver.ver;
    }

    // renderPyDepInfo = (pyDeps: Record<string, string>) => {
    //     if (Object.keys(pyDeps).length) {
    //         return (Object.entries(pyDeps).map(([dep, status]) => {
    //             return <p key={dep} style={{ margin: 0 }}>{dep}: {status === `N/A` ? <span style={{ color: 'red' }}>N/A</span> : status}</p>
    //         }));
    //     }

    //     if (this.state.pyVer.status === "error") {
    //         return <span style={{ color: 'red' }}>Python 3 error</span>
    //     }

    //     return <span>Loading...</span>
    // }

    changePaths = () => {
        return true;
    }

    render() {
        const { pyVer, binVer, dependencyLastInstalledTime } = this.state;
        return (
            <div style={{ textAlign: 'center', margin: 'auto' }}>
                <div>
                    <img src={logo} alt='Interpolatory Simulator' style={{ marginTop: 12, maxWidth: 200, marginBottom: 12 }} />
                    <h2 style={{ fontSize: 36, fontWeight: 800, marginBottom: 0 }}>Interpolatory Simulator v1.0.0</h2>
                    <h4>Video frame-rate interpolation framework for software simulation and benchmarking</h4>
                </div>

                <div style={{ marginTop: 18, marginBottom: 18 }}>
                    <h3 style={{ fontSize: 24 }}>Machine Info</h3>
                    <p style={{ marginBottom: 0 }}>Python Path: {python3}</p>
                    <p style={{ marginBottom: 0 }}>Python Version: {this.renderVer(pyVer)}</p>
                    <p style={{ marginBottom: 0 }}>Interpolatory Path: {binName}</p>
                    <p style={{ marginBottom: 0 }}>Interpolatory Backend Version: {this.renderVer(binVer)}</p>
                    <Button style={{ marginBottom: 18 }}>Change Python 3 / Interpolatory Backend Path</Button>

                    <h3>Python Dependencies Info</h3>
                    <div>Last installed: {dependencyLastInstalledTime}</div>
                    <Popconfirm
                        title="This will reinstall all dependencies. Are you sure you want to continue?"
                        onConfirm={this.reinstallDependencies}
                        okText='Yes'
                        cancelText='No'
                        >
                        <Button danger disabled={binVer.status !== "done"}>Reinstall Dependencies</Button>
                    </Popconfirm>
                </div>
            </div>

        )
    }

}

export default Home;