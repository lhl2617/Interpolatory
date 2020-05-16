/* eslint-disable react/jsx-closing-bracket-location */
import * as React from 'react';
import * as cp from 'child_process';
import * as path from 'path';
import { message, Button, Popconfirm, Modal, Form, Input } from 'antd';
import * as commandExists from 'command-exists';
import { remote } from 'electron';
import { getPython3, getInterpolatory, reloadApp } from '../../../util';
import { LocalStorageKey, getLocalStorage, setLocalStorage, deleteLocalStorage } from '../../../store';

const { Search } = Input;
message.config({ top: 64, maxCount: 3 })
const logo = require('../../../../../assets/img/logo.png').default;

type VerState = { status: "loading" | "done" | "error", ver: string }

type PyVer = VerState;
type BinVer = VerState;

type IProps = {
    setFeaturesEnabled: (b: boolean) => void;
}

type IState = {
    pyVer: PyVer;
    // pyDeps: Record<string, string>;
    binVer: BinVer;
    dependencyLastInstalledTime: string;
    changePathsModalVisible: boolean;
    newPyPath: string;
    newBinPath: string;
}

const python3 = getPython3();
const binName = getInterpolatory();


export class Home extends React.Component<IProps, IState> {

    mounted = false;

    constructor(props: any) {
        super(props);
        this.state = {
            pyVer: { status: "loading", ver: "" },
            binVer: { status: "loading", ver: "" },
            dependencyLastInstalledTime: `Loading...`,
            changePathsModalVisible: false,
            newPyPath: python3,
            newBinPath: binName
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
                        binVer: { status: "error", ver: `Python 3 error` },
                        dependencyLastInstalledTime: `N/A`
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
        const { setFeaturesEnabled } = this.props;
        const proc = cp.spawn(python3, [binName, '-ver']);

        setTimeout(() => proc.kill(), 3000);

        let stdoutTxt = ``;
        let stderrTxt = ``;

        proc.stdout.on('data', (data) => {
            stdoutTxt += data.toString();
            // "Interpolatory Simulator 0.0.1" for example
        });
        proc.stdout.on(`end`, () => {
            if (stdoutTxt.includes(`Interpolatory Simulator`)) {
                const gottenVer = stdoutTxt.substring(25, stdoutTxt.lastIndexOf('"'));
                if (this.mounted) this.setState({ binVer: { status: "done", ver: gottenVer } });
            }
        })

        proc.stderr.on('data', (data) => {
            stderrTxt += data.toString();
        })

        proc.stderr.on(`end`, () => {
            if (stderrTxt.length)
                console.error(stderrTxt);
        });

        proc.on(`close`, (code) => {

            if (code === 0 && this.state.binVer.status === `done`) {
                setFeaturesEnabled(true);
                // success, now get deps
                this.getDependencyInfo();
            }
            else {
                if (this.mounted) message.error(`Could not start Interpolatory backend process, is your Interpolatory Path correct?`)
                if (this.mounted) this.setState({ binVer: { status: "error", ver: this.state.binVer.ver }, dependencyLastInstalledTime: `N/A` });

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
        message.info(`Installing dependencies`)
        const binPathDir = path.dirname(binName);
        const requirementsTxt = path.join(binPathDir, `requirements.txt`);

        const proc = cp.spawn(python3, [`-m`, `pip`, `install`, `-r`, requirementsTxt]);

        let outErr: string;

        proc.stderr.on(`data`, (data) => {
            outErr += data.toString();
        })

        proc.stderr.on(`end`, () => {
            if (outErr.length)
                console.error(outErr);
        })

        proc.on(`close`, (code) => {
            if (code !== 0) {
                if (this.mounted) message.error(`Error installing dependencies, please install manually`);
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

    showChangePathsModal = () => {
        this.setState({ changePathsModalVisible: true })
    }

    hideChangePathsModal = () => {
        this.setState({ changePathsModalVisible: false })
    }

    changePaths = (newPyPath: string, newBinName: string) => {
        let shouldReload = false;
        if (newPyPath !== python3) {
            shouldReload = true;
            setLocalStorage(LocalStorageKey.PythonPath, newPyPath);
        }
        if (newBinName !== binName) {
            shouldReload = true;
            setLocalStorage(LocalStorageKey.InterpolatoryPath, newBinName);
        }
        if (shouldReload) {
            // dependencies are different now
            deleteLocalStorage(LocalStorageKey.DependencyLastInstallTime);
            reloadApp();
        }

    }

    render() {
        const { pyVer, binVer, dependencyLastInstalledTime, changePathsModalVisible, newBinPath, newPyPath } = this.state;
        return (
            <div style={{ textAlign: 'center', margin: 'auto' }}>
                <div>
                    <img src={logo} alt='Interpolatory Simulator' style={{ marginTop: 12, maxWidth: 200, marginBottom: 12 }} />
                    <h2 style={{ fontSize: 36, fontWeight: 800, marginBottom: 0 }}>Interpolatory Simulator v0.0.1</h2>
                    <h4>Video frame-rate interpolation framework for software simulation and benchmarking</h4>
                </div>

                <div style={{ marginTop: 18, marginBottom: 18 }}>
                    <h3 style={{ fontSize: 24 }}>Machine Info</h3>
                    <p style={{ marginBottom: 0 }}>Python Path: {python3}</p>
                    <p style={{ marginBottom: 0 }}>Python Version: {this.renderVer(pyVer)}</p>
                    <p style={{ marginBottom: 0 }}>Interpolatory Path: {binName}</p>
                    <p style={{ marginBottom: 0 }}>Interpolatory Backend Version: {this.renderVer(binVer)}</p>
                    <Button style={{ marginBottom: 18 }} onClick={this.showChangePathsModal}>Change Python 3 / Interpolatory Backend Path</Button>

                    <h3>Python Dependencies Info</h3>
                    <div>Last installed: {dependencyLastInstalledTime}</div>
                    <Popconfirm
                        title="This will reinstall all dependencies. Are you sure you want to continue?"
                        onConfirm={this.reinstallDependencies}
                        okText='Yes'
                        cancelText='No'
                        disabled={binVer.status !== "done"}
                    >
                        <Button danger disabled={binVer.status !== "done"}>Reinstall Dependencies</Button>
                    </Popconfirm>
                </div>
                <Modal
                    style={{ left: 150 }}
                    title='Change Python 3 / Interpolatory Backend Path'
                    visible={changePathsModalVisible}
                    onOk={() => { this.changePaths(newPyPath, newBinPath); this.hideChangePathsModal(); }}
                    onCancel={() => { this.setState({ newBinPath: binName, newPyPath: python3 }); this.hideChangePathsModal(); }}
                    cancelText='Discard Changes'
                    okText='Save Changes'
                    closable={false}
                    maskClosable={false}
                >

                    <Form layout="vertical" >
                        <Form.Item
                            label={<h3>Python 3 Path</h3>}>
                            <Search
                                onPressEnter={undefined}
                                enterButton="Browse"
                                value={newPyPath}
                                onChange={(e) => { this.setState({ newPyPath: e.target.value }) }}
                                onSearch={() => {
                                    const filePath = remote.dialog.showOpenDialogSync(
                                        {
                                            title: `Select Python 3 Path`,
                                            defaultPath: path.dirname(newPyPath),
                                            properties: ['openFile']
                                        }
                                    );

                                    if (filePath && filePath.length) {
                                        this.setState({ newPyPath: filePath[0] })
                                    }
                                }} />
                        </Form.Item>

                        <Form.Item
                            label={<h3>Interpolatory Path</h3>}>
                            <Search
                                onPressEnter={undefined}
                                enterButton="Browse"
                                value={newBinPath}
                                onChange={(e) => { this.setState({ newBinPath: e.target.value }) }}
                                onSearch={() => {
                                    const filePath = remote.dialog.showOpenDialogSync(
                                        {
                                            title: `Select Interpolatory Path`,
                                            defaultPath: path.dirname(newBinPath),
                                            properties: ['openFile'],
                                            filters: [{ name: 'Python', extensions: [`py`] }]
                                        }
                                    );

                                    if (filePath && filePath.length) {
                                        this.setState({ newBinPath: filePath[0] })
                                    }
                                }} />
                        </Form.Item>
                    </Form>
                </Modal>

            </div>

        )
    }

}

export default Home;