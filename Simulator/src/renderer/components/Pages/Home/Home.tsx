import * as React from 'react';
import * as cp from 'child_process';
import { message, Button } from 'antd';
import { getPython3 } from '../../../util';
import { binName } from '../../../globals';
import { LocalStorageKey, getLocalStorage } from '../../../store';

message.config({ top: 64, maxCount: 3 })

const logo = require('../../../../../assets/img/logo.png').default;

type VerState = { status: "loading" | "done" | "error", ver: string }

type PyVer = VerState;
type PyDep = VerState;
type BinVer = VerState;

type IState = {
    pyVer: PyVer;
    pyPath: string;
    pyDeps: Record<string, string>;
    binVer: BinVer;
    depError: boolean;
}

const python3 = getPython3();

export class Home extends React.Component<{}, IState> {
    constructor(props: any) {
        super(props);
        this.state = {
            pyVer: { status: "loading", ver: "" },
            pyPath: `Loading...`,
            pyDeps: {},
            binVer: { status: "loading", ver: "" },
            depError: false,
        };
    }

    componentDidMount = () => {
        this.getPyVer()
    }

    getPyVer = async () => {
        const proc = cp.spawn(python3, [`-V`]);

        proc.stdout.on('data', (data) => {
            this.setState({ pyVer: { status: "done", ver: data.toString() } });
        });


        proc.on('close', (code) => {
            if (code !== 0) {
                message.error(`Python installation not found, please change Python settings`);
                this.setState(
                    {
                        pyVer: { status: "error", ver: this.state.pyVer.ver },
                        pyPath: `N/A`,
                        binVer: { status: "error", ver: `Python 3 error` }
                    }
                );
            }
            else {
                // success, now get path and binVer
                this.getBinVer();
                this.getPyPath();
            }
        })
    }

    getPyPath = async () => {
        const p = getLocalStorage(LocalStorageKey.PythonPath)
        if (p) {
            this.setState({
                pyPath: p
            });
        }
        else {
            // get from sys.executable
            const proc = cp.spawn(python3, [`-c`, "import sys; print(sys.executable)"]);

            proc.stdout.on('data', (data) => {
                const sdata = data.toString();
                this.setState({
                    pyPath: sdata
                })
            })

            proc.on('close', (code) => {
                if (code !== 0) {
                    message.error(`Could not get Python path`)
                    this.setState ({
                        pyPath: `error`
                    })
                }
            });
        }
    }

    getBinVer = async () => {
        const proc = cp.spawn(python3, [binName, '-ver']);

        proc.stdout.on('data', (data) => {
            const str: string = data.toString();
            const gottenVer = str.substring(str.indexOf('"') + 1, str.lastIndexOf('"'));
            this.setState({ binVer: { status: "done", ver: gottenVer } });
        });

        proc.on('close', (code) => {
            if (code !== 0) {
                // TODO:- show modal and exit
                this.setState({ binVer: { status: "error", ver: this.state.binVer.ver } });
            }
            else {
                // success, now get deps
                this.getDeps();
            }
        })
    }

    getDeps = async () => {
        const proc = cp.spawn(python3, [binName, '-deps']);

        let deps: string[];

        proc.stdout.on('data', (data) => {
            const gottenDeps: string[] = JSON.parse(data.toString())
            deps = gottenDeps;
        });

        proc.on('close', (code) => {
            if (code !== 0) {
                // TODO:- show option to install deps
                this.setState({ depError: true })
            }
            else {
                // success, now query deps
                deps.forEach((dep) => {
                    const depProc = cp.spawnSync(python3, [`-m`, `pip`, `show`, dep]);
                    if (depProc.stderr.length || depProc.error) {
                        message.error(`Dependency \`${dep}\` not found, please reinstall dependencies`);
                        const newPyDeps = this.state.pyDeps;
                        newPyDeps[dep] = `N/A`;
                        this.setState({ depError: true, pyDeps: newPyDeps })
                    }
                    else {
                        const out = depProc.stdout.toString();
                        const vLine = out
                            .split(`\n`)
                            .filter((s) => s.includes(`Version`))[0];
                        const vStr = vLine.substring(9);
                        const newPyDeps = this.state.pyDeps;
                        newPyDeps[dep] = vStr;
                        this.setState({ pyDeps: newPyDeps })
                    }

                })
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

    renderPyDepInfo = (pyDeps: Record<string, string>) => {
        if (Object.keys(pyDeps).length) {
            return (Object.entries(pyDeps).map(([dep, status]) => {
                return <p key={dep} style={{ margin: 0 }}>{dep}: {status === `N/A` ? <span style={{ color: 'red' }}>N/A</span> : status}</p>
            }));
        }

        if (this.state.pyVer.status === "error") {
            return <span>Python 3 error</span>
        }

        return <span>Loading...</span>
    }


    render() {
        const { pyVer, pyDeps, binVer, depError, pyPath } = this.state;
        return (
            <div style={{ textAlign: 'center', margin: 'auto' }}>
                <div>
                    <img src={logo} alt='Interpolatory Simulator' style={{ marginTop: 12, maxWidth: 200, marginBottom: 12 }} />
                    <h2 style={{ fontSize: 36, fontWeight: 800, marginBottom: 0 }}>Interpolatory Simulator v1.0.0</h2>
                    <h4>Video frame-rate interpolation framework for software simulation and benchmarking</h4>
                </div>

                <div style={{ marginTop: 18, marginBottom: 18 }}>
                    <h3 style={{ fontSize: 24 }}>Machine Info</h3>
                    <p style={{ marginBottom: 0 }}>Python Version: {this.renderVer(pyVer)}</p>
                    <p style={{ marginBottom: 0 }}>Python Path: {pyPath}</p>
                    <p style={{ marginBottom: 0 }}>Interpolatory Backend Version: {this.renderVer(binVer)}</p>
                    <Button style={{ marginBottom: 18 }}>Change Python 3 / Interpolatory Backend Path</Button>

                    <h3>Python Dependencies Info</h3>
                    <div>{this.renderPyDepInfo(pyDeps)}</div>
                    {depError && <Button danger>Install Missing Dependencies</Button>}
                </div>
            </div>

        )
    }

}

export default Home;