/* eslint-disable no-underscore-dangle */
/* eslint-disable react/jsx-closing-bracket-location */
import * as React from 'react';
import { Input, Form, Select, Radio, message, Button, Popover, Modal, Progress, Popconfirm, Spin } from 'antd';
import { remote } from 'electron';
import * as cp from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

import {
    InfoCircleOutlined
} from '@ant-design/icons';

import { supportedVideoFormats, supportedTargetFPS } from '../../../globals';
import { getPython3, getInterpolatory, getInterpolationModesFromProcess, ValidatorObj, defaultValidatorStatus, getProgressFilePath, processProgressFile, getPercentageFromProgressString } from '../../../util';

message.config({ top: 64, maxCount: 3 })

// conversion process
let convProc: cp.ChildProcessWithoutNullStreams | undefined;

const { Search } = Input;
const { Option } = Select;

const python3 = getPython3();
const binName = getInterpolatory();
/*
{'plugin': 'ffmpeg', 'nframes': 8736, 'ffmpeg_version': '4.1 built with gcc 8.2.1 (GCC) 20181017', 'codec': 'h264', 'pix_fmt': 'yuv420p(progressive)', 'fps': 60.0, 'source_size': (1920, 1080), 'size': (1920, 1080), 'duration': 145.6}
*/
type VideoMetadata = {
    nframes: number,
    codec: string,
    fps: number,
    source_size: number[],
    duration: number
};


const pleaseInput = `Please input video path.`;

type IState = {
    inputVideoPath: string;
    inputVideoMetadata: VideoMetadata | undefined;
    inputValidator: ValidatorObj;
    outputVideoPath: string;
    outputValidator: ValidatorObj;
    interpolationMode: string;
    supportedInterpolationModes: string[];
    targetFPS: number;
    convertState: "done" | "error" | "converting" | "idle";
    progressString: string;
    overrideDisable: boolean;
}

export class Convert extends React.Component<{}, IState> {
    mounted = false;

    constructor(props: any) {
        super(props);
        this.state = {
            inputVideoPath: ``,
            inputVideoMetadata: undefined,
            inputValidator: { status: `error`, help: pleaseInput },
            outputVideoPath: ``,
            outputValidator: { status: `error`, help: pleaseInput },
            interpolationMode: ``,
            supportedInterpolationModes: [],
            targetFPS: 60,
            convertState: "idle",
            progressString: ``,
            overrideDisable: false,
        };
    }

    _setState = (obj: Partial<IState>) => {
        if (this.mounted)
            this.setState(obj as any);
    }


    componentDidMount = () => {
        this.mounted = true;
        this.getInterpolationModes();
    };

    componentWillUnmount = () => {
        this.mounted = false;
        this.resetConvert();
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

    setOutputFilePath = async (filePath: string) => {
        this._setState({
            outputVideoPath: filePath,
        });


        // filePath length
        if (filePath.length === 0) {
            this._setState({
                outputValidator: { status: "error", help: pleaseInput }
            })
            return;
        }

        // check directory exists
        const dirname = path.dirname(filePath);
        if (!fs.existsSync(dirname)) {
            this._setState({
                outputValidator: { status: "error", help: "Directory does not exist." }
            });
            return;
        }

        // match extensions
        const { inputVideoPath } = this.state;
        const srcExt = path.extname(inputVideoPath).substr(1);
        if (srcExt !== path.extname(filePath).substr(1)) {
            this._setState({
                outputValidator: { status: "error", help: "File extension does not match with input." }
            });
            return;
        }

        // same as input
        if (inputVideoPath === filePath) {
            this._setState({
                outputValidator: { status: "error", help: "Video path is identical to source video path." }
            });
            return;
        }

        // check exists to warn
        const fileExists = fs.existsSync(filePath);
        if (fileExists) {
            this._setState({
                outputValidator: { status: `warning`, help: 'Output file exists - conversion will overwrite this file!' }
            })
            return;
        }

        this._setState({
            outputValidator: defaultValidatorStatus
        })

    }



    setInputFilePath = async (filePath: string) => {
        const { outputVideoPath } = this.state;
        this._setState({
            inputVideoPath: filePath,
            inputVideoMetadata: undefined
        });


        // because dest is dependent on input, need to validate again
        const validateDestinationAgain = async () => {
            this.setOutputFilePath(this.state.outputVideoPath);
        }


        // filePath length
        if (filePath.length === 0) {
            this._setState({
                inputValidator: { status: "error", help: pleaseInput }
            })
            return;
        }

        // check exists first
        const fileExists = fs.existsSync(filePath);
        if (!fileExists) {
            this._setState({
                inputValidator: { status: "error", help: 'File does not exist.' }
            })
            return;
        }

        // extension is supported
        const ext = path.extname(filePath).substr(1);
        // console.log(ext);
        if (supportedVideoFormats.indexOf(ext) === -1) {
            this._setState({
                inputValidator: { status: "error", help: 'Format is not supported.' }
            })
            return;
        }

        // load into python
        const args = [binName, `-mv`, filePath];
        const proc = cp.spawn(python3, args)

        let stdoutData: VideoMetadata;
        proc.stdout.on('data', (data) => {
            // console.log(`Gotten stdout: ${data}`);
            stdoutData = JSON.parse(data);
            this._setState({
                inputVideoMetadata: stdoutData,
            })
        })

        proc.stderr.on('data', (data) => {
            // message.error(data.toString())
            console.error(data.toString())
        })

        proc.on('close', (code) => {
            if (code === 0) {
                // in here we set also the outputVideoPath if empty
                const fileName = path.basename(filePath);
                const fileExt = path.extname(fileName).substr(1);
                const fileDir = path.dirname(filePath);

                const fileNameWithoutExt = fileName.slice(0, -(fileExt.length + 1));

                const outputPath = `${fileDir}${path.sep}${fileNameWithoutExt}_output.${fileExt}`

                if (outputVideoPath.length === 0) {
                    this.setOutputFilePath(outputPath);
                }
                else {
                    // the above validates again already
                    validateDestinationAgain();
                }

                this._setState({
                    inputValidator: defaultValidatorStatus
                })
            }
            else {
                // eslint-disable-next-line no-lonely-if
                this._setState({
                    inputValidator: { status: "error", help: 'Format is not supported.' }
                })
            }
        })

    }

    parseMetadata = (metadata: VideoMetadata | undefined) => {
        if (!metadata) {
            return <div style={{ marginBottom: 24 }}>N/A</div>
        }
        const { nframes, codec, fps, source_size, duration } = metadata;
        return (
            <div style={{ marginBottom: 24 }}>
                <div>{`Codec: ${codec}`}</div>
                <div>{`Number of frames: ${nframes}`}</div>
                <div>{`FPS: ${fps}`}</div>
                <div>{`Dimensions: ${source_size[0]}x${source_size[1]}`}</div>
                <div>{`Duration: ${duration}s`}</div>
            </div>
        );
    }

    handleTargetFPSChange = async (fps: number) => {
        this._setState({
            targetFPS: fps,
        })
    }

    handleInterpolationModeChange = async (mode: string) => {
        this._setState({
            interpolationMode: mode,
        });
    }


    // processProgressString = async (stdout: string) => {
    //     const getLastProgressLine = () => {
    //         const lines = stdout.split(`\n`);

    //         // eslint-disable-next-line no-plusplus
    //         for (let i = lines.length - 1; i >= 0; --i) {
    //             if (lines[i].substr(0, 8) === `PROGRESS`) {
    //                 return lines[i];
    //             }
    //         }
    //         return undefined;
    //     }

    //     // get last, don't overwrite error
    //     const lastProgressLine = getLastProgressLine();
    //     if (lastProgressLine && this.state.convertState !== `error`) {
    //         this._setState({
    //             progressString: lastProgressLine.substr(10)
    //         });
    //     }
    // }

    startConvert = async () => {
        this._setState({ convertState: `converting`, progressString: `` });
        const { inputVideoPath, interpolationMode, targetFPS, outputVideoPath } = this.state;

        let gotStderr = ``;

        const args = [binName, `-i`, inputVideoPath, `-m`, interpolationMode, `-f`, targetFPS.toString(), `-o`, outputVideoPath]

        const progressFilePath = getProgressFilePath(args);

        // console.log(progressFilePath);

        args.push(`-pf=${progressFilePath}`)
        args.push(`-gui`)

        convProc = cp.spawn(python3, args);

        // convProc.stdout.pipe(process.stdout)


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

            if (this.mounted && this.state.convertState === `converting`) {
                setTimeout(() => poll(), 1000);
            }
        }

        setTimeout(() => poll(), 1000);

        // not expecting anything from stdout
        // convProc.stdout.on(`data`, (data) => {
        //     console.log(data.toString())
        //     console.log(`-`)
        //     this.processProgressString(data.toString())
        // })


        convProc.stderr.on(`data`, (data) => {
            gotStderr += data.toString();
            console.error(data.toString())
        })

        convProc.on(`close`, (code) => {
            if (code !== 0) {
                const err = `An error occured: ${code ? code.toString() : ''} ${gotStderr}`;
                if (this.state.convertState !== `idle`)
                    this._setState({ convertState: `error`, progressString: err })
            }
            else {
                // message.info(`Conversion successful`);
                // one second delay
                setTimeout(() => this._setState({ convertState: `done` }), 1000);
            }
            convProc = undefined;
        });
    }

    resetConvert = async () => {
        const updateState = () => {
            this._setState({
                convertState: `idle`,
                progressString: ``,
                overrideDisable: false,
            })   
        }
        if (convProc) {
            this._setState({ overrideDisable: true, convertState: `idle` });
            convProc.kill(`SIGKILL`);
            convProc = undefined;
            setTimeout(() => updateState(), 3000);
        }
        else {
            updateState();
        }
    }

    render() {
        const { overrideDisable, inputVideoPath, inputVideoMetadata, outputVideoPath, targetFPS, interpolationMode, supportedInterpolationModes, inputValidator, outputValidator, convertState, progressString } = this.state;

        const disabled = inputValidator.status === "error";
        const conversionDisabled = overrideDisable || disabled || outputValidator.status === "error" || convertState !== `idle`;

        const progressPercentage = getPercentageFromProgressString(progressString);

        return (
            <div>
                <Form layout="vertical" >
                    <Form.Item
                        label={<h3>Source Video Path</h3>}
                        validateStatus={inputValidator.status}
                        help={inputValidator.help} >
                        <Search
                            enterButton="Browse"
                            value={inputVideoPath}
                            onChange={(e) => this.setInputFilePath(e.target.value)}
                            onPressEnter={undefined}
                            onSearch={() => {
                                const filePath = remote.dialog.showOpenDialogSync(
                                    {
                                        title: `Select Source Video`,
                                        defaultPath: path.dirname(inputVideoPath),
                                        properties: ['openFile'],
                                        filters: [{ name: 'Videos', extensions: supportedVideoFormats }]
                                    }
                                );

                                if (filePath && filePath.length) {
                                    this.setInputFilePath(filePath[0]);
                                }
                            }} />
                    </Form.Item>

                    <h3>Source Video Metadata</h3>
                    {this.parseMetadata(inputVideoMetadata)}

                    <Form.Item
                        label={<h3>Destination Video Path</h3>}
                        validateStatus={disabled ? "success" : outputValidator.status}
                        help={disabled ? "" : outputValidator.help} >
                        <Search
                            disabled={disabled}
                            enterButton="Browse"
                            value={outputVideoPath}
                            onChange={(e) => this.setOutputFilePath(e.target.value)}
                            onPressEnter={undefined}
                            onSearch={() => {
                                const srcExtension = path.extname(inputVideoPath).substr(1)

                                const filePath = remote.dialog.showSaveDialogSync(
                                    { title: `Select Destination Video Path`, properties: ['showOverwriteConfirmation'], filters: [{ name: 'Video', extensions: [srcExtension] }] }
                                )

                                if (filePath) {
                                    this.setOutputFilePath(filePath);
                                }
                            }}
                        />
                    </Form.Item>

                    <Form.Item
                        label={<Popover content={<div>More frame rates can be set via CLI.</div>} trigger="hover"><h3>Target FPS <InfoCircleOutlined /></h3></Popover>}
                    >
                        <Radio.Group value={targetFPS} onChange={(e) => this.handleTargetFPSChange(e.target.value)}
                            disabled={disabled}>
                            {
                                (supportedTargetFPS.map((fps) => {
                                    return (<Radio.Button key={fps} value={fps} disabled={fps === inputVideoMetadata?.fps}>{fps}</Radio.Button>)
                                }))
                            }
                        </Radio.Group>
                    </Form.Item>


                    <Form.Item
                        label={<h3>Interpolation Mode</h3>}>
                        <Select value={interpolationMode} onChange={this.handleInterpolationModeChange}
                            disabled={disabled}>
                            {
                                (supportedInterpolationModes.map((m) => {
                                    return (<Option key={m} value={m} >{m}</Option>)
                                }))
                            }
                        </Select>
                    </Form.Item>

                </Form>

                <div style={{ margin: 'auto', textAlign: 'center', marginTop: 48 }}>
                    <Button onClick={this.startConvert} size="large" disabled={conversionDisabled} type="primary">Start Conversion</Button>
                </div>

                <Modal
                    style={{ left: 150 }}
                    title='Conversion'
                    visible={convertState !== `idle`}
                    footer={null}
                    closable={false}
                    maskClosable={false}
                >

                    <h4>Source</h4>
                    <p>`{inputVideoPath}` ({inputVideoMetadata?.fps} fps)</p>
                    <h4>Destination</h4>
                    <p>`{outputVideoPath}` ({targetFPS} fps)</p>
                    <h4>Interpolation Mode</h4>
                    <p>{interpolationMode}</p>
                    {
                        (convertState === `converting`) && <div>
                            <h4 style={{ textAlign: `center`, margin: `auto`, marginTop: 12 }}>Converting... <Spin size="small" /></h4>
                            <Progress status='active' percent={progressPercentage} />
                            <p style={{ textAlign: `center`, margin: `auto` }}>
                                {progressString.substring(6)}
                            </p>
                            <div style={{ textAlign: `center`, margin: `auto`, marginTop: 24 }}>

                                <Popconfirm
                                    title="This will stop the conversion. Are you sure?"
                                    onConfirm={this.resetConvert}
                                    okText='Yes'
                                    cancelText='No'
                                >
                                    <Button danger>Stop</Button>
                                </Popconfirm>
                            </div>
                        </div>
                    }
                    {
                        convertState === `done` && <div>

                            <h4 style={{ textAlign: `center`, margin: `auto`, marginTop: 12 }}>Finished</h4>
                            <Progress status='success' percent={progressPercentage} />
                            <p style={{ textAlign: `center`, margin: `auto` }}>
                                {progressString.substring(6)}
                            </p>

                            <div style={{ textAlign: `center`, margin: `auto`, marginTop: 24 }}>
                                <Button onClick={() => { remote.shell.showItemInFolder(outputVideoPath) }}>Open containing folder</Button>
                                <Button onClick={() => { remote.shell.openItem(outputVideoPath) }}>Open output video</Button>
                                <Button onClick={this.resetConvert}>OK</Button>
                            </div>
                        </div>
                    }
                    {
                        convertState === `error` && <div>
                            <h4 style={{ textAlign: `center`, margin: `auto`, marginTop: 12, color: `red` }}>Error</h4>
                            <Progress status='exception' percent={progressPercentage} />
                            <p style={{ textAlign: `center`, margin: `auto` }}>
                                {progressString}
                            </p>
                            <div style={{ textAlign: `center`, margin: `auto`, marginTop: 24 }}>
                                <Button onClick={this.resetConvert}>OK</Button>
                            </div>
                        </div>
                    }
                </Modal>
            </div>
        )
    }

}

export default Convert;