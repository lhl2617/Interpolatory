/* eslint-disable no-underscore-dangle */
/* eslint-disable react/jsx-closing-bracket-location */
import * as React from 'react';
import * as cp from 'child_process';
import * as path from 'path';
import { message, Button, Popconfirm, Modal, Form, Input } from 'antd';
import * as commandExists from 'command-exists';
import { remote } from 'electron';
import { getPython3, getInterpolatory, reloadApp } from '../../../util';
import { LocalStorageKey, setLocalStorage, deleteLocalStorage } from '../../../store';

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
    binVer: BinVer;
    dependencyStatus: string;
    dependencyInstalling: boolean;
    cudaDependencyStatus: string;
    cudaDependencyInstalling: boolean;
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
            dependencyStatus: `Loading...`,
            dependencyInstalling: false,
            cudaDependencyStatus: `Loading...`,
            cudaDependencyInstalling: false,
            changePathsModalVisible: false,
            newPyPath: python3,
            newBinPath: binName
        };
    }

    _setState = (obj: Partial<IState>) => {
        if (this.mounted)
            this.setState(obj as any);
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
            this._setState(
                {
                    pyVer: { status: "error", ver: this.state.pyVer.ver },
                    binVer: { status: "error", ver: `Python 3 error` }
                }
            );
            return;
        }
        const proc = cp.spawn(python3, [`-V`]);


        proc.stdout.on('data', (data) => {
            this._setState({ pyVer: { status: "done", ver: data.toString() } });
        });

        proc.on('close', (code) => {
            if (code !== 0) {
                if (this.mounted) message.error(`Python installation not found, please change Python settings`);
                this._setState(
                    {
                        pyVer: { status: "error", ver: this.state.pyVer.ver },
                        binVer: { status: "error", ver: `Python 3 error` },
                        dependencyStatus: `N/A`,
                        cudaDependencyStatus: `N/A`
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
                this._setState({ binVer: { status: "done", ver: gottenVer } });

                setFeaturesEnabled(true);
                // success, now get deps
                this.getDependencyInfo();
            }
        })

        proc.stderr.on('data', (data) => {
            stderrTxt += data.toString();
            console.error(data.toString())
        })

        proc.stderr.on(`end`, () => {
            if (stderrTxt.length)
                console.error(stderrTxt);
        });

        proc.on(`close`, (code) => {
            if (code !== 0) {
                if (this.mounted) message.error(`Could not start Interpolatory backend process, is your Interpolatory Path correct?`)
                this._setState({
                    binVer: { status: "error", ver: this.state.binVer.ver },
                    dependencyStatus: `N/A`,
                    cudaDependencyStatus: `N/A`
                });

            }

        })
    }

    getDependencyInfo = async () => {
        const getBasicDepInfo = async () => {
            // console.log(`getting basic`)
            const proc = cp.spawn(python3, [binName, `-dep`]);

            proc.on(`exit`, (code) => {
                if (code !== 0) {
                    this._setState({
                        dependencyStatus: `Error`
                    });
                }
                else {
                    this._setState({
                        dependencyStatus: `OK`
                    });
                }
            });

        }

        const getCudaDepInfo = async () => {
            const proc = cp.spawn(python3, [binName, `-depcuda`]);

            proc.on(`exit`, (code) => {
                if (code !== 0) {
                    this._setState({
                        cudaDependencyStatus: `Error`
                    });
                }
                else {
                    this._setState({
                        cudaDependencyStatus: `OK`
                    });
                }
            });
        }

        getBasicDepInfo();
        getCudaDepInfo();
    }

    reinstallDependencies = async (cuda: boolean = false) => {
        const { setFeaturesEnabled } = this.props;
        setFeaturesEnabled(false);
        message.info(`Installing ${cuda ? `CUDA` : `basic`} dependencies`)
        
        if (cuda) {
            this._setState({ cudaDependencyInstalling: true });
        }
        else {
            this._setState({ dependencyInstalling: true });
        }

        const binPathDir = path.dirname(binName);
        const requirementsTxt = path.join(binPathDir, cuda ? `cuda-requirements.txt` : `requirements.txt`);

        const proc = cp.spawn(python3, [`-m`, `pip`, `install`, `-r`, requirementsTxt]);

        let outErr: string;

        proc.stderr.on(`data`, (data) => {
            outErr += data.toString();
            console.error(data.toString())
        })

        proc.stderr.on(`end`, () => {
            if (outErr.length)
                console.error(outErr);
        })

        proc.on(`exit`, (code) => {
            if (code !== 0) {
                if (this.mounted) message.error(`Error installing dependencies, please install manually`);
            }
            else {
                message.info(`Dependencies installed successfully`);
                this.getDependencyInfo();
            }
            setFeaturesEnabled(true);
            if (cuda) {
                this._setState({ cudaDependencyInstalling: false });
            }
            else {
                this._setState({ dependencyInstalling: false });
            }
        })
    }

    renderVer = (ver: VerState) => {
        if (ver.status === "loading") {
            return "Loading...";
        }
        if (ver.status === "error") {
            return <span style={{ color: 'red' }}>Error</span>
        }
        return ver.ver;
    }

    showChangePathsModal = () => {
        this._setState({ changePathsModalVisible: true })
    }

    hideChangePathsModal = () => {
        this._setState({ changePathsModalVisible: false })
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
            reloadApp();
        }

    }

    render() {
        const { pyVer, binVer, dependencyStatus, cudaDependencyStatus, changePathsModalVisible, newBinPath, newPyPath, dependencyInstalling, cudaDependencyInstalling } = this.state;
        return (
            <div style={{ textAlign: 'center', margin: 'auto' }}>
                <div>
                    <img src={logo} alt='Interpolatory Simulator' style={{ marginTop: 12, maxWidth: 200, marginBottom: 12 }} />
                    <h2 style={{ fontSize: 36, fontWeight: 800, marginBottom: 0 }}>Interpolatory Simulator v0.0.1</h2>
                    <h4>Video frame-rate interpolation framework for software simulation and benchmarking</h4>
                </div>

                <div style={{ marginTop: 18, marginBottom: 12 }}>
                    <h3 style={{ fontSize: 24 }}>Machine Info</h3>
                    <p style={{ marginBottom: 0 }}>Python Path: {python3}</p>
                    <p style={{ marginBottom: 0 }}>Python Version: {this.renderVer(pyVer)}</p>
                    <p style={{ marginBottom: 0 }}>Interpolatory Path: {binName}</p>
                    <p style={{ marginBottom: 0 }}>Interpolatory Backend Version: {this.renderVer(binVer)}</p>
                    <Button style={{ marginBottom: 18 }} onClick={this.showChangePathsModal}>Change Python 3 / Interpolatory Backend Path</Button>

                    <h3>Python Dependencies Info</h3>
                    <div>Basic dependencies status: {dependencyStatus}</div>
                    <Popconfirm
                        title="This will reinstall basic dependencies. Are you sure you want to continue?"
                        onConfirm={() => this.reinstallDependencies()}
                        okText='Yes'
                        cancelText='No'
                        disabled={binVer.status !== "done"|| dependencyInstalling}
                    >
                        <Button danger disabled={binVer.status !== "done" || dependencyInstalling }>Reinstall Basic Dependencies</Button>
                    </Popconfirm>
                    <div>CUDA dependencies status: {cudaDependencyStatus}</div>
                    <Popconfirm
                        title="This will reinstall basic dependencies. Are you sure you want to continue?"
                        onConfirm={() => this.reinstallDependencies(true)}
                        okText='Yes'
                        cancelText='No'
                        disabled={binVer.status !== "done"|| cudaDependencyInstalling}
                    >
                        <Button danger disabled={binVer.status !== "done" || cudaDependencyInstalling }>Reinstall CUDA Dependencies</Button>
                    </Popconfirm>
                </div>
                <Modal
                    style={{ left: 150 }}
                    title='Change Python 3 / Interpolatory Backend Path'
                    visible={changePathsModalVisible}
                    onOk={() => { this.changePaths(newPyPath, newBinPath); this.hideChangePathsModal(); }}
                    onCancel={() => { this._setState({ newBinPath: binName, newPyPath: python3 }); this.hideChangePathsModal(); }}
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
                                onChange={(e) => { this._setState({ newPyPath: e.target.value }) }}
                                onSearch={() => {
                                    const filePath = remote.dialog.showOpenDialogSync(
                                        {
                                            title: `Select Python 3 Path`,
                                            defaultPath: path.dirname(newPyPath),
                                            properties: ['openFile']
                                        }
                                    );

                                    if (filePath && filePath.length) {
                                        this._setState({ newPyPath: filePath[0] })
                                    }
                                }} />
                        </Form.Item>

                        <Form.Item
                            label={<h3>Interpolatory Path</h3>}>
                            <Search
                                onPressEnter={undefined}
                                enterButton="Browse"
                                value={newBinPath}
                                onChange={(e) => { this._setState({ newBinPath: e.target.value }) }}
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
                                        this._setState({ newBinPath: filePath[0] })
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