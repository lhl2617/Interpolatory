/* eslint-disable no-underscore-dangle */
import * as React from 'react';
import { Input, Form, Select, message, Button, Modal, Popconfirm, Progress, Spin } from 'antd';
import { remote } from 'electron';
import * as cp from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import { getInterpolationModesFromProcess, ValidatorObj, getPython3, getInterpolatory, defaultValidatorStatus, getPercentageFromProgressString, getProgressFilePath, processProgressFile } from '../../../util';

const { Search } = Input;
const { Option } = Select;

const python3 = getPython3();
const binName = getInterpolatory();


export type BenchmarkResult = {
    PSNR: number,
    SSIM: number
}
// benchmarking process
let benchProc: cp.ChildProcessWithoutNullStreams | undefined;

type IState = {
    supportedInterpolationModes: string[];
    interpolationMode: string;
    outputPath: string;
    outputPathValidator: ValidatorObj;
    benchmarkState: `done` | `error` | `benchmarking` | `idle`;
    benchmarkResult: BenchmarkResult | undefined;
    progressString: string;
    overrideDisable: boolean;
}

export class Benchmark extends React.Component<{}, IState> {

    mounted = false;

    constructor(props: any) {
        super(props);
        this.state = {
            supportedInterpolationModes: [],
            interpolationMode: ``,
            outputPath: ``,
            outputPathValidator: defaultValidatorStatus,
            benchmarkResult: undefined,
            benchmarkState: `idle`,
            progressString: ``,
            overrideDisable: false,
        };
    }

    _setState = (obj: any) => {
        if (this.mounted)
            this.setState(obj);
    }

    componentDidMount = () => {
        this.mounted = true;
        this.getInterpolationModes();
    };

    componentWillUnmount = () => {
        this.mounted = false;
        this.resetBenchmark();
    }

    getInterpolationModes = async () => {
        try {
            const modes = await getInterpolationModesFromProcess();
            this._setState({
                supportedInterpolationModes: modes,
                interpolationMode: modes.length ? modes[0] : ``
            })
        }
        catch (err) {
            message.error(err.message);
        }
    };


    handleInterpolationModeChange = async (mode: string) => {
        this._setState({
            interpolationMode: mode,
        });
    }


    setOutputPath = async (filePath: string) => {
        // console.log(`Setting filePath to ${filePath}`);

        this._setState({
            outputPath: filePath,
        })

        // filePath length
        if (filePath.length === 0) {
            this._setState({
                outputPathValidator: defaultValidatorStatus
            })
            return;
        }

        // check exists
        const fileExists = fs.existsSync(filePath);
        if (!fileExists) {
            this._setState({
                outputPathValidator: { status: "error", help: 'Path does not exist.' }
            })
            return;
        }

        this._setState({
            outputPathValidator: defaultValidatorStatus
        })
    }

    startBenchmark = async () => {
        this._setState({ benchmarkState: `benchmarking` });
        const { interpolationMode, outputPath } = this.state;


        // eslint-disable-next-line prefer-const
        let args = [binName, `-b`, interpolationMode];

        if (outputPath.length) {
            args.push(outputPath);
        }

        const progressFilePath = getProgressFilePath(args);

        args.push(`-pf=${progressFilePath}`)
        args.push(`-gui`)

        let gotStderr = ``;

        benchProc = cp.spawn(python3, args, { cwd: path.dirname(binName) })

        const poll = async () => {
            try {
                const progressStr = await processProgressFile(progressFilePath);
                if (progressStr) {
                    this._setState({
                        progressString: progressStr,
                    })
                }
            }
            catch (err) {
                console.error(err.message);
            }

            if (this.mounted && this.state.benchmarkState === `benchmarking`) {
                setTimeout(() => poll(), 1000);
            }
        }

        setTimeout(() => poll(), 1000);


        benchProc.stdout.on(`data`, (data) => {
            const res = JSON.parse(data);

            const bRes: BenchmarkResult = {
                PSNR: res.PSNR,
                SSIM: res.SSIM
            }

            // one second delay
            setTimeout(() => this._setState({
                benchmarkResult: bRes,
                benchmarkState: `done`
            }), 1000);
        });

        benchProc.stderr.on(`data`, (data) => {
            gotStderr += data.toString();
            console.error(data.toString())
        })

        benchProc.on(`close`, (code) => {
            if (code !== 0 && benchProc) {
                message.error(`Benchmark failed: ${gotStderr.length ? gotStderr : `Unknown error`}`)
                if (this.state.benchmarkState !== `idle`) this._setState({ benchmarkState: `error` });
            }
            benchProc = undefined;
        })



    }

    resetBenchmark = async () => {
        const updateState = () => {
            this._setState({
                benchmarkState: `idle`,
                progressString: ``,
                overrideDisable: false,
            })
        }
        if (benchProc) {
            this._setState({ overrideDisable: true, benchmarkState: `idle` });
            benchProc.kill(`SIGKILL`);
            benchProc = undefined;
            setTimeout(() => updateState(), 3000);
        }
        else {
            updateState();
        }

    }

    render() {
        const { progressString, overrideDisable, interpolationMode, supportedInterpolationModes, outputPathValidator, outputPath, benchmarkState, benchmarkResult } = this.state;
        const startDisabled = overrideDisable || outputPathValidator.status === `error` || supportedInterpolationModes.length === 0;

        const progressPercentage = getPercentageFromProgressString(progressString);

        return (

            <div>
                <Form layout="vertical" >
                    <Form.Item
                        label={<h3>Benchmark</h3>}>

                        <Select defaultValue="Middlebury">
                            <Option value="Middlebury">Middlebury</Option>
                        </Select>

                    </Form.Item>


                    <Form.Item
                        label={<h3>Interpolation Mode</h3>}>
                        <Select disabled={supportedInterpolationModes.length === 0} value={interpolationMode} onChange={this.handleInterpolationModeChange}>
                            {
                                (supportedInterpolationModes.map((m) => {
                                    return (<Option key={m} value={m} >{m}</Option>)
                                }))
                            }
                        </Select>
                    </Form.Item>


                    <Form.Item
                        label={<h3>Output Frames Path (optional)</h3>}
                        validateStatus={outputPathValidator.status}
                        help={outputPathValidator.help} >
                        <Search
                            enterButton="Browse"
                            value={outputPath}
                            onChange={(e) => this.setOutputPath(e.target.value)}
                            onPressEnter={undefined}
                            onSearch={() => {
                                const filePath = remote.dialog.showOpenDialogSync({
                                    title: `Select Benchmark Output Directory`,
                                    properties: [`openDirectory`]
                                });

                                if (filePath && filePath.length) {
                                    this.setOutputPath(filePath[0]);
                                }
                            }} />
                    </Form.Item>


                </Form>

                <div style={{ margin: 'auto', textAlign: 'center', marginTop: 48 }}>
                    <Button onClick={this.startBenchmark} size="large" disabled={startDisabled} type="primary">Start Benchmark</Button>
                </div>


                <Modal
                    style={{ left: 150 }}
                    title='Benchmark'
                    visible={benchmarkState !== `idle`}
                    footer={null}
                    closable={false}
                    maskClosable={false}
                >

                    <h4>Benchmark</h4>
                    <p>Middlebury</p>
                    <h4>Interpolation Mode</h4>
                    <p>{interpolationMode}</p>
                    <h4>Output Frames Directory</h4>
                    <p>{outputPath.length ? outputPath : `N/A`}</p>
                    {
                        (benchmarkState === `benchmarking`) && <div>
                            <h4 style={{ textAlign: `center`, margin: `auto`, marginTop: 12 }}>Benchmarking... <Spin size="small" /></h4>
                            <Progress status='active' percent={progressPercentage} />
                            <p style={{ textAlign: `center`, margin: `auto` }}>
                                {progressString.substring(6)}
                            </p>
                            <div style={{ textAlign: `center`, margin: `auto`, marginTop: 24 }}>
                                <Popconfirm
                                    title="This will stop the benchmark. Are you sure?"
                                    onConfirm={this.resetBenchmark}
                                    okText='Yes'
                                    cancelText='No'
                                >
                                    <Button danger>Stop</Button>
                                </Popconfirm>
                            </div>
                        </div>
                    }
                    {
                        benchmarkState === `done` && <div>

                            <h4 style={{ textAlign: `center`, margin: `auto`, marginTop: 12, color: `green` }}>Finished</h4>
                            <Progress status='success' percent={progressPercentage} />
                            <p style={{ textAlign: `center`, margin: `auto` }}>
                                {progressString.substring(6)}
                            </p>
                            {
                                benchmarkResult &&
                                <div style={{ textAlign: `center`, margin: `auto`, marginTop: 12 }}>
                                    <h4 style={{ fontWeight: 800 }}>Results</h4>
                                    <p style={{ margin: `auto` }}>PSNR: {benchmarkResult.PSNR}</p>
                                    <p>SSIM: {benchmarkResult.SSIM}</p>
                                </div>

                            }

                            <div style={{ textAlign: `center`, margin: `auto`, marginTop: 24 }}>
                                {
                                    outputPath &&
                                    <Button onClick={() => { remote.shell.showItemInFolder(outputPath) }}>Open containing folder</Button>
                                }
                                <Button onClick={this.resetBenchmark}>OK</Button>
                            </div>
                        </div>
                    }
                    {
                        benchmarkState === `error` && <div>
                            <h4 style={{ textAlign: `center`, margin: `auto`, marginTop: 12, color: `red` }}>An error occured.</h4>

                            <Progress status='exception' percent={progressPercentage} />
                            <p style={{ textAlign: `center`, margin: `auto` }}>
                                {progressString}
                            </p>
                            <div style={{ textAlign: `center`, margin: `auto`, marginTop: 24 }}>
                                <Button onClick={this.resetBenchmark}>OK</Button>
                            </div>
                        </div>
                    }
                </Modal>
            </div>
        )
    }

}

export default Benchmark;