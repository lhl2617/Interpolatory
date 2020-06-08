/* eslint-disable no-underscore-dangle */
import * as React from 'react';
import { Input, Form, Select, message, Button, Modal, Popconfirm, Spin, Popover } from 'antd';
import { remote } from 'electron';
import * as cp from 'child_process';
import * as fs from 'fs';

import {
    InfoCircleOutlined
} from '@ant-design/icons';


import { getInterpolationModesFromProcess, ValidatorObj, getPython3, getInterpolatory, defaultValidatorStatus, InterpolationMode, InterpolationModeSchema, getInterpolationModeSchema, iModeToPrettyString, iModeToString } from '../../../util';
import { BenchmarkResult } from '../Benchmark/Benchmark';
import IMode from '../../IMode/IMode';

let frame1Dim: any; // this is to check whether sizes are OK

const { Search } = Input;
const { Option } = Select;

message.config({ top: 64, maxCount: 3 })

const python3 = getPython3();
const binName = getInterpolatory();


// testing process
let testProc: cp.ChildProcessWithoutNullStreams | undefined;

type IState = {
    iMode: InterpolationMode | undefined;
    outputPath: string;
    outputPathValidator: ValidatorObj;
    inputPaths: { frame1: string, frame2: string }
    inputValidators: { frame1: ValidatorObj, frame2: ValidatorObj }
    groundTruthPath: string;
    groundTruthPathValidator: ValidatorObj;
    testState: `done` | `error` | `testing` | `idle`;
    testResult: BenchmarkResult | undefined;
    overrideDisable: boolean;
}

const pleaseInput = `Please input path.`;
const pleaseInputValidatorObj: ValidatorObj = { status: `error`, help: pleaseInput };

const getImageSize = (imagePath: string) => {
    return new Promise<string>((resolve, reject) => {
        const proc = cp.spawn(python3, [binName, `-mi`, imagePath]);

        let stdoutData = ``;

        proc.stdout.on(`data`, (data) => {
            stdoutData = data;
        })

        proc.stdout.on(`end`, () => {
            const ret: string = stdoutData.toString();
            resolve(ret);
        })

        proc.on(`close`, (code) => {
            if (code !== 0) {
                reject(new Error(`Unable to open image. Format not supported`));
            }
        })
    });
}

export class Test extends React.Component<{}, IState> {

    mounted = false;

    constructor(props: any) {
        super(props);
        this.state = {
            iMode: undefined,
            outputPath: ``,
            outputPathValidator: pleaseInputValidatorObj,
            inputPaths: { frame1: ``, frame2: `` },
            inputValidators: { frame1: pleaseInputValidatorObj, frame2: pleaseInputValidatorObj },
            groundTruthPath: ``,
            groundTruthPathValidator: defaultValidatorStatus,
            testState: `idle`,
            testResult: undefined,
            overrideDisable: false,
        };
    }

    _setState = (obj: Partial<IState>) => {
        if (this.mounted)
            this.setState(obj as any);
    }

    componentDidMount = () => {
        this.mounted = true;
    };


    componentWillUnmount = () => {
        this.mounted = false;
        this.resetTest();
    }

    setIMode = async (iMode: InterpolationMode) => {
        this._setState({ iMode: iMode })
    }

    setFrame1Path = async (filePath: string) => {

        const iPaths = this.state.inputPaths;
        iPaths.frame1 = filePath;
        this._setState({ inputPaths: iPaths });

        // because others are dependent on frame1, need to validate again
        const validateOtherPaths = async () => {
            this.setFrame2Path(this.state.inputPaths.frame2);
            this.setGroundTruthPath(this.state.groundTruthPath);
            this.setOutputPath(this.state.outputPath);
        }


        try {
            // filePath length
            if (filePath.length === 0) {
                throw new Error(pleaseInput);
            }

            // check exists
            const fileExists = fs.existsSync(filePath);
            if (!fileExists) {
                throw new Error(`File does not exist`);
            }

            const size = await getImageSize(filePath);
            frame1Dim = size;

            const iPathVal = this.state.inputValidators;
            iPathVal.frame1 = { status: `success`, help: `Image size: ${size}` };

            this._setState({
                inputValidators: iPathVal
            })
            validateOtherPaths();
        }
        catch (err) {
            const iPathVal = this.state.inputValidators;
            iPathVal.frame1 = { status: `error`, help: err.message }
            this._setState({
                inputValidators: iPathVal
            })
        }
    }

    setFrame2Path = async (filePath: string) => {
        const iPaths = this.state.inputPaths;
        iPaths.frame2 = filePath;
        this._setState({ inputPaths: iPaths });

        try {
            // filePath length
            if (filePath.length === 0) {
                throw new Error(pleaseInput);
            }

            // check exists
            const fileExists = fs.existsSync(filePath);
            if (!fileExists) {
                throw new Error(`File does not exist`);
            }

            // check same as frame 1
            if (filePath === iPaths.frame1) {
                throw new Error(`Frame 2 is identical to frame 1`);
            }

            const size = await getImageSize(filePath);

            // check size matches frame 1
            if (size !== frame1Dim) {
                throw new Error(`Size of Frame 2 ${size} is not the same as Frame 1's ${frame1Dim}`)
            }

            const iPathVal = this.state.inputValidators;
            iPathVal.frame2 = { status: `success`, help: `Image size: ${size}` };

            this._setState({
                inputValidators: iPathVal
            })
        }
        catch (err) {
            const iPathVal = this.state.inputValidators;
            iPathVal.frame2 = { status: `error`, help: err.message }
            this._setState({
                inputValidators: iPathVal
            })
        }

    }

    setGroundTruthPath = async (filePath: string) => {
        this._setState({ groundTruthPath: filePath });

        try {
            // filePath length
            // if does not exist just set as default, this is optional
            if (filePath.length === 0) {
                this._setState({
                    groundTruthPathValidator: defaultValidatorStatus,
                })
                return;
            }

            // check exists
            const fileExists = fs.existsSync(filePath);
            if (!fileExists) {
                throw new Error(`File does not exist`);
            }

            const size = await getImageSize(filePath);

            // check size matches frame 1
            if (size !== frame1Dim) {
                throw new Error(`Size of ground truth frame ${size} is not the same as Frame 1's ${frame1Dim}`)
            }

            this._setState({
                groundTruthPathValidator: { status: `success`, help: `Image size: ${size}` },
            })
        }
        catch (err) {
            const gPathVal: ValidatorObj = { status: `error`, help: err.message };
            this._setState({
                groundTruthPathValidator: gPathVal
            })
        }


    }

    setOutputPath = async (filePath: string) => {

        this._setState({ outputPath: filePath });

        try {
            // filePath length
            if (filePath.length === 0) {
                throw new Error(pleaseInput);
            }

            // check file exists to warn
            const fileExists = fs.existsSync(filePath);
            if (fileExists) {
                this._setState({
                    outputPathValidator: { status: `warning`, help: `Output file exists - running will overwrite this file.` }
                })
                return;
            }

            this._setState({
                outputPathValidator: defaultValidatorStatus
            })
        }
        catch (err) {
            const iPathVal = this.state.inputValidators;
            iPathVal.frame2 = { status: `error`, help: err.message }
            this._setState({
                inputValidators: iPathVal
            })
        }
    }

    startTest = async () => {
        this._setState({ testState: `testing` });
        const { inputPaths, groundTruthPath, outputPath, iMode } = this.state;
        const { frame1, frame2 } = inputPaths;

        if (!iMode) {
            /// should not happen
            message.error(`Invalid Interpolation mode`)
            return;
        }

        const interpolationMode = iModeToString(iMode)

        // eslint-disable-next-line prefer-const
        let args = [binName, `-t`, interpolationMode, `-f`, frame1, frame2, `-o`, outputPath];

        if (groundTruthPath.length) {
            args.push(groundTruthPath);
        }

        args.push(`-gui`);

        let gotStderr = ``;

        testProc = cp.spawn(python3, args);

        testProc.stdout.on(`data`, (data) => {
            if (groundTruthPath.length) {
                const res = JSON.parse(data)

                const tRes: BenchmarkResult = res;

                this._setState({
                    testResult: tRes,
                })
            }
        })

        testProc.stderr.on(`data`, (data) => {
            gotStderr += data.toString();
            console.error(data.toString())
        })

        testProc.on(`close`, (code) => {
            if (code !== 0) {
                if (testProc) {
                    message.error(`Testing failed: ${gotStderr.length ? gotStderr : `Unknown error`}`)
                    if (this.state.testState !== `idle`) this._setState({ testState: `error` });
                }
            }
            else {
                setTimeout(() => this._setState({ testState: `done` }), 1000);
            }
            testProc = undefined;
        });

    }

    resetTest = async () => {
        const updateState = () => {
            this._setState({
                testState: `idle`,
                overrideDisable: false,
            })
        }
        if (testProc) {
            this._setState({ overrideDisable: true, testState: `idle` });
            testProc.kill(`SIGKILL`);
            testProc = undefined;
        }
        setTimeout(() => updateState(), 3000);
    }

    render() {
        const {
            iMode,
            outputPath,
            outputPathValidator,
            inputValidators,
            inputPaths,
            groundTruthPath,
            groundTruthPathValidator,
            testResult,
            testState,
            overrideDisable
        } = this.state;
        const disabled = inputValidators.frame1.status === `error`;
        const testDisabled = overrideDisable || disabled || inputValidators.frame2.status === `error` || outputPathValidator.status === `error` || groundTruthPathValidator.status === `error`;
        return (

            <div>
                <h2>Testing produces the interpolated middle frame of given two frames</h2>
                <Form layout="vertical" >

                    <Form.Item
                        label={<h3>Frame 1 Path</h3>}
                        validateStatus={inputValidators.frame1.status}
                        help={inputValidators.frame1.help} >
                        <Search
                            enterButton="Browse"
                            value={inputPaths.frame1}
                            onChange={(e) => this.setFrame1Path(e.target.value)}
                            onPressEnter={undefined}
                            onSearch={() => {
                                const filePath = remote.dialog.showOpenDialogSync({
                                    title: `Select Frame 1`,
                                    properties: [`openFile`]
                                });

                                if (filePath && filePath.length) {
                                    this.setFrame1Path(filePath[0]);
                                }
                            }} />
                    </Form.Item>


                    <Form.Item
                        label={<h3>Frame 2 Path</h3>}
                        validateStatus={inputValidators.frame2.status}
                        help={inputValidators.frame2.help} >
                        <Search
                            enterButton="Browse"
                            value={inputPaths.frame2}
                            onChange={(e) => this.setFrame2Path(e.target.value)}
                            onPressEnter={undefined}
                            onSearch={() => {
                                const filePath = remote.dialog.showOpenDialogSync({
                                    title: `Select Frame 2`,
                                    properties: [`openFile`]
                                });

                                if (filePath && filePath.length) {
                                    this.setFrame2Path(filePath[0]);
                                }
                            }} />
                    </Form.Item>


                    <Form.Item
                        label={<h3>Output Frame Path</h3>}
                        validateStatus={outputPathValidator.status}
                        help={outputPathValidator.help} >
                        <Search
                            enterButton="Browse"
                            value={outputPath}
                            onChange={(e) => this.setOutputPath(e.target.value)}
                            onPressEnter={undefined}
                            onSearch={() => {
                                const filePath = remote.dialog.showSaveDialogSync({
                                    title: `Select Output Path`,
                                    properties: [`showOverwriteConfirmation`]
                                });

                                if (filePath) {
                                    this.setOutputPath(filePath);
                                }
                            }} />
                    </Form.Item>



                    <Form.Item
                        label={<Popover content={<div>PSNR and SSIM will be given if ground truth frame is given</div>} trigger="hover"><h3>Ground Truth Path (optional) <InfoCircleOutlined /></h3></Popover>}
                        validateStatus={groundTruthPathValidator.status}
                        help={groundTruthPathValidator.help} >
                        <Search
                            enterButton="Browse"
                            value={groundTruthPath}
                            onChange={(e) => this.setGroundTruthPath(e.target.value)}
                            onPressEnter={undefined}
                            onSearch={() => {
                                const filePath = remote.dialog.showOpenDialogSync({
                                    title: `Select Ground Truth Frame`,
                                    properties: [`openFile`]
                                });

                                if (filePath && filePath.length) {
                                    this.setGroundTruthPath(filePath[0]);
                                }
                            }} />
                    </Form.Item>



                    <IMode setIMode={this.setIMode} iMode={iMode} disabled={testDisabled} modeFlag="-t"/>


                    <div style={{ margin: 'auto', textAlign: 'center', marginTop: 48, marginBottom: 48 }}>
                        <Button onClick={this.startTest} size="large" disabled={testDisabled} type="primary">Start Process</Button>
                    </div>


                    <Modal
                        style={{ left: 150 }}
                        title='Test'
                        visible={testState !== `idle`}
                        footer={null}
                        closable={false}
                        maskClosable={false}
                    >

                        <h4>Frame 1 Path</h4>
                        <p>{inputPaths.frame1}</p>
                        <h4>Frame 2 Path</h4>
                        <p>{inputPaths.frame2}</p>
                        <h4>Output Path</h4>
                        <p>{outputPath}</p>
                        {
                            groundTruthPath.length > 0 &&
                            <span>
                                <h4>Ground Truth Path</h4>
                                <p>{groundTruthPath}</p>
                            </span>
                        }
                        <h4>Interpolation Mode</h4>
                        <p>{iMode && iModeToPrettyString(iMode)}</p>
                        <h4>Output Frame Directory</h4>
                        <p>{outputPath.length ? outputPath : `N/A`}</p>
                        {
                            (testState === `testing`) && <div>
                                <h4 style={{ textAlign: `center`, margin: `auto`, marginTop: 12 }}>Testing...</h4>
                                <div style={{ margin: `auto`, textAlign: `center`, marginTop: 12 }}>
                                    <Spin size='large' />
                                </div>
                                <div style={{ textAlign: `center`, margin: `auto`, marginTop: 24 }}>
                                    <Popconfirm
                                        title="This will stop testing. Are you sure?"
                                        onConfirm={this.resetTest}
                                        okText='Yes'
                                        cancelText='No'
                                    >
                                        <Button danger>Stop</Button>
                                    </Popconfirm>
                                </div>
                            </div>
                        }
                        {
                            testState === `done` && <div>

                                <h4 style={{ textAlign: `center`, margin: `auto`, marginTop: 12, color: `green` }}>Finished</h4>

                                {
                                    testResult &&
                                    <div style={{ textAlign: `center`, margin: `auto`, marginTop: 12 }}>
                                        <h4 style={{ fontWeight: 800 }}>Results</h4>
                                        <p style={{ margin: `auto` }}>PSNR: {testResult.PSNR}</p>
                                        <p>SSIM: {testResult.SSIM}</p>
                                    </div>

                                }

                                <div style={{ textAlign: `center`, margin: `auto`, marginTop: 24 }}>
                                    {
                                        outputPath &&
                                        <span>
                                            <Button onClick={() => { remote.shell.showItemInFolder(outputPath) }}>Open containing folder</Button>
                                            <Button onClick={() => { remote.shell.openItem(outputPath) }}>Open output frame</Button>
                                        </span>
                                    }
                                    <Button onClick={this.resetTest}>OK</Button>
                                </div>
                            </div>
                        }
                        {
                            testState === `error` && <div>
                                <h4 style={{ textAlign: `center`, margin: `auto`, marginTop: 12, color: `red` }}>An error occured.</h4>

                                <div style={{ textAlign: `center`, margin: `auto`, marginTop: 24 }}>
                                    <Button onClick={this.resetTest}>OK</Button>
                                </div>
                            </div>
                        }
                    </Modal>

                </Form>
            </div>
        )
    }

}

export default Test;