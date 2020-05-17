import * as React from 'react';
import { Input, Form, Select, message, Button, Popover, Modal, Progress, Popconfirm } from 'antd';
import { remote } from 'electron';
import * as cp from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import { getInterpolationModesFromProcess, ValidatorObj } from '../../../util';

const { Search } = Input;
const { Option } = Select;

// benchmarking process
let benchProc: cp.ChildProcessWithoutNullStreams | undefined;

type IState = {
    supportedInterpolationModes: string[];
    interpolationMode: string;
    outputPath: string;
    outputPathValidator: ValidatorObj;
    benchmarkState: `done` | `error` | `benchmarking` | `idle`;
    benchmarkPercentage: number;
    progressString: string;
}

export class Benchmark extends React.Component<{}, IState> {
    constructor(props: any) {
        super(props);
        this.state = {
            supportedInterpolationModes: [],
            interpolationMode: ``,
            outputPath: ``,
            outputPathValidator: { status: `success`, help: `` },
            benchmarkState: `idle`,
            benchmarkPercentage: 0,
            progressString: ``,
        };
    }

    componentDidMount = () => {
        this.getInterpolationModes();
    };

    getInterpolationModes = async () => {
        try {
            const modes = await getInterpolationModesFromProcess()
            this.setState({
                supportedInterpolationModes: modes,
                interpolationMode: modes.length ? modes[0] : ``
            })
        }
        catch (err) {
            message.error(err.message);
        }
    };


    handleInterpolationModeChange = async (mode: string) => {
        this.setState({
            interpolationMode: mode,
        });
    }


    setOutputPath = async (filePath: string) => {
        // console.log(`Setting filePath to ${filePath}`);

        this.setState({
            outputPath: filePath,
        })

        // filePath length
        if (filePath.length === 0) {
            this.setState({
                outputPathValidator: { status: "success", help: `` }
            })
            return;
        }

        // check exists
        const fileExists = fs.existsSync(filePath);
        if (!fileExists) {
            this.setState({
                outputPathValidator: { status: "error", help: 'Path does not exist.' }
            })
            return;
        }

        this.setState({
            outputPathValidator: { status: "success", help: `` }
        })
    }

    startBenchmark = async () => {
        const { interpolationMode, outputPath } = this.state;


    }

    resetBenchmark = async () => {
        if (benchProc) {
            benchProc.kill(`SIGKILL`);
            benchProc = undefined;
        }
        this.setState({
            benchmarkState: `idle`,
            progressString: ``,
        })

    }

    render() {
        const { interpolationMode, supportedInterpolationModes, outputPathValidator, outputPath, benchmarkState, benchmarkPercentage, progressString } = this.state;
        const startDisabled = outputPathValidator.status === `error`;
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
                        <Select value={interpolationMode} onChange={this.handleInterpolationModeChange}>
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
                                const filePath = remote.dialog.showSaveDialogSync({
                                    title: `Select Benchmark Output Directory`
                                });

                                if (filePath) {
                                    this.setOutputPath(filePath);
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
                            <h4 style={{ textAlign: `center`, margin: `auto`, marginTop: 12 }}>Converting...</h4>
                            <Progress status='active' percent={benchmarkPercentage} />
                            <p style={{ textAlign: `center`, margin: `auto` }}>
                                {progressString.substring(6)}
                            </p>
                            <div style={{ textAlign: `center`, margin: `auto`, marginTop: 24 }}>

                                <Popconfirm
                                    title="This will stop the conversion. Are you sure you want to continue?"
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

                            <h4 style={{ textAlign: `center`, margin: `auto`, marginTop: 12 }}>Finished</h4>
                            <Progress status='success' percent={benchmarkPercentage} />
                            <p style={{ textAlign: `center`, margin: `auto` }}>
                                {progressString.substring(6)}
                            </p>

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
                            <h4 style={{ textAlign: `center`, margin: `auto`, marginTop: 12, color: `red` }}>Error</h4>
                            <Progress status='exception' percent={benchmarkPercentage} />
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