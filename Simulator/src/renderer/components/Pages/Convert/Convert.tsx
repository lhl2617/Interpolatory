import * as React from 'react';
import { Input, Form, Select, Radio, message, Button, Popover } from 'antd';
import { remote } from 'electron';
import * as cp from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

import {
    InfoCircleOutlined
} from '@ant-design/icons';

import { binName, supportedVideoFormats, supportedTargetFPS } from '../../../globals';
import { getPython3 } from '../../../util';

const { Search } = Input;
const { Option } = Select;

const python3 = getPython3();
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
    inputValidator: { status: "success" | "error"; help: string }
    outputVideoPath: string;
    outputValidator: { status: "success" | "error"; help: string }
    interpolationMode: string;
    supportedInterpolationModes: string[];
    targetFPS: number;
}

export class Convert extends React.Component<{}, IState> {
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
        };
    }

    componentDidMount = () => {
        this.getInterpolationModes();
    };

    getInterpolationModes = async () => {
        // load into python
        const args = [binName, `-if`];
        const proc = cp.spawn(python3, args)

        let stdoutData: string[];
        proc.stdout.on('data', (data) => {
            // console.log(`Gotten stdout: ${data}`);
            stdoutData = JSON.parse(data);
            this.setState({
                supportedInterpolationModes: stdoutData,
                interpolationMode: stdoutData[0],
            })
        })

        proc.stderr.on('data', (data) => {
            message.error(data.toString())
        })

        proc.on('close', (code) => {
            if (code !== 0) {
                message.error('Fatal error, please restart the simulator')
                console.error(`Can't get interpolation modes... exited with ${code}`)
            }
        })
    };

    setOutputFilePath = async (filePath: string) => {
        this.setState({
            outputVideoPath: filePath,
        });


        // filePath length
        if (filePath.length === 0) {
            this.setState({
                outputValidator: { status: "error", help: pleaseInput }
            })
            return;
        }

        // check directory exists
        const dirname = path.dirname(filePath);
        if (!fs.existsSync(dirname)) {
            this.setState({
                outputValidator: { status: "error", help: "Directory does not exist." }
            });
            return;
        }

        // match extensions
        const { inputVideoPath } = this.state;
        const srcExt = path.extname(inputVideoPath).substr(1);
        if (srcExt !== path.extname(filePath).substr(1)) {
            this.setState({
                outputValidator: { status: "error", help: "File extension do not match with input." }
            });
            return;
        }

        this.setState({
            outputValidator: { status: "success", help: '' }
        })

    }

    setInputFilePath = async (filePath: string) => {
        // console.log(`Setting filePath to ${filePath}`);

        this.setState({
            inputVideoPath: filePath,
            inputVideoMetadata: undefined
        })

        // filePath length
        if (filePath.length === 0) {
            this.setState({
                inputValidator: { status: "error", help: pleaseInput }
            })
            return;
        }

        // check exists first
        const fileExists = fs.existsSync(filePath);
        if (!fileExists) {
            this.setState({
                inputValidator: { status: "error", help: 'File does not exist.' }
            })
            return;
        }

        // extension is supported
        const ext = path.extname(filePath).substr(1);
        // console.log(ext);
        if (supportedVideoFormats.indexOf(ext) === -1) {
            this.setState({
                inputValidator: { status: "error", help: 'Format is not supported.' }
            })
            return;
        }

        // load into python
        const args = [binName, `-m`, filePath];
        const proc = cp.spawn(python3, args)

        let stdoutData: VideoMetadata;
        proc.stdout.on('data', (data) => {
            // console.log(`Gotten stdout: ${data}`);
            stdoutData = JSON.parse(data);
            this.setState({
                inputVideoMetadata: stdoutData,
            })
        })

        proc.stderr.on('data', (data) => {
            // message.error(data.toString())
        })

        proc.on('close', (code) => {
            if (code === 0) {
                // in here we need to set also the outputVideoPath
                const fileName = path.basename(filePath);
                const fileExt = path.extname(fileName).substr(1);
                const fileDir = path.dirname(filePath);

                const fileNameWithoutExt = fileName.slice(0, -(fileExt.length + 1));

                const outputPath = `${fileDir}${path.sep}${fileNameWithoutExt}_output.${fileExt}`

                this.setOutputFilePath(outputPath);

                this.setState({
                    inputValidator: { status: "success", help: "" }
                })
            }
            else {
                this.setState({
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
        this.setState({
            targetFPS: fps,
        })
    }

    handleInterpolationModeChange = async (mode: string) => {
        this.setState({
            interpolationMode: mode,
        });
    }

    startConvert = () => {
        console.log('start boi');
    }

    render() {
        const { inputVideoPath, inputVideoMetadata, outputVideoPath, targetFPS, interpolationMode, supportedInterpolationModes, inputValidator, outputValidator } = this.state;

        const disabled = inputValidator.status === "error";

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
                            onSearch={() => {
                                const filePath = remote.dialog.showOpenDialogSync(
                                    { properties: ['openFile'], filters: [{ name: 'Videos', extensions: supportedVideoFormats }] }
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
                            onSearch={() => {
                                const srcExtension = path.extname(inputVideoPath).substr(1)

                                const filePath = remote.dialog.showOpenDialogSync(
                                    { properties: ['openFile'], filters: [{ name: 'Video', extensions: [srcExtension] }] }
                                )

                                if (filePath && filePath.length) {
                                    this.setOutputFilePath(filePath[0]);
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
                                    return (<Radio.Button key={fps} value={fps}>{fps}</Radio.Button>)
                                }))
                            }
                        </Radio.Group>
                    </Form.Item>


                    <Form.Item
                        label={<h3>Interpolation Mode</h3>}
                    >
                        <Select value={interpolationMode} onChange={this.handleInterpolationModeChange}
                            disabled={disabled}>
                            {
                                (supportedInterpolationModes.map((m) => {
                                    return (<Option key={m} value={m}>{m}</Option>)
                                }))
                            }
                        </Select>
                    </Form.Item>

                </Form>

                <div style={{ margin: 'auto', textAlign: 'center', marginTop: 48 }}>
                    <Button onClick={this.startConvert} size="large" disabled={disabled} type="primary">Start Conversion</Button>

                </div>

            </div>
        )
    }

}

export default Convert;